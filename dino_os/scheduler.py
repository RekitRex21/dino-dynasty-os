"""Scheduler - Cron-style job scheduling for Dino Dynasty OS."""

import asyncio
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class ScheduleType(Enum):
    """Type of schedule."""
    CRON = "cron"
    INTERVAL = "interval"
    ONCE = "once"


@dataclass
class ScheduledJob:
    """Represents a scheduled job."""
    id: str
    schedule_type: ScheduleType
    schedule: str  # cron expression, interval in seconds, or datetime for once
    func: Callable
    args: tuple
    kwargs: dict
    next_run: Optional[datetime]
    enabled: bool = True


class Scheduler:
    """Cron-style job scheduler."""
    
    # Cron pattern: minute hour day month day_of_week
    CRON_PATTERN = re.compile(r'^(\*|[0-9,/-]+)\s+(\*|[0-9,/-]+)\s+(\*|[0-9,/-]+)\s+(\*|[0-9,/-]+)\s+(\*|[0-9,/-]+)$')

    def __init__(self):
        """Initialize the scheduler."""
        self._jobs: Dict[str, ScheduledJob] = {}
        self._running = False
        self._task: Optional[asyncio.Task] = None

    def add_cron_job(self, job_id: str, cron_expr: str, func: Callable, *args, **kwargs) -> bool:
        """Add a cron-style job.
        
        Args:
            job_id: Unique job identifier
            cron_expr: Cron expression (min hour day month dow)
            func: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            True if added successfully.
        """
        if not self.CRON_PATTERN.match(cron_expr):
            return False
        
        job = ScheduledJob(
            id=job_id,
            schedule_type=ScheduleType.CRON,
            schedule=cron_expr,
            func=func,
            args=args,
            kwargs=kwargs,
            next_run=self._get_next_cron_time(cron_expr),
            enabled=True
        )
        self._jobs[job_id] = job
        return True

    def add_interval_job(self, job_id: str, seconds: int, func: Callable, *args, **kwargs) -> None:
        """Add an interval job.
        
        Args:
            job_id: Unique job identifier
            seconds: Interval in seconds
            func: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments
        """
        job = ScheduledJob(
            id=job_id,
            schedule_type=ScheduleType.INTERVAL,
            schedule=str(seconds),
            func=func,
            args=args,
            kwargs=kwargs,
            next_run=datetime.utcnow(),
            enabled=True
        )
        self._jobs[job_id] = job

    def add_one_shot_job(self, job_id: str, run_at: datetime, func: Callable, *args, **kwargs) -> None:
        """Add a one-time job.
        
        Args:
            job_id: Unique job identifier
            run_at: When to run
            func: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments
        """
        job = ScheduledJob(
            id=job_id,
            schedule_type=ScheduleType.ONCE,
            schedule=run_at.isoformat(),
            func=func,
            args=args,
            kwargs=kwargs,
            next_run=run_at,
            enabled=True
        )
        self._jobs[job_id] = job

    def remove_job(self, job_id: str) -> bool:
        """Remove a job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if removed.
        """
        return self._jobs.pop(job_id, None) is not None

    def get_job(self, job_id: str) -> Optional[ScheduledJob]:
        """Get a job by ID."""
        return self._jobs.get(job_id)

    def list_jobs(self) -> List[Dict[str, Any]]:
        """List all jobs."""
        return [
            {
                "id": job.id,
                "type": job.schedule_type.value,
                "schedule": job.schedule,
                "next_run": job.next_run.isoformat() if job.next_run else None,
                "enabled": job.enabled
            }
            for job in self._jobs.values()
        ]

    async def start(self) -> None:
        """Start the scheduler."""
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._run_loop())

    async def stop(self) -> None:
        """Stop the scheduler."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _run_loop(self) -> None:
        """Main scheduler loop."""
        while self._running:
            now = datetime.utcnow()
            for job_id, job in list(self._jobs.items()):
                if not job.enabled:
                    continue
                if job.next_run and now >= job.next_run:
                    # Run the job
                    try:
                        if asyncio.iscoroutinefunction(job.func):
                            await job.func(*job.args, **job.kwargs)
                        else:
                            job.func(*job.args, **job.kwargs)
                    except Exception as e:
                        print(f"Scheduler job {job_id} error: {e}")
                    
                    # Schedule next run
                    if job.schedule_type == ScheduleType.INTERVAL:
                        interval = int(job.schedule)
                        job.next_run = now.replace(microsecond=0)
                    elif job.schedule_type == ScheduleType.ONCE:
                        self._jobs.pop(job_id, None)
                        continue
                    elif job.schedule_type == ScheduleType.CRON:
                        job.next_run = self._get_next_cron_time(job.schedule)
            
            await asyncio.sleep(1)

    def _get_next_cron_time(self, cron_expr: str) -> datetime:
        """Calculate next run time from cron expression.
        
        This is a simplified implementation.
        """
        now = datetime.utcnow()
        parts = cron_expr.split()
        if len(parts) != 5:
            return now
        
        # Simple implementation: if current time matches, return next hour/day
        minute, hour, _, _, _ = parts
        
        next_minute = now.minute + 1
        next_hour = now.hour
        next_day = now.day
        
        if next_minute >= 60:
            next_minute = 0
            next_hour += 1
        if next_hour >= 24:
            next_hour = 0
            next_day += 1
        
        return now.replace(day=next_day, hour=next_hour, minute=next_minute, second=0, microsecond=0)
