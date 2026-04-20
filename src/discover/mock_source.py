"""Mock job discovery source for testing."""

from typing import AsyncIterator

from src.discover.base import Source
from src.normalize.models import Job


class MockSource(Source):
    """Mock source that returns sample jobs."""
    
    @property
    def name(self) -> str:
        """Source identifier."""
        return "mock"
    
    async def discover(self) -> AsyncIterator[Job]:
        """
        Yield sample jobs for testing.
        
        Yields:
            Sample Job objects.
        """
        sample_jobs = [
            Job(
                title="Senior Python Engineer",
                company="TechCorp",
                url="https://example.com/job/1",
                description="Backend engineering role",
                location="San Francisco, CA",
                salary_min=150000,
                salary_max=200000,
                source="mock"
            ),
            Job(
                title="Data Scientist",
                company="DataInc",
                url="https://example.com/job/2",
                description="ML/AI specialist needed",
                location="Remote",
                salary_min=120000,
                salary_max=180000,
                source="mock"
            ),
        ]
        
        for job in sample_jobs:
            yield job
