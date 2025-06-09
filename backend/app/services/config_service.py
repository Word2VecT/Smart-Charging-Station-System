from enum import Enum


class SchedulingStrategy(str, Enum):
    SHORTEST_INDIVIDUAL_COMPLETION = "SHORTEST_INDIVIDUAL_COMPLETION"
    SHORTEST_BATCH_COMPLETION = "SHORTEST_BATCH_COMPLETION"
    BATCH_FULL_LOAD_SHORTEST_TIME = "BATCH_FULL_LOAD_SHORTEST_TIME"


class ConfigService:
    """
    Manages global application configuration and state.
    """

    def __init__(self):
        self._scheduling_strategy = SchedulingStrategy.SHORTEST_INDIVIDUAL_COMPLETION

    @property
    def scheduling_strategy(self) -> SchedulingStrategy:
        return self._scheduling_strategy

    def set_scheduling_strategy(self, strategy: SchedulingStrategy):
        if not isinstance(strategy, SchedulingStrategy):
            raise ValueError("Invalid scheduling strategy")
        self._scheduling_strategy = strategy


# Global instance of the config service
config_service = ConfigService()
