"""
Time Management and Scheduling System for JARVIS
Handles task scheduling and time-based operations
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger

class TimeManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.timezone = pytz.timezone(config.get("timezone", "UTC"))
        self.min_buffer = timedelta(seconds=config.get("min_buffer_time", 300))
        self._initialize_scheduler()
        
    def _initialize_scheduler(self):
        """Initialize the task scheduler"""
        try:
            jobstores = {
                'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
            }
            
            self.scheduler = AsyncIOScheduler(
                jobstores=jobstores,
                timezone=self.timezone
            )
            
            # Don't start the scheduler during initialization
            self.logger.info("Scheduler initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize scheduler: {e}")
            raise
            
    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            
    def shutdown(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            
    async def schedule_task(self,
                          task_func: callable,
                          task_args: Dict[str, Any],
                          schedule_type: str,
                          schedule_params: Dict[str, Any],
                          task_id: Optional[str] = None) -> str:
        """
        Schedule a task for execution
        
        Args:
            task_func: Function to execute
            task_args: Arguments for the function
            schedule_type: Type of schedule ('once', 'interval', 'cron')
            schedule_params: Parameters for the schedule
            task_id: Optional task identifier
            
        Returns:
            Job ID of the scheduled task
        """
        try:
            # Validate and create trigger
            trigger = self._create_trigger(schedule_type, schedule_params)
            
            # Check for scheduling conflicts
            if not self._check_schedule_conflicts(trigger):
                raise ValueError("Schedule conflict detected")
                
            # Add job to scheduler
            job = self.scheduler.add_job(
                task_func,
                trigger=trigger,
                kwargs=task_args,
                id=task_id,
                replace_existing=True
            )
            
            self.logger.info(f"Scheduled task {job.id} successfully")
            return job.id
            
        except Exception as e:
            self.logger.error(f"Failed to schedule task: {e}")
            raise
            
    def _create_trigger(self,
                       schedule_type: str,
                       params: Dict[str, Any]) -> Any:
        """Create appropriate trigger based on schedule type"""
        if schedule_type == "once":
            run_time = params.get("run_time")
            if not run_time:
                raise ValueError("run_time parameter required for 'once' schedule")
            return DateTrigger(run_date=run_time, timezone=self.timezone)
            
        elif schedule_type == "interval":
            interval = params.get("interval")
            if not interval:
                raise ValueError("interval parameter required for 'interval' schedule")
            return IntervalTrigger(
                seconds=interval,
                start_date=params.get("start_date"),
                end_date=params.get("end_date"),
                timezone=self.timezone
            )
            
        elif schedule_type == "cron":
            return CronTrigger(
                year=params.get("year"),
                month=params.get("month"),
                day=params.get("day"),
                hour=params.get("hour"),
                minute=params.get("minute"),
                second=params.get("second"),
                timezone=self.timezone
            )
            
        else:
            raise ValueError(f"Unsupported schedule type: {schedule_type}")
            
    def _check_schedule_conflicts(self, trigger: Any) -> bool:
        """
        Check for scheduling conflicts
        
        Args:
            trigger: Trigger to check
            
        Returns:
            True if no conflicts, False otherwise
        """
        # Get next run time
        next_run = trigger.get_next_fire_time(None, datetime.now(self.timezone))
        if not next_run:
            return True
            
        # Get existing jobs around that time
        jobs = self.scheduler.get_jobs()
        for job in jobs:
            job_time = job.next_run_time
            if job_time:
                time_diff = abs(job_time - next_run)
                if time_diff < self.min_buffer:
                    return False
                    
        return True
        
    def get_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """
        Get list of scheduled tasks
        
        Returns:
            List of scheduled task information
        """
        tasks = []
        for job in self.scheduler.get_jobs():
            tasks.append({
                "id": job.id,
                "next_run": job.next_run_time,
                "trigger": str(job.trigger),
                "function": job.func.__name__
            })
        return tasks
        
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a scheduled task
        
        Args:
            task_id: ID of task to cancel
            
        Returns:
            True if task was cancelled, False otherwise
        """
        try:
            self.scheduler.remove_job(task_id)
            self.logger.info(f"Cancelled task {task_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to cancel task {task_id}: {e}")
            return False
            
    def modify_task_schedule(self,
                           task_id: str,
                           new_schedule: Dict[str, Any]) -> bool:
        """
        Modify the schedule of an existing task
        
        Args:
            task_id: ID of task to modify
            new_schedule: New schedule parameters
            
        Returns:
            True if task was modified, False otherwise
        """
        try:
            job = self.scheduler.get_job(task_id)
            if not job:
                raise ValueError(f"Task {task_id} not found")
                
            trigger = self._create_trigger(
                new_schedule["type"],
                new_schedule["params"]
            )
            
            job.reschedule(trigger=trigger)
            self.logger.info(f"Modified schedule for task {task_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to modify task {task_id}: {e}")
            return False
            
    def get_next_execution_time(self, task_id: str) -> Optional[datetime]:
        """
        Get next execution time for a task
        
        Args:
            task_id: ID of the task
            
        Returns:
            Next execution time or None if task not found
        """
        try:
            job = self.scheduler.get_job(task_id)
            return job.next_run_time if job else None
        except Exception as e:
            self.logger.error(f"Failed to get next execution time for task {task_id}: {e}")
            return None