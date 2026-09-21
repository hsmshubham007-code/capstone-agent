# Company Policy Agent — Design Document

**Project:** `week2day5proj1`
**Document Status:** Engineering Design
**Audience:** Senior Engineer, Mentor, Technical Reviewer
**Version:** 1.0
**Date:** 2026-09-21

---

# 1. Executive Summary

The Company Policy Agent is an AI-powered internal assistant designed to help employees retrieve and understand information from company policy documents.

The system uses Retrieval-Augmented Generation (RAG) to ground answers in approved company documents rather than relying solely on the language model's internal knowledge. A routing layer determines whether a request should be answered through document retrieval, routed toward an employee-record operation, or handled without a tool.

Because some agent actions can affect business or employee data, potentially risky operations are separated from ordinary information retrieval. Risky tools such as employee-record updates, employee-record deletion, and email sending require explicit human approval before execution.

The system also provides:

* Prompt-injection detection.
* Input and output validation.
* Audit logging.
* LangGraph state management.
* SQLite-based checkpointing.
* Asynchronous tool execution.
* FastAPI serving.
* Streamlit user interface.
* Docker-based deployment.
* Automated testing.
* Evaluation and routing metrics.
* Code-quality and dependency-security checks.

The design intentionally separates **information retrieval** from **state-changing actions**. Reading policy information can proceed automatically, while potentially consequential operations remain behind a human approval boundary.

---

# 2. Problem and Goals

## 2.1 Problem

Employees may need answers to questions such as:

* What is the leave policy?
* What are the company's professional conduct expectations?
* What is the IT password policy?
* What should an employee do after a security incident?
* What company rules apply to a particular situation?

A traditional workflow requires a person to:

1. Receive the question.
2. Identify the relevant policy.
3. Search one or more documents.
4. Read the relevant sections.
5. Interpret the policy.
6. Write an answer.
7. Provide the source to the employee.

This workflow is repetitive and can introduce inconsistency or missed information.

The proposed system assists with the retrieval and explanation portions of this workflow while keeping sensitive actions under human control.

---

## 2.2 Goals

The system should:

1. Retrieve relevant information from approved policy documents.
2. Generate answers grounded in retrieved content.
3. Identify the documents used to answer a question.
4. Route requests to appropriate tools.
5. Reject or contain unsafe requests.
6. Require approval before risky operations.
7. Record important tool activity.
8. Maintain conversational state.
9. Support asynchronous execution where appropriate.
10. Expose the application through an API.
11. Run consistently in a container.
12. Provide measurable evaluation results.

---

## 2.3 Non-Goals

The current system does not attempt to:

* Replace HR decision-making.
* Make autonomous employment decisions.
* Modify real employee records without approval.
* Send autonomous emails without approval.
* Operate directly against a production employee database.
* Treat the language model as an authoritative source independent of company documents.

---

# 3. Requirements

## 3.1 Functional Requirements

### FR1 — Policy Retrieval

The system must retrieve relevant chunks from approved company policy documents.

### FR2 — Grounded Answers

Answers to policy questions should be based on retrieved document content.

### FR3 — Source Attribution

The response should identify the policy documents used to support the answer.

### FR4 — Request Routing

The system must distinguish between:

* Policy/document questions.
* Employee-record operations.
* Requests that require no tool.

### FR5 — Safety Validation

The system must validate user input and model output and detect known prompt-injection patterns.

### FR6 — Human Approval

Potentially consequential operations must stop at an approval boundary until a human explicitly approves them.

### FR7 — Auditability

Important tool operations must produce audit information that can be used for debugging and review.

### FR8 — State Persistence

Conversation state must be associated with a session/thread and support checkpoint-based recovery.

---

## 3.2 Non-Functional Requirements

| Requirement                       |      Target |
| --------------------------------- | ----------: |
| Policy answer accuracy            |       ≥ 90% |
| Source attribution                |       ≥ 90% |
| P50 latency                       | ≤ 2 seconds |
| P95 latency                       | ≤ 5 seconds |
| Cost/query                        |     ≤ $0.01 |
| Prompt-injection resistance       |       ≥ 95% |
| Risky-action approval enforcement |        100% |
| Audit coverage                    |        100% |

These are acceptance targets. Actual measured performance must be reported separately and should not be assumed from the target values.

---

# 4. High-Level Architecture

```text
                         ┌──────────────────────┐
                         │      User            │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Streamlit UI / API   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    Input Safety      │
                         │ Validation +         │
                         │ Injection Detection  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    LangGraph Agent   │
                         │      Workflow        │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       Router         │
                         └──────┬─────┬─────────┘
                                │     │
                    ┌───────────┘     └──────────────┐
                    ▼                                ▼
          ┌──────────────────┐             ┌──────────────────┐
          │ search_documents │             │ Risky Tool       │
          │                  │             │                  │
          │ Chroma +         │             │ Update employee  │
          │ embeddings       │             │ Delete employee  │
          └────────┬─────────┘             │ Send email       │
                   │                       └────────┬─────────┘
                   ▼                                │
          ┌──────────────────┐                       ▼
          │ Policy Documents │             ┌──────────────────┐
          │ HR / Company /   │             │ Approval Queue   │
          │ IT               │             └────────┬─────────┘
          └──────────────────┘                      │
                                                    ▼
                                           ┌──────────────────┐
                                           │ Human Approval   │
                                           └──────────────────┘

                  ┌─────────────────────────────────────────┐
                  │ Audit Logs / Checkpoints / Metrics     │
                  └─────────────────────────────────────────┘
```

---

# 5. Component Design

## 5.1 Streamlit UI

The Streamlit application provides an interactive interface for users to submit questions and inspect agent activity.

The UI exposes information such as:

* Answer.
* Sources cited.
* Tools used.
* Session/thread state.
* Relevant execution information.

The UI is an interaction layer only. Business logic remains inside the `app` package.

Primary module:

```text
app/ui.py
```

---

## 5.2 FastAPI

The FastAPI service provides a programmatic interface to the agent.

Primary endpoints:

```text
GET  /health
POST /chat
```

The chat response contains fields such as:

* `request_id`
* `thread_id`
* `answer`
* `sources`
* `tools_used`
* `trace`

This separation allows the same agent logic to be accessed through a UI or an external client.

---

## 5.3 LangGraph Agent

LangGraph manages the agent workflow and state transitions.

The state contains information such as:

* Session ID.
* User question.
* Conversation history.
* Selected tool.
* Generated answer.
* Sources.
* Tools used.
* Execution trace.

The graph provides a structured execution model instead of allowing arbitrary application flow inside a single model call.

---

## 5.4 Router

The router determines the intended operation.

Current conceptual routing categories are:

```text
search_documents
update_employee_record
no_tool
```

The router is responsible for identifying the requested operation, but it is **not the authorization mechanism**.

For example, if the router identifies an employee-record update, the graph should send the operation toward the approval gate rather than directly executing the update.

This distinction is important:

> Routing decides what the user appears to be requesting; authorization decides whether that action may execute.

---

# 6. Retrieval Architecture

## 6.1 Source Documents

The initial knowledge base contains company policy documents such as:

```text
data/
├── hr_policy.pdf
├── company_policy.pdf
└── it_policy.pdf
```

The documents represent the controlled knowledge source for policy answers.

---

## 6.2 Ingestion Pipeline

The ingestion pipeline performs:

```text
PDF
 ↓
PyPDFLoader
 ↓
Document text
 ↓
RecursiveCharacterTextSplitter
 ↓
Chunks
 ↓
Local embedding model
 ↓
Chroma
```

Current chunk configuration:

```text
chunk_size: 800
chunk_overlap: 150
```

The embedding model is:

```text
sentence-transformers/all-MiniLM-L6-v2
```

The Chroma collection is:

```text
capstone_documents
```

The configured retrieval depth is approximately:

```text
k = 4
```

---

## 6.3 Why Local Embeddings

The design uses a local Hugging Face embedding model rather than a hosted embedding API.

Benefits include:

* Reduced external dependency.
* No embedding API cost.
* Better control over document processing.
* Easier local development.
* Compatibility with the Dockerized application.

The trade-off is that local inference consumes application resources and embedding quality must be validated against the evaluation set.

---

# 7. Safety and Human-in-the-Loop Design

Safety is implemented as multiple layers rather than a single prompt instruction.

## 7.1 Input Validation

The system validates incoming requests before normal agent execution.

This provides an early boundary against malformed or prohibited requests.

---

## 7.2 Prompt-Injection Detection

The system attempts to detect requests designed to manipulate the instruction hierarchy or cause the agent to ignore its intended task.

Examples include requests to:

* Ignore previous instructions.
* Reveal hidden prompts.
* Bypass approval controls.
* Execute unauthorized operations.

Detection is treated as a guardrail, not a guarantee.

---

## 7.3 Output Validation

Generated output is checked before it is returned to the user.

This reduces the chance that an unsafe or invalid response bypasses the application's safety layer.

---

## 7.4 Approval Gate

The most important control is the approval boundary around risky tools.

Current risky operations include:

```text
update_employee_record
delete_employee_record
send_email
```

These operations must not execute merely because the model selected the tool.

The intended flow is:

```text
User request
     ↓
Router
     ↓
Risky operation identified
     ↓
Approval request created
     ↓
PENDING
     ↓
Human decision
   ↙       ↘
REJECTED   APPROVED
              ↓
           Execute
              ↓
          EXECUTED
```

This provides a deterministic authorization boundary independent of model behavior.

---

# 8. Audit and Observability

The system records important execution events through the audit layer.

Audit information can include:

* Request ID.
* Tool name.
* Operation.
* Status.
* Relevant metadata.
* Success/failure information.

This allows engineers to investigate:

* Which tool was selected.
* Whether a risky action was attempted.
* Whether approval was requested.
* Whether execution occurred.
* Where an agent request failed.

The application also exposes execution information through API responses and UI sections such as tools used and sources cited.

---

# 9. Checkpointing and State Management

The agent uses LangGraph checkpointing to preserve state across requests.

A thread identifier associates a conversation with its stored state.

Conceptually:

```text
User
 ↓
thread_id
 ↓
LangGraph
 ↓
Checkpoint
 ↓
Conversation state
```

This enables the system to recover and continue a conversation rather than treating every request as completely independent.

SQLite checkpointing is used for the current implementation.

For a larger production deployment, the checkpoint backend should be reconsidered based on concurrency, durability, backup, and operational requirements.

---

# 10. Async Execution

The project includes asynchronous tool execution.

Two execution approaches are measured:

```text
Sequential:
Tool A → Tool B → Tool C

Parallel:
Tool A ─┐
Tool B ─┼→ Results
Tool C ─┘
```

Independent operations can be executed concurrently when there are no dependencies between them.

The benchmark records:

* Sequential latency.
* Parallel latency.
* Latency reduction.
* Speedup.
* Total asynchronous execution time.

Parallelism should not be applied blindly to state-changing operations. Operations with ordering, authorization, or data-dependency requirements should remain controlled.

---

# 11. Model Configuration

The application uses Groq as the model provider through an OpenAI-compatible interface.

The model configuration separates normal, large, and safety workloads.

Conceptually:

```text
GROQ_MODEL
GROQ_LARGE_MODEL
GROQ_SAFETY_MODEL
```

The intended model-routing strategy is:

```text
Normal request
     ↓
Small/default model
     ↓
Success → return result

Failure / escalation condition
     ↓
Large model
     ↓
Return result or controlled error
```

This allows the system to use a smaller model for routine requests while reserving the larger model for cases requiring escalation.

The application should record which model handled each request if model-level cost and quality analysis is required.

---

# 12. Deployment Architecture

The application is containerized using Docker.

Current deployment components include:

```text
Dockerfile
docker-compose.yml
```

The application container runs the FastAPI server with Uvicorn.

Conceptually:

```text
Docker Compose
      │
      ▼
Company Policy Agent
      │
      ├── FastAPI
      ├── LangGraph
      ├── RAG
      ├── Chroma
      └── Checkpoints
```

Persistent volumes are used for application data that should survive container recreation.

The service includes a healthcheck against:

```text
/health
```

---

# 13. Testing Strategy

Testing is divided into several areas.

## Unit Tests

Individual components should be tested independently.

Examples include:

* LLM configuration.
* Router behavior.
* Safety functions.
* Approval logic.
* Audit logging.
* Async tools.

## Integration Tests

Integration tests verify interactions between components.

Examples:

* Agent → router.
* Router → tool.
* Risky tool → approval gate.
* Agent → checkpoint.
* API → agent.

## Safety Tests

Safety tests verify:

* Prompt-injection handling.
* Input validation.
* Output validation.
* Approval enforcement.
* Rejection behavior.

## Regression Tests

The evaluation set should be used to detect regressions in:

* Answer correctness.
* Retrieval.
* Source attribution.
* Routing.
* Safety behavior.

---

# 14. Evaluation Strategy

A fixed evaluation set should be created before final system evaluation.

The intended evaluation set contains **30 cases** spanning:

* HR questions.
* IT questions.
* Corporate policy questions.
* Retrieval cases.
* Source attribution.
* Ambiguous requests.
* Unsupported questions.
* Prompt-injection attempts.
* Risky operations.

Each case should define the expected behavior.

Example:

```text
ID: HR-001
Category: HR
Question: What is the leave policy?
Expected tool: search_documents
Expected source: hr_policy.pdf
```

Evaluation should compare expected and actual behavior rather than relying only on subjective inspection.

Important metrics include:

```text
Answer accuracy
Source accuracy
Tool-routing accuracy
Prompt-injection resistance
Approval enforcement
P50 latency
P95 latency
Cost/query
```

The evaluation system must distinguish between a target and a measured result.

For example:

> Target answer accuracy ≥ 90%

does not mean:

> The system currently achieves 90%.

The actual measurement should come from the evaluation run.

---

# 15. Known Limitations

## 15.1 Limited Knowledge Base

The agent can only reliably answer questions covered by the documents available to its retrieval system.

Adding documents does not automatically guarantee better answers; document quality and retrieval quality must also be evaluated.

---

## 15.2 Retrieval Errors

RAG is not guaranteed to retrieve the correct document or chunk for every question.

The evaluation data should therefore test retrieval independently from answer generation.

---

## 15.3 Model Hallucination

Even with retrieved context, a language model can produce unsupported claims.

Source attribution and output validation reduce this risk but do not eliminate it.

---

## 15.4 Prompt-Injection Detection

Prompt-injection detection is a defense layer rather than a formal security proof.

Attack patterns can evolve, so the safety evaluation set must be continuously expanded.

---

## 15.5 SQLite Checkpointing

SQLite is suitable for the current project and development deployment.

A high-concurrency production environment may require a more scalable checkpoint/state backend.

---

## 15.6 Heuristic Routing

Keyword or rule-based routing can misclassify ambiguous requests.

Future versions should evaluate routing accuracy systematically and consider stronger classification or model-assisted routing where justified.

---

# 16. Failure Handling

The system should fail safely rather than silently executing uncertain actions.

Expected failure behavior includes:

| Failure                   | Expected behavior                              |
| ------------------------- | ---------------------------------------------- |
| Retrieval failure         | Return controlled error/no-answer response     |
| LLM failure               | Retry or escalate according to routing policy  |
| Safety validation failure | Block request                                  |
| Prompt injection detected | Reject or safely contain request               |
| Risky action              | Require approval                               |
| Approval rejected         | Do not execute                                 |
| Tool failure              | Record failure and return controlled response  |
| Checkpoint failure        | Log error and avoid pretending state was saved |
| API failure               | Return appropriate HTTP error                  |
| Missing source            | Do not invent citation                         |

---

# 17. Security Considerations

The system follows a defense-in-depth model.

Important principles:

### Least privilege

Tools should have only the permissions required for their intended operation.

### Explicit authorization

Tool selection is not authorization.

### Human approval

High-impact operations require explicit approval.

### Secrets management

API keys and credentials must remain outside source code and should be supplied through environment configuration or an appropriate secret-management mechanism.

### Auditability

Sensitive operations must be traceable.

### Input/output validation

Both incoming requests and generated responses require validation.

### No autonomous destructive actions

The agent should not bypass the approval workflow.

---

# 18. Implementation Status

The current implementation includes the following major capabilities:

| Component                  | Status      |
| -------------------------- | ----------- |
| Policy document ingestion  | Implemented |
| Local embeddings           | Implemented |
| Chroma retrieval           | Implemented |
| Document search tool       | Implemented |
| Router                     | Implemented |
| LangGraph agent            | Implemented |
| Safety validation          | Implemented |
| Prompt-injection detection | Implemented |
| Risky tools                |             |
