import datetime as dt

from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud
from ..queue_manager import queue_manager
from ..services.billing_service import billing_service


class ChargingMonitorService:
    """
    Monitors active charging sessions and finalizes them upon completion.
    """

    async def check_completed_charges(self, db: AsyncSession):
        """
        Iterates through all active charging piles, checks if the currently
        charging vehicle has finished, and if so, processes the session completion.
        """
        now = dt.datetime.now(dt.timezone.utc)

        # Iterate over a copy of pile_queues' items to avoid issues with modification during iteration
        for pile_id, pile_queue in list(queue_manager.pile_queues.items()):
            if not pile_queue:
                continue

            # The first request in the queue is the one currently charging
            charging_request = pile_queue[0]

            if charging_request.status != "CHARGING" or not charging_request.start_time:
                continue

            pile = await crud.get_pile(db, pile_id)
            if not pile or pile.power_rate <= 0:
                continue

            # Calculate estimated completion time
            charge_duration_hours = charging_request.requested_charge_amount / pile.power_rate
            estimated_end_time = charging_request.start_time + dt.timedelta(hours=float(charge_duration_hours))

            if now >= estimated_end_time:
                print(f"Charge for request {charging_request.queue_number} seems to be complete. Finalizing...")
                await billing_service.finish_charging_session(
                    db=db,
                    request_id=charging_request.request_id,
                    end_time=estimated_end_time,
                    actual_charge_amount=charging_request.requested_charge_amount,
                )


# Global instance
charging_monitor_service = ChargingMonitorService()
