# Company Policy Agent — Production Demo Script

## 1. Introduction — 30 seconds

> This project is a productionized RAG-based company policy agent.
>
> It uses LangGraph for agent orchestration, ChromaDB for local vector retrieval, Hugging Face embeddings, and Groq-hosted OpenAI-compatible models for generation.
>
> The project also includes durable checkpointing, safety guardrails, approval gates, audit logging, evaluation, cost tracking, runtime monitoring, Docker deployment, and CI quality gates.

---

## 2. Show the Architecture — 45 seconds

Open the architecture diagram and explain:

```text
User
  ↓
FastAPI
  ↓
LangGraph
  ↓
Router
  ↓
search_documents
  ↓
ChromaDB
  ↓
Retrieved policy context
  ↓
Groq LLM
  ↓
Answer + Sources + Trace
  ↓
Metrics
```

Say:

> The important design decision is that the model doesn't directly decide how to execute arbitrary operations.
>
> The router determines which tool is appropriate, retrieval supplies evidence from the company documents, and risky tools are placed behind an approval gate.

---

## 3. Demonstrate the Health Check — 30 seconds

Run:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

Expected:

```text
status   service                version
------   -------                -------
healthy  company-policy-agent   1.1.0
```

Explain:

> The health endpoint confirms that the API process is alive.

Then run:

```powershell
Invoke-RestMethod http://localhost:8000/ready
```

Explain:

> Readiness goes further. It verifies that the important runtime dependencies, including the Groq configuration, Chroma storage, and checkpoint storage, are available.

---

## 4. Demonstrate a Real RAG Request — 60 seconds

Run:

```powershell
$body = @{
    question = "What does the company say about professional conduct?"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri http://localhost:8000/chat `
    -Method Post `
    -ContentType "application/json; charset=utf-8" `
    -Body $body | ConvertTo-Json -Depth 10
```

Point out:

```text
answer
sources
tools_used
request_id
thread_id
trace
```

Explain:

> The router selected `search_documents`.
>
> The retriever found relevant evidence in `hr_policy.pdf` and `company_policy.pdf`.
>
> The LLM then generated the answer from that retrieved context.
>
> The API returns the sources and trace so the request is observable rather than being a black box.

---

## 5. Demonstrate Runtime Monitoring — 45 seconds

Run:

```powershell
Invoke-RestMethod http://localhost:8000/metrics |
    ConvertTo-Json -Depth 10
```

Point out:

```text
chat_requests_success_total
retrieval_success_total
chat_latency
retrieval_latency
llm_latency
prompt_tokens
completion_tokens
total_tokens
cost_per_request_usd
error_rate
```

Explain:

> This gives us application-level observability.
>
> We can see not only whether a request succeeded, but also where the time was spent, how many tokens were consumed, and the estimated request cost.

Mention the live verification:

> In the final live test, the request completed successfully with zero recorded errors, 828 total tokens, and an estimated cost of $0.000151.

---

## 6. Explain the Latency Finding — 45 seconds

Say:

> One useful production finding was that retrieval and model initialization can dominate latency.
>
> The evaluation showed a cold-start request around 21.5 seconds, while warm requests averaged roughly 0.8 seconds.
>
> To address this, the API warms up the embedding model during startup.

Then explain the live request:

> In the live production test, total chat latency was about 7.5 seconds, with approximately 4.36 seconds spent in retrieval and 2.37 seconds in the LLM call.

Important:

> I would not describe this as a final latency target. It is an observed measurement from a small evaluation and a single live request.

---

## 7. Demonstrate Evaluation — 60 seconds

Show:

```text
evals/evaluation_results.json
```

Explain:

> I separated evaluation from the application itself so that changes to prompts, retrieval, routing, or models can be tested systematically.

Show the latest results:

```text
5 cases
5 passed
0 failed
0 errors
100% completion
100% source hit rate
```

Then immediately add:

> This is a small five-case evaluation set, so 100% here should not be interpreted as 100% real-world accuracy.

This demonstrates responsible evaluation rather than overclaiming.

---

## 8. Demonstrate Prompt-Injection Testing — 45 seconds

Show:

```text
evals/injection_results.json
```

Explain:

> I also created a separate injection-resistance evaluation covering direct overrides, role overrides, policy bypass attempts, instruction overrides, and system-prompt extraction attempts.

Results:

```text
5/5 passed
0 failed
```

Then say:

> Again, this is evidence against the tested cases, not proof that the system is immune to every possible attack.

---

## 9. Explain Approval Gates — 45 seconds

Show the approval implementation.

Explain:

> Read-only retrieval doesn't require approval.
>
> Potentially destructive operations such as updating employee records, deleting records, or sending email are routed through an approval workflow.

Show:

```text
PENDING
   ↓
APPROVED → EXECUTED

or

PENDING
   ↓
REJECTED
```

Say:

> This separates the agent's ability to propose an action from the ability to actually perform a risky action.

---

## 10. Explain Durable Checkpointing — 30 seconds

Show the LangGraph checkpoint code.

Say:

> Each conversation has a thread ID, and LangGraph checkpointing allows state to persist across requests.
>
> This means the agent can resume conversational state rather than treating every request as completely independent.

---

## 11. Explain CI — 45 seconds

Open:

```text
.github/workflows/ci.yml
```

Explain:

> The project treats prompts, evaluation, and application code as things that should be tested before deployment.

CI checks include:

```text
Ruff
pytest
evaluation gate
dependency audit
```

Mention the latest local verification:

```text
Ruff:  passed
Pytest: 40 passed
pip check: no broken requirements
```

---

## 12. Explain Security — 45 seconds

Open:

```text
SECURITY.md
```

Say:

> During dependency auditing, ChromaDB was flagged by several security advisories.
>
> Instead of hiding the result or blindly downgrading, I investigated the affected attack surfaces and documented the remaining dependency as an explicit security exception.
>
> The current architecture uses ChromaDB as local persistent storage and does not expose a standalone Chroma server to untrusted clients.

Then say:

> This is a limitation that needs to be revisited when an appropriate patched release becomes available.

---

## 13. Show Docker — 30 seconds

Run:

```powershell
docker compose ps
```

Expected:

```text
STATUS
Up ... (healthy)
```

Explain:

> The application is packaged as a Docker service with persistent storage for the vector database and checkpoint state.

---

## 14. Final Git Verification — 20 seconds

Run:

```powershell
git status
```

Expected:

```text
nothing to commit, working tree clean
```

Say:

> The final repository is clean and synchronized with the main branch.

---

# Final Interview Summary

End with:

> The main engineering goal wasn't just to make a RAG chatbot answer questions.
>
> I treated the agent as a production system.
>
> That meant investigating retrieval quality, measuring latency and cost, adding safety controls and approval gates, making state durable, adding observability, evaluating prompt-injection resistance, creating CI quality gates, reviewing dependency vulnerabilities, and verifying the deployed service with a real request.
>
> The remaining limitations are explicitly documented, particularly the small evaluation set, cold-start latency, in-memory runtime metrics, modeled cost projections, and the current ChromaDB security exception.
