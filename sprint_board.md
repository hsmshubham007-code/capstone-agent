# Sprint Board â€” Company Policy Agent

## Project

**Project Name:** Company Policy Agent

**Project:** `week2day5proj1`

**Goal:** Build a production-oriented AI agent that answers company policy questions using RAG, routes requests to appropriate tools, applies safety controls, requires human approval for risky actions, maintains audit trails, and supports deployment through an API and Docker.

---

# 1. Sprint Objective

Build an end-to-end Company Policy Agent that can:

- Retrieve relevant information from company policy documents.
- Answer employee policy questions with source attribution.
- Route requests to the appropriate tool.
- Detect and block prompt-injection attempts.
- Prevent unauthorized execution of risky actions.
- Require human approval before destructive or sensitive operations.
- Maintain audit logs for important tool activity.
- Persist conversation state using LangGraph checkpointing.
- Execute independent tools asynchronously where appropriate.
- Expose the agent through a FastAPI service.
- Run consistently in Docker.
- Provide automated tests and evaluation evidence.

---

# 2. MoSCoW Prioritisation

## Must Have

These capabilities are required for the core system.

- [x] Collect and inspect policy documents.
- [x] Build document ingestion pipeline.
- [x] Split documents into retrieval chunks.
- [x] Generate local embeddings.
- [x] Store embeddings in Chroma.
- [x] Implement `search_documents`.
- [x] Build request/tool router.
- [x] Build LangGraph agent workflow.
- [x] Generate answers from retrieved policy information.
- [x] Return policy sources.
- [x] Implement input validation.
- [x] Implement prompt-injection detection.
- [x] Implement output validation.
- [x] Add human approval for risky tools.
- [x] Add audit logging.
- [x] Write automated tests.

## Should Have

Important production and reliability features.

- [x] LangGraph checkpointing.
- [x] Conversation/session persistence.
- [x] Asynchronous tool execution.
- [x] Sequential vs parallel latency benchmarking.
- [x] FastAPI API.
- [x] Health endpoint.
- [x] Docker deployment.
- [x] Docker Compose configuration.
- [x] Evaluation pipeline.
- [x] Routing evaluation.
- [x] Monitoring/metrics foundation.
- [x] Code quality checks with Ruff.
- [x] Dependency/security audit with `pip-audit`.

## Could Have

Useful improvements that are not essential to the first production version.

- [ ] More advanced tool-routing logic.
- [ ] Additional company document sources.
- [ ] More detailed monitoring dashboards.
- [ ] More advanced evaluation metrics.
- [ ] Expanded Streamlit UI.
- [ ] Additional model-routing experiments.

## Won't Have in This Version

Explicitly excluded from the current scope.

- [ ] Fully autonomous employee-record modification.
- [ ] Autonomous destructive operations without approval.
- [ ] Autonomous email sending without approval.
- [ ] Direct connection to a real employee database.
- [ ] Fully autonomous HR decision-making.

---

# 2A. Productionization Scope Decision

## Scope Decision

The current productionization phase will focus on proving that the existing Company Policy Agent is reliable, safe, auditable, and testable in an automated workflow.

The scope is intentionally focused on **verification and production readiness rather than adding new business features**.

## In Scope

- End-to-end execution using the real company policy documents in `data/`.
- RAG retrieval and policy-grounded answer generation.
- Tool routing.
- Input and output guardrails.
- Prompt-injection detection.
- Human approval for risky tools.
- Audit logging for important tool activity.
- LangGraph checkpointing and session persistence.
- FastAPI `/health` and `/chat` endpoints.
- Docker-based deployment.
- Automated regression tests.
- Evaluation of routing and safety behavior.
- Retrieval-quality evaluation.
- Latency and cost measurement.
- One-command evaluation execution.
- CI gates that fail when evaluation quality regresses.
- Pull-request review and resolution of review comments.

## Explicitly Deferred

The following are intentionally outside the current productionization scope:

- Connection to a real employee database.
- Real employee record modification or deletion.
- Real email delivery.
- Fully autonomous HR decision-making.
- Additional external enterprise-system integrations.
- Major retrieval-architecture changes unless evaluation demonstrates a measurable retrieval-quality problem.
- Full elimination of Groq/provider latency variability.
- Advanced production monitoring dashboards.

## Reason for the Decision

The core agent, RAG pipeline, safety controls, approval workflow, audit logging, checkpointing, API, Docker configuration, automated tests, and routing evaluation are already implemented.

The highest-risk remaining work is therefore **verification rather than feature expansion**.

The productionization phase will prioritize proving that the existing system:

1. Runs end-to-end on real policy data.
2. Maintains its safety controls.
3. Requires approval for risky operations.
4. Produces audit records.
5. Meets defined evaluation requirements.
6. Detects regressions automatically through CI.
7. Provides measurable latency and cost evidence.

## Current Riskiest Task

**Evaluation and production verification â€” In Progress**

Current evidence:

- Routing evaluation: **32/32 passed (100%)**
- Infrastructure errors: **0**
- Warm retrieval: generally approximately **12â€“23 ms**
- Cold-start embedding initialization: approximately **17 seconds**
- Latest average latency: **2,334.53 ms**
- Latest P50 latency: **752.17 ms**
- Latest P95 latency: **6,964.21 ms**

The current performance risk is primarily **LLM/provider latency**, rather than warm retrieval latency.

---

# 3. Sprint Task Board

| ID | Task | Priority | Estimate | Status | Deliverable |
| --- | --- | --- | ---: | --- | --- |
| T01 | Identify stakeholder workflow | Must | 1 hr | Done | Stakeholder workflow notes |
| T02 | Define problem statement | Must | 1 hr | Done | `stakeholder_problem_statement.md` |
| T03 | Define success metrics and human boundary | Must | 1 hr | Done | `success_metrics_and_human_boundary.md` |
| T04 | Perform data feasibility spike | Must | 2 hrs | Done | `data_feasibility_spike.md` |
| T05 | Collect policy PDFs | Must | 1 hr | Done | `data/` policy documents |
| T06 | Build PDF ingestion pipeline | Must | 2 hrs | Done | `ingest.py` |
| T07 | Configure document chunking | Must | 1 hr | Done | Text splitter configuration |
| T08 | Configure local embeddings | Must | 1 hr | Done | `all-MiniLM-L6-v2` |
| T09 | Configure Chroma vector store | Must | 1 hr | Done | Chroma collection |
| T10 | Implement document retrieval | Must | 2 hrs | Done | `search_documents` |
| T11 | Build tool router | Must | 2 hrs | Done | `app/router.py` |
| T12 | Build agent workflow | Must | 3 hrs | Done | `app/agent.py` / graph |
| T13 | Implement LangGraph state | Must | 2 hrs | Done | `app/state.py` |
| T14 | Add safety validation | Must | 3 hrs | Done | `app/safety.py` |
| T15 | Add prompt-injection detection | Must | 2 hrs | Done | Safety guardrail |
| T16 | Implement risky tools | Must | 2 hrs | Done | `app/risky_tools.py` |
| T17 | Implement approval queue | Must | 3 hrs | Done | `app/approval.py` |
| T18 | Implement audit trail | Should | 2 hrs | Done | `app/audit.py` |
| T19 | Add LangGraph checkpointing | Should | 2 hrs | Done | SQLite checkpointing |
| T20 | Add async tool execution | Should | 3 hrs | Done | `app/async_tools.py` |
| T21 | Benchmark async execution | Should | 2 hrs | Done | `benchmark_async.py` |
| T22 | Build Streamlit UI | Should | 2 hrs | Done | `app/ui.py` |
| T23 | Build FastAPI API | Should | 2 hrs | Done | `app/api.py` |
| T24 | Add health endpoint | Should | 30 min | Done | `/health` |
| T25 | Create Dockerfile | Should | 1 hr | Done | `Dockerfile` |
| T26 | Create Docker Compose setup | Should | 1 hr | Done | `docker-compose.yml` |
| T27 | Add automated tests | Must | 3 hrs | Done | `tests/` |
| T28 | Add evaluation pipeline | Should | 2 hrs | Done | `evals/` |
| T29 | Run Ruff checks | Should | 1 hr | Done | Code-quality verification |
| T30 | Run dependency security audit | Should | 1 hr | Done | `pip-audit` results |
| T31 | Verify Docker deployment | Should | 1 hr | Done | Running container |
| T32 | Document architecture | Should | 2 hrs | Done | README / architecture documentation |
| T33 | Document results and limitations | Should | 2 hrs | Done | Results documentation |
| T34 | Verify end-to-end production flow | Must | 1 hr | In Progress | Real-data run with guardrails and audit logging |
| T35 | Build one-command evaluation suite | Must | 2 hrs | Done | Routing, retrieval, and prompt-injection evaluations run through one command with a 90% CI-ready gate |
| T36 | Add evaluation pass-rate CI gate | Must | 2 hrs | Done | Build fails on evaluation regression |
| T37 | Raise and review production PR | Must | 1 hr | Done | Reviewed PR with comments resolved |
| T38 | Record final evaluation results | Should | 1 hr | Done | Baseline and regression results |
| T39 | Investigate LLM/provider tail latency | Should | 2 hr | Done
| T40 | Separate cold-start/warm-request latency | Should | 1 hr | Done
| T41 | Resolve Chroma security advisories | Should | 2 hrs | In Progress | Verify fixed Chroma release, upgrade safely, rebuild index, rerun tests/evals and pip-audit |

---

# 4. Estimates by Workstream

| Workstream | Estimated Effort |
| ---------------------------------- | ---------------: |
| Stakeholder discovery and planning | 3 hrs |
| Data feasibility and ingestion | 7 hrs |
| RAG and retrieval | 4 hrs |
| Agent and routing | 7 hrs |
| Safety and approval system | 10 hrs |
| Audit and checkpointing | 4 hrs |
| Async execution and benchmarking | 5 hrs |
| UI and API | 4.5 hrs |
| Docker/deployment | 2 hrs |
| Testing | 3 hrs |
| Evaluation | 2 hrs |
| Code quality/security checks | 2 hrs |
| Documentation | 4 hrs |

**Estimated total:** approximately **57.5 hours**

> Estimates represent planned engineering effort and are not a measurement of actual elapsed development time.

---

# 5. Definition of Done

A task is considered complete when:

- The implementation is working.
- The relevant test passes.
- Errors are handled appropriately.
- The feature does not bypass safety controls.
- The feature is documented where necessary.
- The change does not break existing functionality.

For production-oriented tasks, completion also requires appropriate verification through tests, evaluation, or deployment checks.

---

# 6. Sprint Acceptance Criteria

The sprint is considered technically complete when the system can:

## Retrieval

- Load the available company policy documents.
- Split documents into searchable chunks.
- Generate local embeddings.
- Store and retrieve chunks using Chroma.
- Return relevant policy information and sources.

## Agent

- Accept a user question.
- Determine the appropriate action/tool.
- Retrieve policy information when required.
- Generate an answer.
- Return sources and tool information.

## Safety

- Validate user input.
- Detect prompt-injection attempts.
- Validate generated output.
- Prevent risky operations from executing automatically.

## Human Approval

The following operations require explicit approval:

- `update_employee_record`
- `delete_employee_record`
- `send_email`

Approval states are tracked through the approval workflow.

## Auditability

Important tool operations must produce audit information including:

- Request identifier.
- Tool/action.
- Execution status.
- Relevant metadata.
- Result or failure information.

## Reliability

The system should support:

- LangGraph checkpointing.
- Session/thread persistence.
- Resume capability.
- Automated regression tests.

## Performance

The project should measure:

- Sequential tool execution latency.
- Parallel tool execution latency.
- Latency reduction.
- Speedup.
- Total async execution time.
- LLM latency.
- Retrieval latency.
- P50 latency.
- P95 latency.
- Token usage.
- Cost per query.

## Deployment

The project should:

- Start through Docker.
- Expose the FastAPI service.
- Provide `/health`.
- Provide `/chat`.
- Persist required application data through Docker volumes.

## Evaluation and CI

The project should:

- Execute the evaluation suite with one command.
- Report pass/fail results.
- Fail the build when the evaluation pass rate falls below the defined threshold.
- Preserve evaluation results as CI evidence.
- Detect regressions before merge.

---

# 7. Evaluation Plan

Evaluation cases are designed to test different categories of behavior.

| Category | What is tested |
| --------------------- | ---------------------------------------------------- |
| HR | Employee and HR policy questions |
| IT | Technology and security policy questions |
| Corporate | General company policies |
| Retrieval | Whether relevant documents are found |
| Source attribution | Whether the correct source is returned |
| Routing | Whether the correct tool is selected |
| Safety | Whether unsafe requests are blocked |
| Prompt injection | Resistance to malicious instructions |
| Risky actions | Whether approval is required |
| Unsupported questions | Appropriate handling when information is unavailable |

The current evaluation set contains **32 cases** covering the required behavioral categories.

Each evaluation case should define, where applicable:

- Question.
- Category.
- Expected tool.
- Expected source.
- Expected safety behavior.
- Expected answer characteristics.

---

# 8. Current Evaluation Baseline

The latest routing evaluation was executed against all **32 evaluation cases**.

| Metric | Current Baseline |
| --------------------------------- | ----------------: |
| Evaluation cases | 32 |
| Passed | 32 |
| Failed | 0 |
| Infrastructure errors | 0 |
| Routing pass rate | **100.00%** |
| Average latency | **2,334.53 ms** |
| P50 latency | **752.17 ms** |
| P95 latency | **6,964.21 ms** |
| Warm retrieval latency | approximately **12â€“23 ms** |
| Cold-start retrieval latency | approximately **17.37 sec** |

### Baseline Interpretation

The routing and safety evaluation currently passes all 32 cases.

Warm retrieval is low latency relative to the end-to-end request.

The main performance concern is LLM/provider latency and its effect on tail latency.

The cold-start embedding initialization is tracked separately from warm-request performance.

These measurements are the current baseline for future optimization and regression comparisons.

---

# 9. Success Metrics

The planned success targets for the project are:

| Metric | Target |
| --------------------------------- | ----------: |
| Policy answer accuracy | â‰¥ 90% |
| Source attribution accuracy | â‰¥ 90% |
| P50 latency | â‰¤ 2 seconds |
| P95 latency | â‰¤ 5 seconds |
| Cost per query | â‰¤ $0.01 |
| Prompt-injection resistance | â‰¥ 95% |
| Risky-action approval enforcement | 100% |
| Audit coverage | 100% |

These are **target acceptance criteria**, not claims that every target has already been achieved.

Actual measured results should be reported separately in the evaluation/results documentation.

---

# 10. Risks and Mitigations

| Risk | Impact | Mitigation |
| -------------------------- | -------------------- | ----------------------------------------------------------------- |
| Poor document quality | Incorrect answers | Validate source documents and retrieval results |
| Missing policy information | Unsupported answers | Return an appropriate limitation instead of inventing information |
| Incorrect retrieval | Wrong answer | Evaluate retrieval separately from generation |
| Prompt injection | Unsafe behavior | Input validation and injection detection |
| Risky tool execution | Business/data impact | Human approval gate |
| Model failure | Request failure | Error handling and model fallback/routing |
| LLM/provider latency | Poor user experience | Measure repeated runs, P50/P95, and investigate tail latency |
| Cold-start latency | Slow first request | Measure cold start separately from warm requests |
| Slow tool execution | Poor user experience | Async execution and benchmarking |
| Lost conversation state | Reduced reliability | LangGraph checkpointing |
| Deployment failure | Service unavailable | Docker healthcheck and API testing |
| Dependency vulnerabilities | Security risk | `pip-audit` |
| Code quality regressions | Maintenance risk | Ruff and automated tests |
| Evaluation regression | Reduced reliability | CI evaluation pass-rate gate |
| Scope expansion | Delivery risk | Explicit productionization scope decision |

---

# 11. Sprint Verification

The final verification checklist is:

- [x] Planning completed.
- [x] MoSCoW priorities defined.
- [x] Tasks estimated.
- [x] Stakeholder problem documented.
- [x] Success metrics defined.
- [x] Human-in-the-loop boundary documented.
- [x] Data feasibility investigated.
- [x] RAG pipeline implemented.
- [x] Agent implemented.
- [x] Routing implemented.
- [x] Safety controls implemented.
- [x] Approval workflow implemented.
- [x] Audit trail implemented.
- [x] Checkpointing implemented.
- [x] Async execution implemented.
- [x] API implemented.
- [x] Docker deployment implemented.
- [x] Automated tests implemented.
- [x] Code-quality checks performed.
- [x] Dependency audit performed.
- [x] 32-case routing evaluation executed.
- [x] Current routing baseline recorded.
- [x] Productionization scope decision documented.

### Remaining Verification

- [ ] End-to-end system verified using real policy data.
- [ ] Guardrails confirmed active during end-to-end execution.
- [ ] Audit logging confirmed active during end-to-end execution.
- [ ] Retrieval/source-quality evaluation completed.
- [ ] Final evaluation results compared against success targets.
- [ ] One-command evaluation suite created.
- [ ] Evaluation suite fails when pass rate drops below the required threshold.
- [ ] CI evaluation gate implemented.
- [ ] Productionization PR raised and reviewed.
- [ ] Every PR review comment addressed or answered with a documented reason.
- [ ] LLM/provider latency investigation completed.
- [ ] Final results and limitations documented.
- [ ] Stakeholder/mentor sign-off recorded.

---

# 12. Current Sprint Status

## Completed

The core production-oriented agent functionality is implemented, including:

- RAG retrieval.
- Agent routing.
- Safety guardrails.
- Prompt-injection detection.
- Approval workflow.
- Audit logging.
- Checkpointing.
- Async execution.
- FastAPI API.
- Docker deployment.
- Automated tests.
- Routing evaluation.
- Latency and cost instrumentation.

## In Progress

The current productionization work is focused on:

1. End-to-end verification on real policy data.
2. Verification of guardrails and audit logging.
3. Retrieval-quality evaluation.
4. LLM/provider latency investigation.
5. One-command evaluation.
6. CI regression gates.
7. Production pull-request review.

## Current Riskiest Task

**Production verification and evaluation automation â€” In Progress**

The main remaining engineering risk is proving that the existing system continues to meet its safety, evaluation, and reliability requirements automatically.

---

# 13. Sign-Off

## Intern

**Name:** _______________________________________________

**Signature:** ____________________________________________

**Date:** ________________________________________________

## Mentor

**Name:** _______________________________________________

**Signature:** ____________________________________________

**Date:** ________________________________________________

## Stakeholder

**Name:** _______________________________________________

**Signature:** ____________________________________________

**Date:** ________________________________________________

---

# 14. Summary

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
11. Production verification.
12. Automated regression detection.

The current routing evaluation contains **32 cases** and achieved a **100% pass rate** with no infrastructure errors.

The latest baseline shows a **752 ms P50** and **6.96 second P95** latency. Warm retrieval is generally low latency, while LLM/provider latency is currently the primary performance concern.

The remaining productionization work is focused on proving end-to-end behavior, completing evaluation automation, adding CI regression gates, reviewing the production PR, and documenting final results and limitations.
