# NEXUS Multi-Agent Intelligence Layer Manual

This document details the production design, operational specifications, and inter-agent communication protocols constituting the NEXUS Multi-Agent Intelligence Layer.

---

## 1. System Integration Landscape

The Multi-Agent Layer sits atop the Core Kernel, integrating seamlessly with the existing managers:

```
               +-------------------------------------------+
               |                User Intent                |
               +-----------------------------+-------------+
                                             |
                                             v
               +-----------------------------+-------------+
               |                Planner Agent              |  <-- Refines goal stages
               +-----------------------------+-------------+
                                             |
                                             v
               +-----------------------------+-------------+
               |               Reasoner Agent              |  <-- Audits plan coherence
               +-----------------------------+-------------+
                                             |
                                             v
+------------------+            +------------+------------+            +-------------------+
|  Context Manager | -------->  |     Orchestrator        |  <-------- |  Safety Manager   |
| (Uniform Context)|            |   Sequential & Parallel |            | (High-risk gates) |
+------------------+            +------------+------------+            +-------------------+
                                             |
                      +----------------------+----------------------+
                      |                      |                      |
                      v                      v                      v
               +--------------+       +--------------+       +--------------+
               |  CEO Agent   |       | Travel Agent |       | Reviewer QA  |  ... [17 Agents]
               +--------------+       +--------------+       +--------------+
```

### Integration Touchpoints

1. **Planner**: Transforms user's raw intent into specific stage tracks featuring a target `specialty_agent` key (e.g., `travel`, `finance`, `learning`).
2. **Reasoner**: Verifies alignment of multi-stage loops prior to execution, flagging inconsistencies or requesting clarifications.
3. **Safety Manager**: Performs critical scans on target tools and payloads. The `FinanceAgent`, for instance, generates budget plans but relies on Safety Manager to block payment authorizations.
4. **Context Manager**: Gathers unified conversation context, files, RAG documents, and preferences, structuring them into a shared payload for the active agent's lifecycle.
5. **Memory Manager**: Saves the parameters, state outcomes, and extracted long-term user preferences generated during multi-agent trace runs.
6. **Tool Manager**: Allows specialized agents to invoke sandboxed workspace tools (calculator, calendar, files, terminal) during their lifecycle runs.
7. **Workflow Engine**: Governs state machine progression (`Planning` -> `Reasoning` -> `Executing` -> `Completed`), coordinating multi-agent steps asynchronously with resume capabilities.

---

## 2. Communication Messaging Protocol

All inter-agent message transits are governed by the structured `AgentMessage` schema:

```json
{
  "sender": "orchestrator",
  "receiver": "travel_agent",
  "timestamp": "2026-06-22T06:29:48Z",
  "task": "Plan a trip to Hyderabad, India.",
  "context": {
    "conversation_history": "User: Let's visit Hyderabad soon...",
    "user_preferences": "Preference: Vegan dining prefered."
  },
  "confidence": 0.95,
  "dependencies": [],
  "payload": {}
}
```

---

## 3. Specialized Agent Catalog (17 Nodes)

NEXUS registers 17 specialized authority agents, each with dedicated capability scopes:

| Agent Identifier | Professional Role Name | Core Operational Capabilities / Mandates |
| :--- | :--- | :--- |
| `ceo_agent` | NEXUS CEO Coordinating Authority | Directs timelines, prioritizes goals, manages fallback execution tracks. |
| `planner_agent` | NEXUS Planning Architect | Deconstructs complex strings into granular sequential task records. |
| `research_agent` | NEXUS Core Analyst Eng | Collares facts, queries search indices, processes background reports. |
| `coding_agent` | NEXUS Software Engineer | Authoritative TypeScript/Python generation, syntax debugging, dry-runs. |
| `browser_agent` | NEXUS Browser Specialist | Visual locator lookup, outlines crawling pathways. |
| `automation_agent`| NEXUS Core Scheduler | Evaluates background macros, coordinates cron event triggers. |
| `memory_agent` | NEXUS Memory Registrar | Extracts strategic behavioral indices and compresses long-term facts. |
| `document_agent` | NEXUS Document Synthesizer | Bullet summarization, parsing PDF headers and structured markdown sheets. |
| `calendar_agent` | NEXUS Time Scheduler | Non-conflict slot allocation, agenda timeline audits. |
| `travel_agent` | NEXUS Travel Consultant | Generates detailed checklists, hotel matches, flight duration estimates. |
| `finance_agent` | NEXUS Financial Advisory | Formulates budgets and projections. **Strictly forbidden from checkout auth**. |
| `learning_agent` | NEXUS Curricula Coordinator | Drafts structured study planners and tracks academic topic sequences. |
| `career_agent` | NEXUS Career Consultant | Conducts CV audits, structures cover letters, simulates interview prep. |
| `security_agent` | NEXUS Threat Intelligence | Scans sequences for leaked tokens, credential disclosures, or rm actions. |
| `vision_agent` | NEXUS Visual Sensor | Outlines future multi-modal layout dimensions, canvas objects tracking. |
| `health_agent` | NEXUS Lifestyle Consultant | Generates hydration and posture drills. **Avoids clinical medical diagnosis**. |
| `reviewer_agent` | NEXUS QA Quality Control | Cross-audits outputs for internal contradictions, polishing finalized reports. |

---

## 4. Collaborative Scenario Breakdown

### Sample Request:
> "Plan a trip to Hyderabad, estimate my budget, update my calendar, and prepare a packing checklist."

### Collaboration Timeline Tracing:

1. **CEO Agent**: Reviews starting conditions and assigns strategic priorities.
2. **Planner Agent**: Structures the five stages: Travel lookup, Budget forecasting, Schedule allocation, Packing inventory drafting, and Quality review.
3. **Travel Agent**: Formulates a detailed travel schedule for Hyderabad (historical spots, transport options).
4. **Finance Agent**: Computes estimates ($250 approx) and enforces safety parameters (no auto-purchases).
5. **Calendar Agent**: Assesses existing slots and blocks corresponding timezone hours.
6. **Reviewer Agent**: Checks for contradictions (e.g., matching travel flight dates with occupied calendar spots) and synthesizes the finalized unified report.
