from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, models, schemas


class PileSimulatorService:
    """
    Simulates the behavior of charging piles, including status changes
    and reporting data back to the system.
    """

    async def simulate_pile_behavior(self, db: AsyncSession, pile_id: int):
        """
        Main simulation loop for a single pile. This would be run as a
        separate task for each pile in a real simulation environment.
        """
        pile = await crud.get_pile(db, pile_id=pile_id)
        if not pile:
            print(f"Simulator: Pile {pile_id} not found.")
            return

        # This is a placeholder for more complex simulation logic.
        # In a real system, this service would listen to events from the pile hardware.
        # Here, we'll just log its current state periodically.

        log_create = schemas.PileLogCreate(
            pile_id=pile.pile_id,
            event_type="SIMULATOR_HEARTBEAT",
            details=f"Pile '{pile.pile_code}' is currently in state '{pile.status.value}'",
        )
        await crud.create_pile_log(db, log=log_create)

    async def update_pile_status_from_system(
        self, db: AsyncSession, pile_id: int, new_status: models.PileStatus, details: str
    ):
        """
        Allows the system to command a status change on the pile and logs the event.
        This simulates an admin turning a pile ON/OFF or marking it as FAULTY.
        """
        pile = await crud.get_pile(db, pile_id=pile_id)
        if not pile:
            raise ValueError(f"Pile with ID {pile_id} not found.")

        old_status = pile.status
        if old_status != new_status:
            pile.status = new_status
            await db.commit()
            await db.refresh(pile)

            log_create = schemas.PileLogCreate(
                pile_id=pile.pile_id,
                event_type="STATUS_CHANGE_COMMAND",
                details=f"Status changed from {old_status.value} to {new_status.value}. Reason: {details}",
            )
            await crud.create_pile_log(db, log=log_create)
            print(f"Pile {pile.pile_code} status changed to {new_status.value}")

            # Update in-memory representation if necessary
            # This part is crucial for the scheduler to see the change instantly.
            # (Currently, scheduler refetches piles, so this is implicitly handled)

        return pile


# Global instance of the pile simulator service
pile_simulator_service = PileSimulatorService()
