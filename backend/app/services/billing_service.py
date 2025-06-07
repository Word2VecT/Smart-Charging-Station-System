import datetime as dt
from decimal import Decimal
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, models, schemas
from ..queue_manager import queue_manager


class BillingService:
    """
    Handles billing, fee calculation, and order generation.
    """

    SERVICE_FEE_PER_KWH = Decimal("0.8")

    # Time-of-use (TOU) tariff periods (in UTC, assuming server runs in UTC)
    # The prices are in Yuan per kWh.
    # To handle timezones correctly in a real app, all times should be UTC.
    TOU_TARIFFS = [
        # Peak: 10:00–15:00, 18:00–21:00
        {"start_hour": 10, "end_hour": 15, "rate": Decimal("1.0")},
        {"start_hour": 18, "end_hour": 21, "rate": Decimal("1.0")},
        # Standard: 07:00–10:00, 15:00–18:00, 21:00–23:00
        {"start_hour": 7, "end_hour": 10, "rate": Decimal("0.7")},
        {"start_hour": 15, "end_hour": 18, "rate": Decimal("0.7")},
        {"start_hour": 21, "end_hour": 23, "rate": Decimal("0.7")},
        # Off-peak: 23:00–次日07:00
        {"start_hour": 23, "end_hour": 24, "rate": Decimal("0.4")},
        {"start_hour": 0, "end_hour": 7, "rate": Decimal("0.4")},
    ]

    def get_price_for_time(self, timestamp: dt.datetime) -> Decimal:
        """Gets the electricity rate for a specific timestamp."""
        hour = timestamp.hour
        for tariff in self.TOU_TARIFFS:
            if tariff["start_hour"] <= hour < tariff["end_hour"]:
                return tariff["rate"]
        # This should not be reached if tariffs cover 24h
        return Decimal("0.7")  # Default to standard rate

    def calculate_charge_fee(self, start_time: dt.datetime, end_time: dt.datetime, power_rate_kw: Decimal) -> Decimal:
        """
        Calculates the total charge fee for a session, accurately handling TOU changes.
        """
        total_fee = Decimal(0)
        energy_per_second = power_rate_kw / Decimal(3600)

        current_time = start_time
        while current_time < end_time:
            # Determine the end of the current tariff block or the end of the charge
            rate = self.get_price_for_time(current_time)
            next_hour = (current_time + dt.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)

            # Find the next boundary (either next hour or end of charge)
            boundary_time = min(end_time, next_hour)

            duration_in_block = (boundary_time - current_time).total_seconds()

            if duration_in_block > 0:
                energy_in_block = Decimal(duration_in_block) * energy_per_second
                total_fee += energy_in_block * rate

            current_time = boundary_time

        return total_fee

    async def finish_charging_session(
        self, db: AsyncSession, request_id: int, end_time: dt.datetime, actual_charge_amount: Decimal
    ) -> Optional[models.ChargingOrder]:
        """
        Finalizes a charging session: calculates fees, creates an order, and updates system state.
        """
        request = await crud.get_request(db, request_id)
        if not request or not request.start_time or not request.assigned_pile_id:
            return None  # Cannot process if request is invalid or hasn't started

        pile = await crud.get_pile(db, request.assigned_pile_id)
        if not pile:
            return None

        # 1. Calculate fees
        charge_fee = self.calculate_charge_fee(request.start_time, end_time, pile.power_rate)
        service_fee = actual_charge_amount * self.SERVICE_FEE_PER_KWH
        total_fee = charge_fee + service_fee

        # 2. Create ChargingOrder
        order_create = schemas.ChargingOrderCreate(
            request_id=request.request_id,
            user_id=request.user_id,
            pile_id=pile.pile_id,
            start_time=request.start_time,
            end_time=end_time,
            actual_charge_amount=round(actual_charge_amount, 2),
            charge_fee=round(charge_fee, 2),
            service_fee=round(service_fee, 2),
            total_fee=round(total_fee, 2),
        )
        order = await crud.create_order(db, order=order_create)

        # 3. Update related entities
        request.status = models.RequestStatus.FINISHED
        request.end_time = end_time

        pile_queue = queue_manager.pile_queues.get(pile.pile_id)
        if pile_queue:
            # Remove the finished request from the in-memory queue
            # This is a simple but potentially slow approach for a deque
            new_deque = [r for r in pile_queue if r.request_id != request.request_id]
            pile_queue.clear()
            pile_queue.extend(new_deque)

        # 4. Check if a new vehicle can start charging at the same pile
        if pile_queue:
            # There is another vehicle waiting at the pile, start it.
            next_request = pile_queue[0]
            next_request.status = models.RequestStatus.CHARGING
            next_request.start_time = dt.datetime.now(dt.timezone.utc)
            pile.status = models.PileStatus.CHARGING
            await db.merge(next_request)
        else:
            # The pile is now free
            pile.status = models.PileStatus.AVAILABLE

        await db.merge(request)
        await db.merge(pile)
        await db.commit()

        # Refresh the instances to get the latest state from the DB, including server-side defaults
        await db.refresh(order)
        await db.refresh(request)
        order.request = request  # Manually attach the refreshed request

        print(f"Session finished for request {request.queue_number}. Order {order.order_id} created.")
        return order


# Global instance
billing_service = BillingService()
