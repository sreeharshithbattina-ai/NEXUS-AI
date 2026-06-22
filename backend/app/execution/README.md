# NEXUS AI OS — Agent Execution Engine Module

The **Agent Execution Engine** is the central orchestration brain of the NEXUS AI operating system. It integrates every cognitive, database, security, and physical subsystem into a dynamic full-stack loop.

---

## 1. Complete Integration Sequence Diagram

This diagram displays the unified execution pipeline: how human intent propagates cleanly through neural classifications, DAG step formulations, multi-agent registries, RAG indexing context injection, and real-time safety gates prior to machine action.

```
 User        IntentEngine     Planner        Orchestrator      RAG / DB      Safety/Approval      DesktopRuntime      Reflection/Learning
  │               │              │                │               │                 │                   │                     │
  │───Intent─────▶│              │                │               │                 │                   │                     │
  │   Query       │              │                │               │                 │                   │                     │
  │               │──Classified─▶│                │               │                 │                   │                     │
  │               │  Goal        │                │               │                 │                   │                     │
  │               │              │──Generate DAG─▶│               │                 │                   │                     │
  │               │              │  Plan (Steps)  │               │                 │                   │                     │
  │               │              │                │──Search RAG──▶│                 │                   │                     │
  │               │              │                │  for Context  │                 │                   │                     │
  │               │              │                │◀─Docs/Memos───│                 │                   │                     │
  │               │              │                │               │                 │                   │                     │
  │               │              │                │───────────Evaluate Safety──────▶│                   │                     │
  │               │              │                │                                 │                   │                     │
  │               │              │                │◀──────────Granted / Denied──────│                   │                     │
  │               │              │                │                                                     │                     │
  │               │              │                │────────────────────Execute Action──────────────────▶│                     │
  │               │              │                │                                                     │                     │
  │               │              │                │◀───────────────────Completed Result─────────────────│                     │
  │               │              │                │                                                                           │
  │               │              │                │──────────────────────────────Trigger Reflection & Auditing───────────────▶│
  │               │              │                │                                                                           │
  │               │              │                │──────────────────────────────Extract Preferences/Memos────────────────────▶│
  │               │              │                │                                                                           │
  │◀──Response────│              │                │                                                                           │
  │  (Completed)  │              │                │                                                                           │
```

---

## 2. DAG Execution Loop with Safety & Recovery

The execution loop processes ready steps in the Constructed topological DAG. It intercepts actions falling under safety rules, transitions to `suspended` state, and runs recovery strategies if failures occur.

```
             ┌────────────────────────────────┐
             │    Generate Directed Graph     │◀─────────┐
             │             (DAG)              │          │
             └───────────────┬────────────────┘          │
                             ▼                           │
             ┌────────────────────────────────┐          │
             │     Get Topologically Ready    │          │
             │           Node Steps           │          │
             └───────────────┬────────────────┘          │
                             ▼                           │
              /‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\           │ Retry Node
             <   Is Safety Gate Triggered?   >          │
              \_____________________________/           │
                     /               \                  │
                YES /                 \ NO              │
                   ▼                   ▼                │
       ┌──────────────────────┐  ┌───────────┐          │
       │ Pause Loop / Suspends│  │  Run Node │          │
       │   Waiting Approval   │  │ Execution │          │
       └──────────┬───────────┘  └─────┬─────┘          │
                  │                    ▼                │
                  │             /‾‾‾‾‾‾‾‾‾‾‾‾‾\         │
                  ▼            <   Succeeded   >────────┘
           Approved?            \_____________/
           /       \               /         \
      YES /         \ NO      YES /           \ NO
         ▼           ▼           ▼             ▼
  ┌────────────┐  ┌───────┐  ┌───────────┐  ┌────────────────┐
  │ Resume Run │  │ Term  │  │ Save Memo │  │ Recovery Engine│
  │ Step Loop  │  │ Fail  │  │ to Memory │  │  Attempt Retry │
  └────────────┘  └───────┘  └───────────┘  └────────────────┘
```

---

## 3. Operations State Transition Diagrams

### Workflow Lifecycle States:
- **`running`**: Standard active execution loop.
- **`suspended`**: Stopped at a human safety approval gate, waiting for `resume_workflow`.
- **`completed`**: Every step in the DAG has completed successfully.
- **`failed`**: A step failed beyond maximum retry capacity or safety clearance was rejected.
- **`cancelled`**: Aborted manually, triggering a trash rollback.

```
       ┌─────────┐         (Safety Check Triggered)         ┌───────────┐
       │ Pending │───▶[ RUNNING ]─────────────────────────▶│ Suspended │
       └─────────┘     │   │   │                            └─────┬─────┘
                       │   │   │                                  │
      ┌────────────────┘   │   └─────────────────┐                │
      ▼ (All Steps Done)   ▼ (Max Retries Done)  ▼ (Cancel Cmd)   ▼ (Approval Resolved)
┌───────────┐          ┌────────┐            ┌───────────┐  [ BACK TO RUNNING ]
│ Completed │          │ Failed │            │ Cancelled │
└───────────┘          └────────┘            └───────────┘
```

### Task Node States:
- **`pending`**: Prerequisite dependencies are not yet complete.
- **`running`**: Node driver is actively executing.
- **`suspended`**: Halted waiting for prompt resolution.
- **`completed`**: Completed successfully. Result is written to shared execution Memory.
- **`failed`**: Blocked permanently.
- **`skipped`**: Omitted due to conditional branch evaluation logic.

---

## 4. Module System Architecture Review

| Engine Module | Class / Singleton Reference | Functional Integrity |
| :--- | :--- | :--- |
| **Intent Engine** | `IntentEngine` | Converts text commands into goals, extracting arguments and identifying ambiguous inputs. |
| **Execution Planner** | `ExecutionPlanner` | Translates goal categories into topological graph plans with dependencies. |
| **Task Graph** | `TaskGraph` / `TaskNode` | State manager of the DAG, providing topological cycle verification (DFS-based). |
| **Confidence Engine** | `ConfidenceEngine` | Scores planner structures, agents compliance, RAG document similarities, and aggregates them. |
| **Approval Manager** | `ApprovalManager` | Monitors six safety categories (Money, Bookings, File deletion, Terminal, Personal info, Emails) on demand. |
| **Reflection Engine** | `ReflectionEngine` | Reviews completed runs, logs mistake factors and saves retrospective updates. |
| **Learning Engine** | `LearningEngine` | Extracts preferences (IDE, coding style, travel modes, hours) and commits them to the Database. |
| **Experience Manager** | `ExperienceManager` | Indexes historical pipelines to recommend best templates for future intents. |
| **Workflow Optimizer**| `WorkflowOptimizer` | Detects redundant action pairs in history to suggest saved reusable custom skills. |
| **Recovery Engine** | `RecoveryEngine` | Re-establishes execution via exponential backup offsets, command alternatives, and fallback models. |
| **Execution Memory** | `ExecutionMemory` | Manages variables across execution steps, resolving placeholders like `${step_id.output}`. |
| **Metrics Tracker** | `MetricsTracker` | Measures averages across latencies, success rates, approvals, and RAG retrieval qualities. |
| **Execution Controller**| `ExecutionController` | The central coordinator, hosting step execution threads and coordinating components. |

---

## 5. Unified API Integration

The `Agent Execution Engine` exposes stable HTTP endpoints:

1. **/api/execution/execute** `[POST]`: Submits fresh natural-language input query, initiating complete Pipeline flow.
2. **/api/execution/workflows** `[GET]`: Lists uncompleted currently running or suspended workflows.
3. **/api/execution/workflows/history** `[GET]`: Queries experience lists of complete runs.
4. **/api/execution/workflows/resume** `[POST]`: Resumes a suspended workflow gate (approves/rejects).
5. **/api/execution/workflows/cancel** `[POST]`: Aborts a running task, rolling back temporal folder parameters.
6. **/api/execution/learning** `[GET]`: Queries database-extracted preferences and optimizer custom macros.
7. **/api/execution/preferences** `[GET / POST]`: Alters overall platform personality, voice, speed, and safety parameters.
8. **/api/execution/reflection** `[GET]`: Dumps lesson retrospective logs.
9. **/api/execution/metrics** `[GET]`: Exposes performance telemetry data for frontend dynamic displays.
