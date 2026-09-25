# Final Report - Company Policy Agent

## 1. Executive Summary

The Company Policy Agent is a production-oriented AI application designed to answer questions about company policies using retrieval-augmented generation (RAG). The system combines document retrieval, agent routing, safety controls, human approval for risky operations, audit logging, evaluation gates, monitoring, and containerized deployment.

The project was developed with a production-hardening mindset rather than treating the language model as the entire application. The final system includes explicit boundaries around retrieval, tool execution, safety, approval, observability, and evaluation.

The application uses Groq as the model provider through an OpenAI-compatible API interface. LangGraph manages the agent workflow, Chroma provides vector retrieval, and Hugging Face sentence-transformer embeddings are used for document representation. FastAPI provides the production API, while Streamlit provides the interactive user interface.

The final implementation completed the major requirements for the defined project scope. Verification included automated testing, routing evaluation, retrieval evaluation, prompt-injection testing, evaluation gates, Docker deployment, API health checks, real production requests, approval workflow testing, and audit verification.

The current implementation has 41 automated tests passing, clean Ruff checks, a 100% routing evaluation pass rate across 32 cases, successful retrieval evaluation using Top-2 retrieval, 100% prompt-injection resistance on the current test dataset, and a passing production evaluation gate.

---

## 2. System Design and Architecture

The system follows a controlled agent architecture.

A user submits a policy question through the Streamlit interface or FastAPI API. The LangGraph workflow determines whether the request requires document retrieval, another tool, or no tool. Policy questions are sent to the `search_documents` tool, which retrieves relevant policy chunks from Chroma.

The retrieved evidence is then supplied to the language model so that the response can be grounded in the available company documentation.

The architecture also separates normal retrieval from risky operations. Operations such as employee-record updates, employee-record deletion, and email sending are treated as risky tools. These operations cannot be executed directly by the agent. They first enter an approval workflow.

The approval lifecycle is:

```text
User Request
    |
    v
Safety / Routing
    |
    v
Tool Selection
    |
    +----------------------+
    |                      |
    v                      v
Normal Retrieval       Risky Operation
    |                      |
    v                      v
Retrieve Evidence      Approval Required
    |                      |
    v                  +---+---+
LLM Response           |       |
                       v       v
                   Rejected  Approved
                               |
                               v
                            Execute
                               |
                               v
                          Audit Event
```

The system also maintains audit events for tool calls, approval events, and security events. LangGraph checkpointing provides durable workflow state for conversations.

---

## 3. Production Hardening

The project was deliberately extended beyond a basic RAG demonstration.

### Safety

Prompt-injection detection is applied to identify malicious instructions attempting to manipulate the agent. Input and output validation are also included.

Risky tools require explicit human approval. A production test demonstrated that an employee-record update request was intercepted and returned an approval requirement rather than executing automatically.

The approval lifecycle was independently verified through:

```text
PENDING -> APPROVED -> EXECUTED
```

Rejection was also verified, with rejected requests remaining unexecuted.

### Auditability

Application audit events are written to:

```text
audit_logs/audit.jsonl
```

The audit trail records tool execution and approval-related events, providing evidence of what the system attempted and what happened during the workflow.

### Deployment

The application is packaged with Docker and deployed using Docker Compose.

Production verification confirmed:

* Docker image builds successfully
* Container starts successfully
* Container reports healthy status
* `/health` returns `healthy`
* `/ready` returns `ready`
* Groq configuration is detected
* Chroma storage is detected
* Checkpoint storage is detected

A real production `/chat` request was also successfully processed and returned an answer, sources, and tool information.

---

## 4. Evaluation Results

Evaluation was treated as a release gate rather than an optional demonstration.

### Automated Tests

The final verification produced:

```text
41 passed
```

The only reported warning came from the installed ChromaDB telemetry implementation using a deprecated Python API. The warning did not fail the test suite.

### Code Quality

Ruff verification returned:

```text
All checks passed!
```

### Routing Evaluation

The routing evaluation contained 32 cases.

```text
Total cases: 32
Passed: 32
Pass rate: 100%
```

The dataset covered policy categories, approval cases, out-of-scope requests, and prompt-injection cases.

### Retrieval Evaluation

Retrieval quality was evaluated at different values of Top-K.

Top-1 retrieval achieved 3/4 relevant in-scope results. Top-2 and Top-3 both achieved 4/4.

The production retrieval configuration therefore uses Top-2 retrieval.

The out-of-scope no-evidence case also passed.

### Prompt-Injection Evaluation

The current injection dataset contained five cases.

```text
Blocked: 5/5
Resistance: 100%
```

This result demonstrates resistance against the tested attacks but does not establish protection against every possible adaptive, indirect, or future attack pattern.

### Production Evaluation Gate

The final evaluation gate reported:

```text
Completion rate: 100.00%
Warm P95 latency: 1080.27 ms

HR: 2/2
Company: 1/1
Out-of-scope: 1/1

Injection resistance: 100.00%

PASS: All evaluation gates satisfied.
```

These results provide evidence that the current implementation satisfies the defined evaluation thresholds.

---

## 5. Performance and Cost

Latency testing showed a substantial difference between cold-start and warm execution.

Cold-start requests are affected by embedding-model initialization. After initialization, retrieval and model execution are substantially faster.

The evaluation package measures:

* P50 latency
* P95 latency
* Cold versus warm latency
* Retrieval latency
* LLM latency
* Cost per request
* Projected monthly cost

The cost model also evaluates projected usage at 10 times the baseline volume.

The documented projection estimates approximately:

| Strategy           | 10,000 queries/month | 100,000 queries/month |
| ------------------ | -------------------: | --------------------: |
| Always small model |                $1.65 |                $16.50 |
| Always large model |                $3.30 |                $33.00 |
| Routed strategy    |               $1.815 |                $18.15 |

These are estimates based on the documented provider-pricing assumptions and usage model rather than guaranteed future billing amounts.

---

## 6. Security and Failure Handling

Several failure modes were identified and documented.

External provider rate limits are treated as an external dependency rather than an application defect. The same applies to provider/network latency.

Cold-start latency is an accepted operational limitation.

The approval queue is currently process-local and in-memory. Consequently, pending approval state is not durable across application restarts and is not shared between independent application processes or replicas. A production-scale implementation would require persistent approval storage and an appropriate approval API/workflow.

The current evaluation datasets are intentionally limited. Passing the current tests does not prove perfect production behavior.

Dependency auditing also identified known ChromaDB security advisories in the installed version. The issue is documented in `SECURITY.md` and the failure-mode documentation. The current application uses ChromaDB as local persistent storage rather than exposing a standalone network-facing Chroma service.

---

## 7. What Was Learned

The project demonstrated that productionizing an agent involves substantially more than improving the model prompt.

The most important lessons were:

### Retrieval must be measured

A RAG system can appear correct while still returning weak evidence. Testing Top-1 versus Top-2 retrieval exposed a real retrieval-quality difference. This justified a production Top-2 configuration.

### Risky actions require explicit controls

The agent should not be trusted to decide whether a sensitive operation is safe to execute. The approval gate creates a clear boundary between agent reasoning and consequential action.

### Evaluation must be executable

The evaluation suite became a build gate rather than a manually inspected report. This makes regressions visible and prevents a release from silently falling below defined quality thresholds.

### Observability matters

Latency, token usage, cost, tool execution, approval events, and audit information provide evidence about what the system is actually doing. Without these measurements, production behavior is difficult to diagnose.

---

## 8. Final Status

The major implementation and production-hardening requirements for the defined scope are complete.

Verified:

* RAG retrieval
* Agent routing
* Safety controls
* Prompt-injection protection
* Risky-tool approval
* Approval rejection
* Approval execution
* Audit logging
* Checkpointing
* FastAPI API
* Docker deployment
* Health/readiness checks
* Automated tests
* Evaluation suite
* Evaluation gates
* Cost reporting
* Security documentation
* Failure-mode documentation
* Sprint Board
* Handover Pack
* Independent verification

Remaining activities are delivery and project-completion activities:

* PR review and comment evidence
* Demo delivery
* Stakeholder feedback capture
* Final retrospective submission

No additional application feature development is required unless final verification identifies a defect that blocks an existing requirement.

---

## 9. Conclusion

The Company Policy Agent has progressed from an agent/RAG prototype into a production-oriented system with explicit controls around retrieval, safety, approval, auditability, evaluation, and deployment.

The final verification evidence demonstrates that the system operates successfully on real policy data, blocks the tested prompt-injection cases, prevents automatic execution of risky operations, records relevant audit events, passes its automated test suite, satisfies the defined evaluation gate, and runs successfully in a Dockerized production environment.

The remaining limitations are documented rather than hidden. In particular, approval persistence, dependency security updates, broader adversarial testing, larger evaluation datasets, and production-scale operational evidence remain areas for future hardening.

For the current project scope, the implementation is feature-complete and ready for final handover, demonstration, and reporting.

