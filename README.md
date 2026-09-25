# Company Policy Agent

Production-oriented RAG agent for answering company-policy questions using local document retrieval, Groq-hosted LLMs, LangGraph orchestration, durable checkpointing, safety guardrails, human approval workflows, audit logging, monitoring, automated evaluation, CI quality gates, and Docker deployment.

---

## 1. Project Overview

The Company Policy Agent is a production-oriented AI system designed to answer questions from internal company-policy documents while maintaining clear safety, approval, audit, evaluation, and operational boundaries.

The system combines:

* Local document retrieval with Chroma
* Hugging Face sentence-transformer embeddings
* Groq-hosted OpenAI-compatible LLMs
* LangGraph agent orchestration
* Durable conversation checkpointing
* Tool routing
* Prompt-injection guardrails
* Input and output validation
* Human approval for risky actions
* Audit logging
* FastAPI production endpoints
* Streamlit user interface
* Latency and cost instrumentation
* Automated evaluation
* Retrieval evaluation
* Prompt-injection evaluation
* CI quality gates
* Docker deployment
* LangSmith tracing support

The goal is not simply to demonstrate an LLM application, but to demonstrate how an AI agent can be engineered with production-oriented controls and measurable evaluation evidence.

---

## 2. Architecture

```text
                         ┌──────────────────────┐
                         │      Client/UI       │
                         │   Streamlit / API    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     FastAPI API      │
                         │ /health /ready       │
                         │ /metrics /chat       │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      LangGraph       │
                         │    Agent Workflow    │
                         └──────────┬───────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
             ┌────────────┐  ┌────────────┐  ┌─────────────┐
             │   Router   │  │   Safety   │  │ Checkpoint  │
             │            │  │ Guardrails │  │   Storage   │
             └─────┬──────┘  └────────────┘  └─────────────┘
                   │
          ┌────────┴─────────┐
          │                  │
          ▼                  ▼
 ┌────────────────┐  ┌──────────────────┐
 │ search_documents│  │ Risky operations │
 │      Tool       │  │  Approval Gate   │
 └───────┬─────────┘  └────────┬─────────┘
         │                     │
         ▼                     ▼
 ┌────────────────┐     ┌───────────────┐
 │     Chroma     │     │ Human Approval│
 │  Vector Store  │     │     Queue     │
 └───────┬────────┘     └───────────────┘
         │
         ▼
 ┌────────────────────────────┐
 │ Hugging Face Embeddings    │
 │ all-MiniLM-L6-v2           │
 └────────────────────────────┘

                 ┌──────────────────────┐
                 │       Groq LLM       │
                 │ OpenAI-compatible API│
                 └──────────────────────┘

                 ┌──────────────────────┐
                 │ Audit + Metrics      │
                 │ Evaluation + Tracing │
                 └──────────────────────┘
```

---

## 3. Core Components

### LangGraph

LangGraph manages the agent workflow and durable state.

The state includes information such as:

* session/thread information
* question
* conversation history
* selected tool
* answer
* sources
* tools used
* trace information

### Router

The router determines whether a request should:

* search company documents
* perform a risky employee operation
* return without using a tool
* invoke a safety or guardrail path

The `search_documents` tool does not require approval.

Risky operations are routed through the approval workflow.

---

## 4. Document Corpus

The current policy corpus contains:

```text
data/
├── hr_policy.pdf
├── company_policy.pdf
└── it_policy.pdf
```

The documents provide the source material used by the RAG system.

---

## 5. Retrieval Configuration

The application uses local embeddings rather than a hosted embedding API.

### Embedding model

```text
sentence-transformers/all-MiniLM-L6-v2
```

### Current production retrieval configuration

```text
Embedding:
sentence-transformers/all-MiniLM-L6-v2

Chunk size:
800

Chunk overlap:
150

Top-K:
2

Maximum retrieval distance:
1.10

Chroma collection:
capstone_documents
```

The retrieval layer uses Chroma similarity search with local Hugging Face embeddings.

The retrieval implementation also supports query expansion for policy-related terminology.

The retrieval threshold is intentionally maintained as part of the production configuration rather than being changed solely to optimize a small benchmark.

---

## 6. LLM Configuration

The application uses the Groq OpenAI-compatible endpoint:

```text
https://api.groq.com/openai/v1
```

Primary model configuration:

```text
GROQ_MODEL=openai/gpt-oss-20b
GROQ_LARGE_MODEL=openai/gpt-oss-120b
GROQ_SAFETY_MODEL=openai/gpt-oss-safeguard-20b
```

The application does not require a direct OpenAI API connection for LLM inference.

---

## 7. Model Routing

The production design supports a small-model-first strategy.

```text
User request
     │
     ▼
Small model
     │
     ├── Success ──► Return result
     │
     └── Failure / escalation
                 │
                 ▼
           Large model
```

The objective is to avoid sending every request to the larger model.

A separate cost model estimates the effect of this routing strategy.

Under the documented assumptions:

```text
Base monthly volume:
10,000 queries

Projected volume:
100,000 queries

Prompt tokens/query:
1,000

Completion tokens/query:
300

Large-model fraction:
10%
```

The modeled routed cost is approximately:

```text
10,000 queries/month:
$1.815

100,000 queries/month:
$18.15
```

The model estimates approximately 45% lower cost than routing every request to the larger model under those assumptions.

These figures are projections rather than guaranteed production billing.

---

## 8. Safety and Human Approval

The application includes multiple safety layers.

### Input Validation

Inputs are checked before agent execution.

### Prompt-Injection Detection

The application detects common attempts to override system instructions or bypass policy controls.

The injection evaluation covers cases such as:

* direct instruction override
* role override
* instruction override
* system prompt extraction

### Output Validation

Generated output is checked before being returned to the client.

### Risky Tool Protection

Risky operations include:

* updating employee records
* deleting employee information
* sending sensitive emails or communications
* other defined destructive operations

These operations require explicit human approval.

The approval lifecycle is:

```text
PENDING
   │
   ├── REJECTED
   │
   └── APPROVED
          │
          ▼
       EXECUTED
```

The AI system can prepare or request an action, but defined high-risk actions remain subject to human authorization.

---

## 9. Audit Logging

The application records audit information for important tool and approval operations.

Audit records can include:

* request ID
* tool name
* arguments
* status
* outcome
* errors
* execution status
* relevant metadata

Runtime audit artifacts are excluded from source control where appropriate.

The project uses `audit.json` for runtime audit information and excludes it through `.gitignore`.

---

## 10. Durable Checkpointing

LangGraph durable checkpointing is implemented for conversation state.

Each conversation uses a thread ID.

Checkpoint storage is persisted separately from the application container.

This allows the application to restart without losing durable conversation state.

---

## 11. Observability and Metrics

The application records operational metrics including:

* request count
* error count
* latency
* token usage
* estimated LLM cost
* tool usage
* request traces

The application also records detailed timing information for retrieval and LLM calls.

Example instrumentation:

```text
[RETRIEVAL TIMING]
db
search
filter
total

[LLM TIMING]
model
total
prompt tokens
completion tokens
reasoning tokens
total tokens
cost
```

LangSmith tracing is supported through environment variables.

Example:

```text
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=week2day5proj1
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

---

## 12. API and Health Checks

The production FastAPI service exposes endpoints including:

```text
GET /health
GET /ready
GET /metrics
POST /chat
GET /checkpoint/{thread_id}
```

The health endpoint verifies application availability.

The readiness endpoint verifies important production dependencies such as:

* Groq configuration
* configured model
* Chroma storage
* checkpoint storage

---

## 13. Docker Deployment

The application can be deployed using Docker Compose.

Build and start:

```powershell
docker compose up --build
```

The service is exposed on:

```text
http://localhost:8000
```

Persistent storage includes:

```text
storage/chroma
storage/checkpoints
```

The Docker service includes a health check against:

```text
/health
```

The production deployment has been verified with Docker health and readiness checks.

---

## 14. Evaluation Strategy

The project uses multiple evaluation layers rather than relying on a single benchmark.

The evaluation suite covers:

1. Routing behavior
2. Retrieval quality
3. Prompt-injection resistance
4. Latency
5. Cost modeling
6. Automated tests
7. Dependency checks

This separation makes it possible to distinguish application correctness from retrieval quality, security evidence, and operational performance.

---

## 15. Routing Evaluation

The routing evaluation contains 32 cases.

Categories:

```text
HR                 8
Company            6
IT                 6
Out-of-scope       5
Prompt-injection   5
Approval           2
```

Latest completed routing evaluation:

```text
Total cases:       32
Passed:            32
Failed:             0
Errors:             0
Completion:       100%
Pass rate:        100%
```

Category results:

```text
Approval:          2/2   100%
Company:           6/6   100%
HR:                8/8   100%
IT:                6/6   100%
Out-of-scope:      5/5   100%
Prompt-injection:  5/5   100%
```

The routing evaluation completed without provider infrastructure errors.

This distinction matters because an incomplete evaluation caused by provider rate limits should not be treated as successful evaluation evidence.

---

## 16. Retrieval Evaluation

The dedicated retrieval benchmark contains five cases.

Latest Top-2 results:

```text
In-scope retrieval:
4/4 = 100%

Out-of-scope clean:
1/1 = 100%
```

Additional retrieval-depth results:

```text
Top-1 in-scope:
3/4 = 75%

Top-2 in-scope:
4/4 = 100%

Top-3 in-scope:
4/4 = 100%
```

One IT benchmark query retrieved `company_policy.pdf` at rank 1 and `it_policy.pdf` at rank 2.

The production retrieval configuration therefore uses Top-2 rather than relying only on Top-1 retrieval.

The retrieval benchmark remains small and should be expanded with additional golden cases.

---

## 17. Latency Evaluation

Latency is measured separately for cold-start and warm requests.

The latest routing evaluation should be treated as the current reference run.

```text
Average latency:
1,599.54 ms

P50:
662.41 ms

P95:
1,295.26 ms
```

Cold-start behavior:

```text
Cold-start latency:
35,348.30 ms

Embedding initialization:
32,022.36 ms

Chroma initialization:
32,407.47 ms

Retrieval total:
33,083.58 ms

LLM latency:
2,183.32 ms
```

Warm-request behavior:

```text
Warm average:
510.87 ms

Warm P50:
636.80 ms

Warm maximum:
1,473.21 ms
```

The cold-start event is primarily associated with local embedding-model and Chroma initialization.

The API therefore performs retrieval warm-up during application startup.

Cold-start behavior remains separately reported rather than being hidden from the evaluation.

---

## 18. Cost Evaluation

LLM instrumentation records:

* prompt tokens
* completion tokens
* reasoning tokens
* total tokens
* estimated cost per request

The project also maintains a separate cost projection for model routing.

Under the documented routing assumptions:

```text
10,000 queries/month:
approximately $1.815

100,000 queries/month:
approximately $18.15
```

These are modeled projections.

Actual production cost can change based on:

* token usage
* model selection
* routing behavior
* provider pricing
* request distribution
* retries
* traffic volume

Measured evaluation cost and modeled monthly cost should therefore be treated as separate metrics.

---

## 19. Prompt-Injection Evaluation

The dedicated injection evaluation contains five adversarial cases.

Latest result:

```text
Passed:
5/5

Failed:
0

Errors:
0

Completion rate:
100%

Resistance rate:
100%
```

The evaluation includes cases covering:

* direct instruction override
* role override
* prompt manipulation
* instruction override
* system prompt extraction

The current result provides evidence against the tested cases.

It does not demonstrate that every possible prompt-injection technique is blocked.

A larger continuously growing adversarial dataset is required for stronger security evidence.

---

## 20. Production Evaluation Gates

The project uses explicit evaluation thresholds.

The current operational routing gate includes:

```text
Minimum overall pass rate:
90%

Minimum completion rate:
95%

Minimum category pass rate:
80%

Maximum configured warm P95 latency:
20,000 ms
```

The dedicated injection evaluation uses:

```text
Minimum injection resistance:
90%
```

The latest routing evaluation produced:

```text
Overall pass rate:
100%

Completion rate:
100%

Category pass rates:
100%

Injection resistance:
100%
```

The latest evidence therefore satisfies the currently configured evaluation thresholds.

Evaluation completeness is treated separately from benchmark quality so that provider rate-limit or infrastructure errors cannot silently become evaluation failures or successful evidence.

---

## 21. Automated Tests and CI

The project uses automated checks for application correctness and code quality.

Latest local test run:

```text
41 passed
1 warning
```

The warning originates from a ChromaDB telemetry dependency using the deprecated:

```text
asyncio.iscoroutinefunction
```

The warning does not currently cause the test suite to fail.

Latest Ruff verification:

```text
All checks passed!
```

Recommended local checks:

```powershell
pytest -q
ruff check app tests evals *.py
python -m pip check
```

The project also includes GitHub Actions workflows for automated CI and evaluation checks.

---

## 22. Dependency Security

Dependency auditing is performed with:

```text
pip-audit
```

The current ChromaDB dependency has documented security advisories.

The project does not expose ChromaDB as a standalone network service. ChromaDB is used as local persistent storage within the application architecture.

The findings and architectural mitigation are documented separately in:

```text
SECURITY.md
```

The project does not claim that the dependency has no known vulnerabilities.

The dependency should be re-evaluated when an appropriate patched release becomes available.

---

## 23. Project Structure

```text
week2day5proj1/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── evaluation.yml
│
├── app/
│   ├── agent.py
│   ├── api.py
│   ├── approval.py
│   ├── audit.py
│   ├── async_agent.py
│   ├── async_tools.py
│   ├── checkpoint.py
│   ├── config.py
│   ├── ingest.py
│   ├── llm.py
│   ├── metrics.py
│   ├── router.py
│   ├── risky_tools.py
│   ├── safety.py
│   ├── state.py
│   └── tools.py
│
├── data/
│   ├── hr_policy.pdf
│   ├── company_policy.pdf
│   └── it_policy.pdf
│
├── docs/
│
├── evals/
│   ├── charts/
│   ├── evaluation_dataset.json
│   ├── evaluation_results.json
│   ├── injection_results.json
│   ├── routing_evaluation_results.json
│   ├── retrieval_evaluation_results.json
│   ├── cost_projection.json
│   ├── evaluation_report.json
│   ├── evaluate.py
│   ├── evaluate_injection.py
│   ├── evaluate_routing.py
│   ├── check_evaluation_gate.py
│   └── run_all.py
│
├── storage/
│   ├── chroma/
│   └── checkpoints/
│
├── tests/
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-lock.txt
├── pytest.ini
├── SECURITY.md
├── PRODUCTION_EVIDENCE.md
├── README.md
└── .gitignore
```

---

## 24. Running Locally

Create and activate the virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create the local environment file from `.env.example` and configure the required Groq and application settings.

Build the document index:

```powershell
python -m app.ingest
```

Run the API:

```powershell
uvicorn app.api:app --reload
```

The API is available at:

```text
http://localhost:8000
```

---

## 25. Running with Docker

Build and start the production service:

```powershell
docker compose up --build
```

Check health:

```text
http://localhost:8000/health
```

Check readiness:

```text
http://localhost:8000/ready
```

View metrics:

```text
http://localhost:8000/metrics
```

Stop the service:

```powershell
docker compose down
```

---

## 26. Running Evaluations

Run the routing evaluation:

```powershell
python -m evals.evaluate_routing
```

Run the full evaluation orchestration:

```powershell
python -m evals.run_all
```

Run the dedicated injection evaluation:

```powershell
python -m evals.evaluate_injection
```

Run the production evaluation gate:

```powershell
python -m evals.check_evaluation_gate
```

Run tests:

```powershell
pytest -q
```

Run Ruff:

```powershell
ruff check app tests evals *.py
```

Check dependency consistency:

```powershell
python -m pip check
```

Run dependency auditing:

```powershell
python -m pip_audit
```

---

## 27. Evaluation Artifacts

The project generates evaluation artifacts including:

```text
evals/evaluation_results.json
evals/injection_results.json
evals/routing_evaluation_results.json
evals/retrieval_evaluation_results.json
evals/cost_projection.json
evals/evaluation_report.json
```

Evaluation charts include:

```text
evals/charts/category_pass_rate.png
evals/charts/cold_vs_warm_latency.png
evals/charts/injection_evaluation.png
evals/charts/latency_metrics.png
evals/charts/monthly_cost_projection.png
evals/charts/retrieval_quality.png
```

These artifacts provide evidence for:

* quality
* routing
* retrieval
* latency
* cost
* prompt-injection resistance
* category-level performance

---

## 28. Production Limitations

The current system has several known limitations.

### Evaluation Size

The routing evaluation contains 32 cases, while the retrieval and injection benchmarks remain relatively small.

A 100% benchmark result should not be interpreted as proof of perfect production quality.

### Prompt-Injection Coverage

The current injection benchmark contains five adversarial examples.

A larger continuously growing adversarial dataset is required for stronger security evidence.

### Cold-Start Latency

Local embedding initialization can produce substantially higher cold-start latency than warm requests.

Cold-start behavior is therefore reported separately.

### External Model Latency

LLM latency depends on provider response time, network conditions, traffic, and rate limits.

### Approval State

The current approval queue is process-local and stored in memory.

This means pending approvals are not durable across application restarts and are not automatically shared between multiple application processes or replicas.

A production-scale deployment would require persistent approval storage and an API-level approval workflow.

### Cost Projections

Cost projections are estimates based on documented token usage, routing assumptions, and provider pricing. Actual costs can vary with traffic, model selection, token usage, retries, and provider pricing.

### Dependency Security

`pip-audit` currently reports security advisories for the installed ChromaDB dependency.

The application uses ChromaDB as local persistent storage rather than exposing ChromaDB as a standalone network service. The dependency finding is documented separately in `SECURITY.md` and should be re-evaluated when an appropriate patched release becomes available.

---


## 29. Production Hardening Status

The project has completed the major production-hardening areas:

* [x] RAG document ingestion
* [x] Local embeddings
* [x] Chroma persistence
* [x] LangGraph orchestration
* [x] Durable checkpointing
* [x] Tool routing
* [x] Input validation
* [x] Prompt-injection protection
* [x] Output validation
* [x] Human approval workflow
* [x] Audit logging
* [x] FastAPI API
* [x] Docker deployment
* [x] Health/readiness checks
* [x] Runtime metrics
* [x] Token and cost instrumentation
* [x] Latency measurement
* [x] Routing evaluation
* [x] Retrieval evaluation
* [x] Injection-resistance evaluation
* [x] Evaluation gate
* [x] CI lint gate
* [x] CI test gate
* [x] Dependency audit
* [x] Production documentation

---

## 30. Final Verification

Latest verified local evidence:

```text
Routing evaluation:
32/32 passed
100% completion
100% pass rate

Retrieval Top-2:
4/4 passed

Prompt-injection evaluation:
5/5 passed

Automated tests:
41 passed
1 warning

Ruff:
All checks passed
```

Latest routing latency evidence:

```text
Average:
1,599.54 ms

P50:
662.41 ms

P95:
1,295.26 ms

Warm average:
510.87 ms

Warm P50:
636.80 ms

Warm maximum:
1,473.21 ms

Cold start:
35,348.30 ms
```

The project therefore has automated evidence for application correctness, routing behavior, retrieval behavior, safety controls, approval workflows, observability, latency, cost modeling, dependency review, and deployment readiness.

The evaluation evidence should be interpreted within the documented limitations and benchmark sizes.

---

## 31. Next Improvements

The next production iteration should focus on increasing the quality and reliability of the evidence rather than simply increasing the number of application features.

Recommended improvements include:

1. Expand the golden evaluation set.
2. Grow the dataset from production traces.
3. Stratify evaluations by query type.
4. Add more adversarial injection cases.
5. Add human/inter-rater evaluation for answer quality.
6. Track retrieval precision and recall over a larger benchmark.
7. Track latency and cost distributions in production.
8. Add regression checks for retrieval changes.
9. Continue monitoring dependency security advisories.
10. Add canary or shadow evaluation before major model or prompt changes.

---

## 32. Summary

The Company Policy Agent is a production-oriented RAG/agent system combining:

* Local document retrieval
* Chroma vector storage
* Hugging Face embeddings
* Groq-hosted LLMs
* LangGraph orchestration
* Model routing
* Safety guardrails
* Human approval workflows
* Audit logging
* Durable checkpointing
* FastAPI
* Streamlit
* Docker deployment
* Runtime observability
* Automated evaluation
* CI quality gates

Latest evaluation evidence:

```text
Routing evaluation:        32/32 = 100%
Routing completion:        100%
Retrieval Top-2:            4/4 = 100%
Out-of-scope retrieval:     1/1 = 100%
Injection evaluation:       5/5 = 100%

Tests:                     41 passed
Ruff:                      Passed
```

The system has completed the major production-hardening work for the current project scope. The documented limitations identify the remaining areas requiring additional evaluation, persistent approval infrastructure, security testing, and operational evidence before large-scale production deployment.

