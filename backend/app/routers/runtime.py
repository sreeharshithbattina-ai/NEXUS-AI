import os
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import BaseModel

from ..models import AuthUser
from ..auth import get_current_user
from ..runtime import (
    global_event_bus,
    global_permission_manager,
    global_desktop_controller,
    global_desktop_runtime,
    global_scheduler,
    global_activity_monitor
)

router = APIRouter(prefix="/api/runtime", tags=["Desktop Agent Runtime"])

# Define Pydantic request body schemas for type-safety and OpenAPI schema auto-generation

class AppOpenPayload(BaseModel):
    name: str

class AppActionPayload(BaseModel):
    identifier: str

class FileCreatePayload(BaseModel):
    path: str
    content: str

class FileActionPayload(BaseModel):
    path: str
    force: Optional[bool] = False

class FileMovePayload(BaseModel):
    source: str
    destination: str

class FileTagPayload(BaseModel):
    path: str
    tag: str

class ClipboardWritePayload(BaseModel):
    text: str

class ScreenshotPayload(BaseModel):
    x: Optional[int] = None
    y: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None

class PermissionSetPayload(BaseModel):
    action: str
    policy: str # "allow", "deny", "ask"

class PermissionResolvePayload(BaseModel):
    approved: bool

class ScheduleJobPayload(BaseModel):
    job_id: str
    action_type: str
    payload: Dict[str, Any]
    seconds_from_now: int
    repeat_interval_sec: Optional[int] = None

class ActivityStatePayload(BaseModel):
    enabled: bool

class WorkflowActionPayload(BaseModel):
    name: str
    actions: List[Dict[str, Any]]

# --- 1. Application Manager API ---

@router.get("/apps")
def list_desktop_apps(user: AuthUser = Depends(get_current_user)):
    """Retrieves all tracked and natively running programs on the active system Desktop."""
    return global_desktop_controller.apps.list_running_apps()

@router.post("/apps/open")
def open_desktop_app(payload: AppOpenPayload, user: AuthUser = Depends(get_current_user)):
    """Triggers program launch with appropriate platform drivers and privileges."""
    res = global_desktop_runtime.execute_action("open_app", {"name": payload.name}, user_id=user.id)
    if not res.get("success"):
        raise HTTPException(status_code=403, detail=res.get("reason"))
    return res

@router.post("/apps/close")
def close_desktop_app(payload: AppActionPayload, user: AuthUser = Depends(get_current_user)):
    """Instructs active window/PID to close down cleanly."""
    res = global_desktop_runtime.execute_action("close_app", {"identifier": payload.identifier}, user_id=user.id)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("reason"))
    return res

@router.post("/apps/focus")
def focus_desktop_app(payload: AppActionPayload, user: AuthUser = Depends(get_current_user)):
    """Transfers foreground application focus to requested process."""
    res = global_desktop_controller.apps.focus_app(payload.identifier)
    if res.get("status") == "error":
        raise HTTPException(status_code=404, detail=res.get("message"))
    return res

@router.get("/apps/active")
def get_active_window_summary(user: AuthUser = Depends(get_current_user)):
    """Locates the currently focused desktop utility window."""
    return global_desktop_controller.apps.get_active_window()

# --- 2. Filesystem Manager API ---

@router.get("/files")
def query_files(pattern: str = "", root_dir: str = ".", user: AuthUser = Depends(get_current_user)):
    """Searches workspace files matching pattern under specific folder scopes."""
    return global_desktop_controller.files.search_files(pattern, root_dir)

@router.post("/files/create")
def create_file_resource(payload: FileCreatePayload, user: AuthUser = Depends(get_current_user)):
    """Writes a fresh document file atomically to target location."""
    res = global_desktop_runtime.execute_action("write_file", {"path": payload.path, "content": payload.content}, user_id=user.id)
    return res

@router.post("/files/delete")
def delete_file_resource(payload: FileActionPayload, user: AuthUser = Depends(get_current_user)):
    """Moves target file safely to Recycle Bin, or purges permanently if chosen."""
    res = global_desktop_runtime.execute_action("delete_file", {"path": payload.path, "force": payload.force}, user_id=user.id)
    return res

@router.post("/files/move")
def move_file_resource(payload: FileMovePayload, user: AuthUser = Depends(get_current_user)):
    """Relocates folders/files to new directory paths."""
    res = global_desktop_controller.files.move_item(payload.source, payload.destination)
    if res.get("status") == "error":
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res

@router.post("/files/copy")
def copy_file_resource(payload: FileMovePayload, user: AuthUser = Depends(get_current_user)):
    """Duplicates target workspace documents safely."""
    res = global_desktop_controller.files.copy_item(payload.source, payload.destination)
    if res.get("status") == "error":
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res

@router.post("/files/tag")
def add_file_metadata_tag(payload: FileTagPayload, user: AuthUser = Depends(get_current_user)):
    """Assigns custom organizational meta-tags to workspace files."""
    res = global_desktop_controller.files.tag_file(payload.path, payload.tag)
    if res.get("status") == "error":
        raise HTTPException(status_code=404, detail=res.get("message"))
    return res

@router.get("/files/recycle-bin")
def list_recycled_files(user: AuthUser = Depends(get_current_user)):
    """Lists current documents inside the simulated OS Recycle Bin."""
    return global_desktop_controller.files.list_recycle_bin()

@router.delete("/files/recycle-bin")
def empty_recycled_files(user: AuthUser = Depends(get_current_user)):
    """Permanently purges Recycle Bin files."""
    return global_desktop_controller.files.empty_recycle_bin()

# --- 3. Terminal Manager API ---

@router.get("/processes")
def fetch_system_processes(user: AuthUser = Depends(get_current_user)):
    """Lists detailed cpu, memory, active logs, and thread processes matching OS standards."""
    return {
        "metrics": global_desktop_controller.processes.get_system_metrics(),
        "processes": global_desktop_controller.processes.list_processes()
    }

@router.post("/terminal/execute")
def execute_shell_command(command: str = Body(..., embed=True), user: AuthUser = Depends(get_current_user)):
    """Natively executes a shell input command with real-time risk-classification telemetry."""
    res = global_desktop_runtime.execute_action("run_command", {"command": command}, user_id=user.id)
    return res

@router.get("/terminal/history")
def fetch_shell_execution_history(user: AuthUser = Depends(get_current_user)):
    """Locates running workspace terminal task pipelines history log."""
    return global_desktop_controller.terminal.get_history()

# --- 4. Clipboard Manager API ---

@router.get("/clipboard")
def get_clipboard_content(user: AuthUser = Depends(get_current_user)):
    """Reads characters from internal system pasteboard register."""
    # Since checking permission is needed for read
    auth = global_permission_manager.check_permission("read_clipboard", user_id=user.id)
    if not auth.get("granted"):
        raise HTTPException(status_code=403, detail=auth.get("reason"))
        
    return {
        "text": global_desktop_controller.clipboard.read(),
        "history": global_desktop_controller.clipboard.get_history()
    }

@router.post("/clipboard")
def update_clipboard_content(payload: ClipboardWritePayload, user: AuthUser = Depends(get_current_user)):
    """Writes raw text lines directly to Clipboard registry."""
    success = global_desktop_controller.clipboard.write(payload.text)
    if not success:
         raise HTTPException(status_code=400, detail="Failed writing input value.")
    return {"status": "success", "length": len(payload.text)}

# --- 5. Screenshot Manager API ---

@router.post("/screenshot")
def take_system_screenshot(payload: Optional[ScreenshotPayload] = None, user: AuthUser = Depends(get_current_user)):
    """Captures monitor screen, region boundaries, or active overlays."""
    bbox_payload = {}
    if payload and payload.x is not None and payload.y is not None and payload.width is not None and payload.height is not None:
        bbox_payload = {
            "bbox": {
                "x": payload.x,
                "y": payload.y,
                "width": payload.width,
                "height": payload.height
            }
        }
    res = global_desktop_runtime.execute_action("take_screenshot", bbox_payload, user_id=user.id)
    if not res.get("success"):
        raise HTTPException(status_code=403, detail=res.get("reason"))
    return res

# --- 6. Permission & Safety Manager API ---

@router.get("/permissions")
def list_system_permissions(user: AuthUser = Depends(get_current_user)):
    """Gathers all standard policy configurations and interactive dialog logs."""
    return {
        "policies": global_permission_manager.get_policies(),
        "pending_approvals": global_permission_manager.get_pending_approvals()
    }

@router.post("/permissions/policy")
def set_permission_policy(payload: PermissionSetPayload, user: AuthUser = Depends(get_current_user)):
    """Updates security clearance profiles (e.g. adjust file_delete to auto-allow or deny)."""
    success = global_permission_manager.set_policy(payload.action, payload.policy)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid action or security policy designation.")
    return {"status": "success", "action": payload.action, "policy": payload.policy}

@router.post("/permissions/resolve/{approval_id}")
def resolve_pending_permission(approval_id: str, payload: PermissionResolvePayload, user: AuthUser = Depends(get_current_user)):
    """Signs/resolves outstanding policy security clearances manually (allow/deny)."""
    success = global_permission_manager.resolve_approval(approval_id, payload.approved, user_id=user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Coordinates expired or approval ID invalid.")
    return {"status": "resolved", "approval_id": approval_id, "approved": payload.approved}

# --- 7. Event Bus (Dashboard Feeds) API ---

@router.get("/events")
def list_runtime_events(limit: int = 50, user: AuthUser = Depends(get_current_user)):
    """Dumps sequence events directly to live operational intelligence layout dashboards."""
    return global_event_bus.get_history(limit=limit, user_id=user.id)

# --- 8. Scheduler & Workflow Pipeline API ---

@router.get("/schedule")
def list_scheduled_jobs(user: AuthUser = Depends(get_current_user)):
    """Lists delayed automatic routines inside the workspace."""
    return global_scheduler.list_jobs()

@router.post("/schedule")
def create_scheduled_job(payload: ScheduleJobPayload, user: AuthUser = Depends(get_current_user)):
    """Queues workflow executions or cron triggers delayed by specific times."""
    job = global_scheduler.schedule_job(
        job_id=payload.job_id,
        action_type=payload.action_type,
        payload=payload.payload,
        seconds_from_now=payload.seconds_from_now,
        repeat_interval=payload.repeat_interval_sec
    )
    return job

@router.post("/schedule/pause/{job_id}")
def pause_scheduled_job(job_id: str, user: AuthUser = Depends(get_current_user)):
    success = global_scheduler.pause_job(job_id)
    if not success:
         raise HTTPException(status_code=404, detail="Target job ID not found.")
    return {"status": "paused", "id": job_id}

@router.post("/schedule/resume/{job_id}")
def resume_scheduled_job(job_id: str, user: AuthUser = Depends(get_current_user)):
    success = global_scheduler.resume_job(job_id)
    if not success:
         raise HTTPException(status_code=404, detail="Target job ID not found.")
    return {"status": "resumed", "id": job_id}

@router.delete("/schedule/{job_id}")
def cancel_scheduled_job(job_id: str, user: AuthUser = Depends(get_current_user)):
    success = global_scheduler.cancel_job(job_id)
    if not success:
         raise HTTPException(status_code=404, detail="Target job ID not found.")
    return {"status": "cancelled", "id": job_id}

# --- 9. Workflow Sequential Execution API ---

@router.post("/workflows/execute")
def execute_workflow(payload: WorkflowActionPayload, user: AuthUser = Depends(get_current_user)):
    """Runs a multi-step structured sequential workflow with safety gates."""
    res = global_desktop_runtime.run_sequential_workflow(payload.name, payload.actions, user_id=user.id)
    return res

# --- 10. Activity Monitor API ---

@router.get("/activity")
def get_activity_report(user: AuthUser = Depends(get_current_user)):
    """Retrieves session analytics reports if tracking is enabled."""
    return global_activity_monitor.get_summary()

@router.post("/activity/state")
def set_activity_tracking_state(payload: ActivityStatePayload, user: AuthUser = Depends(get_current_user)):
    """Switches automatic task tracking loops on/off securely."""
    enabled = global_activity_monitor.set_tracking(payload.enabled)
    return {"tracking_enabled": enabled}
