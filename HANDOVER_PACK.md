# Handover Pack - Company Policy Agent

## 1. Project Overview

**Project:** Company Policy Agent
**Repository:** `week2day5proj1`

The system is a production-oriented policy assistant that uses RAG to answer questions from company policy documents.

Core components:

* Groq API with OpenAI-compatible models
* LangGraph agent routing
* Chroma vector database
* Hugging Face sentence-transformer embeddings
* FastAPI production API
* Streamlit interface
* Prompt-injection protection
* Input/output safety validation
* Human approval for risky operations
* Audit logging
* Durable LangGraph checkpointing
* Docker deployment
* Evaluation and quality gates
* Metrics and monitoring

---

## 2. Project Structure

Important directories/files:

```text
app/              Application code
tests/            Automated tests
evals/            Evaluation suite and evaluation reports
data/             Policy documents
storage/           Persistent Chroma/checkpoint storage
audit_logs/        Application audit trail
charts/            Evaluation charts
README.md          Project documentation
SECURITY.md       Security information
FAILURE_MODES.md  Failure-mode documentation
sprint_board.md   Sprint status and scope
HANDOVER_PACK.md  This handover document
Dockerfile        Container image definition
docker-compose.yml Docker deployment
```

---

## 3. Environment Setup

Activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Configure the required environment variables in `.env`.

Important variables include:

```text
GROQ_API_KEY
GROQ_MODEL
GROQ_LARGE_MODEL
GROQ_SAFETY_MODEL
EMBEDDING_MODEL
CHROMA_PATH
LANGCHAIN_TRACING_V2
LANGCHAIN_PROJECT
LANGCHAIN_ENDPOINT
```

Do not commit secrets or `.env` files.

---

## 4. Run the Application Locally

Run the Streamlit interface:

```powershell
streamlit run app/ui.py
```

The application provides:

* Policy question answering
* Retrieved sources
* Tool information
* Safety handling
* Approval workflow
* Conversation/checkpoint support
* Metrics

---

## 5. Run the API

Start the FastAPI application:

```powershell
uvicorn app.api:app --reload
```

Important endpoints:

```text
GET  /
GET  /health
GET  /ready
GET  /metrics
POST /chat
GET  /checkpoint/{thread_id}
```

The health endpoint verifies that the service is running.

The readiness endpoint checks important runtime dependencies including:

* Groq configuration
* Model configuration
* Chroma storage
* Checkpoint storage

---

## 6. Docker Deployment

Build the production image:

```powershell
docker compose build
```

Start the service:

```powershell
docker compose up -d
```

Check the container:

```powershell
docker ps
```

Check logs:

```powershell
docker compose logs
```

Verify the API:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

Verify readiness:

```powershell
Invoke-RestMethod http://localhost:8000/ready
```

The verified production container was healthy and exposed port `8000`.

---

## 7. Running Tests

Run the complete automated test suite:

```powershell
pytest -q
```

Current verified result:

```text
41 passed
```

A dependency warning from installed ChromaDB telemetry code may appear. It does not currently fail the test suite.

---

## 8. Code Quality

Run Ruff:

```powershell
ruff check app tests evals *.py
```

Current verified result:

```text
All checks passed
```

---

## 9. Evaluation Suite

Run the routing evaluation:

```powershell
python -m evals.evaluate_routing
```

Run the evaluation gate:

```powershell
python -m evals.check_evaluation_gate
```

The evaluation gate is designed to fail when configured quality thresholds are not met.

Current verified evaluation:

* Completion: 100%
* HR: 2/2
* Company: 1/1
* IT: 1/1
* Out-of-scope: 1/1
* Warm P95 latency: 1080.27 ms
* Overall gate: PASS

---

## 10. Evaluation Evidence

Current evaluation evidence includes:

### Routing

```text
32/32 passed
100% pass rate
```

### Retrieval

```text
Top-2: 4/4 relevant in-scope cases
Out-of-scope no-evidence: 1/1
```

### Prompt Injection

```text
5/5 blocked
100% resistance on the current dataset
```

### Cost and Performance

Evaluation reporting includes:

* Pass rate by category
* Latency metrics
* Cold versus warm latency
* Retrieval quality
* Injection evaluation
* Monthly cost projection
* Projected 10x volume

---

## 11. Safety and Approval Workflow

The system distinguishes normal document retrieval from risky operations.

Risky operations include:

* `update_employee_record`
* `delete_employee_record`
* `send_email`

Risky operations require human approval.

The intended lifecycle is:

```text
Request
  |
  v
Risk detection
  |
  v
Approval request
  |
  v
PENDING
  |
  +----> REJECTED
  |
  +----> APPROVED
             |
             v
          EXECUTED
```

A production verification confirmed that an employee-record update request was stopped at the approval gate instead of being executed automatically.

---

## 12. Audit Logging

Application audit events are stored in:

```text
audit_logs/audit.jsonl
```

The audit trail records relevant events including:

* Tool calls
* Approval creation
* Approval approval
* Approval rejection
* Approval execution
* Security events

The root-level `audit.json` file is a dependency security report and is intentionally separate from the application audit trail.

---

## 13. Security

Review:

```text
SECURITY.md
```

Important security controls include:

* Prompt-injection detection
* Input validation
* Output validation
* Risky-tool approval
* Audit logging
* Dependency auditing
* No automatic execution of risky operations

The current installed ChromaDB version has advisories reported by `pip-audit`. This limitation is documented rather than hidden.

---

## 14. Known Limitations

The following limitations are accepted for the current project scope:

1. Approval state is currently process-local/in-memory and is not durable across application restarts or shared across replicas.
2. Cold-start embedding/model initialization can produce higher initial latency.
3. LLM response time depends on the external provider and network conditions.
4. The evaluation dataset is limited.
5. Prompt-injection testing does not cover every adaptive or indirect attack.
6. Current ChromaDB dependency advisories require future dependency review.
7. Cost projections are estimates based on documented assumptions.

See:

```text
FAILURE_MODES.md
```

for the complete failure-mode table.

---

## 15. Troubleshooting

### Import error when running evaluations

Use module execution from the repository root:

```powershell
python -m evals.evaluate_routing
```

rather than:

```powershell
python evals/evaluate_routing.py
```

### Slow first request

The first run may be slower because the embedding model must be initialized.

Subsequent warm requests are substantially faster.

### Groq rate limit

A provider rate-limit response is an external dependency condition. Wait for the provider limit to reset before rerunning a large evaluation.

### Docker container status

Check:

```powershell
docker ps
```

and:

```powershell
docker compose logs
```

Then verify:

```powershell
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod http://localhost:8000/ready
```

---

## 16. Final Verification Checklist

### Application

* [x] Real policy documents loaded
* [x] RAG retrieval working
* [x] Agent routing working
* [x] Safety controls active
* [x] Prompt-injection protection active
* [x] Risky-tool approval active
* [x] Audit logging active
* [x] Checkpointing active

### Quality

* [x] 41 automated tests passed
* [x] Ruff checks passed
* [x] Routing evaluation passed
* [x] Retrieval evaluation passed
* [x] Injection evaluation passed
* [x] Evaluation gate passed

### Production

* [x] Docker image builds
* [x] Docker container runs
* [x] Container healthy
* [x] `/health` verified
* [x] `/ready` verified
* [x] Real `/chat` request verified
* [x] Risky `/chat` request verified
* [x] Approval lifecycle verified
* [x] Audit lifecycle verified

### Documentation

* [x] README updated
* [x] SECURITY.md available
* [x] FAILURE_MODES.md created
* [x] Sprint Board updated
* [x] Handover Pack created

### Remaining Handover Tasks

* [ ] PR/review evidence verified
* [x] Independent unaided run completed
* [ ] Demo delivered
* [ ] Stakeholder feedback captured
* [ ] Three-page final report submitted
* [ ] Retrospective completed

---
## 16.1 Independent Verification

A fresh verification run was completed from the project environment using the documented commands.

Results:

* `pytest -q`: **41 passed**
* `ruff check app tests evals *.py`: **All checks passed**
* `python -m evals.check_evaluation_gate`: **PASS**
* `GET /health`: **healthy**
* `GET /ready`: **ready**
* Groq API configuration detected
* Chroma storage detected
* Checkpoint storage detected

This confirms that the documented test, evaluation, and production-health commands can be executed successfully from the project environment.

The test suite produced one existing ChromaDB telemetry deprecation warning. The warning does not currently fail the test suite.

 ---

## 17. Handover Statement

The current implementation has completed the major production-hardening work for the defined project scope.

The remaining activities are delivery and verification tasks rather than new feature development.

A new maintainer should begin with:

1. `README.md`
2. `sprint_board.md`
3. `FAILURE_MODES.md`
4. `SECURITY.md`
5. This handover document

Then run the automated test and evaluation commands before making changes.

The project should remain within the documented scope unless a verified requirement failure requires corrective work.
