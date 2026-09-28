# Production Evidence

## 1. Project

**Project:** Company Policy Agent
**Repository:** `week2day5proj1`
**Deployment:** Docker + FastAPI
**LLM Provider:** Groq
**Vector Store:** ChromaDB
**Embeddings:** `sentence-transformers/all-MiniLM-L6-v2`

---

## 2. Production Architecture

The application implements an end-to-end policy question-answering agent:

```text
User
  |
  v
FastAPI
  |
  v
LangGraph Agent
  |
  +--> Router
  |
  +--> search_documents
          |
          v
       ChromaDB
          |
          v
      Retrieved context
          |
          v
       Groq LLM
          |
          v
   Answer + Sources + Trace
          |
          v
       Metrics
```

The application also includes:

* durable LangGraph checkpointing
* input safety validation
* prompt-injection detection
* output validation
* approval gates for risky actions
* audit logging
* runtime metrics
* Docker health checks
* CI quality gates
* evaluation suites
* dependency vulnerability review

---

## 3. Deployment Verification

Docker Compose reports the production container as healthy:

```text
week2day5proj1-company-policy-agent-1
STATUS: Up (healthy)
PORT: 8000
```

The service exposes:

* `/health`
* `/ready`
* `/metrics`
* `/chat`
* `/checkpoint/{thread_id}`

Health verification returned:

```text
status: healthy
service: company-policy-agent
version: 1.1.0
```

Readiness verification confirmed:

```text
groq_api_key=True
groq_model=True
chroma_storage=True
checkpoint_storage=True
```

---

## 4. Live End-to-End Request

A real production request was sent to:

```text
POST /chat
```

Question:

```text
What does the company say about professional conduct?
```

The deployed application successfully:

1. accepted the request through FastAPI
2. routed the question to `search_documents`
3. retrieved relevant policy documents
4. generated an answer using the Groq LLM
5. returned source documents
6. returned a request ID and thread ID
7. recorded execution trace information
8. recorded runtime metrics

Returned sources:

```text
hr_policy.pdf
company_policy.pdf
```

Tool used:

```text
search_documents
```

Retrieval status:

```text
RELEVANT
```

---

## 5. Live Runtime Metrics

The live request produced the following metrics:

| Metric                   |    Result |
| ------------------------ | --------: |
| Chat requests            |         1 |
| Successful chat requests |         1 |
| LLM requests             |         1 |
| Successful LLM requests  |         1 |
| Tool-using requests      |         1 |
| Retrieval successes      |         1 |
| Error rate               |        0% |
| Chat latency             |  7,526 ms |
| Retrieval latency        |  4,357 ms |
| LLM latency              |  2,370 ms |
| Prompt tokens            |       433 |
| Completion tokens        |       395 |
| Total tokens             |       828 |
| Request cost             | $0.000151 |

The metrics demonstrate that application-level monitoring is recording real production request data rather than returning static or placeholder values.

---

## 6. Evaluation Results

The main evaluation suite contains five representative cases.

Latest results:

| Metric                          |    Result |
| ------------------------------- | --------: |
| Completed cases                 |         5 |
| Passed                          |         5 |
| Failed                          |         0 |
| Errors                          |         0 |
| Completion rate                 |      100% |
| Pass rate among completed cases |      100% |
| Source hit rate                 |      100% |
| In-scope retrieval success      |      100% |
| Out-of-scope no-evidence        |       1/1 |
| Average documents retrieved     |         3 |
| Average prompt tokens           |     470.8 |
| Average completion tokens       |     360.2 |
| Average total tokens            |       831 |
| Average cost/query              | $0.000143 |

The evaluation set is intentionally small and should not be interpreted as evidence of 100% real-world accuracy.

---

## 7. Latency Evaluation

The evaluation showed a significant cold-start effect.

### Cold start

```text
Cold-start latency: 21.539 seconds
```

### Warm requests

```text
Warm average: 801.66 ms
Warm p50:      838.48 ms
Warm p95:    1,410.55 ms
```

The production API therefore warms the retrieval model during application startup.

This avoids paying the embedding initialization cost on the first user request after deployment.

---

## 8. Cost Evaluation

Measured evaluation cost:

```text
Average cost/query: $0.000143
```

Projected costs from the evaluation assumptions:

|          Volume | Projected cost |
| --------------: | -------------: |
|   1,000 queries |         $0.143 |
|  10,000 queries |         $1.434 |
| 100,000 queries |        $14.338 |

These projections are modeled estimates rather than guaranteed future bills.

---

## 9. Model Routing

The project supports a small-model-first routing strategy:

```text
openai/gpt-oss-20b
        |
        | failure/escalation
        v
openai/gpt-oss-120b
```

The routing evaluation and cost model estimate the potential savings from using the smaller model for normal requests and escalating only when required.

The modeled routing cost is approximately 45% lower than the modeled always-large-model baseline under the documented assumptions.

This is a modeled estimate and should be validated against production traffic before being treated as an actual savings figure.

---

## 10. Retrieval Quality Investigation

Retrieval quality was investigated using a dedicated benchmark.

The investigation tested:

* relevant document retrieval
* top-1 retrieval
* top-2 retrieval
* top-3 retrieval
* query expansion
* chunk size
* chunk overlap
* section-aware chunking
* document metadata
* embedding behavior

The final configuration uses:

```text
Embedding:
sentence-transformers/all-MiniLM-L6-v2

Chunk size:
800

Chunk overlap:
120

Vector store:
ChromaDB

Collection:
capstone_documents
```

The investigation found that section-aware chunking did not improve the benchmark's top-1 result, so it was not adopted.

---

## 11. Prompt-Injection Evaluation

The injection evaluation contains five cases covering:

* direct instruction override
* role override
* policy bypass
* instruction override
* system-prompt extraction

Latest result:

```text
Passed: 5/5
Failed: 0
Errors: 0
Resistance rate: 100%
```

This provides evidence that the current guardrails resisted the tested injection examples.

Because the test set is small, this should be treated as limited evidence rather than proof of complete prompt-injection protection.

---

## 12. Safety and Approval Controls

Risky tools are protected by an approval workflow.

Examples include:

```text
update_employee_record
delete_employee_record
send_email
```

The approval lifecycle supports:

```text
PENDING
   |
   +--> REJECTED
   |
   +--> APPROVED
           |
           v
        EXECUTED
```

Tests cover:

* pending approvals blocking execution
* rejected approvals blocking execution
* approved actions executing
* execution status being recorded

Read-only document retrieval does not require approval.

---

## 13. CI Quality Gates

The project CI pipeline checks:

* dependency installation
* Ruff linting
* pytest
* evaluation gate
* dependency auditing

Latest local verification:

```text
Ruff:
All checks passed

Pytest:
40 passed

pip check:
No broken requirements found
```

There is currently one dependency-related deprecation warning from ChromaDB's telemetry implementation, but it does not cause the test suite to fail.

---

## 14. Security Review

`pip-audit` identified four unique security advisories affecting the currently pinned ChromaDB version.

The project does not expose ChromaDB as a standalone network service. ChromaDB is used through local persistent storage inside the application architecture.

The advisories and architectural mitigation are documented in:

```text
SECURITY.md
```

The dependency remains an explicitly documented security exception rather than being silently ignored.

The dependency should be re-evaluated when an appropriate patched release becomes available.

---

## 15. Repository Verification

Final Git verification:

```text
Branch:
main

Remote:
origin/main

Working tree:
clean
```

The repository is synchronized with the remote branch and contains no uncommitted changes.

---

## 16. Production Readiness Evidence

The completed production checklist is:

* [x] Standup / riskiest task identified
* [x] Retrieval quality investigated
* [x] Docker deployment
* [x] Health check
* [x] Readiness check
* [x] Runtime monitoring
* [x] CI lint gate
* [x] CI test gate
* [x] Evaluation gate
* [x] Prompt-injection evaluation
* [x] Dependency vulnerability investigation
* [x] Security exception documented
* [x] Cost evaluation
* [x] Latency evaluation
* [x] Safety approval gates
* [x] Audit trail
* [x] Durable checkpointing
* [x] Live end-to-end request
* [x] Live metrics verification
* [x] Final Git verification

---

## 17. Known Limitations

The current production evidence has several limitations:

1. The main evaluation set contains only five cases.
2. The injection evaluation contains only five test cases.
3. Evaluation scoring includes keyword-based checks.
4. Model/API latency depends on external network and provider conditions.
5. Cold-start latency remains substantially higher than warm-request latency.
6. Runtime metrics are currently in-memory and reset when the application restarts.
7. Cost projections depend on documented token and routing assumptions.
8. ChromaDB security advisories remain an explicitly documented dependency exception.
9. Retrieval performance depends on the current document corpus and embedding model.

These limitations are documented rather than hidden.

---

## 18. Final Status

The project has completed its planned production-hardening work.

The final verification demonstrates that the deployed application can:

```text
Receive a real request
        ↓
Route it
        ↓
Retrieve policy evidence
        ↓
Generate an answer
        ↓
Return sources
        ↓
Record execution trace
        ↓
Record latency
        ↓
Record token usage
        ↓
Record cost
```

The repository is clean, the Docker service is healthy, and the production verification has been completed.
