import datetime as dt
import sys
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, models
from ..queue_manager import queue_manager


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

    async def schedule_next_vehicle(self, db: AsyncSession):
        """
        The main scheduling logic. Checks for available pile slots and schedules
        the next vehicle from the appropriate waiting queue based on FIFO and best fit.
        """
        # Find all piles that have space in their queue (capacity > current length)
        available_piles_map: Dict[models.PileType, List[models.ChargingPile]] = {
            models.PileType.FAST: [],
            models.PileType.TRICKLE: [],
        }

        all_piles = await crud.get_piles(db, limit=100)
        for pile in all_piles:
            if pile.status not in [models.PileStatus.FAULTY, models.PileStatus.OFF]:
                if len(queue_manager.pile_queues.get(pile.pile_id, [])) < queue_manager.pile_queue_capacity:
                    available_piles_map[pile.type].append(pile)

        # Attempt to schedule from the FAST queue first
        if available_piles_map[models.PileType.FAST] and queue_manager.waiting_queue_fast:
            request_to_schedule = queue_manager.waiting_queue_fast[0]  # Peek, don't pop yet
            best_pile, _ = await self._find_best_pile_for_request(
                request_to_schedule, available_piles_map[models.PileType.FAST], db
            )

            if best_pile:
                queue_manager.waiting_queue_fast.popleft()  # Now pop
                await self._assign_request_to_pile(db, request_to_schedule, best_pile)

        # Attempt to schedule from the TRICKLE queue
        if available_piles_map[models.PileType.TRICKLE] and queue_manager.waiting_queue_trickle:
            request_to_schedule = queue_manager.waiting_queue_trickle[0]  # Peek
            best_pile, _ = await self._find_best_pile_for_request(
                request_to_schedule, available_piles_map[models.PileType.TRICKLE], db
            )

            if best_pile:
                queue_manager.waiting_queue_trickle.popleft()  # Now pop
                await self._assign_request_to_pile(db, request_to_schedule, best_pile)


# Global instance of the scheduling service
scheduling_service = SchedulingService()
