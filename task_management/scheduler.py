import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime

class TaskScheduler:
    """Manages recurring task schedules using APScheduler."""

    def __init__(self, task_manager):
        self.manager = task_manager
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.logger = logging.getLogger("TaskScheduler")

    def add_schedule(self, task_id: str, schedule_type: str, schedule_value: str):
        """Adds a new schedule for a task."""
        trigger = None
        if schedule_type == "cron":
            trigger = CronTrigger.from_crontab(schedule_value)
        elif schedule_type == "interval":
            trigger = IntervalTrigger(seconds=float(schedule_value))
        
        if trigger:
            self.scheduler.add_job(
                self._trigger_task,
                trigger,
                args=[task_id],
                id=task_id,
                replace_existing=True
            )
            self.logger.info(f"Scheduled task {task_id} with {schedule_type}: {schedule_value}")

    def remove_schedule(self, task_id: str):
        """Removes a schedule for a task."""
        if self.scheduler.get_job(task_id):
            self.scheduler.remove_job(task_id)
            self.logger.info(f"Removed schedule for task {task_id}")

    def _trigger_task(self, task_id: str):
        """Internal callback to trigger task execution."""
        self.logger.info(f"Triggering scheduled task: {task_id}")
        with self.manager.lock:
            task = self.manager.get_task(task_id)
            if task:
                # Reset task status to PENDING so it can be picked up by execute_all
                # We also need to reset dependents if we want a full re-run
                self._reset_task_for_rerun(task)
        
        # Trigger execution of the DAG
        self.manager.execute_all()

    def _reset_task_for_rerun(self, task):
        """Recursively resets task and its dependents to PENDING."""
        from .models import TaskStatus
        
        if task.status == TaskStatus.PENDING:
             return
             
        task.status = TaskStatus.PENDING
        task.result = None
        task.error = None
        task.retries = 0
        
        if self.manager.state_store:
            self.manager.state_store.save_task(task)
            
        for dep_id in task.dependents:
            dep_task = self.manager.get_task(dep_id)
            if dep_task:
                self._reset_task_for_rerun(dep_task)
