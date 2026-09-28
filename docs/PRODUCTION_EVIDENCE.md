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

A real production smoke-test request was sent to:

```text
POST /chat
```

Question:

```text
What is the leave policy?
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

Latest successful smoke-test request:

```text
request_id:
2d1822b1-934f-49e8-92d6-19fc2ed57f2e

thread_id:
production-smoke-final-001
```

Returned source:

```text
hr_policy.pdf
```

Tool used:

```text
search_documents
```

Retrieval status:

```text
RELEVANT
```

The response returned a policy answer covering available leave types, the leave-request process, manager/HR communication, emergency leave, and consequences of unauthorized absence.

---

## 5. Live Runtime Monitoring

The application exposes a `/metrics` endpoint containing runtime request, latency, retrieval, LLM, token, cost, and error information.

The latest successful production smoke test was followed by this metrics snapshot:

| Metric                    |      Result |
| ------------------------- | ----------: |
| HTTP requests             |          10 |
| Successful HTTP requests  |           8 |
| Recorded request errors   |           1 |
| LLM requests              |           2 |
| Successful LLM requests   |           2 |
| Tool-using requests       |           2 |
| Retrieval successes       |           2 |
| Error rate                |       10.0% |
| Average HTTP latency      |   282.89 ms |
| HTTP p50 latency          |     1.54 ms |
| HTTP p95 latency          | 1,339.20 ms |
| Average chat latency      |   841.09 ms |
| Chat p50 latency          |   909.41 ms |
| Chat p95 latency          | 1,543.40 ms |
| Average retrieval latency |    64.87 ms |
| Retrieval p95 latency     |   107.36 ms |
| Average LLM latency       | 1,085.20 ms |
| LLM p95 latency           | 1,273.53 ms |
| Prompt tokens             |       1,082 |
| Completion tokens         |         748 |
| Total tokens              |       1,830 |
| Total LLM cost            |   $0.000306 |
| Average cost/request      |   $0.000153 |

The metrics demonstrate that application-level monitoring is recording real runtime data rather than returning static or placeholder values.

### Metrics interpretation

The measured `10.0%` error rate should **not** be interpreted as a production-scale error-rate estimate.

The sample includes a deliberately generated invalid-input request used to verify failure monitoring. The traffic volume is also too small to represent normal production behavior.

The latency percentiles are similarly based on a small smoke-test sample and are included as verification evidence rather than as a statistically representative production performance benchmark.

---

## 6. Failure Monitoring and Recovery

Failure handling was explicitly tested using controlled failure scenarios.

### 6.1 Invalid request handling

An intentionally invalid request was sent with an empty question.

The API returned:

```text
HTTP 400

error:
invalid_request

message:
Question cannot be empty.

request_id:
b38c91e3-8e10-4922-b8f0-2f75a9b698a7

thread_id:
monitoring-invalid-001
```

This demonstrates that invalid input is rejected at the API layer with:

* an appropriate HTTP status
* a structured error response
* a unique request ID
* the associated thread ID

The invalid request did not invoke the LLM.

---

### 6.2 LLM service failure handling

A controlled failure-injection test was performed using a temporary invalid Groq model configuration.

The normal `.env` file was not modified.

The temporary test API returned:

```text
HTTP 503

error:
llm_unavailable

message:
The Groq LLM service is currently unavailable.

request_id:
c8c74421-b060-4d30-931d-eed4007d6c63

thread_id:
monitoring-llm-failure-001
```

This demonstrates that an underlying LLM service failure is converted into a controlled HTTP `503 Service Unavailable` response rather than exposing an unhandled provider exception.

---

### 6.3 LLM failure metrics

The temporary failure-injection API produced the following monitoring snapshot:

| Metric                              |    Result |
| ----------------------------------- | --------: |
| Requests                            |         3 |
| LLM requests                        |         2 |
| LLM errors                          |         2 |
| LLM service errors                  |         2 |
| Request errors                      |         2 |
| Error rate                          |    66.67% |
| Average HTTP latency                | 349.88 ms |
| HTTP p95 latency                    | 529.72 ms |
| Average chat latency                | 345.88 ms |
| Average retrieval latency           |  67.98 ms |
| Average LLM failure latency         | 189.30 ms |
| Successful LLM requests with tokens |         0 |
| Total tokens                        |         0 |
| Total cost                          |     $0.00 |

The `66.67%` error rate is specific to the intentional failure-injection test and must not be interpreted as a production error-rate estimate.

The important monitoring evidence is that:

```text
llm_requests_total
llm_errors_total
llm_service_errors_total
requests_errors_total
```

were all recorded by the application.

No successful LLM generation occurred during the failure test, so:

```text
prompt_tokens = 0
completion_tokens = 0
total_tokens = 0
cost = $0.00
```

---

### 6.4 Recovery verification

After the controlled failure test:

1. the temporary API server was stopped
2. the temporary `GROQ_MODEL` environment override was removed
3. the project `.env` file was not modified
4. the normal Groq configuration was verified
5. `/ready` returned `ready`
6. a normal `/chat` request succeeded again

Normal configuration after recovery:

```text
GROQ_API_KEY loaded: True

GROQ_MODEL:
openai/gpt-oss-20b
```

Readiness after recovery:

```text
status: ready

groq_api_key=True
groq_model=True
chroma_storage=True
checkpoint_storage=True
```

A subsequent real request to port `8000` succeeded with:

```text
request_id:
2d1822b1-934f-49e8-92d6-19fc2ed57f2e

thread_id:
production-smoke-final-001

tool:
search_documents

source:
hr_policy.pdf

retrieval_status:
RELEVANT
```

This verifies that the controlled failure test did not permanently affect the normal application configuration.

---

## 7. LangSmith Trace Verification

A successful request was verified through LangSmith tracing.

Successful request:

```text
request_id:
c1933d35-0cf3-4a10-8114-a450a0a81550

thread_id:
langsmith-success-002

question:
What is the leave policy?
```

The trace recorded the router and retrieval execution.

LLM metadata:

| Metric            |               Result |
| ----------------- | -------------------: |
| Model             | `openai/gpt-oss-20b` |
| Prompt tokens     |                  541 |
| Completion tokens |                  374 |
| Reasoning tokens  |                  230 |
| Total tokens      |                  915 |
| LLM latency       |          1,294.45 ms |
| Cost              |          $0.00015277 |

Retrieval metadata:

| Metric              |          Result |
| ------------------- | --------------: |
| Documents retrieved |               3 |
| Retrieval latency   |       112.08 ms |
| Context characters  |           1,994 |
| Retrieval status    |      `RELEVANT` |
| Source              | `hr_policy.pdf` |

The retrieved distance scores were:

```text
0.9156
0.9465
0.9747
```

These values represent retrieval distances rather than confidence percentages. Lower distance indicates greater similarity according to the configured retrieval metric.

The LangSmith trace provides an external observability record of the request execution and complements the application's own runtime metrics.

---

## 8. Evaluation Results

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

## 9. Latency Evaluation

The evaluation showed a significant cold-start effect.

### Cold start

```text
Cold-start latency: 21.539 seconds
```

### Warm requests

```text
Warm average: 801.66 ms

Warm p50: 838.48 ms

Warm p95: 1,410.55 ms
```

The production API therefore warms the retrieval model during application startup.

This avoids paying the embedding initialization cost on the first user request after deployment.

---

## 10. Cost Evaluation

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

## 11. Model Routing

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

## 12. Retrieval Quality Investigation

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

## 13. Prompt-Injection Evaluation

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

## 14. Safety and Approval Controls

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

## 15. CI Quality Gates

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

41 passed

pip check:

No broken requirements found
```

There is currently one dependency-related deprecation warning from ChromaDB's telemetry implementation, but it does not cause the test suite to fail.

---

## 16. Security Review

`pip-audit` identified four unique security advisories affecting the currently pinned ChromaDB version.

The project does not expose ChromaDB as a standalone network service. ChromaDB is used through local persistent storage inside the application architecture.

The advisories and architectural mitigation are documented in:

```text
SECURITY.md
```

The dependency remains an explicitly documented security exception rather than being silently ignored.

The dependency should be re-evaluated when an appropriate patched release becomes available.

---

## 17. Repository Verification

Final Git verification:

```text
Branch:

main

Remote:

origin/main

Working tree:

Modified during the current production-hardening update; final clean-tree status will be verified after the changes are committed.
```

The repository is synchronized with origin/main; the working tree contains the production-hardening changes described above, which will be committed after final verification.

---

## 18. Production Readiness Evidence

The completed production checklist is:

* [x] Standup / riskiest task identified
* [x] Retrieval quality investigated
* [x] Docker deployment
* [x] Health check
* [x] Readiness check
* [x] Runtime monitoring
* [x] LLM failure monitoring
* [x] API validation failure monitoring
* [x] LLM recovery verification
* [x] LangSmith trace verification
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

## 19. Known Limitations

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

10. The live monitoring metrics were collected from a small local smoke-test sample and should not be interpreted as statistically representative production traffic.

11. The LLM failure metrics were generated through intentional failure injection using a temporary invalid model configuration.

12. Failure-injection results demonstrate error handling and observability behavior but do not represent normal provider reliability.

These limitations are documented rather than hidden.

---

## 20. Final Status

The project has completed its planned production-hardening work.

The final verification demonstrates that the deployed application can:

Receive a real request
        |
        v
Validate the request
        |
        v
Route it
        |
        v
Retrieve policy evidence
        |
        v
Generate an answer
        |
        v
Return sources
        |
        v
Record execution trace
        |
        v
Record retrieval latency
        |
        v
Record LLM latency
        |
        v
Record token usage
        |
        v
Record cost
        |
        v
Monitor failures
        |
        v
Return controlled errors
        |
        v
Recover to normal operation

The production verification also demonstrated controlled behavior for both invalid API input and LLM service failure.

The Docker service is healthy, runtime monitoring is operational, and the production verification evidence has been completed. Final repository cleanliness will be verified after the production-hardening changes are committed.





