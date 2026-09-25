# Sprint Board - Company Policy Agent

## Project

**Project:** Company Policy Agent  
**Repository:** `week2day5proj1`  
**Goal:** Build and production-harden a policy-focused AI agent with RAG, safety guardrails, approval workflows, audit logging, evaluation gates, deployment, monitoring, and complete handover documentation.

---

## Sprint Goal

Deliver a production-oriented Company Policy Agent that:

- Answers company-policy questions using retrieved documents.
- Routes questions to the appropriate tool or no-tool path.
- Uses ChromaDB with local Hugging Face embeddings for retrieval.
- Protects against prompt injection.
- Prevents risky actions from executing without human approval.
- Maintains an audit trail for tool and approval activity.
- Supports durable LangGraph checkpoints.
- Runs through FastAPI and Docker.
- Provides health and readiness checks.
- Includes automated evaluation and build-quality gates.
- Documents limitations, failure modes, deployment, handover, and lessons learned.

---

# Scope Decision

## In Scope

The final implementation scope includes:

- Company policy RAG
- ChromaDB retrieval
- Hugging Face embeddings
- LangGraph agent routing
- Groq-hosted OpenAI-compatible LLMs
- Prompt-injection detection
- Input and output validation
- Risky-tool approval workflow
- Approval states:
  - `PENDING`
  - `REJECTED`
  - `APPROVED`
  - `EXECUTED`
- Audit logging
- LangGraph checkpointing
- FastAPI API
- Streamlit UI
- Docker deployment
- Health and readiness endpoints
- Evaluation suite
- Evaluation build gate
- Latency and cost reporting
- Security/dependency audit documentation
- Production documentation
- Failure-mode documentation
- Handover documentation
- Final report
- Retrospective
- Demonstration and stakeholder feedback capture

## Out of Scope

The following are intentionally outside the final implementation scope:

- Production multi-user distributed approval storage
- External approval service
- Fully distributed audit infrastructure
- Enterprise identity and access management
- Production cloud infrastructure provisioning
- Adaptive/continuous red-team testing
- Large-scale evaluation datasets
- Guaranteed elimination of third-party dependency vulnerabilities
- Automatic execution of risky operations without human approval

## Scope Rule

The implementation scope is considered frozen.

Remaining work should follow a **fix-and-document** approach:

1. Fix verified defects that block a stated requirement.
2. Document accepted limitations honestly.
3. Avoid introducing new features unless required to satisfy the project requirements.

---

# Sprint Status

| Work Item | Status | Evidence |
|---|---|---|
| Project architecture | ✅ Complete | Agent, RAG, safety, approval, audit, API, UI |
| Real policy data | ✅ Complete | HR, company, and IT policy documents |
| RAG implementation | ✅ Complete | ChromaDB + Hugging Face embeddings |
| Agent routing | ✅ Complete | Routing evaluation |
| Prompt-injection protection | ✅ Complete | Injection evaluation |
| Risky-tool approval workflow | ✅ Complete | Approval lifecycle verified |
| Audit logging | ✅ Complete | `audit_logs/audit.jsonl` |
| Durable checkpointing | ✅ Complete | LangGraph SQLite checkpointing |
| FastAPI API | ✅ Complete | `/chat`, `/health`, `/ready`, `/metrics` |
| Streamlit UI | ✅ Complete | Company Policy Agent UI |
| Docker deployment | ✅ Complete | Docker Compose deployment verified |
| Production health check | ✅ Complete | `/health` returned healthy |
| Production readiness check | ✅ Complete | `/ready` returned ready |
| Automated tests | ✅ Complete | 41 tests passed |
| Ruff quality gate | ✅ Complete | All checks passed |
| Routing evaluation | ✅ Complete | 32/32 passed |
| Retrieval evaluation | ✅ Complete | Top-2: 4/4 |
| Injection evaluation | ✅ Complete | 5/5 blocked |
| Evaluation build gate | ✅ Complete | All evaluation gates passed |
| Evaluation/cost reporting | ✅ Complete | Charts and projected cost report |
| Failure-mode documentation | ✅ Complete | `FAILURE_MODES.md` |
| Sprint scope decision | ✅ Complete | This document |
| Handover Pack | ✅ Complete | `HANDOVER_PACK.md` |
| Independent unaided run | ✅ Complete | Fresh tests, Ruff, evaluation, health/readiness |
| Final report | ✅ Complete | `FINAL_REPORT.md` |
| Retrospective | ✅ Complete | `RETROSPECTIVE.md` |
| Demo evidence | ✅ Complete | `DEMO_AND_FEEDBACK.md` |
| Stakeholder feedback | ⏳ Pending | Awaiting actual stakeholder feedback |
| PR raised | ⏳ Pending | GitHub PR still required |
| PR review | ⏳ Pending | Reviewer comments/review still required |
| Final PR comments addressed | ⏳ Pending | Depends on PR review |

---

# Verification Evidence

## Automated Tests

Latest test run:

```text
41 passed
1 warning