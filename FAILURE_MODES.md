# Failure Modes and Handling

This table documents the main failure modes identified during development and production verification of the Company Policy Agent.

| Failure mode                      | What happens now                                                                                                                                                                            | Status                       |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- |
| LLM/provider failure              | The application can escalate from the small model to the configured large model when escalation is triggered.                                                                               | Fixed/handled                |
| Provider rate limit               | A request or evaluation can fail when the external provider rate limit is reached.                                                                                                          | Accepted external dependency |
| Prompt injection                  | Detected prompt-injection attempts are blocked before unsafe execution.                                                                                                                     | Fixed/handled                |
| Risky tool request                | Risky operations are stopped at the approval gate until human approval is provided.                                                                                                         | Fixed/handled                |
| Approval rejected                 | The requested action remains rejected and is not executed.                                                                                                                                  | Fixed/handled                |
| Approval state lost after restart | Approval state is stored in memory, so pending approvals are not durable across process restarts or shared across replicas.                                                                 | Accepted limitation          |
| Retrieval miss at Top-1           | A relevant document can appear below the first result. The production configuration uses Top-2 retrieval.                                                                                   | Addressed                    |
| Out-of-scope question             | The system does not rely on unsupported documents when relevant evidence is unavailable.                                                                                                    | Fixed/handled                |
| Cold-start latency                | Initial embedding/model initialization can produce substantially higher latency than warm requests.                                                                                         | Accepted limitation          |
| External LLM latency              | Response time depends on provider latency, network conditions, traffic, and rate limits.                                                                                                    | Accepted external dependency |
| ChromaDB security advisories      | `pip-audit` reports known security advisories for the installed ChromaDB dependency. The application uses local persistent Chroma storage rather than exposing a standalone Chroma service. | Documented exception         |
| Small evaluation dataset          | Current evaluation results provide evidence for the tested cases but do not prove perfect production quality.                                                                               | Accepted limitation          |
| Keyword-based evaluation          | Some evaluation checks use expected keywords or structured rules and may not fully measure semantic answer quality.                                                                         | Accepted limitation          |
| Audit logging                     | Tool calls and approval events are recorded in `audit_logs/audit.jsonl`.                                                                                                                    | Implemented                  |

## Scope Decision

The application feature set is considered frozen at the current project scope.

Remaining work is **fix-and-document only** unless a verification activity identifies a genuine defect that prevents a stated project requirement from being met.

## Evidence

Current verification includes:

* 41 automated tests passed
* Ruff checks passed
* Routing evaluation: 32/32 passed
* Retrieval Top-2 evaluation: 4/4 passed
* Prompt-injection evaluation: 5/5 passed
* Evaluation gate: passed
* Docker container: healthy
* API health check: healthy
* API readiness check: ready
* Approval lifecycle verified through `PENDING → APPROVED → EXECUTED`
* Audit events verified for approval and tool execution

