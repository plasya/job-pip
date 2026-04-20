"""Base classes for job discovery sources."""

from abc import ABC, abstractmethod
from typing import AsyncIterator

from src.normalize.models import Job


class Source(ABC):
    """Abstract base class for job discovery sources."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Source identifier."""
        pass
    
    @abstractmethod
    async def discover(self) -> AsyncIterator[Job]:
        """
        Discover jobs from this source.
        
        Yields:
            Job objects discovered from source.
        """
        pass
