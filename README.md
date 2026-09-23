# Company Policy Agent

A production-oriented AI agent for answering company-policy questions using Retrieval-Augmented Generation (RAG), query routing, relevance filtering, asynchronous tool execution, durable checkpointing, human-in-the-loop approval, audit logging, safety guardrails, monitoring, automated evaluation, CI quality gates, and Docker deployment.

The system uses **Groq** as the LLM provider through its OpenAI-compatible API, with local Hugging Face embeddings and ChromaDB for document retrieval.

---

## 1. Overview

The Company Policy Agent answers questions using a controlled collection of company policy documents.

The system is designed to:

* Route questions to the appropriate execution path
* Retrieve relevant policy documents
* Apply retrieval relevance filtering
* Generate answers grounded in retrieved documents
* Return source documents with answers
* Avoid fabricating answers when evidence is unavailable
* Execute independent tools asynchronously
* Persist agent state using durable checkpoints
* Require human approval for risky operations
* Maintain an audit trail
* Detect prompt-injection attempts
* Expose runtime metrics
* Track LLM token usage and estimated cost
* Run automated evaluation suites
* Enforce quality gates in CI
* Run as a Dockerized FastAPI service
* Provide health and readiness checks

The project demonstrates production-style AI-agent engineering rather than only a basic RAG chatbot.

---

# 2. Architecture

```text
                         User
                           |
                           v
                  +----------------+
                  |  Streamlit UI  |
                  +--------+-------+
                           |
                           v
                  +----------------+
                  |    FastAPI     |
                  |     /chat      |
                  +--------+-------+
                           |
                           v
                  +----------------+
                  |    LangGraph   |
                  |      Agent     |
                  +--------+-------+
                           |
              +------------+------------+
              |                         |
              v                         v
      +---------------+         +---------------+
      |    Safety     |         | Query Router  |
      |  Guardrails   |         +-------+-------+
      +---------------+                 |
                                        |
                           +------------+------------+
                           |                         |
                           v                         v
                  +----------------+          +-------------+
                  | search_documents|         |   no_tool   |
                  +--------+-------+          +-------------+
                           |
                           v
                  +----------------+
                  |    ChromaDB    |
                  | Vector Storage  |
                  +--------+-------+
                           |
                           v
                  +----------------+
                  |   Relevance    |
                  |    Filter      |
                  +--------+-------+
                           |
                           v
                  +----------------+
                  |     RAG        |
                  | Context Build  |
                  +--------+-------+
                           |
                           v
                  +----------------+
                  |    Groq LLM    |
                  +--------+-------+
                           |
                           v
                  +----------------+
                  | Answer +       |
                  | Sources + Trace|
                  +--------+-------+
                           |
              +------------+------------+
              |            |             |
              v            v             v
        Checkpoint      Audit       Runtime Metrics
              |            |             |
              +------------+-------------+
                           |
                           v
                    Observability
```

The production service runs inside Docker.

Persistent application state includes:

```text
Host storage
    |
    +--> ./storage/chroma
    |        |
    |        +--> Chroma vector database
    |
    +--> checkpoint_data
             |
             +--> LangGraph checkpoint state
```

---

# 3. Key Features

## AI and RAG

* ChromaDB vector retrieval
* Local Hugging Face embeddings
* Recursive document chunking
* Retrieval relevance threshold
* Grounded answer generation
* Source citation
* Honest insufficient-information responses

## Query Routing

The router determines whether a question should:

* Use `search_documents`
* Use another available tool
* Require no tool

Example:

```text
"What is the company leave policy?"
                |
                v
        search_documents
                |
                v
            ChromaDB
                |
                v
       Relevant documents
                |
                v
             Groq LLM
                |
                v
         Answer + sources
```

Out-of-scope questions such as:

```text
"What is Python?"
"What is the weather today?"
```

can be routed to `no_tool`.

## Async Execution

Independent tools can be executed in parallel.

Implementation:

```text
app/async_agent.py
app/async_tools.py
```

Benchmark:

```text
benchmark_async.py
```

Parallel execution is useful when independent tools can safely execute concurrently.

## Durable Checkpointing

The agent maintains durable state using LangGraph checkpointing.

Checkpointed state can include:

* Request ID
* Session ID
* Question
* Conversation history
* Selected tool
* Answer
* Sources
* Tools used
* Approval information
* Execution trace

Checkpoint storage is persisted through Docker storage.

## Human-in-the-Loop Approval

Potentially risky operations require explicit approval before execution.

Examples include:

```text
update_employee_record
delete_employee_record
send_email
```

Approval lifecycle:

```text
PENDING
   |
   +---- REJECTED ----> BLOCKED
   |
   +---- APPROVED ----> EXECUTED
                           |
                           v
                      AUDIT TRAIL
```

Search and retrieval operations do not require approval.

## Audit Trail

Tool calls and important actions are recorded with request identifiers.

The audit system provides traceability for:

* Tool calls
* Success/failure
* Request IDs
* Approval status
* Execution events

Relevant modules:

```text
app/audit.py
app/approval.py
```

## Safety and Prompt Injection Protection

Implemented controls include:

* Input validation
* Prompt-injection detection
* Output validation
* Risky-tool restrictions
* Human approval
* Safety regression tests
* Prompt-injection evaluation

Relevant modules:

```text
app/safety.py
app/guardrails.py
app/risky_tools.py
```

These controls reduce risk but should not be considered universal protection against every possible attack.

---

# 4. Technology Stack

| Component           | Technology                               |
| ------------------- | ---------------------------------------- |
| Language            | Python 3.12                              |
| LLM Provider        | Groq                                     |
| LLM Interface       | OpenAI-compatible Groq endpoint          |
| Primary Model       | `openai/gpt-oss-20b`                     |
| Large Model         | `openai/gpt-oss-120b`                    |
| Safety Model        | `openai/gpt-oss-safeguard-20b`           |
| Agent Orchestration | LangGraph                                |
| Embeddings          | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector Database     | ChromaDB                                 |
| API                 | FastAPI                                  |
| UI                  | Streamlit                                |
| Server              | Uvicorn                                  |
| Testing             | Pytest                                   |
| Linting             | Ruff                                     |
| Security Audit      | pip-audit                                |
| Containerization    | Docker                                   |
| CI                  | GitHub Actions                           |

---

# 5. Request Flow

A normal policy request follows:

```text
User question
     |
     v
Safety validation
     |
     v
Query router
     |
     v
Tool selection
     |
     v
Document retrieval
     |
     v
Similarity/relevance filtering
     |
     v
Context construction
     |
     v
Groq LLM
     |
     v
Answer validation
     |
     v
Answer + Sources
     |
     +--------> Runtime Metrics
     |
     +--------> Audit Logging
     |
     +--------> Checkpoint
```

For risky operations:

```text
User request
     |
     v
Safety validation
     |
     v
Risky tool detected
     |
     v
Approval request
     |
     v
Human decision
     |
     +---- REJECTED ----> Block
     |
     +---- APPROVED ----> Execute
                              |
                              v
                         Audit trail
```

---

# 6. Project Structure

```text
week2day5proj1/
|
+-- app/
|   +-- __init__.py
|   +-- agent.py
|   +-- api.py
|   +-- approval.py
|   +-- async_agent.py
|   +-- async_tools.py
|   +-- audit.py
|   +-- checkpoint.py
|   +-- context.py
|   +-- evaluate.py
|   +-- graph.py
|   +-- guardrails.py
|   +-- ingest.py
|   +-- llm.py
|   +-- memory.py
|   +-- metrics.py
|   +-- rag.py
|   +-- retrieval.py
|   +-- risky_tools.py
|   +-- router.py
|   +-- safety.py
|   +-- state.py
|   +-- tools.py
|   +-- ui.py
|   +-- vectorstore.py
|
+-- tests/
|   +-- evaluation_cases.py
|   +-- test_agent.py
|   +-- test_approval_execution.py
|   +-- test_approval_safety.py
|   +-- test_checkpoint_resume.py
|   +-- test_query_routing_retrieval.py
|   +-- test_rag.py
|   +-- test_safety.py
|
+-- evals/
|   +-- check_evaluation_gate.py
|   +-- evaluate.py
|   +-- evaluate_injection.py
|   +-- evaluate_routing.py
|   +-- evaluation_dataset.json
|   +-- evaluation_results.json
|   +-- injection_dataset.json
|   +-- injection_results.json
|   +-- query_routing_dataset.json
|   +-- routing_evaluation_results.json
|
+-- .github/
|   +-- workflows/
|       +-- ci.yml
|       +-- evaluation.yml
|
+-- benchmark_async.py
+-- docker-compose.yml
+-- Dockerfile
+-- .env
+-- .env.example
+-- .gitignore
+-- pytest.ini
+-- README.md
+-- requirements.txt
+-- SECURITY.md
```

---

# 7. Environment Variables

Create a local `.env` file.

Example:

```text
GROQ_API_KEY=your_groq_api_key_here

GROQ_MODEL=openai/gpt-oss-20b
GROQ_LARGE_MODEL=openai/gpt-oss-120b
GROQ_SAFETY_MODEL=openai/gpt-oss-safeguard-20b
```

The project also uses configuration for:

```text
LANGCHAIN_TRACING_V2
LANGCHAIN_PROJECT
LANGCHAIN_ENDPOINT
EMBEDDING_MODEL
```

Never commit the real API key.

The repository contains:

```text
.env.example
```

for configuration reference.

**Do not use `OPENAI_API_KEY` for this project. Groq is the API provider.**

---

# 8. Clean Clone Setup

Clone the repository:

```powershell
git clone <repository-url>
cd week2day5proj1
```

Create a virtual environment:

```powershell
python -m venv venv
```

Activate it in Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create `.env` from `.env.example` and configure the Groq API key.

---

# 9. Build the Retrieval Index

Policy documents are stored in the project's `data` directory.

The ingestion script is:

```text
app/ingest.py
```

Build the Chroma retrieval index:

```powershell
python -m app.ingest
```

Current policy documents:

```text
company_policy.pdf
hr_policy.pdf
it_policy.pdf
```

Verified ingestion result:

```text
PDF pages loaded : 21
Chunks created   : 39
```

The production Chroma storage location is:

```text
storage/chroma
```

---

# 10. Run Tests

Run the complete test suite:

```powershell
python -m pytest -q
```

Latest verified result:

```text
40 passed
```

There is currently one Chroma/OpenTelemetry deprecation warning. It does not cause the test suite to fail.

---

# 11. Code Quality Checks

Run Ruff:

```powershell
python -m ruff check .
```

Latest verification:

```text
All checks passed!
```

Run the Git whitespace check:

```powershell
git diff --check
```

---

# 12. Local API Development

The API is implemented in:

```text
app/api.py
```

Run the API locally:

```powershell
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

API:

```text
http://localhost:8000
```

---

# 13. API Endpoints

## Health

```text
GET /health
```

Test:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

Verified response:

```text
status   service                version
------   -------                -------
healthy  company-policy-agent   1.1.0
```

## Readiness

```text
GET /ready
```

Test:

```powershell
Invoke-RestMethod http://localhost:8000/ready
```

The readiness check verifies:

* Groq API key
* Groq model
* Chroma storage
* Checkpoint storage

Verified state:

```text
groq_api_key=True
groq_model=True
chroma_storage=True
checkpoint_storage=True
```

## Chat

```text
POST /chat
```

The endpoint executes the production agent flow and returns:

* Request ID
* Thread ID
* Answer
* Sources
* Tools used
* Trace

## Metrics

```text
GET /metrics
```

The metrics endpoint exposes:

* Request counts
* Successful requests
* Errors
* Latency
* Error rate
* LLM requests
* Token usage
* Estimated cost
* Retrieval counters
* Tool counters

## Checkpoint

```text
GET /checkpoint/{thread_id}
```

Returns persisted agent state for a LangGraph thread.

---

# 14. Query Routing

The router determines which execution path a question should take.

Examples:

| Query                                                 | Expected route     |
| ----------------------------------------------------- | ------------------ |
| What is the company leave policy?                     | `search_documents` |
| What does the company say about professional conduct? | `search_documents` |
| What are the company's confidentiality requirements?  | `search_documents` |
| What is the company's IT security policy?             | `search_documents` |
| What is Python?                                       | `no_tool`          |
| What is the weather today?                            | `no_tool`          |

The routing evaluation is a separate evaluation suite from the main RAG quality evaluation.

Latest routing evaluation:

```text
Total queries: 7
Passed: 7
Failed: 0
Overall pass rate: 100%
```

Breakdown:

```text
HR:           2/2
Company:      1/1
IT:           1/1
Out-of-scope: 3/3
```

Because this is a small targeted evaluation set, these results should not be interpreted as universal routing accuracy.

---

# 15. Retrieval and RAG

Retrieval implementation:

```text
app/retrieval.py
app/rag.py
```

Embedding model:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Retrieval flow:

```text
Question
   |
   v
Embedding
   |
   v
Chroma similarity search
   |
   v
Distance threshold
   |
   v
Relevant documents
   |
   v
LLM context
   |
   v
Answer
```

Current empirically calibrated maximum retrieval distance:

```text
1.10
```

For the professional-conduct query, observed distances were approximately:

```text
1.04 - 1.08
```

An unrelated query previously produced distances approximately around:

```text
1.29 - 1.34
```

The threshold is calibrated for the current dataset and should be recalibrated if the documents, embedding model, chunking strategy, or retrieval system changes significantly.

---

# 16. Retrieval Quality Investigation

Retrieval quality was investigated using a dedicated benchmark.

The investigation considered:

* Relevant document retrieval
* Top-1 retrieval
* Top-2 retrieval
* Top-3 retrieval
* Query expansion
* Chunk size
* Chunk overlap
* Section-aware chunking
* Document metadata
* Embedding behavior

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

Section-aware chunking was tested but was not adopted because it did not improve the benchmark's top-1 result.

---

# 17. Honest Retrieval Behavior

If no retrieved document passes the relevance threshold, the system does not fabricate an answer.

It returns an honest limitation such as:

```text
I don't have enough information in the provided documents to answer that question.
```

This behavior is important because a RAG system should distinguish between:

```text
Relevant evidence found
```

and:

```text
No sufficient evidence found
```

rather than treating every question as answerable.

---

# 18. Async Parallel Tool Execution

Async execution is implemented in:

```text
app/async_agent.py
app/async_tools.py
```

Independent tools can run concurrently.

Benchmark:

```text
benchmark_async.py
```

Conceptually:

```text
Sequential:

Tool A -> Tool B -> Tool C
                   |
                   v
              Total latency
```

versus:

```text
Parallel:

Tool A ----+
Tool B ----+----> Combined result
Tool C ----+
```

Parallel execution can reduce latency when tools are independent and safe to execute concurrently.

---

# 19. Durable Checkpointing

Checkpoint implementation:

```text
app/checkpoint.py
app/memory.py
app/state.py
```

Persisted state can include:

* Request ID
* Session ID
* Question
* Conversation history
* Selected tool
* Answer
* Sources
* Tools used
* Approval status
* Execution trace

Docker checkpoint storage:

```text
/app/storage/checkpoints
```

Persistent volume:

```text
checkpoint_data
```

---

# 20. Human-in-the-Loop Approval

Approval implementation:

```text
app/approval.py
app/risky_tools.py
```

Risky operations include:

```text
update_employee_record
delete_employee_record
send_email
```

Approval lifecycle:

```text
PENDING
   |
   +---- REJECTED ----> BLOCKED
   |
   +---- APPROVED ----> EXECUTED
                           |
                           v
                       AUDIT TRAIL
```

Search operations do not require approval.

Tests cover pending, rejected, and approved execution paths.

---

# 21. Audit Trail

Audit implementation:

```text
app/audit.py
```

The system records information such as:

* Request IDs
* Tool calls
* Tool success/failure
* Approval status
* Execution events

Request IDs allow important actions to be correlated across the application.

---

# 22. Safety and Prompt Injection

Safety modules:

```text
app/safety.py
app/guardrails.py
app/risky_tools.py
```

Safety controls include:

* Input validation
* Prompt-injection detection
* Output validation
* Risky-tool restrictions
* Human approval
* Safety regression tests
* Prompt-injection evaluation

Run safety tests:

```powershell
python -m pytest -q tests/test_safety.py tests/test_approval_safety.py
```

Run the prompt-injection evaluation:

```powershell
python -m evals.evaluate_injection
```

Latest injection evaluation:

```text
5 cases
5 passed
0 failed
100% resistance among completed cases
```

The injection suite is intentionally small and should not be interpreted as proof that the system is immune to all future attacks.

---

# 23. Monitoring

Monitoring implementation:

```text
app/metrics.py
```

Tracked metrics include:

* Total requests
* Successful requests
* Failed requests
* Error rate
* Chat latency
* Retrieval latency
* LLM latency
* LLM request count
* Prompt tokens
* Completion tokens
* Total tokens
* Estimated LLM cost
* Cost per request
* Retrieval success
* Tool usage

Metrics endpoint:

```text
GET /metrics
```

The current metrics implementation provides application-level runtime telemetry.

The metrics are currently stored in memory and therefore reset when the application restarts.

A larger deployment could export these metrics to an external monitoring system such as Prometheus/Grafana.

---

# 24. Cost Tracking

The LLM layer records:

* Prompt tokens
* Completion tokens
* Total tokens
* Estimated request cost
* Total estimated cost

Configured models include:

```text
openai/gpt-oss-20b
openai/gpt-oss-120b
openai/gpt-oss-safeguard-20b
```

Cost figures are estimates based on observed token usage and configured pricing assumptions.

---

# 25. Model Routing

The project supports a small-model-first routing strategy:

```text
openai/gpt-oss-20b
        |
        | escalation
        v
openai/gpt-oss-120b
```

The purpose is to use the smaller model for normal requests and escalate when required.

The cost analysis contains a modeled comparison between:

```text
Always use large model
```

and:

```text
Small model first + escalation
```

Under the documented assumptions, the modeled routed strategy showed approximately **45% lower cost** than the modeled always-large baseline.

This is a modeled estimate, not a guaranteed production savings figure.

---

# 26. Evaluation Suite

Evaluation implementation:

```text
evals/
```

Main evaluation scripts:

```text
evaluate.py
evaluate_routing.py
evaluate_injection.py
check_evaluation_gate.py
```

Datasets:

```text
evaluation_dataset.json
query_routing_dataset.json
injection_dataset.json
```

Results:

```text
evaluation_results.json
routing_evaluation_results.json
injection_results.json
```

The project uses separate evaluation suites because RAG quality, routing behavior, and prompt-injection resistance measure different properties.

---

# 27. Main RAG Evaluation Results

The main evaluation contains five representative cases.

Latest verified result:

```text
Completed cases: 5
Passed: 5
Failed: 0
Errors: 0
Completion rate: 100%
Pass rate among completed cases: 100%
Source hit rate: 100%
In-scope retrieval success: 100%
Out-of-scope no-evidence: 1/1
```

Additional measurements:

```text
Average documents retrieved: 3
Average prompt tokens: 470.8
Average completion tokens: 360.2
Average total tokens: 831
Average cost/query: $0.000143
```

The evaluation dataset is small and should not be interpreted as evidence of 100% real-world accuracy.

---

# 28. Latency Evaluation

The evaluation demonstrated a significant cold-start effect.

Measured cold-start latency:

```text
21.539 seconds
```

Warm-request measurements:

```text
Warm average: 801.66 ms
Warm p50:     838.48 ms
Warm p95:   1,410.55 ms
```

The API therefore warms up the retrieval model during startup.

This reduces the likelihood that the first user request pays the full embedding-model initialization cost.

Latency remains dependent on:

* Embedding initialization
* Retrieval
* Network conditions
* Groq API latency
* Model generation time
* Runtime environment

---

# 29. Evaluation Cost Projection

Measured average cost from the main evaluation:

```text
$0.000143/query
```

Projected costs from the documented evaluation assumptions:

|          Volume | Projected cost |
| --------------: | -------------: |
|   1,000 queries |         $0.143 |
|  10,000 queries |         $1.434 |
| 100,000 queries |        $14.338 |

These are modeled projections rather than guaranteed future bills.

---

# 30. AI Evaluation Quality Gate

The evaluation quality gate checks:

* Overall pass rate
* Query-category pass rates
* P95 latency

The latest verified gate passed.

The quality gate used:

```text
Minimum overall pass rate: 90%
Maximum allowed P95 latency: 20 seconds
```

The latest gate reported:

```text
Overall pass rate: 100%
P95 latency:       15.594 seconds
```

All configured AI quality gates passed.

The routing evaluation is a separate suite and should not be conflated with the main RAG quality gate.

---

# 31. CI/CD

The repository contains two GitHub Actions workflows:

```text
.github/workflows/ci.yml
.github/workflows/evaluation.yml
```

The CI workflow performs checks including:

* Dependency installation
* Retrieval index construction
* Ruff linting
* Pytest
* AI evaluation quality gate
* Dependency auditing
* Docker build

The retrieval index is built during CI so that evaluation and tests can reproduce the required vector-store state.

The evaluation workflow additionally checks prompt-injection resistance.

---

# 32. Dependency Security

The project uses:

```text
pip-audit
```

The current ChromaDB dependency is affected by four documented security advisories.

These findings are documented in:

```text
SECURITY.md
```

The current application architecture uses ChromaDB as local persistent storage and does not expose a standalone ChromaDB server to untrusted clients.

This reduces exposure to the documented server/API attack paths but does **not** remove the underlying dependency advisories.

The project therefore treats these findings as an explicit architecture-scoped security exception.

The dependency should be re-evaluated when an appropriate patched release becomes available.

The security status should therefore be understood as:

```text
Known ChromaDB advisories are documented
and architecture-scoped.
```

rather than:

```text
No known vulnerabilities exist.
```

---

# 33. Docker Deployment

Docker files:

```text
Dockerfile
docker-compose.yml
```

Base image:

```text
python:3.12-slim
```

Application command:

```text
uvicorn app.api:app --host 0.0.0.0 --port 8000
```

Build:

```powershell
docker compose build
```

Start:

```powershell
docker compose up -d
```

Check:

```powershell
docker compose ps
```

Expected status:

```text
healthy
```

---

# 34. Docker Storage

The production Docker Compose configuration persists application state using:

```text
./storage/chroma
      |
      v
/app/storage/chroma
```

for ChromaDB and:

```text
checkpoint_data
      |
      v
/app/storage/checkpoints
```

for LangGraph checkpoints.

The Chroma storage uses a host bind mount so the deployed application uses the current retrieval index.

Checkpoint state uses a persistent Docker volume.

These storage mechanisms allow state to survive normal container restarts.

---

# 35. Docker Healthcheck

The Docker healthcheck calls:

```text
/health
```

Configuration:

```text
Start period: 30 seconds
Interval:     30 seconds
Timeout:      10 seconds
Retries:      3
```

Verified production response:

```text
status   service                version
------   -------                -------
healthy  company-policy-agent   1.1.0
```

---

# 36. Readiness Check

The readiness endpoint:

```text
GET /ready
```

checks:

```text
Groq API key
Groq model
Chroma storage
Checkpoint storage
```

Verified readiness state:

```text
groq_api_key=True
groq_model=True
chroma_storage=True
checkpoint_storage=True
```

This separates basic process health from application dependency readiness.

---

# 37. Production Logging

The API uses request logging for operational visibility.

Logged information includes fields such as:

```text
timestamp
level
logger
message
request_id
endpoint
latency_ms
status
```

Request IDs allow application activity to be correlated with traces and audit events.

---

# 38. Live Production Verification

A real request was executed against the running Docker deployment:

```text
POST /chat
```

Question:

```text
What does the company say about professional conduct?
```

The deployed service successfully:

1. Accepted the request through FastAPI
2. Routed it to `search_documents`
3. Retrieved relevant policy documents
4. Generated a grounded answer through Groq
5. Returned `hr_policy.pdf`
6. Returned `company_policy.pdf`
7. Returned a request ID
8. Returned a thread ID
9. Returned execution trace information
10. Recorded runtime metrics

Live metrics from the request:

| Metric                   |    Result |
| ------------------------ | --------: |
| Successful chat requests |         1 |
| Retrieval successes      |         1 |
| LLM requests             |         1 |
| Error rate               |        0% |
| Chat latency             |  7,526 ms |
| Retrieval latency        |  4,357 ms |
| LLM latency              |  2,370 ms |
| Prompt tokens            |       433 |
| Completion tokens        |       395 |
| Total tokens             |       828 |
| Estimated request cost   | $0.000151 |

Final Docker verification:

```text
Container: healthy
/health:   healthy
/ready:    ready
```

Final Git verification:

```text
Branch: main
Remote: origin/main
Working tree: clean
```

This demonstrates that the deployed application was tested with a real end-to-end request rather than only through automated tests.

---

# 39. Useful Commands

Install dependencies:

```powershell
pip install -r requirements.txt
```

Build retrieval index:

```powershell
python -m app.ingest
```

Run tests:

```powershell
python -m pytest -q
```

Run routing evaluation:

```powershell
python -m evals.evaluate_routing
```

Run main evaluation:

```powershell
python -m evals.evaluate
```

Run evaluation quality gate:

```powershell
python -m evals.check_evaluation_gate
```

Run prompt-injection evaluation:

```powershell
python -m evals.evaluate_injection
```

Run Ruff:

```powershell
python -m ruff check .
```

Check whitespace:

```powershell
git diff --check
```

Build Docker image:

```powershell
docker compose build
```

Start Docker service:

```powershell
docker compose up -d
```

Stop Docker service:

```powershell
docker compose down
```

Check container:

```powershell
docker compose ps
```

View logs:

```powershell
docker compose logs --tail=100 company-policy-agent
```

Health:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

Readiness:

```powershell
Invoke-RestMethod http://localhost:8000/ready
```

Metrics:

```powershell
Invoke-RestMethod http://localhost:8000/metrics
```

---

# 40. Known Limitations

## Evaluation Coverage

The main RAG evaluation contains only five cases.

The routing evaluation contains seven cases.

The injection evaluation contains five cases.

These targeted datasets are useful regression tests but do not represent every possible production query or attack.

## Retrieval Threshold

The current relevance threshold was calibrated against the current policy dataset.

It should be re-evaluated when:

* Documents change significantly
* Embeddings change
* Chunking changes
* The retrieval model changes

## Cold-Start Latency

The first retrieval request can be significantly slower because the embedding model may need to initialize.

Startup warm-up reduces this impact for the deployed API.

## Runtime Metrics

The current metrics implementation stores measurements in memory.

Metrics reset when the application restarts.

A larger production deployment would normally export telemetry to an external monitoring system.

## Cost

Cost calculations are estimates based on observed token usage and documented pricing assumptions.

Actual provider billing can vary.

## Security

The application includes multiple safety controls, but no prompt-injection defense should be considered perfect.

The ChromaDB dependency also has documented security advisories that remain an explicit architecture-scoped exception.

## Evaluation Scoring

Some evaluation checks use targeted or keyword-based criteria.

Future improvements could include:

* Larger datasets
* Human-reviewed golden sets
* Semantic answer evaluation
* Retrieval precision/recall measurements
* Judge calibration
* Production trace sampling
* Regression testing from real user queries

---

# 41. Security Practices

Never commit:

```text
.env
API keys
Access tokens
Credentials
Private configuration
```

Use:

```text
.env.example
```

for configuration documentation.

Before pushing:

```powershell
git status
git diff --check
```

If an API key is exposed, revoke it and generate a replacement.

---

# 42. Final Verification Checklist

Before considering the repository ready:

* [x] `.env` is not committed
* [x] `.env.example` contains placeholders
* [x] Retrieval index can be built from source documents
* [x] Pytest passes
* [x] Ruff passes
* [x] `git diff --check` passes
* [x] Docker Compose configuration is valid
* [x] Docker image builds
* [x] Container starts
* [x] Container becomes healthy
* [x] `/health` returns healthy
* [x] `/ready` returns ready
* [x] `/chat` returns an answer
* [x] Sources are returned for grounded policy questions
* [x] Out-of-scope behavior is evaluated
* [x] Checkpoint persistence is implemented
* [x] Risky operations require approval
* [x] Audit trail records tool calls
* [x] Prompt-injection tests pass
* [x] Main evaluation quality gate passes
* [x] CI workflows are configured
* [x] Security audit is reviewed
* [x] Live production request verified
* [x] Runtime metrics verified
* [x] Git working tree verified clean

---

# 43. Current Verification Results

## Test Suite

```text
40 passed
```

## Ruff

```text
All checks passed!
```

## Dependency Check

```text
No broken requirements found.
```

## Main RAG Evaluation

```text
Cases:        5
Passed:       5
Failed:       0
Errors:       0
Completion:   100%
Source hit:   100%
```

## Query Routing Evaluation

```text
Total queries: 7
Passed:        7
Failed:        0
Pass rate:     100%
```

## Prompt-Injection Evaluation

```text
Total cases:   5
Passed:        5
Failed:        0
Resistance:    100% among completed cases
```

## AI Quality Gate

```text
Overall pass rate: 100%
Required minimum:  90%
P95 latency:       15.594 seconds
Maximum allowed:   20 seconds

ALL AI QUALITY GATES PASSED
```

## Production Docker Verification

```text
Docker build:       PASSED
Container startup:  PASSED
Container health:   HEALTHY
/health:             HEALTHY
/ready:              READY
/chat:               VERIFIED
/metrics:            VERIFIED
```

## Live Request Metrics

```text
Chat latency:       7,526 ms
Retrieval latency:  4,357 ms
LLM latency:        2,370 ms

Prompt tokens:      433
Completion tokens:  395
Total tokens:       828

Estimated cost:     $0.000151
Error rate:         0%
```

---

# 44. Production Completion Summary

The completed Company Policy Agent demonstrates:

```text
RAG
+
Query Routing
+
Retrieval Relevance Filtering
+
Async Parallel Tool Execution
+
Durable Checkpointing
+
Human-in-the-Loop Approval
+
Audit Trail
+
Safety Guardrails
+
Prompt-Injection Evaluation
+
Runtime Monitoring
+
Token and Cost Tracking
+
Automated Evaluation
+
CI Quality Gates
+
Dependency Security Review
+
Docker Deployment
+
Health Checks
+
Readiness Checks
+
Production Logging
+
Live End-to-End Verification
```

The project is designed to demonstrate the engineering practices required to move an AI agent beyond a prototype and toward a production-oriented system.

---

# 45. Final Status

The production-hardening work is complete.

The final system has been verified at three levels:

### Code quality

```text
Ruff
Pytest
pip check
```

### AI quality

```text
RAG evaluation
Routing evaluation
Prompt-injection evaluation
Latency and cost evaluation
```

### Runtime

```text
Docker
Health
Readiness
Live /chat request
Runtime metrics
Git verification
```

Known limitations and security findings are documented rather than hidden.

The repository's final production state is intended to be reproducible, testable, observable, and reviewable.
