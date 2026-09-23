# Company Policy Agent

Production-oriented RAG agent for answering company-policy questions using local document retrieval, Groq-hosted LLMs, LangGraph orchestration, durable checkpointing, safety guardrails, approval workflows, audit logging, evaluation gates, monitoring, and Docker deployment.

## 1. Project Overview

The Company Policy Agent is an end-to-end AI application designed to answer questions from internal company policy documents.

The system combines:

* RAG over company policy PDFs
* Local Hugging Face embeddings
* Chroma vector storage
* Groq-hosted OpenAI-compatible LLMs
* LangGraph agent orchestration
* Durable conversation checkpointing
* Tool routing
* Safety and prompt-injection guardrails
* Human approval for risky actions
* Audit logging
* Production API endpoints
* Runtime metrics
* Automated evaluation
* Injection-resistance evaluation
* CI quality gates
* Docker deployment

The goal is not simply to demonstrate an LLM application, but to demonstrate a production-oriented AI system with measurable quality, safety, observability, and deployment controls.

---

# 2. Architecture

```text
                         ┌──────────────────────┐
                         │      Client/UI       │
                         │    Streamlit/API     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      FastAPI API     │
                         │ /health /ready       │
                         │ /metrics /chat       │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     LangGraph        │
                         │   Agent Workflow     │
                         └──────────┬───────────┘
                                    │
                     ┌──────────────┼──────────────┐
                     │              │              │
                     ▼              ▼              ▼
              ┌────────────┐ ┌────────────┐ ┌─────────────┐
              │   Router   │ │   Safety   │ │ Checkpoint  │
              │            │ │ Guardrails │ │   Storage   │
              └─────┬──────┘ └────────────┘ └─────────────┘
                    │
          ┌─────────┴─────────┐
          │                   │
          ▼                   ▼
 ┌────────────────┐   ┌──────────────────┐
 │ search_documents│   │ Risky operations │
 │      Tool       │   │ Approval Gate    │
 └───────┬────────┘   └────────┬─────────┘
         │                     │
         ▼                     ▼
 ┌────────────────┐     ┌───────────────┐
 │    Chroma      │     │ Human Approval│
 │ Vector Store   │     │ Queue         │
 └───────┬────────┘     └───────────────┘
         │
         ▼
 ┌────────────────────────────┐
 │ Local HF Embeddings        │
 │ all-MiniLM-L6-v2           │
 └────────────────────────────┘

                    ┌──────────────────────┐
                    │      Groq LLM        │
                    │ OpenAI-compatible API│
                    └──────────────────────┘

                    ┌──────────────────────┐
                    │ Audit + Metrics      │
                    │ Evaluation + Tracing │
                    └──────────────────────┘
```

---

# 3. Main Components

## API

FastAPI provides:

* `GET /health`
* `GET /ready`
* `GET /metrics`
* `POST /chat`
* `GET /checkpoint/{thread_id}`

The API exposes request IDs, thread IDs, answers, sources, tools used, and execution traces.

## Agent

LangGraph manages the agent workflow and durable state.

The state includes information such as:

* request ID
* session ID
* question
* conversation history
* selected tool
* answer
* sources
* tools used
* retrieval metadata
* approval status
* LLM metadata
* execution trace

## Router

The router determines whether a request should:

* search company documents
* perform a risky employee operation
* return without using a tool

The `search_documents` tool does not require approval.

Risky operations are routed through the approval workflow.

---

# 4. RAG Pipeline

The current policy corpus contains:

```text
data/
├── hr_policy.pdf
├── company_policy.pdf
└── it_policy.pdf
```

The ingestion pipeline:

1. Loads PDF documents.
2. Preserves source metadata.
3. Splits documents into chunks.
4. Generates local embeddings.
5. Stores vectors in Chroma.

Current configuration:

```text
Embedding model:
sentence-transformers/all-MiniLM-L6-v2

Chunk size:
800

Chunk overlap:
120

Chroma collection:
capstone_documents

Storage:
storage/chroma
```

The latest clean ingestion produced:

```text
21 PDF pages
39 chunks
```

The system uses local embeddings rather than a hosted embedding API.

---

# 5. Retrieval

The retrieval layer uses Chroma similarity search with local Hugging Face embeddings.

The retrieval system includes query expansion for policy questions involving areas such as:

* working hours
* time off
* company information
* company mission

The retrieval quality investigation was completed before final productionization.

The investigation compared retrieval behavior and confirmed that the current chunking and embedding configuration provided better results than the tested section-aware alternative.

The retrieval threshold is intentionally kept as part of the current production configuration rather than being changed solely to improve a small evaluation set.

---

# 6. LLM Configuration

The application uses Groq as the API provider through its OpenAI-compatible API.

The application does **not** require a direct OpenAI API key.

Primary model configuration:

```text
GROQ_MODEL=openai/gpt-oss-20b
GROQ_LARGE_MODEL=openai/gpt-oss-120b
GROQ_SAFETY_MODEL=openai/gpt-oss-safeguard-20b
```

The application uses the Groq OpenAI-compatible endpoint.

The production routing design supports a small-model-first strategy with escalation to the larger model when required.

---

# 7. Model Routing

The production design uses:

```text
User request
     │
     ▼
Small model
     │
     ├── Success ──────────► Return result
     │
     └── Failure / escalation
                │
                ▼
          Large model
```

The objective is to avoid sending every request to the larger model.

Cost projections for routing are maintained separately from measured evaluation costs.

---

# 8. Safety

The application includes multiple safety layers.

## Input validation

Inputs are checked before agent execution.

## Prompt-injection detection

The application detects common attempts to override system instructions or bypass policy controls.

Examples evaluated include:

* direct instruction override
* role override
* policy bypass
* instruction override
* system prompt extraction

## Output validation

Generated output is checked before being returned to the client.

## Risky tool protection

Risky operations include:

* `update_employee_record`
* `delete_employee_record`
* `send_email`

These operations require explicit approval.

---

# 9. Human Approval Workflow

Risky actions follow:

```text
User request
     │
     ▼
Risky tool detected
     │
     ▼
Approval required
     │
     ├── REJECTED ──► Action blocked
     │
     ├── PENDING ───► Action blocked
     │
     └── APPROVED ──► Execute action
                           │
                           ▼
                       EXECUTED
```

Approval tests cover:

* pending requests
* rejected requests
* approved requests
* execution after approval
* safety behavior

This prevents high-impact tools from executing directly from an LLM decision.

---

# 10. Audit Logging

Tool calls are recorded using request IDs and audit metadata.

The audit system provides traceability for:

* request ID
* tool name
* operation
* success/failure
* relevant metadata

Audit artifacts are intentionally excluded from source control when appropriate.

For example:

```gitignore
audit.json
```

---

# 11. Durable Checkpointing

LangGraph durable checkpointing is implemented for conversation state.

Each conversation uses a thread ID.

The API and UI use the thread ID to resume conversation state.

Checkpoint storage is persisted separately from the application container.

This allows the application to restart without losing durable conversation state.

---

# 12. Monitoring

The application exposes runtime metrics through:

```text
GET /metrics
```

Metrics include:

* total requests
* successful requests
* LLM requests
* successful LLM requests
* chat requests
* tool-using requests
* retrieval requests
* latency
* chat latency
* retrieval latency
* LLM latency
* error rate
* token usage
* estimated LLM cost

Example production measurements from a recent run included:

```text
LLM requests:              2
LLM prompt tokens:       866
LLM completion tokens:   790
LLM total tokens:       1656
```

The monitoring layer was verified using real API requests.

---

# 13. Health and Readiness

The application exposes:

```text
GET /health
GET /ready
```

Health verifies that the service is running.

Readiness verifies important production dependencies such as:

* Groq API configuration
* model configuration
* Chroma storage
* checkpoint storage

Example successful readiness state:

```text
ready
```

with all required dependencies reported as available.

---

# 14. Docker Deployment

The production container uses:

```text
python:3.12-slim
```

The container starts FastAPI using Uvicorn:

```text
uvicorn app.api:app --host 0.0.0.0 --port 8000
```

Docker Compose exposes:

```text
localhost:8000
```

Persistent storage includes:

```text
./storage/chroma:/app/storage/chroma
checkpoint_data:/app/storage/checkpoints
```

The service includes a Docker health check against:

```text
/health
```

The production container was successfully started and reported healthy.

---

# 15. Evaluation Dataset

The main evaluation set currently contains 5 cases:

| ID               | Category     | Purpose                         |
| ---------------- | ------------ | ------------------------------- |
| hr_001           | HR           | Professional conduct            |
| hr_002           | HR           | Workplace harassment            |
| company_001      | Company      | Policy violation                |
| it_001           | IT           | Information protection          |
| out_of_scope_001 | Out-of-scope | Unsupported stock-price request |

The evaluation checks:

* answer correctness
* expected keywords
* source correctness
* completion
* latency
* retrieval behavior
* cost

The evaluation dataset is intentionally small at this stage and should grow as production traces become available.

---

# 16. Latest Evaluation Results

The latest production evaluation completed successfully.

```text
Total cases:       5
Passed:            5
Failed:            0
Errors:            0
Completion rate:   100%
Pass rate:         100%
```

## Category Results

| Category     | Passed | Total | Pass Rate |
| ------------ | -----: | ----: | --------: |
| HR           |      2 |     2 |      100% |
| Company      |      1 |     1 |      100% |
| IT           |      1 |     1 |      100% |
| Out-of-scope |      1 |     1 |      100% |

The evaluation gate now reads the evaluator's `category_stats` field directly and verifies each category independently.

---

# 17. Retrieval Evaluation

Latest retrieval results:

| Metric                              | Result |
| ----------------------------------- | -----: |
| Source hit rate                     |   100% |
| In-scope retrieval success          |   100% |
| In-scope cases with evidence        |    4/4 |
| Out-of-scope no-evidence rate       |   100% |
| Out-of-scope cases with no evidence |    1/1 |
| Average documents retrieved         |   3.00 |
| Average retrieval distance          | 0.8194 |

The latest evaluation therefore produced evidence for all four in-scope cases and correctly produced no evidence for the out-of-scope case.

---

# 18. Latency Evaluation

Latency is measured separately for cold-start and warm requests.

Latest results:

| Metric                  |       Result |
| ----------------------- | -----------: |
| Cold-start latency      | 31,171.76 ms |
| Overall average latency |  6,841.10 ms |
| Overall P50             |  1,006.61 ms |
| Overall P95             | 25,156.06 ms |
| Warm average            |    758.43 ms |
| Warm P50                |    950.93 ms |
| Warm P95                |  1,080.27 ms |

The large cold-start value is primarily associated with local embedding-model initialization.

For production gating, the system uses **warm P95 latency** rather than treating the one-time initialization event as representative steady-state request latency.

The current latency gate is:

```text
Maximum warm P95:
20,000 ms
```

Latest warm P95:

```text
1,080.27 ms
```

Therefore the latency gate passes.

Cold-start latency remains reported separately so that startup behavior is not hidden.

---

# 19. Cost Evaluation

Latest measured evaluation usage:

| Metric                    |      Result |
| ------------------------- | ----------: |
| Average prompt tokens     |      470.75 |
| Average completion tokens |      337.00 |
| Average reasoning tokens  |      201.75 |
| Average total tokens      |      807.75 |
| Average cost/query        | $0.00013641 |
| Total evaluation cost     | $0.00054562 |

Projected cost using the measured average cost/query:

| Query volume | Projected cost |
| -----------: | -------------: |
|        1,000 |        $0.1364 |
|       10,000 |        $1.3640 |
|      100,000 |       $13.6405 |

These are estimates, not billing guarantees.

Actual production cost can change based on:

* token usage
* model selection
* routing behavior
* provider pricing
* request distribution
* retries
* traffic volume

---

# 20. Model-Routing Cost Projection

A separate routing model is maintained for planning.

The routing assumptions include:

```text
Base volume:
10,000 queries

Projected volume:
100,000 queries

Prompt tokens/query:
1,000

Completion tokens/query:
300

Large-model routing:
10%
```

The modeled routing cost is approximately:

```text
Small model:
$0.000165/query

Large model:
$0.000330/query

Modeled routed cost:
$0.0001815/query
```

The routing model estimates approximately 45% savings versus routing every request to the larger model under those assumptions.

This is a **modeled projection**, not the same as the measured evaluation cost.

---

# 21. Injection-Resistance Evaluation

The injection evaluation currently contains 5 adversarial cases.

Latest result:

```text
Passed:              5/5
Injection resistance: 100%
Errors:              0
```

Evaluated attack categories include:

* direct override
* role override
* policy bypass
* instruction override
* system prompt extraction

The CI gate requires:

```text
Minimum injection resistance:
90%
```

The latest result is:

```text
100%
```

---

# 22. Production Evaluation Gate

The production gate currently enforces:

| Gate                 |   Threshold | Latest Result |
| -------------------- | ----------: | ------------: |
| Overall pass rate    |       ≥ 90% |          100% |
| Completion rate      |       ≥ 95% |          100% |
| Category pass rate   |       ≥ 80% |          100% |
| Warm P95 latency     | ≤ 20,000 ms |   1,080.27 ms |
| Injection resistance |       ≥ 90% |          100% |

Latest result:

```text
============================================================
EVALUATION GATE
============================================================
Overall pass rate: 100.00%
Completion rate: 100.00%
Warm P95 latency: 1080.27 ms

Category checks:
  HR: 2/2 passed (100.00%), errors=0
  Company: 1/1 passed (100.00%), errors=0
  IT: 1/1 passed (100.00%), errors=0
  Out-of-scope: 1/1 passed (100.00%), errors=0

Injection resistance: 100.00%

============================================================
PASS: All evaluation gates satisfied.
============================================================
```

---

# 23. CI Quality Gates

The project uses GitHub Actions for automated quality checks.

CI includes:

1. Dependency installation
2. Vector-store build
3. Ruff linting
4. Pytest
5. Evaluation gate
6. Injection-resistance evaluation
7. Dependency auditing

The project also uses:

```text
ruff
pytest
pip check
pip-audit
```

Local verification:

```text
Ruff:
All checks passed!

Pytest:
40 passed, 1 warning

pip check:
No broken requirements found.

Evaluation gate:
PASS
```

---

# 24. Test Suite

The latest local test run:

```text
40 passed
1 warning
```

The warning originates from a ChromaDB telemetry dependency using the deprecated:

```text
asyncio.iscoroutinefunction
```

The warning does not currently cause test failure.

The project should continue monitoring this dependency as Python evolves.

---

# 25. Dependency Security

Dependency auditing is performed with:

```text
pip-audit
```

The current ChromaDB version has documented security advisories for which a patched release was not available during the project's security review.

The application uses ChromaDB as local persistent storage rather than exposing a standalone ChromaDB server to untrusted clients.

This reduces the relevant exposure surface but does not eliminate the underlying dependency advisories.

The findings and architectural mitigation are documented separately in:

```text
SECURITY.md
```

The project does not claim that the dependency has no known vulnerabilities.

---

# 26. Observability and Tracing

The project supports LangSmith tracing through environment variables.

Example configuration:

```text
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=week2day5proj1
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

Tracing can be used to investigate:

* router decisions
* tool execution
* retrieval
* LLM calls
* latency
* failed requests
* agent execution paths

The application also maintains its own request-level trace information for production observability.

---

# 27. Project Structure

```text
week2day5proj1/
│
├── app/
│   ├── agent.py
│   ├── api.py
│   ├── approval.py
│   ├── audit.py
│   ├── ingest.py
│   ├── llm.py
│   ├── rag.py
│   ├── retrieval.py
│   ├── risky_tools.py
│   ├── router.py
│   ├── safety.py
│   ├── state.py
│   ├── tools.py
│   └── ...
│
├── data/
│   ├── hr_policy.pdf
│   ├── company_policy.pdf
│   └── it_policy.pdf
│
├── evals/
│   ├── evaluation_dataset.json
│   ├── evaluation_results.json
│   ├── injection_results.json
│   ├── routing_evaluation_results.json
│   ├── cost_projection.json
│   ├── evaluate.py
│   ├── evaluate_injection.py
│   ├── evaluate_retrieval.py
│   ├── evaluate_routing.py
│   └── check_evaluation_gate.py
│
├── tests/
│   ├── test_approval.py
│   ├── test_approval_execution.py
│   ├── test_approval_safety.py
│   ├── test_async_tools.py
│   ├── test_audit.py
│   ├── test_checkpoint.py
│   ├── test_checkpoint_resume.py
│   ├── test_groq.py
│   ├── test_llm.py
│   ├── test_metrics.py
│   └── test_safety.py
│
├── audit_logs/
│
├── storage/
│   └── chroma/
│
├── charts/
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── evaluation.yml
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── SECURITY.md
├── README.md
└── .gitignore
```

---

# 28. Running Locally

Create and activate the virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Configure environment variables in:

```text
.env
```

Build the vector store:

```powershell
python -m app.ingest
```

Run the API:

```powershell
uvicorn app.api:app --reload
```

The API is then available on:

```text
http://localhost:8000
```

---

# 29. Running with Docker

Build and start the production service:

```powershell
docker compose up -d --build
```

Check the service:

```powershell
docker compose ps
```

Check health:

```powershell
Invoke-WebRequest http://localhost:8000/health
```

Check readiness:

```powershell
Invoke-WebRequest http://localhost:8000/ready
```

Check metrics:

```powershell
Invoke-WebRequest http://localhost:8000/metrics
```

Stop the service:

```powershell
docker compose down
```

---

# 30. Running Tests

Run the full test suite:

```powershell
python -m pytest -q
```

Run Ruff:

```powershell
python -m ruff check .
```

Check installed dependency consistency:

```powershell
python -m pip check
```

Run the functional evaluation:

```powershell
python -m evals.evaluate
```

Run injection evaluation:

```powershell
python -m evals.evaluate_injection
```

Run the production evaluation gate:

```powershell
python -m evals.check_evaluation_gate
```

Run dependency auditing:

```powershell
python -m pip_audit
```

---

# 31. Evaluation Artifacts

The project generates evaluation artifacts including:

```text
evals/evaluation_results.json
evals/injection_results.json
evals/routing_evaluation_results.json
evals/cost_projection.json
```

Evaluation charts include:

```text
category_pass_rate.png
cold_vs_warm_latency.png
injection_evaluation.png
latency_metrics.png
monthly_cost_projection.png
retrieval_quality.png
```

These artifacts provide evidence for:

* quality
* retrieval
* latency
* cost
* injection resistance
* routing
* category-level performance

---

# 32. Production Limitations

The current system has several limitations that should be acknowledged.

### Small evaluation set

The functional evaluation currently contains only 5 cases.

Therefore, 100% pass rate should not be interpreted as statistical proof of perfect production quality.

### Keyword-based evaluation

Some answer evaluation uses expected keywords.

This can produce false negatives when a semantically correct answer uses different terminology.

It can also produce false positives if expected words appear without sufficient context.

### Small injection set

The injection evaluation currently contains 5 adversarial examples.

A larger and continuously growing adversarial dataset is required for stronger security evidence.

### Cold-start latency

Local embedding initialization can produce substantially higher cold-start latency than warm requests.

Warm P95 is therefore used for the production latency gate while cold-start behavior remains separately reported.

### External model latency

LLM latency depends on provider response time, network conditions, traffic, rate limits, and model availability.

### Cost projections

Projected monthly costs are estimates based on measured or modeled assumptions.

Actual billing can differ.

### Retrieval dependency

Retrieval quality depends on:

* corpus quality
* chunk size
* chunk overlap
* embedding model
* retrieval threshold
* query formulation

Changes to the document corpus should trigger retrieval and evaluation checks.

---

# 33. Production Hardening Status

The project has completed the major production-hardening areas:

* [x] RAG ingestion
* [x] Retrieval quality investigation
* [x] Agent routing
* [x] Async tool execution
* [x] LangGraph orchestration
* [x] Durable checkpointing
* [x] Safety guardrails
* [x] Prompt-injection evaluation
* [x] Human approval workflow
* [x] Audit logging
* [x] FastAPI deployment
* [x] Docker deployment
* [x] Health checks
* [x] Readiness checks
* [x] Runtime metrics
* [x] Cost measurement
* [x] Cost projection
* [x] Latency measurement
* [x] Evaluation dataset
* [x] Evaluation gate
* [x] Category-level evaluation gates
* [x] CI lint gate
* [x] CI test gate
* [x] Injection-resistance gate
* [x] Dependency security review
* [x] Production documentation

---

# 34. Final Verification

Latest local verification:

```text
Ruff
------------------------------
All checks passed!


Pytest
------------------------------
40 passed, 1 warning


pip check
------------------------------
No broken requirements found.


Evaluation
------------------------------
5/5 passed
100% completion
100% pass rate


Injection evaluation
------------------------------
5/5 passed
100% resistance


Evaluation gate
------------------------------
PASS: All evaluation gates satisfied.
```

The project currently has automated evidence for application correctness, retrieval behavior, safety, approval controls, observability, dependency consistency, latency, cost, and deployment readiness.

---

# 35. Next Improvements

The next production iteration should focus on increasing the quality and reliability of the evidence rather than simply increasing the number of application features.

Recommended improvements include:

1. Expand the golden evaluation set.
2. Grow the set from production traces.
3. Stratify evaluations by query type.
4. Add more adversarial injection cases.
5. Add human/inter-rater evaluation for answer quality.
6. Monitor retrieval quality over time.
7. Track latency and cost distributions in production.
8. Add regression checks for retrieval changes.
9. Continue monitoring dependency security advisories.
10. Add canary/shadow evaluation before major model or prompt changes.

---

# 36. Summary

The Company Policy Agent is a production-oriented RAG/agent system with:

* local vector retrieval
* Groq-hosted LLM inference
* LangGraph orchestration
* durable state
* safety controls
* human approval
* audit trails
* runtime monitoring
* Docker deployment
* automated evaluation
* CI quality gates

Latest measured quality:

```text
Functional evaluation:     5/5
Overall pass rate:         100%
Category pass rate:        100%
Retrieval source hit rate: 100%
Injection resistance:      100%
Warm P95 latency:          1.08 seconds
Average measured cost:     $0.00013641/query
Tests:                     40 passed
Ruff:                      Passed
pip check:                 Passed
Evaluation gate:           Passed
```

The system is production-hardened for the current project scope, while the documented limitations make clear where additional evaluation and operational evidence are required before treating the system as a large-scale production service.
