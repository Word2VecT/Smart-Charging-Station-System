import datetime as dt
from decimal import Decimal
from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, models
from ..queue_manager import queue_manager
from ..services.billing_service import billing_service


class FaultService:
    """
    Handles fault reporting and management for charging piles.
    """

    async def handle_pile_fault(self, db: AsyncSession, pile_id: int) -> Dict[str, Any]:
        """
        Handles a fault report for a charging pile. This is a single transactional operation.
        """
        pile = await crud.get_pile(db, pile_id)
        if not pile:
            return {"error": "充电桩不存在"}
        if pile.status == models.PileStatus.FAULTY:
            return {"error": "充电桩已经处于故障状态"}
        if pile.status == models.PileStatus.OFF:
            return {"error": "充电桩已关闭，无法上报故障"}

        # Fallback: if in-memory queue is out of sync, find charging request from DB
        pile_queue = queue_manager.pile_queues.get(pile.pile_id)
        charging_request = None
        if pile_queue:
            charging_request = pile_queue[0] if pile_queue[0].status == models.RequestStatus.CHARGING else None

        if not charging_request:
            charging_request = await crud.get_charging_request_by_pile_id(db, pile_id)

        result = {
            "error": None,
            "pile_id": pile_id,
            "stopped_charging": False,
            "requeued_request_id": None,
            "bill_generated": False,
        }

        if (
            charging_request
            and charging_request.status == models.RequestStatus.CHARGING
            and charging_request.start_time
        ):
            # Step 1: Stop ongoing charging session and generate bill
            end_time = dt.datetime.now(dt.timezone.utc)
            duration_seconds = (end_time - charging_request.start_time).total_seconds()
            actual_charge_amount = (Decimal(duration_seconds) / Decimal(3600)) * pile.power_rate

            if actual_charge_amount < 0:
                actual_charge_amount = Decimal(0)

            # Create bill, but don't commit yet
            await billing_service.create_final_order(db, charging_request, pile, end_time, actual_charge_amount)
            result["bill_generated"] = True
            result["stopped_charging"] = True

            # Mark original request as finished
            charging_request.status = models.RequestStatus.FINISHED
            charging_request.end_time = end_time
            await db.merge(charging_request)

            # Step 2: Re-queue remaining charge amount
            remaining_charge = charging_request.requested_charge_amount - actual_charge_amount
            if remaining_charge > Decimal("0.1"):  # Only requeue if a meaningful amount is left
                new_req = await self._requeue_remaining_charge(db, charging_request, remaining_charge)
                result["requeued_request_id"] = new_req.request_id

        # Step 3: Clear in-memory pile queue and set pile status to FAULTY
        if pile_queue:
            pile_queue.clear()

        pile.status = models.PileStatus.FAULTY
        await db.merge(pile)

        # Step 4: Log the event
        await self._log_fault_event(db, pile_id, "USER_REPORTED_FAULT", "用户上报充电桩故障")

        # Step 5: Commit all changes as a single transaction
        await db.commit()

        return result

    async def _requeue_remaining_charge(
        self,
        db: AsyncSession,
        original_request: models.ChargingRequest,
        remaining_charge: Decimal,
    ) -> models.ChargingRequest:
        """
        Creates a new request for the remaining charge and adds it to the front of the waiting queue.
        Does not commit.
        """
        new_queue_number = queue_manager._generate_queue_number(original_request.requested_charge_type)
        new_request = models.ChargingRequest(
            user_id=original_request.user_id,
            queue_number=new_queue_number,
            requested_charge_type=original_request.requested_charge_type,
            requested_charge_amount=remaining_charge,
            status=models.RequestStatus.WAITING,
            request_time=dt.datetime.now(dt.timezone.utc),
        )
        db.add(new_request)
        await db.flush()  # Flush to get the new request_id without committing
        await db.refresh(new_request)

        if new_request.requested_charge_type == models.RequestType.FAST:
            queue_manager.waiting_queue_fast.appendleft(new_request)
        else:
            queue_manager.waiting_queue_trickle.appendleft(new_request)

        return new_request

    async def _log_fault_event(self, db: AsyncSession, pile_id: int, event_type: str, details: str):
        """
        Logs a fault event. Does not commit.
        """
        log_entry = models.PileLog(pile_id=pile_id, event_type=event_type, details=details)
        db.add(log_entry)


fault_service = FaultService()
