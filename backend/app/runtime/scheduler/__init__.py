import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Callable, Optional
from ..event_manager import global_event_bus

logger = logging.getLogger("scheduler")

class ScheduledJob:
    def __init__(self, job_id: str, action_type: str, payload: Dict[str, Any], execute_at: datetime, repeat_interval_sec: Optional[int] = None):
        self.id = job_id
        self.action_type = action_type # e.g. "workflow", "reminder"
        self.payload = payload
        self.execute_at = execute_at
        self.repeat_interval_sec = repeat_interval_sec
        self.status = "scheduled" # "scheduled", "running", "completed", "paused"

class RuntimeScheduler:
    def __init__(self):
        self._jobs: Dict[str, ScheduledJob] = {}

    def schedule_job(self, job_id: str, action_type: str, payload: Dict[str, Any], seconds_from_now: int, repeat_interval: Optional[int] = None) -> Dict[str, Any]:
        execute_time = datetime.utcnow() + timedelta(seconds=seconds_from_now)
        job = ScheduledJob(job_id, action_type, payload, execute_time, repeat_interval)
        self._jobs[job_id] = job
        
        global_event_bus.emit(
            "WorkflowScheduled",
            "Scheduler",
            {"job_id": job_id, "action_type": action_type, "run_at": execute_time.isoformat()}
        )
        return self._get_job_dict(job)

    def cancel_job(self, job_id: str) -> bool:
        if job_id in self._jobs:
            self._jobs[job_id].status = "cancelled"
            del self._jobs[job_id]
            global_event_bus.emit(
                "WorkflowCancelled",
                "Scheduler",
                {"job_id": job_id}
            )
            return True
        return False

    def list_jobs(self) -> List[Dict[str, Any]]:
        return [self._get_job_dict(j) for j in self._jobs.values()]

    def pause_job(self, job_id: str) -> bool:
        if job_id in self._jobs:
            self._jobs[job_id].status = "paused"
            global_event_bus.emit(
                "WorkflowPaused",
                "Scheduler",
                {"job_id": job_id}
            )
            return True
        return False

    def resume_job(self, job_id: str) -> bool:
        if job_id in self._jobs:
            self._jobs[job_id].status = "scheduled"
            # Refresh execute_at if it has expired so it fires immediately or shortly
            if self._jobs[job_id].execute_at < datetime.utcnow():
                self._jobs[job_id].execute_at = datetime.utcnow() + timedelta(seconds=2)
            global_event_bus.emit(
                "WorkflowResumed",
                "Scheduler",
                {"job_id": job_id}
            )
            return True
        return False

    def check_and_trigger(self, executor_callback: Callable[[str, Dict[str, Any]], None]) -> List[Dict[str, Any]]:
        """Invoked periodically to process elapsed schedules."""
        now = datetime.utcnow()
        triggered = []
        
        for job in list(self._jobs.values()):
            if job.status == "scheduled" and job.execute_at <= now:
                job.status = "running"
                global_event_bus.emit(
                    "WorkflowStarted",
                    "Scheduler",
                    {"job_id": job.id, "action_type": job.action_type}
                )
                
                try:
                    executor_callback(job.action_type, job.payload)
                    triggered.append(self._get_job_dict(job))
                    
                    if job.repeat_interval_sec:
                        job.execute_at = now + timedelta(seconds=job.repeat_interval_sec)
                        job.status = "scheduled"
                    else:
                        job.status = "completed"
                        del self._jobs[job.id]
                except Exception as e:
                    job.status = "failed"
                    logger.error(f"Error handling job {job.id}: {e}")
                    
        return triggered

    def _get_job_dict(self, job: ScheduledJob) -> Dict[str, Any]:
        return {
            "id": job.id,
            "action_type": job.action_type,
            "payload": job.payload,
            "execute_at": job.execute_at.isoformat(),
            "repeat_interval_sec": job.repeat_interval_sec,
            "status": job.status
        }

global_scheduler = RuntimeScheduler()
