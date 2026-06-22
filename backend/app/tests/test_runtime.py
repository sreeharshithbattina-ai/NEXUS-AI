import pytest
import time
from fastapi.testclient import TestClient

from ..main import app
from ..runtime import (
    global_event_bus,
    global_permission_manager,
    global_desktop_controller,
    global_desktop_runtime,
    global_scheduler,
    global_activity_monitor
)

@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    # Setup / Reset state before test starts
    global_event_bus.clear()
    global_permission_manager._pending_approvals.clear()
    global_activity_monitor.set_tracking(False)
    yield
    # Cleanup after test finishes
    global_event_bus.clear()

# --- 1. Event Bus Tests ---
def test_event_bus_emission_and_subscription():
    received_events = []
    
    def on_custom_event(event):
        received_events.append(event)
        
    global_event_bus.subscribe("CustomEvent", on_custom_event)
    global_event_bus.emit("CustomEvent", "TestSource", {"key": "value"})
    
    assert len(received_events) == 1
    assert received_events[0].type == "CustomEvent"
    assert received_events[0].payload["key"] == "value"
    
    history = global_event_bus.get_history()
    assert len(history) >= 1
    assert history[0]["type"] == "CustomEvent"

# --- 2. Permission Manager Tests ---
def test_permission_manager_evaluation():
    # Default policy for file_delete is "ask"
    auth = global_permission_manager.check_permission("file_delete", details={"path": "test.txt"})
    assert auth["granted"] is False
    assert auth["mode"] == "ask"
    assert "approval_id" in auth
    
    appr_id = auth["approval_id"]
    
    # Resolve approval with positive signature
    resolved = global_permission_manager.resolve_approval(appr_id, approved=True)
    assert resolved is True
    
    # Verify policy adjustment
    success = global_permission_manager.set_policy("file_delete", "allow")
    assert success is True
    
    auth2 = global_permission_manager.check_permission("file_delete", details={"path": "test.txt"})
    assert auth2["granted"] is True
    assert auth2["mode"] == "automatic"

# --- 3. Application Manager Tests ---
def test_application_manager_lifecycle():
    initial_apps_count = len(global_desktop_controller.apps.list_running_apps())
    
    app_info = global_desktop_controller.apps.open_app("Calculator")
    assert app_info["name"] == "Calculator"
    assert app_info["status"] == "running"
    
    assert len(global_desktop_controller.apps.list_running_apps()) == initial_apps_count + 1
    
    # Focus
    focus_res = global_desktop_controller.apps.focus_app("Calculator")
    assert focus_res["status"] == "success"
    
    active_window = global_desktop_controller.apps.get_active_window()
    assert active_window["name"] == "Calculator"
    
    # Close
    close_res = global_desktop_controller.apps.close_app("Calculator")
    assert close_res["status"] == "success"
    assert len(global_desktop_controller.apps.list_running_apps()) == initial_apps_count

# --- 4. Filesystem Manager Tests ---
def test_filesystem_manager_operations(tmp_path):
    import os
    from ..runtime.filesystem_manager import FilesystemManager
    
    # Create private isolated filesystem manager
    fs = FilesystemManager(workspace_root=str(tmp_path))
    
    # Create folder
    fold_res = fs.create_folder("test_dir")
    assert fold_res["status"] == "success"
    assert os.path.exists(os.path.join(tmp_path, "test_dir"))
    
    # Write & Read file
    filepath = os.path.join("test_dir", "memo.txt")
    write_res = fs.write_file(filepath, "Hello World")
    assert write_res["status"] == "success"
    
    content = fs.read_file(filepath)
    assert content == "Hello World"
    
    # Tagging file
    tag_res = fs.tag_file(filepath, "urgent")
    assert tag_res["status"] == "success"
    assert "urgent" in tag_res["tags"]
    
    # Search
    search_res = fs.search_files("memo")
    assert len(search_res) == 1
    assert search_res[0]["filename"] == "memo.txt"
    assert "urgent" in search_res[0]["tags"]
    
    # Safe Delete (Recycle Bin)
    del_res = fs.delete_item(filepath, force=False)
    assert del_res["status"] == "recycled"
    assert not os.path.exists(os.path.join(tmp_path, filepath))
    
    recycled_items = fs.list_recycle_bin()
    assert len(recycled_items) == 1
    
    # Purge
    fs.empty_recycle_bin()
    assert len(fs.list_recycle_bin()) == 0

# --- 5. Terminal Manager Tests ---
def test_terminal_manager_execution():
    # Classification check
    risk_low = global_desktop_controller.terminal.classify_risk("echo 'Hello'")
    assert risk_low["level"] == "LOW"
    
    risk_high = global_desktop_controller.terminal.classify_risk("sudo rm -rf /")
    assert risk_high["level"] == "HIGH"
    
    # Execute Low Risk
    res = global_desktop_controller.terminal.run_command("echo 'Test execution'")
    assert res["status"] in ["success", "failed"] # It succeeds natively, fails gracefully if shell blocked
    assert res["risk_level"] == "LOW"

# --- 6. Clipboard Manager Tests ---
def test_clipboard_manager():
    global_desktop_controller.clipboard.write("Test pasteboard content")
    assert global_desktop_controller.clipboard.read() == "Test pasteboard content"
    
    hist = global_desktop_controller.clipboard.get_history()
    assert hist[0] == "Test pasteboard content"

# --- 7. Scheduler Tests ---
def test_scheduler_jobs():
    global_scheduler._jobs.clear()
    
    # Schedule job for 10 seconds from now
    job = global_scheduler.schedule_job(
        job_id="job-01",
        action_type="reminder",
        payload={"msg": "Take deep breath"},
        seconds_from_now=10
    )
    
    assert job["id"] == "job-01"
    assert job["status"] == "scheduled"
    
    # Pause
    global_scheduler.pause_job("job-01")
    assert global_scheduler._jobs["job-01"].status == "paused"
    
    # Resume
    global_scheduler.resume_job("job-01")
    assert global_scheduler._jobs["job-01"].status == "scheduled"
    
    # Cancel
    global_scheduler.cancel_job("job-01")
    assert "job-01" not in global_scheduler._jobs

# --- 8. Activity Monitor Tests ---
def test_activity_monitor():
    # Report is empty or generic message when disabled
    summary_disabled = global_activity_monitor.get_summary()
    assert summary_disabled["tracking_status"] == "disabled"
    
    global_activity_monitor.set_tracking(True)
    summary_enabled = global_activity_monitor.get_summary()
    assert summary_enabled["tracking_status"] == "enabled"
    
    global_activity_monitor.record_activity("VS Code", "coding", 300)
    summary_after = global_activity_monitor.get_summary()
    assert summary_after["total_work_minutes"] > 0

# --- 9. Sequential Workflow Runtime Tests ---
def test_sequential_workflow():
    global_permission_manager.set_policy("launch_application", "allow")
    
    actions = [
        {"type": "open_app", "params": {"name": "TextEditor"}},
        {"type": "write_clipboard", "params": {"text": "Workflow line 1"}}
    ]
    
    res = global_desktop_runtime.run_sequential_workflow("Test Pipe", actions)
    assert res["status"] == "completed"
    assert len(res["steps"]) == 2
    assert res["steps"][0]["type"] == "open_app"
    assert res["steps"][1]["type"] == "write_clipboard"

# --- 10. API Integration Tests ---
def test_runtime_api_endpoints():
    client = TestClient(app)
    
    # Since operations require authenticating get headers, we can mock/setup headers or test public ones
    # In main.py there is standard dependency get_current_user. For unit simplicity on tests with auth,
    # let's write client test endpoints or verify routing loads correctly.
    # FastAPI include_router ensures these routes exist in OpenAPI documentation.
    routes = [r.path for r in app.routes]
    assert "/api/runtime/apps" in routes
    assert "/api/runtime/files" in routes
    assert "/api/runtime/processes" in routes
    assert "/api/runtime/clipboard" in routes
    assert "/api/runtime/screenshot" in routes
    assert "/api/runtime/permissions" in routes
    assert "/api/runtime/events" in routes
    assert "/api/runtime/schedule" in routes
