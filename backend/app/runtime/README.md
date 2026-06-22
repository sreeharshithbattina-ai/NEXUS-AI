# NEXUS AI OS — Desktop Agent Runtime Module

The **Desktop Agent Runtime** is the native execution boundary for the NEXUS AI operating system. It converts high-level intent matrices and linear workflow plans issued by the **Planner** and **Orchestrator** into robust, secure, physical actions executed safely on the workspace computer.

---

## 1. Core Architecture Diagram

```
        ┌────────────────────────────────────────────────────────┐
        │                 Planner & Orchestrator                 │
        │             (Intent Matrix & Workflow Plan)            │
        └───────────────────────────┬────────────────────────────┘
                                    │ Step Actions
                                    ▼
        ┌────────────────────────────────────────────────────────┐
        │                     Safety Manager                     │
        │                  (Risk Classification)                 │
        └───────────────────────────┬────────────────────────────┘
                                    │ Risk Rating
                                    ▼
        ┌────────────────────────────────────────────────────────┐
        │                   Permission Manager                   │
        │              (Policy Guard: Allow/Deny/Ask)            │
        └───────────────────────────┬────────────────────────────┘
                                    │ Permission Clearances
                                    ▼
        ┌────────────────────────────────────────────────────────┐
        │                 Desktop Agent Runtime                  │
        │              (Execution Orchestration Layer)           │
        └───────┬───────────────────┼───────────────────┬────────┘
                │                   │                   │
                ▼                   ▼                   ▼
     ┌─────────────────┐   ┌─────────────────┐   ┌───────────────┐
     │ Terminal Manager│   │FilesystemManager│   │  App Manager  │
     └─────────────────┘   └─────────────────┘   └───────────────┘
     ┌─────────────────┐   ┌─────────────────┐   ┌───────────────┐
     │Clipboard Manager│   │ScreenshotManager│   │Process Manager│
     └─────────────────┘   └─────────────────┘   └───────────────┘
                │                   │                   │
                └───────────────────┼───────────────────┘
                                    │ Activity Monitoring & Reminders
                                    ▼
        ┌────────────────────────────────────────────────────────┐
        │                  Dynamic Event Bus                     │
        │         (Feeds Workspace Intel & Dashboards)           │
        └────────────────────────────────────────────────────────┘
```

---

## 2. Desktop runtime components

| Module | Purpose / Interface Coverage | Windows First Native Abstraction |
| :--- | :--- | :--- |
| **Application Manager** | Handles application lifecycles (Open, Close, Focus, Active). | Integrates Shell Execution (`start`) and active `taskkill` commands. |
| **Filesystem Manager** | Organizes paths safely (Create, Rename, Copy, Move, Search, Metadata tag). | Includes built-in support for simulated `.nexus_recycle_bin` path moving. |
| **Terminal Manager** | Executes subprocess utilities, tracking console outputs with risk evaluation. | Formulates low, medium, and high risk-classifications on script strings. |
| **Process Manager** | Gathers cpu, ram, gpu telemetry, and running processes list. | Employs psutil fallbacks for sandboxed deployment integrity. |
| **Clipboard Manager** | Manages OS clipboard buffers with trace history depth. | Synced cleanly back to desktop registers upon execution. |
| **Screenshot Manager** | Captures display frames and region bounding boxes. | Integrates PIL graphics fallbacks for headless services. |
| **Notification Manager** | Emits toasts and solicits manual operator confirmations. | Keeps a standard unread trace queue matching frontend designs. |
| **Permission Manager** | Evaluates sensitive actions against preconfigured security policies. | Resolves live approval tickets before action loops occur. |
| **Activity Monitor** | Measures session lengths, coding loops, and app changes on demand. | Feeds productivity metrics directly to dashboards. |
| **Scheduler** | Pipelines background workflows and recurring cron triggers. | Tracks paused/active execution intervals. |
| **Event Bus** | Publishes runtime system events (`ApplicationOpened`, `FileModified`, etc.). | Feeds instant telemetry streams matching RAG OS architectures. |

---

## 3. Permission Model

For security, sensitive operating system functions are routed through strict policies before executing. The policy levels are:

1. **ALLOW**: Executes automatically without prompt.
2. **ASK**: Generates a temporary approval ticket inside the Permission Manager. Emits an `ApprovalRequested` notification to the Operator's Dashboard. Holds execution until signed.
3. **DENY**: Instantly blocks execution, raising an authorization exception and emitting a `PermissionDenied` event.

### Policy Defaults Map:
- **`file_delete`**: `ask` (Protects against accidental directory clearing)
- **`shell_execution`**: `ask` (Intercepts raw cmd operations)
- **`launch_application`**: `allow`
- **`read_clipboard`**: `allow`
- **`take_screenshot`**: `allow`
- **`payments`**: `deny` (Guards financial risk)
- **`bookings`**: `ask`
- **`email_sending`**: `ask`

---

## 4. Workflows & Event Lifecycles

### Sequential Workflow Lifecycle Flow:
1. **Initialize Workflow**: Orchestrator submits `WorkflowActionPayload` naming steps.
2. **Trigger Progress Tracker**: Event bus emits `WorkflowStarted`.
3. **Safety Evaluation**: Runtime submits task parameters to Permission Manager.
4. **Resolution Gate**:
   - If *Denied*, workflow terminates with `WorkflowFailed` status.
   - If *Ask*, waits for `/api/runtime/permissions/resolve/{id}` with `approved: True`.
5. **Driver Trigger**: Runtime fires command executing under targeted sub-managers.
6. **Log Verification**: Event bus fires specific execution details (e.g. `FileModified`, `CommandExecuted`).
7. **Next Step**: Runtime steps to subsequent actions until complete.
8. **Completion Summary**: Fires completion toast and registers `WorkflowCompleted`.
