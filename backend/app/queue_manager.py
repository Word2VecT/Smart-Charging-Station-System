from collections import deque
from typing import Deque, Dict, List, Optional, Tuple

import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from . import crud, models, schemas


class QueueManager:
    """
    Manages the waiting area and charging pile queues in memory.
    """

    def __init__(self, waiting_area_capacity: int = 6, pile_queue_capacity: int = 2):
        self.waiting_area_capacity = waiting_area_capacity
        self.pile_queue_capacity = pile_queue_capacity

        # In-memory queues for requests waiting for a pile
        self.waiting_queue_fast: Deque[models.ChargingRequest] = deque()
        self.waiting_queue_trickle: Deque[models.ChargingRequest] = deque()

        # In-memory queues for each pile (1 charging + 1 waiting)
        self.pile_queues: Dict[int, Deque[models.ChargingRequest]] = {}

        # Queue number counters
        self.fast_queue_counter = 1
        self.trickle_queue_counter = 1

    async def initialize(self, db: AsyncSession):
        """
        Initialize queues and counters from the database state on startup.
        This makes the queue manager resilient to server restarts.
        """
        print("Initializing QueueManager...")

        # Initialize pile queues from database
        piles = await crud.get_piles(db, limit=100)
        for pile in piles:
            self.pile_queues[pile.pile_id] = deque(maxlen=self.pile_queue_capacity)

        # Correctly initialize counters by finding the max queue number from ALL requests
        stmt_f = select(func.max(func.cast(func.substring(models.ChargingRequest.queue_number, 2), sa.Integer))).where(
            models.ChargingRequest.queue_number.startswith("F")
        )
        stmt_t = select(func.max(func.cast(func.substring(models.ChargingRequest.queue_number, 2), sa.Integer))).where(
            models.ChargingRequest.queue_number.startswith("T")
        )

        max_f_num = await db.scalar(stmt_f) or 0
        max_t_num = await db.scalar(stmt_t) or 0

        self.fast_queue_counter = max_f_num + 1
        self.trickle_queue_counter = max_t_num + 1

        # Load requests that are in 'WAITING' or 'CHARGING' state to populate in-memory queues
        stmt = (
            select(models.ChargingRequest)
            .filter(models.ChargingRequest.status.in_([models.RequestStatus.WAITING, models.RequestStatus.CHARGING]))
            .order_by(models.ChargingRequest.request_time)
        )
        result = await db.execute(stmt)
        active_requests = result.scalars().all()
        self._process_active_requests(active_requests)

        print("QueueManager initialized.")
        print(f"Waiting Fast: {len(self.waiting_queue_fast)}, Waiting Trickle: {len(self.waiting_queue_trickle)}")
        print(f"Next F#: {self.fast_queue_counter}, Next T#: {self.trickle_queue_counter}")

    def _process_active_requests(self, requests: List[models.ChargingRequest]):
        """Helper to populate in-memory queues from a list of active requests."""
        for req in requests:
            # Assign request to the correct queue
            if req.status == models.RequestStatus.WAITING:
                if req.requested_charge_type == models.RequestType.FAST:
                    self.waiting_queue_fast.append(req)
                else:
                    self.waiting_queue_trickle.append(req)
            elif req.status == models.RequestStatus.CHARGING and req.assigned_pile_id:
                if req.assigned_pile_id in self.pile_queues:
                    self.pile_queues[req.assigned_pile_id].append(req)

    def _generate_queue_number(self, charge_type: schemas.RequestType) -> str:
        """Generates a sequential queue number based on charge type."""
        if charge_type == schemas.RequestType.FAST:
            num = self.fast_queue_counter
            self.fast_queue_counter += 1
            return f"F{num}"
        else:  # TRICKLE
            num = self.trickle_queue_counter
            self.trickle_queue_counter += 1
            return f"T{num}"

    async def add_request_to_waiting_queue(
        self, db: AsyncSession, request: schemas.ChargingRequestCreate
    ) -> Tuple[Optional[models.ChargingRequest], Optional[str]]:
        """
        Adds a new charging request to the appropriate waiting queue.
        Returns the created request object and an error message if any.
        """
        current_waiting_count = len(self.waiting_queue_fast) + len(self.waiting_queue_trickle)
        if current_waiting_count >= self.waiting_area_capacity:
            return None, "Waiting area is full."

        queue_number = self._generate_queue_number(request.requested_charge_type)

        # Use the existing CRUD function to create the request
        # We need to adapt the schema or the CRUD function. Let's create a full schema object.
        full_request_data = models.ChargingRequest(
            **request.dict(), queue_number=queue_number, status=models.RequestStatus.WAITING
        )

        db.add(full_request_data)
        await db.commit()
        await db.refresh(full_request_data)

        # Add to the correct in-memory waiting queue
        if full_request_data.requested_charge_type == models.RequestType.FAST:
            self.waiting_queue_fast.append(full_request_data)
        else:
            self.waiting_queue_trickle.append(full_request_data)

        return full_request_data, None

    async def cancel_request(
        self, db: AsyncSession, request_id: int, user_id: int
    ) -> Tuple[Optional[models.ChargingRequest], Optional[str]]:
        """
        Cancels a request that is currently in a waiting queue.
        """
        # Find which queue the request is in and remove it
        target_request = None

        # Check fast queue
        for req in self.waiting_queue_fast:
            if req.request_id == request_id:
                if req.user_id != user_id:
                    return None, "Permission denied: You can only cancel your own requests."
                target_request = req
                self.waiting_queue_fast.remove(req)
                break

        # Check trickle queue if not found
        if not target_request:
            for req in self.waiting_queue_trickle:
                if req.request_id == request_id:
                    if req.user_id != user_id:
                        return None, "Permission denied: You can only cancel your own requests."
                    target_request = req
                    self.waiting_queue_trickle.remove(req)
                    break

        if not target_request:
            # Maybe the request is already charging or finished, check DB
            db_req = await crud.get_request(db, request_id)
            if db_req:
                return (
                    None,
                    f"Request is in status '{db_req.status.value}' and cannot be cancelled from here. Try stopping the charge if it's ongoing.",
                )
            return None, "Request not found in any active queue."

        # Update status in DB
        target_request.status = models.RequestStatus.CANCELLED
        merged_request = await db.merge(target_request)
        await db.commit()
        await db.refresh(merged_request)

        return merged_request, None

    async def modify_request(
        self,
        db: AsyncSession,
        request_id: int,
        user_id: int,
        updates: schemas.ChargingRequestUpdate,
    ) -> Tuple[Optional[models.ChargingRequest], Optional[str]]:
        """
        Modifies a request in the waiting queue.
        - Changing charge amount keeps the queue position.
        - Changing charge type moves the request to the end of the new queue.
        """
        # Find the request in the waiting queues
        original_request = None
        original_queue = None

        for req in self.waiting_queue_fast:
            if req.request_id == request_id:
                original_request = req
                original_queue = self.waiting_queue_fast
                break
        if not original_request:
            for req in self.waiting_queue_trickle:
                if req.request_id == request_id:
                    original_request = req
                    original_queue = self.waiting_queue_trickle
                    break

        if not original_request or not original_queue:
            db_req = await crud.get_request(db, request_id)
            if db_req:
                return None, f"Request is in status '{db_req.status.value}' and cannot be modified."
            return None, "Request not found in any active queue."

        if original_request.user_id != user_id:
            return None, "Permission denied: You can only modify your own requests."

        # Apply updates
        update_data = updates.dict(exclude_unset=True)
        type_changed = (
            "requested_charge_type" in update_data
            and update_data["requested_charge_type"] != original_request.requested_charge_type
        )

        for key, value in update_data.items():
            setattr(original_request, key, value)

        if type_changed:
            # Type has changed, so move to the other queue with a new number
            original_queue.remove(original_request)
            new_queue_number = self._generate_queue_number(original_request.requested_charge_type)
            original_request.queue_number = new_queue_number

            if original_request.requested_charge_type == models.RequestType.FAST:
                self.waiting_queue_fast.append(original_request)
            else:
                self.waiting_queue_trickle.append(original_request)

        # Persist changes to DB
        merged_request = await db.merge(original_request)
        await db.commit()
        await db.refresh(merged_request)

        return merged_request, None


# Create a single, globally accessible instance of the QueueManager
queue_manager = QueueManager()
