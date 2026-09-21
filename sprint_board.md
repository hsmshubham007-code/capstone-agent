# Sprint Board — Company Policy Agent

## Project

**Project Name:** Company Policy Agent
**Project:** `week2day5proj1`
**Goal:** Build a production-oriented AI agent that answers company policy questions using RAG, routes requests to appropriate tools, applies safety controls, requires human approval for risky actions, maintains audit trails, and supports deployment through an API and Docker.

---

# 1. Sprint Objective

Build an end-to-end Company Policy Agent that can:

* Retrieve relevant information from company policy documents.
* Answer employee policy questions with source attribution.
* Route requests to the appropriate tool.
* Detect and block prompt-injection attempts.
* Prevent unauthorized execution of risky actions.
* Require human approval before destructive or sensitive operations.
* Maintain audit logs for important tool activity.
* Persist conversation state using LangGraph checkpointing.
* Execute independent tools asynchronously where appropriate.
* Expose the agent through a FastAPI service.
* Run consistently in Docker.
* Provide automated tests and evaluation evidence.

---

# 2. MoSCoW Prioritisation

## Must Have

These capabilities are required for the core system.

* [x] Collect and inspect policy documents.
* [x] Build document ingestion pipeline.
* [x] Split documents into retrieval chunks.
* [x] Generate local embeddings.
* [x] Store embeddings in Chroma.
* [x] Implement `search_documents`.
* [x] Build request/tool router.
* [x] Build LangGraph agent workflow.
* [x] Generate answers from retrieved policy information.
* [x] Return policy sources.
* [x] Implement input validation.
* [x] Implement prompt-injection detection.
* [x] Implement output validation.
* [x] Add human approval for risky tools.
* [x] Add audit logging.
* [x] Write automated tests.

## Should Have

Important production and reliability features.

* [x] LangGraph checkpointing.
* [x] Conversation/session persistence.
* [x] Asynchronous tool execution.
* [x] Sequential vs parallel latency benchmarking.
* [x] FastAPI API.
* [x] Health endpoint.
* [x] Docker deployment.
* [x] Docker Compose configuration.
* [x] Evaluation pipeline.
* [x] Routing evaluation.
* [x] Monitoring/metrics foundation.
* [x] Code quality checks with Ruff.
* [x] Dependency/security audit with `pip-audit`.

## Could Have

Useful improvements that are not essential to the first production version.

* [ ] More advanced tool-routing logic.
* [ ] Additional company document sources.
* [ ] More detailed monitoring dashboards.
* [ ] More advanced evaluation metrics.
* [ ] Expanded Streamlit UI.
* [ ] Additional model-routing experiments.

## Won't Have in This Version

Explicitly excluded from the current scope.

* [ ] Fully autonomous employee-record modification.
* [ ] Autonomous destructive operations without approval.
* [ ] Autonomous email sending without approval.
* [ ] Direct connection to a real employee database.
* [ ] Fully autonomous HR decision-making.

---

# 3. Sprint Task Board

| ID  | Task                                      | Priority | Estimate | Status | Deliverable                             |
| --- | ----------------------------------------- | -------- | -------: | ------ | --------------------------------------- |
| T01 | Identify stakeholder workflow             | Must     |     1 hr | Done   | Stakeholder workflow notes              |
| T02 | Define problem statement                  | Must     |     1 hr | Done   | `stakeholder_problem_statement.md`      |
| T03 | Define success metrics and human boundary | Must     |     1 hr | Done   | `success_metrics_and_human_boundary.md` |
| T04 | Perform data feasibility spike            | Must     |    2 hrs | Done   | `data_feasibility_spike.md`             |
| T05 | Collect policy PDFs                       | Must     |     1 hr | Done   | `data/` policy documents                |
| T06 | Build PDF ingestion pipeline              | Must     |    2 hrs | Done   | `ingest.py`                             |
| T07 | Configure document chunking               | Must     |     1 hr | Done   | Text splitter configuration             |
| T08 | Configure local embeddings                | Must     |     1 hr | Done   | `all-MiniLM-L6-v2`                      |
| T09 | Configure Chroma vector store             | Must     |     1 hr | Done   | Chroma collection                       |
| T10 | Implement document retrieval              | Must     |    2 hrs | Done   | `search_documents`                      |
| T11 | Build tool router                         | Must     |    2 hrs | Done   | `app/router.py`                         |
| T12 | Build agent workflow                      | Must     |    3 hrs | Done   | `app/agent.py` / graph                  |
| T13 | Implement LangGraph state                 | Must     |    2 hrs | Done   | `app/state.py`                          |
| T14 | Add safety validation                     | Must     |    3 hrs | Done   | `app/safety.py`                         |
| T15 | Add prompt-injection detection            | Must     |    2 hrs | Done   | Safety guardrail                        |
| T16 | Implement risky tools                     | Must     |    2 hrs | Done   | `app/risky_tools.py`                    |
| T17 | Implement approval queue                  | Must     |    3 hrs | Done   | `app/approval.py`                       |
| T18 | Implement audit trail                     | Should   |    2 hrs | Done   | `app/audit.py`                          |
| T19 | Add LangGraph checkpointing               | Should   |    2 hrs | Done   | SQLite checkpointing                    |
| T20 | Add async tool execution                  | Should   |    3 hrs | Done   | `app/async_tools.py`                    |
| T21 | Benchmark async execution                 | Should   |    2 hrs | Done   | `benchmark_async.py`                    |
| T22 | Build Streamlit UI                        | Should   |    2 hrs | Done   | `app/ui.py`                             |
| T23 | Build FastAPI API                         | Should   |    2 hrs | Done   | `app/api.py`                            |
| T24 | Add health endpoint                       | Should   |   30 min | Done   | `/health`                               |
| T25 | Create Dockerfile                         | Should   |     1 hr | Done   | `Dockerfile`                            |
| T26 | Create Docker Compose setup               | Should   |     1 hr | Done   | `docker-compose.yml`                    |
| T27 | Add automated tests                       | Must     |    3 hrs | Done   | `tests/`                                |
| T28 | Add evaluation pipeline                   | Should   |    2 hrs | Done   | `evals/`                                |
| T29 | Run Ruff checks                           | Should   |     1 hr | Done   | Code-quality verification               |
| T30 | Run dependency security audit             | Should   |     1 hr | Done   | `pip-audit` results                     |
| T31 | Verify Docker deployment                  | Should   |     1 hr | Done   | Running container                       |
| T32 | Document architecture                     | Should   |    2 hrs | Done   | README / architecture documentation     |
| T33 | Document results and limitations          | Should   |    2 hrs | Done   | Results documentation                   |

---

# 4. Estimates by Workstream

| Workstream                         | Estimated Effort |
| ---------------------------------- | ---------------: |
| Stakeholder discovery and planning |            3 hrs |
| Data feasibility and ingestion     |            7 hrs |
| RAG and retrieval                  |            4 hrs |
| Agent and routing                  |            7 hrs |
| Safety and approval system         |           10 hrs |
| Audit and checkpointing            |            4 hrs |
| Async execution and benchmarking   |            5 hrs |
| UI and API                         |          4.5 hrs |
| Docker/deployment                  |            2 hrs |
| Testing                            |            3 hrs |
| Evaluation                         |            2 hrs |
| Code quality/security checks       |            2 hrs |
| Documentation                      |            4 hrs |

**Estimated total:** approximately **57.5 hours**

> Estimates represent planned engineering effort and are not a measurement of actual elapsed development time.

---

# 5. Definition of Done

A task is considered complete when:

* The implementation is working.
* The relevant test passes.
* Errors are handled appropriately.
* The feature does not bypass safety controls.
* The feature is documented where necessary.
* The change does not break existing functionality.

For production-oriented tasks, completion also requires appropriate verification through tests, evaluation, or deployment checks.

---

# 6. Sprint Acceptance Criteria

The sprint is considered technically complete when the system can:

### Retrieval

* Load the available company policy documents.
* Split documents into searchable chunks.
* Generate local embeddings.
* Store and retrieve chunks using Chroma.
* Return relevant policy information and sources.

### Agent

* Accept a user question.
* Determine the appropriate action/tool.
* Retrieve policy information when required.
* Generate an answer.
* Return sources and tool information.

### Safety

* Validate user input.
* Detect prompt-injection attempts.
* Validate generated output.
* Prevent risky operations from executing automatically.

### Human Approval

The following operations require explicit approval:

* `update_employee_record`
* `delete_employee_record`
* `send_email`

Approval states are tracked through the approval workflow.

### Auditability

Important tool operations must produce audit information including:

* Request identifier.
* Tool/action.
* Execution status.
* Relevant metadata.
* Result or failure information.

### Reliability

The system should support:

* LangGraph checkpointing.
* Session/thread persistence.
* Resume capability.
* Automated regression tests.

### Performance

The project should measure:

* Sequential tool execution latency.
* Parallel tool execution latency.
* Latency reduction.
* Speedup.
* Total async execution time.

### Deployment

The project should:

* Start through Docker.
* Expose the FastAPI service.
* Provide `/health`.
* Provide `/chat`.
* Persist required application data through Docker volumes.

---

# 7. Evaluation Plan

Evaluation cases are designed to test different categories of behavior.

| Category              | What is tested                                       |
| --------------------- | ---------------------------------------------------- |
| HR                    | Employee and HR policy questions                     |
| IT                    | Technology and security policy questions             |
| Corporate             | General company policies                             |
| Retrieval             | Whether relevant documents are found                 |
| Source attribution    | Whether the correct source is returned               |
| Routing               | Whether the correct tool is selected                 |
| Safety                | Whether unsafe requests are blocked                  |
| Prompt injection      | Resistance to malicious instructions                 |
| Risky actions         | Whether approval is required                         |
| Unsupported questions | Appropriate handling when information is unavailable |

The evaluation set should contain **30 cases** covering these categories.

Each evaluation case should define, where applicable:

* Question.
* Category.
* Expected tool.
* Expected source.
* Expected safety behavior.
* Expected answer characteristics.

---

# 8. Success Metrics

The planned success targets for the project are:

| Metric                            |      Target |
| --------------------------------- | ----------: |
| Policy answer accuracy            |       ≥ 90% |
| Source attribution accuracy       |       ≥ 90% |
| P50 latency                       | ≤ 2 seconds |
| P95 latency                       | ≤ 5 seconds |
| Cost per query                    |     ≤ $0.01 |
| Prompt-injection resistance       |       ≥ 95% |
| Risky-action approval enforcement |        100% |
| Audit coverage                    |        100% |

These are **target acceptance criteria**, not claims that every target has already been achieved.

Actual measured results should be reported separately in the evaluation/results documentation.

---

# 9. Risks and Mitigations

| Risk                       | Impact               | Mitigation                                                        |
| -------------------------- | -------------------- | ----------------------------------------------------------------- |
| Poor document quality      | Incorrect answers    | Validate source documents and retrieval results                   |
| Missing policy information | Unsupported answers  | Return an appropriate limitation instead of inventing information |
| Incorrect retrieval        | Wrong answer         | Evaluate retrieval separately from generation                     |
| Prompt injection           | Unsafe behavior      | Input validation and injection detection                          |
| Risky tool execution       | Business/data impact | Human approval gate                                               |
| Model failure              | Request failure      | Error handling and model fallback/routing                         |
| Slow tool execution        | Poor user experience | Async execution and benchmarking                                  |
| Lost conversation state    | Reduced reliability  | LangGraph checkpointing                                           |
| Deployment failure         | Service unavailable  | Docker healthcheck and API testing                                |
| Dependency vulnerabilities | Security risk        | `pip-audit`                                                       |
| Code quality regressions   | Maintenance risk     | Ruff and automated tests                                          |

---

# 10. Sprint Verification

The final verification checklist is:

* [x] Planning completed.
* [x] MoSCoW priorities defined.
* [x] Tasks estimated.
* [x] Stakeholder problem documented.
* [x] Success metrics defined.
* [x] Human-in-the-loop boundary documented.
* [x] Data feasibility investigated.
* [x] RAG pipeline implemented.
* [x] Agent implemented.
* [x] Routing implemented.
* [x] Safety controls implemented.
* [x] Approval workflow implemented.
* [x] Audit trail implemented.
* [x] Checkpointing implemented.
* [x] Async execution implemented.
* [x] API implemented.
* [x] Docker deployment implemented.
* [x] Automated tests implemented.
* [x] Code-quality checks performed.
* [x] Dependency audit performed.
* [ ] 30-case evaluation set confirmed as created before implementation.
* [ ] Final evaluation results compared against success targets.
* [ ] Stakeholder/mentor sign-off recorded.

---

# 11. Sign-Off

## Intern

**Name:** ______________________________

**Signature:** ___________________________

**Date:** ________________________________

## Mentor

**Name:** ______________________________

**Signature:** ___________________________

**Date:** ________________________________

## Stakeholder

**Name:** ______________________________

**Signature:** ___________________________

**Date:** ________________________________

---

# 12. Summary

The sprint was planned around delivering a production-oriented Company Policy Agent rather than only a basic chatbot.

The implementation prioritised:

1. Reliable policy retrieval.
2. Tool-based agent routing.
3. Safety and prompt-injection protection.
4. Human approval for risky operations.
5. Auditability.
6. Persistent agent state.
7. Asynchronous execution.
8. API and Docker deployment.
9. Automated testing.
10. Evaluation against predefined success criteria.

The remaining verification requirement is to ensure that the **30-case evaluation set exists as a distinct evaluation artifact** and that final measured results are compared against the predefined targets.
