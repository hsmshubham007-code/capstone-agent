# Company Policy Agent

A production-style company policy assistant built with **LangGraph, RAG, ChromaDB, Groq, FastAPI, Docker, and durable checkpointing**.

The agent retrieves information from company policy documents and generates grounded answers using an LLM. The API exposes the agent through FastAPI and the application is containerized with Docker for reproducible deployment.

---

## 1. Project Overview

The Company Policy Agent answers questions about internal company documents such as:

* HR policies
* Corporate policies
* IT policies

The system uses retrieval-augmented generation (RAG) so that answers are based on the available company documents rather than relying only on the model's general knowledge.

The agent also records:

* Which tool was used
* Which sources were retrieved
* Execution trace
* LangGraph checkpoint state
* Conversation/session identifier

---

## 2. Architecture

```text
                    ┌──────────────────────┐
                    │        Client        │
                    │ Browser / API Client │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │       FastAPI        │
                    │                      │
                    │ GET  /health         │
                    │ POST /chat           │
                    │ GET  /checkpoint     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      LangGraph       │
                    │                      │
                    │       Router         │
                    └──────────┬───────────┘
                               │
                    ┌──────────┴───────────┐
                    │                      │
                    ▼                      ▼
             ┌──────────────┐       ┌──────────────┐
             │    Chroma    │       │     Groq     │
             │  Vector DB   │       │      LLM     │
             └──────────────┘       └──────────────┘
                    │                      │
                    └──────────┬───────────┘
                               ▼
                    ┌──────────────────────┐
                    │ Answer + Sources +   │
                    │ Tools + Execution    │
                    │ Trace                │
                    └──────────────────────┘

                 Persistent Docker Volumes
                 ├── Chroma data
                 └── Checkpoint database
```

---

## 3. Technology Stack

| Component           | Technology                               |
| ------------------- | ---------------------------------------- |
| Agent orchestration | LangGraph                                |
| LLM provider        | Groq                                     |
| LLM model           | `openai/gpt-oss-20b`                     |
| Embeddings          | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector database     | ChromaDB                                 |
| API                 | FastAPI                                  |
| API server          | Uvicorn                                  |
| Containerization    | Docker                                   |
| Persistence         | Docker named volumes                     |
| Checkpointing       | LangGraph SQLite checkpointer            |
| Configuration       | python-dotenv                            |
| Observability       | LangSmith                                |

---

## 4. Project Structure

```text
week2day5proj1/
│
├── app/
│   ├── api.py
│   ├── agent.py
│   ├── checkpoint.py
│   ├── config.py
│   ├── embedding.py
│   ├── graph.py
│   ├── llm.py
│   ├── retrieval.py
│   ├── router.py
│   ├── state.py
│   ├── tools.py
│   └── ...
│
├── data/
│   ├── hr_policy.pdf
│   ├── company_policy.pdf
│   └── it_policy.pdf
│
├── storage/
│   ├── chroma/
│   └── checkpoints/
│
├── tests/
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

# 5. Environment Variables and Secrets

The application uses environment variables for configuration and secrets.

Example:

```env
GROQ_API_KEY=your_groq_api_key

GROQ_MODEL=openai/gpt-oss-20b
GROQ_LARGE_MODEL=openai/gpt-oss-120b
GROQ_SAFETY_MODEL=openai/gpt-oss-safeguard-20b

LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=week2day5proj1
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

CHROMA_PATH=./chroma_db
```

### Security rules

The real API key must **never** be committed to Git.

The `.env` file is excluded from the Docker build using `.dockerignore`.

It should also be excluded from Git using `.gitignore`:

```gitignore
.env
.env.*
!.env.example
```

The Docker image does not contain the API key.

The key is supplied to the running container at runtime.

### Production recommendation

For production deployment, replace the local `.env` approach with a proper secret manager or Docker/Kubernetes secrets.

Examples include:

* Docker Secrets
* Kubernetes Secrets
* Cloud secret managers
* CI/CD secret stores

Never hard-code API keys inside Python files or the Dockerfile.

---

# 6. Dockerfile

The application uses a lightweight Python 3.12 image.

```dockerfile
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

The Docker image:

1. Starts from Python 3.12
2. Creates `/app`
3. Installs Python dependencies
4. Copies the application
5. Exposes port `8000`
6. Starts FastAPI using Uvicorn

---

# 7. Docker Compose

The application is deployed using Docker Compose.

```yaml
services:

  company-policy-agent:
    build: .

    ports:
      - "8000:8000"

    env_file:
      - .env

    volumes:
      - chroma_data:/app/storage/chroma
      - checkpoint_data:/app/storage/checkpoints

    restart: unless-stopped

    healthcheck:
      test:
        [
          "CMD",
          "python",
          "-c",
          "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
        ]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

volumes:
  chroma_data:
    external: true

  checkpoint_data:
    external: true
```

The named volumes prevent application data from disappearing when the container is recreated.

---

# 8. Create Persistent Volumes

Create the Docker volumes once:

```powershell
docker volume create week2day5proj1_checkpoint_data
docker volume create week2day5proj1_chroma_data
```

These volumes store:

```text
week2day5proj1_checkpoint_data
    └── LangGraph SQLite checkpoints

week2day5proj1_chroma_data
    └── Chroma vector database
```

The volumes exist independently from the container.

Therefore:

```text
Container deleted
       ↓
Volumes remain
       ↓
New container
       ↓
Same data available
```

---

# 9. Build and Start the Application

From the project directory:

```powershell
cd "C:\Users\HSM\Desktop\week 2\week2day5proj1"
```

Build and start:

```powershell
docker compose up -d --build
```

Check the container:

```powershell
docker compose ps
```

Expected status:

```text
Up ... (healthy)
```

---

# 10. Health Check

The application exposes:

```text
GET /health
```

Test it:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Expected response:

```text
status  service
------  -------
healthy company-policy-agent
```

The Docker healthcheck also calls this endpoint automatically.

The healthcheck verifies that the FastAPI service is responding.

### Important distinction

The healthcheck identifies whether the container is healthy or unhealthy.

The Docker Compose setting:

```yaml
restart: unless-stopped
```

handles container/process restart behavior.

A Docker healthcheck by itself does **not** mean Docker Compose automatically restarts a container merely because its healthcheck becomes unhealthy.

For advanced automatic remediation based specifically on health status, an orchestrator such as Kubernetes or Docker Swarm can be used.

---

# 11. Chat API

The main endpoint is:

```text
POST /chat
```

Example PowerShell request:

```powershell
$body = @{
    question = "What are the rules for professional conduct?"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/chat" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

The response contains:

```text
answer
sources
tools_used
trace
thread_id
```

Example structure:

```json
{
  "thread_id": "example-thread-id",
  "answer": "The rules for professional conduct are...",
  "sources": [
    "hr_policy.pdf",
    "company_policy.pdf"
  ],
  "tools_used": [
    "search_documents"
  ],
  "trace": [
    {
      "step": "router",
      "tool": "search_documents"
    },
    {
      "step": "search_documents",
      "tool": "search_documents"
    }
  ]
}
```

---

# 12. Durable Checkpointing

LangGraph uses a SQLite checkpointer.

The checkpoint database is stored inside the Docker persistent volume.

```text
/app/storage/checkpoints/
    └── checkpoints.sqlite
```

The API accepts a `thread_id`.

Example:

```json
{
  "question": "What are the rules for professional conduct?",
  "thread_id": "demo-thread-001"
}
```

LangGraph associates the execution state with that thread.

The checkpoint stores information such as:

* Question
* Tool selected
* Answer
* Sources
* Execution trace
* Graph state

---

# 13. Checkpoint Persistence Test

A checkpoint can be inspected using:

```text
GET /checkpoint/{thread_id}
```

Example:

```powershell
Invoke-RestMethod `
    http://127.0.0.1:8000/checkpoint/demo-thread-001
```

To verify persistence:

```text
1. Send a request
       ↓
2. Check checkpoint
       ↓
3. Stop container
       ↓
4. Start container again
       ↓
5. Check same checkpoint
```

The checkpoint remains because the SQLite database is stored in a Docker named volume.

---

# 14. Container Restart Test

Stop the application:

```powershell
docker compose down
```

Start it again:

```powershell
docker compose up -d
```

Check:

```powershell
docker compose ps
```

Then verify:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

The application should return:

```text
healthy
```

Previously stored checkpoints and Chroma data remain available because they are stored in persistent Docker volumes.

---

# 15. Why Named Volumes Are Used

The project initially used host bind mounts for persistence.

The SQLite checkpoint database experienced file-access problems with the Windows/Docker bind-mounted storage.

The deployment was changed to Docker named volumes:

```text
Docker container
      │
      ├── /app/storage/chroma
      │       ↓
      │   chroma_data
      │
      └── /app/storage/checkpoints
              ↓
          checkpoint_data
```

This keeps the persistent application state inside Docker-managed storage rather than relying on Windows host filesystem behavior for SQLite.

---

# 16. Failover Strategy

The application has several failure-handling layers.

## Failure 1: Application/container crash

If the application process exits unexpectedly:

```text
Application crash
       ↓
Docker restart policy
       ↓
Container restarted
       ↓
Application available again
```

Configured with:

```yaml
restart: unless-stopped
```

---

## Failure 2: Groq/LLM unavailable

The LLM layer raises a controlled `LLMServiceError`.

FastAPI catches the error and returns HTTP `503 Service Unavailable`.

```text
User request
     ↓
LangGraph
     ↓
Groq unavailable
     ↓
LLMServiceError
     ↓
FastAPI
     ↓
HTTP 503
```

The response contains a structured error:

```json
{
  "detail": {
    "error": "llm_unavailable",
    "message": "The Groq LLM service is currently unavailable.",
    "thread_id": "example-thread-id",
    "failover": "Retry the request when the Groq service is available."
  }
}
```

The client can retry the request when the LLM service becomes available.

---

## Failure 3: Container recreation

If the container is removed:

```text
Container removed
       ↓
Docker named volumes remain
       ↓
New container starts
       ↓
Chroma data remains
       ↓
Checkpoint data remains
```

This allows the application to recover its persistent state.

---

## Failure 4: Persistent storage loss

If the Docker volumes themselves are lost or corrupted, the recovery process is:

```text
Storage failure
       ↓
Restore Chroma backup
       +
Restore checkpoint database backup
       ↓
Recreate containers
       ↓
Verify /health
       ↓
Verify /checkpoint/{thread_id}
       ↓
Verify /chat
```

Production deployments should therefore back up persistent volumes.

---

# 17. Failover Test

The LLM failure path can be tested safely by running a temporary container with an invalid model name.

The expected behavior is:

```text
Invalid/unavailable model
        ↓
Groq request fails
        ↓
LLMServiceError
        ↓
FastAPI catches exception
        ↓
HTTP 503
```

The production `.env` should not be permanently modified for this test.

After testing, restore the normal application:

```powershell
docker compose up -d
```

Verify:

```powershell
docker compose ps
```

and:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

---

# 18. Secret Handling During Deployment

The Docker image should never contain the real Groq API key.

The `.dockerignore` contains:

```text
.env
```

Therefore:

```text
Docker build
    ↓
.env excluded
    ↓
Image does not contain secret
```

At runtime:

```text
.env
  ↓
Docker Compose
  ↓
Environment variable
  ↓
FastAPI container
  ↓
Groq client
```

Never run commands that print the complete environment configuration or API key into logs or terminal output.

If an API key is accidentally exposed, revoke/rotate it immediately.

---

# 19. Production Deployment Checklist

Before production deployment:

* [ ] Never commit `.env`
* [ ] Use a production secret manager
* [ ] Rotate any exposed API keys
* [ ] Use HTTPS/TLS
* [ ] Put FastAPI behind a reverse proxy
* [ ] Restrict network access
* [ ] Back up Chroma storage
* [ ] Back up checkpoint storage
* [ ] Monitor `/health`
* [ ] Monitor application logs
* [ ] Configure alerting
* [ ] Verify Groq failure handling
* [ ] Verify container restart behavior
* [ ] Verify checkpoint recovery
* [ ] Verify vector database recovery

---

# 20. Useful Docker Commands

### Start

```powershell
docker compose up -d
```

### Build and start

```powershell
docker compose up -d --build
```

### Stop

```powershell
docker compose down
```

### View status

```powershell
docker compose ps
```

### View logs

```powershell
docker compose logs
```

### Follow logs

```powershell
docker compose logs -f
```

### Restart

```powershell
docker compose restart
```

### List volumes

```powershell
docker volume ls
```

---

# 21. API Endpoints

| Method | Endpoint                  | Purpose                           |
| ------ | ------------------------- | --------------------------------- |
| GET    | `/health`                 | Service health check              |
| POST   | `/chat`                   | Ask the company policy agent      |
| GET    | `/checkpoint/{thread_id}` | Inspect persisted LangGraph state |

---

# 22. Example Workflow

```text
User
 │
 │ "What are the rules for professional conduct?"
 ▼
FastAPI /chat
 │
 ▼
LangGraph Router
 │
 │ decides search_documents
 ▼
Chroma Retrieval
 │
 │ retrieves relevant policy chunks
 ▼
Groq LLM
 │
 │ generates grounded answer
 ▼
FastAPI Response
 │
 ├── Answer
 ├── Sources
 ├── Tools Used
 ├── Trace
 └── Thread ID
```

---

# 23. Current Deployment Status

The following deployment requirements have been implemented and tested:

| Requirement                      | Status   |
| -------------------------------- | -------- |
| Docker containerization          | Complete |
| FastAPI deployment               | Complete |
| Docker healthcheck               | Complete |
| Runtime secret injection         | Complete |
| `.env` excluded from image       | Complete |
| Persistent Chroma storage        | Complete |
| Persistent checkpoint storage    | Complete |
| Container recreation persistence | Tested   |
| Groq failure handling            | Complete |
| HTTP 503 failover response       | Tested   |
| Durable LangGraph checkpointing  | Tested   |
| API health verification          | Tested   |

---

# 24. Summary

The Company Policy Agent is deployed as a Dockerized FastAPI service with LangGraph orchestration, Chroma-based retrieval, Groq LLM inference, and durable SQLite checkpointing.

The deployment separates:

* Application code
* LLM credentials
* Vector database state
* Agent checkpoint state

Docker named volumes preserve the application's persistent state across container recreation.

FastAPI exposes health and chat endpoints, while the LLM layer converts provider failures into controlled HTTP `503` responses.

This provides a basic production-oriented deployment architecture with:

**containerization + secrets handling + health monitoring + persistent state + durable checkpointing + documented failover.**
