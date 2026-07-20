from abc import ABC, abstractmethod

from alpharadar.domain.entities.recommendation import Recommendation


class Notifier(ABC):
    @abstractmethod
    async def send(self, recommendation: Recommendation) -> bool:
        """Send recommendation notification. Returns True if successful."""
