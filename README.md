# Company Policy Agent

A production-oriented AI agent for answering company-policy questions using Retrieval-Augmented Generation (RAG), query routing, relevance filtering, asynchronous tool execution, durable checkpointing, human-in-the-loop approval, audit logging, safety guardrails, monitoring, Docker deployment, and automated AI evaluation gates.

The system uses Groq as the LLM provider with OpenAI-compatible models and local Hugging Face embeddings with ChromaDB for document retrieval.

---

## 1. Overview

The Company Policy Agent answers questions using a controlled set of company policy documents.

The system is designed to:

- Route questions to the appropriate tool
- Retrieve relevant policy documents
- Reject irrelevant retrieval results
- Generate answers grounded in retrieved documents
- Avoid hallucinating answers when information is unavailable
- Execute independent tools asynchronously
- Persist agent state using durable checkpoints
- Require human approval for risky operations
- Maintain an audit trail
- Detect prompt-injection attempts
- Expose operational metrics
- Run automated evaluation suites
- Enforce quality gates in CI
- Run as a Dockerized FastAPI service

This project demonstrates production-style AI-agent engineering with reliability, safety, observability, evaluation, and deployment controls.

---

# 2. Key Features

## AI and RAG

- ChromaDB vector retrieval
- Local Hugging Face embeddings
- Recursive document chunking
- Retrieval relevance threshold
- Grounded answer generation
- Source citation
- Honest "insufficient information" responses

## Query Routing

The agent determines whether a question should:

- Use `search_documents`
- Use another available tool
- Require no tool

Example:

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
             LLM
              |
              v
       Answer + sources

Out-of-scope questions such as:

    "What is Python?"
    "What is the weather today?"

are routed to `no_tool`.

---

## Async Execution

Independent tools can be executed in parallel to reduce overall execution latency.

Implementation:

    app/async_agent.py
    app/async_tools.py

Benchmarking:

    benchmark_async.py

---

## Durable Checkpointing

The agent maintains durable state using LangGraph checkpointing.

Checkpointed information includes:

- Request ID
- Session ID
- Question
- Conversation history
- Selected tool
- Answer
- Sources
- Tools used
- Approval information
- Execution trace

Checkpoint storage is persisted through the Docker volume:

    checkpoint_data

---

## Human-in-the-Loop Approval

Risky operations require explicit approval before execution.

Examples include:

    update_employee_record
    delete_employee_record
    send_email

Approval lifecycle:

    PENDING
       |
       v
    APPROVED
       |
       v
    EXECUTED

Rejected requests are blocked.

Search and retrieval operations do not require approval.

---

## Audit Trail

Tool calls and important actions are recorded with request identifiers.

The audit system provides traceability for:

- Tool calls
- Success/failure
- Request IDs
- Approval status
- Execution events

Relevant modules:

    app/audit.py
    app/approval.py

---

## Safety and Prompt Injection Protection

The project includes input and output safety controls.

Implemented controls include:

- Input validation
- Prompt-injection detection
- Output validation
- Risky-tool approval gates
- Safety regression tests
- Prompt-injection evaluation

Relevant modules:

    app/safety.py
    app/guardrails.py
    app/risky_tools.py

The system is designed to reduce unsafe behavior but should not be considered universally secure against all possible attacks.

---

# 3. Architecture

```text
                         User
                          |
                          v
                    Streamlit UI
                          |
                          v
                    FastAPI /chat
                          |
                          v
                    LangGraph Agent
                          |
              +-----------+-----------+
              |                       |
              v                       v
        Safety / Guardrails      Query Router
                                      |
                        +-------------+-------------+
                        |                           |
                        v                           v
                search_documents                 no_tool
                        |
                        v
                    ChromaDB
                        |
                        v
              Relevance Threshold
                        |
                 +------+------+
                 |             |
              Relevant      Irrelevant
                 |             |
                 v             v
                RAG     Honest limitation
                 |
                 v
              Groq LLM
                 |
                 v
          Answer + Sources
                 |
                 v
             API Response
                 |
          +------+------+
          |             |
          v             v
       Metrics       Audit Trail
          |
          v
   Monitoring Dashboard

---

# 4. Request Flow

A normal policy request follows:
                                
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
     +---------> Metrics
     |
     +---------> Audit logging


 For risky operations:
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
+-- evaluation_results.json
+-- pytest.ini
+-- README.md
+-- requirements.txt
+-- run_all.py
+-- SECURITY.md
|
+-- test_approval.py
+-- test_async_tools.py
+-- test_audit.py
+-- test_checkpoint.py
+-- test_groq.py
+-- test_llm.py
+-- test_metrics.py

7. Environment Variables

Create a local .env file.

Example:

GROQ_API_KEY=your_groq_api_key_here

GROQ_MODEL=openai/gpt-oss-20b
GROQ_LARGE_MODEL=openai/gpt-oss-120b
GROQ_SAFETY_MODEL=openai/gpt-oss-safeguard-20b

Never commit the real API key.

The repository contains:

.env.example

for configuration reference.

Do not use OPENAI_API_KEY for this project. Groq is the API provider.

8. Clean Clone Setup

Clone the repository:

git clone <repository-url>
cd week2day5proj1

Create a virtual environment:

python -m venv venv

Activate it in Windows PowerShell:

.\venv\Scripts\Activate.ps1

Install dependencies:

pip install -r requirements.txt

Create .env from .env.example and configure the Groq API key.

9. Build the Retrieval Index

The policy documents are stored in the project's data directory.

The ingestion script is:

app/ingest.py

Build the Chroma retrieval index:

python app/ingest.py

Current policy documents:

company_policy.pdf
hr_policy.pdf
it_policy.pdf

Verified ingestion result:

PDF pages loaded : 21
Chunks created   : 39
10. Run Tests

Run the complete test suite:

pytest -q

Latest verified result:

40 passed

There is currently one Chroma/OpenTelemetry deprecation warning. It does not cause the test suite to fail.

11. Run Code Quality Checks

Run Ruff:

ruff check app tests evals *.py

Run whitespace/diff validation:

git diff --check

Latest verification:

Ruff:
All checks passed

git diff --check:
Passed
12. Local API Development

The API is implemented in:

app/api.py

Run the API locally:

uvicorn app.api:app --reload --host 0.0.0.0 --port 8000

API:

http://localhost:8000
13. API Endpoints
Health
GET /health

Test:

Invoke-RestMethod http://localhost:8000/health

Verified response:

status   service              version
------   -------              -------
healthy  company-policy-agent 1.1.0
Readiness
GET /ready

Test:

Invoke-RestMethod http://localhost:8000/ready

The readiness check verifies:

Groq API key
Groq model
Chroma storage
Checkpoint storage
Chat
POST /chat

The endpoint executes the production agent flow and returns:

Request ID
Thread ID
Answer
Sources
Tools used
Trace
Metrics
GET /metrics

The metrics endpoint exposes:

Request counts
Successful requests
Errors
Latency
Error rate
LLM requests
Token usage
Estimated cost
Retrieval counters
Tool counters
Checkpoint
GET /checkpoint/{thread_id}

Returns persisted agent state for a LangGraph thread.

14. Query Routing

The router determines which execution path a question should take.

Examples:

Query	Expected route
What is the company leave policy?	search_documents
What does the company say about professional conduct?	search_documents
What are the company's confidentiality requirements?	search_documents
What is the company's IT security policy?	search_documents
What is Python?	no_tool
What is the weather today?	no_tool

Latest routing evaluation:

Total queries: 7
Passed: 7
Overall pass rate: 100.00%

Category results:

HR:            2/2 (100.00%)
Company:       1/1 (100.00%)
IT:            1/1 (100.00%)
Out-of-scope:  3/3 (100.00%)

No routing failures were reported.

15. Retrieval and RAG

Retrieval implementation:

app/retrieval.py
app/rag.py

Embedding model:

sentence-transformers/all-MiniLM-L6-v2

The retrieval flow:

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

Current empirically calibrated maximum retrieval distance:

1.10

Professional-conduct queries produced distances approximately around:

1.04 - 1.08

An unrelated relocation-policy query produced distances approximately around:

1.29 - 1.34

The threshold is calibrated for the current dataset and should be recalibrated if the documents, embedding model, chunking strategy, or retrieval system changes significantly.

16. Honest Retrieval Behavior

If no retrieved document passes the relevance threshold, the system does not fabricate an answer.

It returns:

I don't have enough information in the provided documents to answer that question.

Example:

What is the company's relocation allowance policy?

If the indexed documents do not contain relevant information, the system returns an honest limitation rather than inventing a policy.

17. Async Parallel Tool Execution

Async execution is implemented in:

app/async_agent.py
app/async_tools.py

Independent tools can run concurrently.

Benchmarking:

benchmark_async.py

Conceptually:

Sequential:

Tool A -> Tool B -> Tool C
             |
             v
        Total latency

versus:

Parallel:

Tool A ----+
Tool B ----+----> Combined result
Tool C ----+

Parallel execution can reduce latency when tools are independent and safe to execute concurrently.

18. Durable Checkpointing

Checkpoint implementation:

app/checkpoint.py
app/memory.py
app/state.py

Persisted state can include:

Request ID
Session ID
Question
Conversation history
Selected tool
Answer
Sources
Tools used
Approval status
Execution trace

Docker checkpoint storage:

/app/storage/checkpoints

Volume:

checkpoint_data
19. Human-in-the-Loop Approval

Approval implementation:

app/approval.py
app/risky_tools.py

Risky operations include:

update_employee_record
delete_employee_record
send_email

Approval lifecycle:

PENDING
   |
   +---- REJECTED ----> BLOCKED
   |
   +---- APPROVED ----> EXECUTED
                              |
                              v
                         AUDIT TRAIL

Search operations do not require approval.

20. Audit Trail

Audit implementation:

app/audit.py

The system records information such as:

Request IDs
Tool calls
Tool success/failure
Approval status
Execution events

This provides traceability for important agent actions.

21. Safety and Prompt Injection

Safety modules:

app/safety.py
app/guardrails.py
app/risky_tools.py

Safety controls include:

Input validation
Prompt-injection detection
Output validation
Risky-tool restrictions
Human approval
Safety regression tests
Prompt-injection evaluation

Run safety tests:

pytest -q tests/test_safety.py tests/test_approval_safety.py

Run prompt-injection evaluation:

python evals/evaluate_injection.py

The CI injection-resistance gate requires:

95%

This is a test-set evaluation threshold and is not a guarantee against all future prompt-injection attacks.

22. Monitoring

Monitoring implementation:

app/metrics.py

Tracked metrics include:

Total requests
Successful requests
Failed requests
Error rate
Latency
LLM request count
Prompt tokens
Completion tokens
Total tokens
Estimated LLM cost
Cost per request
Retrieval success
Tool usage

Metrics endpoint:

GET /metrics

Production request flow:

Agent UI
   |
   v
FastAPI /chat
   |
   v
LangGraph
   |
   v
Router
   |
   v
Chroma
   |
   v
Groq
   |
   v
Metrics
   |
   v
Monitoring Dashboard

The production chat path is connected to the same metrics service used by the monitoring dashboard.

23. Cost Tracking

The LLM layer records:

Prompt tokens
Completion tokens
Total tokens
Estimated request cost
Total estimated cost

Configured models:

openai/gpt-oss-20b
openai/gpt-oss-120b
openai/gpt-oss-safeguard-20b

Cost figures are estimates based on configured model pricing and observed token usage.

24. Evaluation Suite

Evaluation implementation:

evals/

Main evaluation scripts:

evaluate.py
evaluate_routing.py
evaluate_injection.py
check_evaluation_gate.py

Datasets:

evaluation_dataset.json
query_routing_dataset.json
injection_dataset.json

Evaluation results:

evaluation_results.json
routing_evaluation_results.json
injection_results.json
25. Routing Evaluation Results

Latest verified result:

Total queries: 7
Passed: 7
Overall pass rate: 100.00%

Breakdown:

HR:            2/2 (100.00%)
Company:       1/1 (100.00%)
IT:            1/1 (100.00%)
Out-of-scope:  3/3 (100.00%)

No failures were reported.

26. AI Evaluation Quality Gate

Run:

python evals/check_evaluation_gate.py

Latest verified quality gate:

AI EVALUATION QUALITY GATE
Overall pass rate: 100.00%
Required minimum: 90.00%

Overall pass-rate gate passed

Category results:
  HR: 2/2 (100.00%)
  Company: 1/1 (100.00%)
  IT: 1/1 (100.00%)
  Out-of-scope: 1/1 (100.00%)

Query-type pass-rate gates passed

P95 latency: 15593.67 ms
Maximum allowed: 20000.00 ms
P95 latency gate passed

ALL AI QUALITY GATES PASSED

The quality gate checks:

Overall pass rate
Query-category pass rates
P95 latency

The separate routing evaluation reported a higher P95 because the first query experienced an embedding-model cold-start effect. That value should not automatically be treated as steady-state latency.

27. CI/CD

The repository contains two GitHub Actions workflows:

.github/workflows/ci.yml
.github/workflows/evaluation.yml
CI Workflow

The CI workflow performs:

Unit and integration tests
Retrieval index construction
Ruff linting
Dependency security audit
Docker build
Safety and approval regression tests
AI evaluation quality gate

The retrieval index is built during CI:

python app/ingest.py

This allows a clean clone to reproduce the required retrieval state instead of depending on a pre-existing local Chroma database.

AI Evaluation Workflow

The evaluation workflow performs:

Full test suite
Ruff
Prompt-injection evaluation
Injection-resistance gate

Minimum injection resistance:

95%

If the result falls below the threshold, the workflow fails.

28. Dependency Security

The project uses:

pip-audit

The dependency audit checks:

requirements.txt

The current CI configuration explicitly ignores:

PYSEC-2026-311
PYSEC-2026-3813
PYSEC-2026-3814
PYSEC-2026-3815

These advisories should continue to be reviewed when dependency updates become available.

Therefore, the security result should be interpreted as:

No unignored known vulnerabilities

rather than:

No known vulnerabilities exist

Additional security information:

SECURITY.md
29. Docker Deployment

Docker files:

Dockerfile
docker-compose.yml

Base image:

python:3.12-slim

Application command:

uvicorn app.api:app --host 0.0.0.0 --port 8000

Build:

docker compose build

Start:

docker compose up -d

Check:

docker compose ps

Expected:

healthy
30. Docker Volumes

Two named volumes are used:

chroma_data
checkpoint_data

Mounts:

chroma_data
    |
    v
/app/storage/chroma
checkpoint_data
    |
    v
/app/storage/checkpoints

These volumes allow persistent vector and checkpoint storage across normal container restarts.

31. Docker Healthcheck

The container healthcheck calls:

GET /health

Configuration:

Start period: 30 seconds
Interval: 30 seconds
Timeout: 10 seconds
Retries: 3

Verified production response:

status   service              version
------   -------              -------
healthy  company-policy-agent 1.1.0
32. Readiness Check

The readiness endpoint:

GET /ready

checks:

Groq API key
Groq model
Chroma storage
Checkpoint storage

Verified readiness state:

groq_api_key=True
groq_model=True
chroma_storage=True
checkpoint_storage=True
33. Production Logging

The API uses structured request logging.

Logged fields include:

timestamp
level
logger
message
request_id
endpoint
latency_ms
status

Example:

HTTP request completed
endpoint: /health
latency_ms: 0.59
status: 200

Request IDs allow requests to be correlated with logs and traces.

34. Production Verification

The production Docker deployment has been locally verified with:

docker compose config
docker compose build
docker compose up -d
docker compose ps

Final container status:

Up ... (healthy)

Health endpoint:

HTTP 200
healthy

Readiness endpoint:

ready

The application logs also confirmed successful HTTP requests and request IDs.

35. Useful Commands
Install dependencies
pip install -r requirements.txt
Build retrieval index
python app/ingest.py
Run tests
pytest -q
Run routing evaluation
python evals/evaluate_routing.py
Run evaluation quality gate
python evals/check_evaluation_gate.py
Run prompt-injection evaluation
python evals/evaluate_injection.py
Run Ruff
ruff check app tests evals *.py
Check whitespace
git diff --check
Build Docker image
docker compose build
Start Docker service
docker compose up -d
Stop Docker service
docker compose down
Check container
docker compose ps
View logs
docker compose logs --tail=100 company-policy-agent
Health
Invoke-RestMethod http://localhost:8000/health
Readiness
Invoke-RestMethod http://localhost:8000/ready
Metrics
Invoke-RestMethod http://localhost:8000/metrics
36. Startup Helper

The repository includes:

run_all.py

This provides a convenient local startup workflow.

Individual commands in this README can also be used when running individual components during development.

37. Known Limitations
Retrieval Threshold

The current relevance threshold was calibrated against the current policy dataset.

It should be recalibrated when:

Documents change significantly
Embeddings change
Chunking changes
The retrieval model changes
Cold-Start Latency

The first retrieval request can be significantly slower because the embedding model may need to load into memory.

Therefore, first-request latency should not automatically be treated as normal steady-state latency.

Monitoring Latency

The current metrics system records multiple types of latency.

HTTP/API latency and LLM-related latency should be interpreted according to their metric definitions rather than treating a single metric as complete end-to-end model latency.

Security

The system includes multiple safety controls, but no prompt-injection defense should be considered perfect.

Production deployments should continue to:

Expand attack datasets
Run regression evaluations
Review tool permissions
Rotate secrets
Update dependencies
Monitor unusual behavior
Evaluation Coverage

The current evaluation datasets are targeted to the capstone requirements.

A passing evaluation does not guarantee correct behavior for every possible future question.

38. Security Practices

Never commit:

.env
API keys
Access tokens
Credentials
Private configuration

Use:

.env.example

for configuration documentation.

Before pushing:

git status
git diff --check

If an API key is exposed, revoke it and generate a replacement.

39. Final Verification Checklist

Before considering the repository ready:

[ ] .env is not committed
[ ] .env.example contains placeholders only
[ ] Retrieval index can be built from source documents
[ ] pytest passes
[ ] Ruff passes
[ ] git diff --check passes
[ ] Docker Compose configuration is valid
[ ] Docker image builds
[ ] Container starts
[ ] Container becomes healthy
[ ] /health returns healthy
[ ] /ready returns ready
[ ] /chat returns an answer
[ ] Sources are returned for grounded policy questions
[ ] Out-of-scope questions are handled appropriately
[ ] Checkpoint persistence works
[ ] Risky operations require approval
[ ] Audit trail records tool calls
[ ] Prompt-injection tests pass
[ ] Evaluation quality gate passes
[ ] CI workflows are configured
[ ] Security audit is reviewed
40. Current Verification Results
Test Suite
40 passed
Ruff
All checks passed!
Git Diff Check
Passed
Query Routing Evaluation
Total queries: 7
Passed: 7
Overall pass rate: 100.00%

Category results:

HR:            2/2 (100.00%)
Company:       1/1 (100.00%)
IT:            1/1 (100.00%)
Out-of-scope:  3/3 (100.00%)
AI Evaluation Quality Gate
Overall pass rate: 100.00%
Required minimum: 90.00%

P95 latency: 15593.67 ms
Maximum allowed: 20000.00 ms

ALL AI QUALITY GATES PASSED
Production Docker Verification
Docker build: PASSED
Container startup: PASSED
Container health: HEALTHY
/health: HTTP 200
/ready: READY
41. Final Architecture Summary
                         +----------------+
                         |      User      |
                         +-------+--------+
                                 |
                                 v
                         +---------------+
                         | Streamlit UI  |
                         +-------+-------+
                                 |
                                 v
                         +---------------+
                         |   FastAPI     |
                         |     /chat     |
                         +-------+-------+
                                 |
                                 v
                         +---------------+
                         |   LangGraph   |
                         |     Agent     |
                         +-------+-------+
                                 |
                                 v
                      +---------------------+
                      | Safety / Guardrails |
                      +----------+----------+
                                 |
                                 v
                      +-------------------+
                      |   Query Router    |
                      +----+---------+----+
                           |         |
                    Policy |         | General
                           |         |
                           v         v
                    +-----------+ +--------+
                    |  ChromaDB | | no_tool|
                    +-----+-----+ +--------+
                          |
                          v
                  +---------------+
                  | Relevance     |
                  | Threshold     |
                  +-------+-------+
                          |
                          v
                    +-----------+
                    |  Groq LLM |
                    +-----+-----+
                          |
                          v
                  +---------------+
                  | Answer +      |
                  | Sources       |
                  +-------+-------+
                          |
              +-----------+-----------+
              |           |           |
              v           v           v
        Checkpoint      Audit      Metrics
              |           |           |
              +-----------+-----------+
                          |
                          v
                  +---------------+
                  |  Monitoring   |
                  |   Dashboard   |
                  +---------------+
42. Project Completion Summary

The completed Company Policy Agent demonstrates:

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
Prompt Injection Evaluation
+
Monitoring
+
Cost Tracking
+
Automated Evaluation
+
CI Quality Gates
+
Dependency Security Checks
+
Docker Deployment
+
Health and Readiness Checks
+
Production Logging