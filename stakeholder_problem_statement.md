# Stakeholder Problem Statement & Workflow

## Project

**Company Policy Agent**

**Project:** `week2day5proj1`

---

## 1. Stakeholder Discovery

### Stakeholders

| Role                                     | Responsibility                                               |
| ---------------------------------------- | ------------------------------------------------------------ |
| Internal Stakeholder / HR Representative | Explains the current company-policy workflow and pain points |
| Intern / Developer                       | Documents the problem and builds the AI-assisted workflow    |
| Mentor                                   | Reviews the requirements, constraints, and proposed solution |

---

## 2. Stakeholder Problem Statement

> "Employees frequently ask questions about company policies, such as HR, IT, and general company policies. Currently, HR or another responsible employee has to manually search through multiple policy documents, find the relevant information, read and interpret it, and then prepare a response.
>
> This process is repetitive and takes time, especially when multiple employees ask similar questions. There is also a risk of providing incomplete or incorrect information if the wrong document or section is used.
>
> We need a system that can quickly search the authorized company policy documents, provide an accurate answer, and identify the sources used to generate the answer. Sensitive employee actions should not be performed automatically and must remain under human approval."

---

# 3. Problem Being Solved

The existing company-policy support process relies on manual document searching.

When an employee asks a question, the responsible employee must:

1. Understand the question.
2. Identify the relevant policy.
3. Search one or more policy documents.
4. Find the relevant sections.
5. Interpret the information.
6. Write an answer.
7. Send the response to the employee.

This process creates repetitive work and can increase response time.

The project addresses this problem by providing an AI-assisted policy question-answering system that searches authorized company documents and returns answers with supporting sources.

---

# 4. Current Human Workflow

The current workflow is:

```text
Employee asks a policy question
            ↓
HR / responsible employee receives question
            ↓
Identify the relevant policy
            ↓
Search policy documents manually
            ↓
Find relevant sections
            ↓
Read and interpret the policy
            ↓
Write the answer
            ↓
Send answer to employee
```

---

# 5. Problems With the Current Workflow

| Problem                          | Impact                                          |
| -------------------------------- | ----------------------------------------------- |
| Manual document searching        | Takes employee time                             |
| Multiple policy documents        | Relevant information may be difficult to locate |
| Repeated questions               | Creates repetitive work                         |
| Manual interpretation            | Incorrect interpretation is possible            |
| No centralized retrieval process | Different documents may need to be checked      |
| High workload                    | Response time can increase                      |
| Sensitive actions                | Some actions cannot safely be automated         |

---

# 6. AI-Assisted Workflow

The Company Policy Agent changes the repetitive information-retrieval portion of the workflow.

```text
Employee asks question
            ↓
Company Policy Agent
            ↓
Router determines required action
            ↓
Search authorized company documents
            ↓
Retrieve relevant document chunks
            ↓
LLM generates response
            ↓
Return answer + sources + tools used
```

---

# 7. RAG Workflow

The policy-question workflow uses Retrieval-Augmented Generation (RAG).

```text
Policy Documents
      ↓
Document Loading
      ↓
Text Splitting
      ↓
Embeddings
      ↓
Chroma Vector Database
      ↓
Similarity Search
      ↓
Relevant Policy Chunks
      ↓
LLM
      ↓
Answer + Sources
```

The project uses local Hugging Face embeddings:

```text
sentence-transformers/all-MiniLM-L6-v2
```

and Chroma for vector storage.

---

# 8. Documents Used

The policy knowledge base contains company policy documents such as:

* `hr_policy.pdf`
* `company_policy.pdf`
* `it_policy.pdf`

The documents are indexed and retrieved when a user asks a policy-related question.

---

# 9. Tool Routing

The system uses a router to determine which action is appropriate.

The main tool categories include:

| Tool                     | Purpose                                    |
| ------------------------ | ------------------------------------------ |
| `search_documents`       | Search company policy documents            |
| `update_employee_record` | Request an employee-record update          |
| `no_tool`                | Handle requests that do not require a tool |

The router should send risky operations toward the approval workflow rather than executing them directly.

---

# 10. Human-in-the-Loop

Not every action should be automated.

The system includes an approval workflow for risky operations.

```text
User requests risky action
            ↓
System creates approval request
            ↓
Approval status = PENDING
            ↓
Human reviews request
            ↓
       ┌────┴────┐
       ↓         ↓
    APPROVE    REJECT
       ↓         ↓
    Execute    Block
```

Examples of risky actions include:

* Updating employee records
* Deleting information
* Sending email
* Other sensitive or potentially irreversible operations

Policy document searching does not require approval.

---

# 11. Safety Requirements

The system includes safety controls around the agent.

The safety workflow includes:

```text
User Input
    ↓
Input Validation
    ↓
Prompt-Injection Detection
    ↓
Agent / Tool Execution
    ↓
Output Validation
    ↓
Response
```

The system also records audit information for relevant tool calls.

---

# 12. Audit Trail

High-risk operations should be auditable.

The project includes:

* Request IDs
* Tool-call records
* Approval status
* Execution status
* Audit logs

Example flow:

```text
Request
   ↓
Request ID generated
   ↓
Tool call recorded
   ↓
Approval requested
   ↓
Human decision recorded
   ↓
Execution recorded
```

This provides traceability for sensitive operations.

---

# 13. Async Tool Execution

The project also evaluates asynchronous tool execution.

Where multiple independent operations can be performed concurrently:

```text
                 ┌── Tool A
User Request ────┼── Tool B
                 └── Tool C
```

can be executed in parallel rather than:

```text
User Request
     ↓
Tool A
     ↓
Tool B
     ↓
Tool C
```

The project measures:

* Parallel latency
* Sequential latency
* Latency reduction
* Speedup
* Total async latency

---

# 14. Persistent Conversation State

The agent uses LangGraph checkpointing to maintain conversation state.

The workflow can preserve information associated with a conversation thread.

```text
User Session
     ↓
Thread ID
     ↓
LangGraph State
     ↓
Checkpoint
     ↓
Resume Conversation
```

This supports durable agent workflows rather than treating every request as completely independent.

---

# 15. User Interface

The project provides a Streamlit interface called:

**Company Policy Agent**

The UI exposes information such as:

* Agent answer
* Tools used
* Sources cited
* Session/thread information
* Async performance metrics

This makes the system behavior more transparent to the user.

---

# 16. API Workflow

The production version also exposes a FastAPI service.

Example workflow:

```text
Client
  ↓
FastAPI
  ↓
Agent / LangGraph
  ↓
Router
  ↓
Tools / RAG
  ↓
LLM
  ↓
Response
```

The API includes endpoints such as:

```text
GET  /health
POST /chat
```

The chat response includes information such as:

* `request_id`
* `thread_id`
* `answer`
* `sources`
* `tools_used`
* `trace`

---

# 17. Model and Infrastructure Constraints

The project uses Groq as the model API provider.

The model configuration includes:

```text
GROQ_MODEL
GROQ_LARGE_MODEL
GROQ_SAFETY_MODEL
```

The project is designed to use a smaller model for normal requests and a larger model when escalation is required.

The RAG embeddings are generated locally using:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Vector storage uses:

```text
Chroma
```

---

# 18. Production Constraints

The production system should satisfy the following categories of requirements.

| Category      | Requirement                                                          |
| ------------- | -------------------------------------------------------------------- |
| Accuracy      | Policy answers should be evaluated against a test/evaluation dataset |
| Latency       | Measure p50 and p95 response latency                                 |
| Cost          | Track cost per query and projected monthly cost                      |
| Safety        | Test resistance to prompt injection                                  |
| Data          | Restrict retrieval to authorized company documents                   |
| Human control | Require approval for risky operations                                |
| Auditability  | Record important requests and tool actions                           |
| Reliability   | Provide health checks and automated tests                            |
| Deployment    | Support containerized deployment                                     |
| Quality       | Run linting, tests, and security checks before deployment            |

---

# 19. Success Metrics

The following metrics can be used to evaluate the system:

### Accuracy

Measure the percentage of questions answered correctly.

```text
Pass Rate = Correct Answers / Total Questions × 100
```

Accuracy should also be examined by query type, such as:

* HR
* IT
* Company policy
* Other supported categories

---

### Latency

Measure:

```text
p50 latency
p95 latency
```

This helps distinguish typical performance from slower requests.

---

### Cost

Track:

```text
Cost per query
Current monthly cost
Projected monthly cost
```

This is particularly important when comparing small-model and large-model routing.

---

### Safety

Evaluate:

* Prompt-injection resistance
* Tool authorization
* Approval enforcement
* Output validation
* Risky-action blocking

---

### Reliability

Measure:

* Test pass rate
* API health
* Tool execution failures
* LLM failures
* Retrieval failures

---

# 20. What Must Never Be Automatically Executed

The system should not automatically perform sensitive operations without the required approval.

Examples:

```text
✗ Delete employee information
✗ Change sensitive employee records
✗ Perform destructive operations
✗ Send sensitive communication without approval
```

Instead:

```text
AI proposes
    ↓
Human reviews
    ↓
Human approves/rejects
    ↓
System executes only after approval
```

---

# 21. Problem → Requirement → Solution

The project follows this progression:

| Stage          | Project Example                                                       |
| -------------- | --------------------------------------------------------------------- |
| Problem        | Employees and HR staff spend time manually searching policy documents |
| Requirement    | Provide fast, accurate, source-based policy answers                   |
| Constraint     | Sensitive actions must remain under human control                     |
| Success Metric | Measure accuracy, latency, cost, safety, and reliability              |
| Solution       | RAG-based Company Policy Agent                                        |
| Safety         | Guardrails + approval gates + audit trail                             |
| Production     | FastAPI + Docker + tests + monitoring/evaluation                      |

---

# 22. Final Workflow

The overall project can be represented as:

```text
Stakeholder Problem
        ↓
Manual Policy Search
        ↓
Define Requirements
        ↓
Define Constraints
        ↓
Build RAG System
        ↓
Add Tool Routing
        ↓
Add Safety Guardrails
        ↓
Add Human Approval
        ↓
Add Audit Trail
        ↓
Add LangGraph Checkpointing
        ↓
Add Async Execution
        ↓
Add API + Docker Deployment
        ↓
Evaluate Accuracy / Cost / Latency / Safety
        ↓
Production-Ready Company Policy Agent
```

---

# 23. Stakeholder Validation Checklist

Before considering the problem definition complete:

* [ ] Stakeholder confirms the problem statement.
* [ ] Current human workflow is accurate.
* [ ] Repetitive manual work is clearly identified.
* [ ] AI's role is clearly defined.
* [ ] Human-in-the-loop boundaries are documented.
* [ ] Sensitive actions are identified.
* [ ] Accuracy requirements are measurable.
* [ ] Latency requirements are measurable.
* [ ] Cost requirements are measurable.
* [ ] Safety requirements are measurable.
* [ ] Evaluation criteria are defined.
* [ ] Mentor has reviewed the requirements.

---

# 24. Key Principle

> **The Company Policy Agent is not designed simply to demonstrate an LLM. It is designed to assist an existing company-policy workflow by reducing repetitive document searching while preserving source attribution, safety controls, human approval for risky actions, and measurable evaluation.**

The project follows:

```text
Understand the stakeholder
        ↓
Understand the existing workflow
        ↓
Define the problem
        ↓
Define constraints
        ↓
Define measurable success
        ↓
Build the AI system
        ↓
Evaluate it
        ↓
Deploy safely
```
