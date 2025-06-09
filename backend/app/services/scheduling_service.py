import datetime as dt
import itertools
import sys
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, models
from ..queue_manager import queue_manager
from ..services.config_service import SchedulingStrategy, config_service


class SchedulingService:
    """
    Handles the logic for scheduling vehicles from the waiting queue to charging piles.
    """

    async def _get_charge_time_estimate_hours(
        self, request: models.ChargingRequest, pile: models.ChargingPile
    ) -> Decimal:
        """Calculates the estimated charging time in hours for a request at a given pile."""
        if pile.power_rate <= 0:
            return Decimal(sys.maxsize)  # Avoid division by zero
        return Decimal(request.requested_charge_amount) / Decimal(pile.power_rate)

    async def _get_pile_wait_time_hours(self, pile_id: int, db: AsyncSession) -> Decimal:
        """
        Calculates the total expected wait time for a new vehicle at a specific pile.
        This is the sum of the remaining charge times of all vehicles ahead of it in the pile's queue.
        """
        wait_time_hours = Decimal(0)
        pile_queue = queue_manager.pile_queues.get(pile_id)
        if not pile_queue:
            return wait_time_hours

        pile = await crud.get_pile(db, pile_id=pile_id)
        if not pile:
            return wait_time_hours

        for i, request_in_queue in enumerate(pile_queue):
            estimated_total_time = await self._get_charge_time_estimate_hours(request_in_queue, pile)

            if i == 0 and request_in_queue.status == models.RequestStatus.CHARGING and request_in_queue.start_time:
                # For the car currently charging, calculate remaining time.
                time_elapsed = dt.datetime.now(dt.timezone.utc) - request_in_queue.start_time
                elapsed_hours = Decimal(time_elapsed.total_seconds()) / Decimal(3600)
                remaining_time = estimated_total_time - elapsed_hours
                wait_time_hours += max(Decimal(0), remaining_time)
            else:
                # For cars waiting at the pile, add their full estimated charge time.
                wait_time_hours += estimated_total_time

        return wait_time_hours

    async def _find_best_pile_for_request(
        self, request: models.ChargingRequest, available_piles: List[models.ChargingPile], db: AsyncSession
    ) -> Tuple[Optional[models.ChargingPile], Decimal]:
        """
        Finds the best pile for a request by minimizing the total completion time.
        Total Completion Time = Wait Time at Pile + Vehicle's Own Charging Time.
        """
        best_pile = None
        min_completion_time = Decimal(sys.maxsize)

        for pile in available_piles:
            wait_time = await self._get_pile_wait_time_hours(pile.pile_id, db)
            self_charging_time = await self._get_charge_time_estimate_hours(request, pile)
            total_completion_time = wait_time + self_charging_time

            if total_completion_time < min_completion_time:
                min_completion_time = total_completion_time
                best_pile = pile

        return best_pile, min_completion_time

    async def _assign_request_to_pile(
        self, db: AsyncSession, request: models.ChargingRequest, pile: models.ChargingPile
    ):
        """Assigns a request to a pile, updating DB and in-memory queues."""
        print(f"Assigning request {request.queue_number} to pile {pile.pile_code}")

        # Update request state
        request.assigned_pile_id = pile.pile_id

        # If this is the first vehicle to be in the pile queue, it starts charging.
        is_first_in_queue = len(queue_manager.pile_queues[pile.pile_id]) == 0
        if is_first_in_queue:
            request.status = models.RequestStatus.CHARGING
            request.start_time = dt.datetime.now(dt.timezone.utc)
            pile.status = models.PileStatus.CHARGING
            await db.merge(pile)

        await db.merge(request)
        await db.commit()

        # Add to the pile's in-memory queue after DB commit
        queue_manager.pile_queues[pile.pile_id].append(request)

    async def _schedule_individual_shortest_completion(self, db: AsyncSession):
        """
        Strategy: Schedule one vehicle at a time to the pile that offers the
        shortest total completion time (wait + charge).
        """
        # Find all piles that have space in their queue
        available_piles_map: Dict[models.PileType, List[models.ChargingPile]] = {
            models.PileType.FAST: [],
            models.PileType.TRICKLE: [],
        }
        all_piles = await crud.get_available_piles(db)
        for pile in all_piles:
            if len(queue_manager.pile_queues.get(pile.pile_id, [])) < queue_manager.pile_queue_capacity:
                available_piles_map[pile.type].append(pile)

        # Attempt to schedule from the FAST queue first
        if available_piles_map[models.PileType.FAST] and queue_manager.waiting_queue_fast:
            request_to_schedule = queue_manager.waiting_queue_fast.popleft()
            best_pile, _ = await self._find_best_pile_for_request(
                request_to_schedule, available_piles_map[models.PileType.FAST], db
            )
            if best_pile:
                await self._assign_request_to_pile(db, request_to_schedule, best_pile)
            else:
                queue_manager.waiting_queue_fast.appendleft(request_to_schedule)  # Re-add if no pile found

        # Attempt to schedule from the TRICKLE queue
        if available_piles_map[models.PileType.TRICKLE] and queue_manager.waiting_queue_trickle:
            request_to_schedule = queue_manager.waiting_queue_trickle.popleft()
            best_pile, _ = await self._find_best_pile_for_request(
                request_to_schedule, available_piles_map[models.PileType.TRICKLE], db
            )
            if best_pile:
                await self._assign_request_to_pile(db, request_to_schedule, best_pile)
            else:
                queue_manager.waiting_queue_trickle.appendleft(request_to_schedule)  # Re-add if no pile found

    async def _schedule_batch_shortest_completion(self, db: AsyncSession):
        """
        Strategy: For each pile type, take a batch of waiting vehicles and find
        the optimal assignment to available piles to minimize total completion time for the batch.
        """
        for pile_type, waiting_queue in [
            (models.PileType.FAST, queue_manager.waiting_queue_fast),
            (models.PileType.TRICKLE, queue_manager.waiting_queue_trickle),
        ]:
            available_piles = [
                p
                for p in await crud.get_available_piles_by_type(db, pile_type)
                if len(queue_manager.pile_queues.get(p.pile_id, [])) < queue_manager.pile_queue_capacity
            ]
            if not available_piles or not waiting_queue:
                continue

            # Take a batch of N requests for M piles (N <= M)
            num_piles = len(available_piles)
            batch_requests = [waiting_queue[i] for i in range(min(len(waiting_queue), num_piles))]
            if not batch_requests:
                continue

            best_assignment = None
            min_total_time = Decimal(sys.maxsize)

            # Generate all possible assignments of requests to piles
            for pile_permutation in itertools.permutations(available_piles, len(batch_requests)):
                current_total_time = Decimal(0)
                for request, pile in zip(batch_requests, pile_permutation):
                    wait_time = await self._get_pile_wait_time_hours(pile.pile_id, db)
                    charge_time = await self._get_charge_time_estimate_hours(request, pile)
                    current_total_time += wait_time + charge_time

                if current_total_time < min_total_time:
                    min_total_time = current_total_time
                    best_assignment = list(zip(batch_requests, pile_permutation))

            # Assign based on the best permutation found
            if best_assignment:
                for request, pile in best_assignment:
                    await self._assign_request_to_pile(db, request, pile)
                    waiting_queue.remove(request)  # Remove from waiting queue

    async def _is_any_pile_active(self, db: AsyncSession) -> bool:
        """Check if any pile is currently charging or has a waiting queue."""
        for pile_id in queue_manager.pile_queues:
            if len(queue_manager.pile_queues[pile_id]) > 0:
                return True
        return False

    async def _schedule_batch_full_load_shortest_time(self, db: AsyncSession):
        """
        Strategy: When waiting cars == available piles, schedule them all to
        minimize total batch completion time, ignoring request charge type.
        """
        # Condition 1: No piles should be currently active (charging or with a queue)
        if await self._is_any_pile_active(db):
            return

        all_available_piles = await crud.get_available_piles(db)
        all_waiting_requests = list(queue_manager.waiting_queue_fast) + list(queue_manager.waiting_queue_trickle)

        # Condition 2: Number of waiting requests must equal number of available piles
        if not all_waiting_requests or len(all_waiting_requests) != len(all_available_piles):
            return

        print(f"Full load condition met: {len(all_waiting_requests)} vehicles, {len(all_available_piles)} piles.")

        best_assignment = None
        min_total_time = Decimal(sys.maxsize)

        # Find the optimal assignment of all vehicles to all piles
        for pile_permutation in itertools.permutations(all_available_piles, len(all_waiting_requests)):
            current_total_time = Decimal(0)
            # In this strategy, wait time is 0 since we start with all empty piles
            for request, pile in zip(all_waiting_requests, pile_permutation):
                charge_time = await self._get_charge_time_estimate_hours(request, pile)
                current_total_time += charge_time  # Wait time is 0 for all

            if current_total_time < min_total_time:
                min_total_time = current_total_time
                best_assignment = list(zip(all_waiting_requests, pile_permutation))

        if best_assignment:
            print(f"Found best full load assignment with total time: {min_total_time}")
            for request, pile in best_assignment:
                await self._assign_request_to_pile(db, request, pile)

            # Clear waiting queues as all have been scheduled
            queue_manager.waiting_queue_fast.clear()
            queue_manager.waiting_queue_trickle.clear()

    async def schedule_next_vehicle(self, db: AsyncSession):
        """
        The main scheduling logic. Dispatches to the correct strategy.
        """
        strategy = config_service.scheduling_strategy
        if strategy == SchedulingStrategy.SHORTEST_INDIVIDUAL_COMPLETION:
            await self._schedule_individual_shortest_completion(db)
        elif strategy == SchedulingStrategy.SHORTEST_BATCH_COMPLETION:
            await self._schedule_batch_shortest_completion(db)
        elif strategy == SchedulingStrategy.BATCH_FULL_LOAD_SHORTEST_TIME:
            await self._schedule_batch_full_load_shortest_time(db)
        else:
            print(f"Unknown scheduling strategy: {strategy}")
            return

        await db.commit()


# Global instance of the scheduling service
scheduling_service = SchedulingService()
