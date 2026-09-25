# Project Retrospective - Company Policy Agent

## 1. Overview

This retrospective records the main mistakes, unexpected problems, and lessons from developing and production-hardening the Company Policy Agent.

The purpose is not to present the project as error-free. The project improved because several problems were discovered through testing, evaluation, deployment, and verification.

---

## 2. Mistake 1 - Treating Retrieval Quality as an Implementation Detail

### What happened

The initial retrieval evaluation showed that Top-1 retrieval did not always return the most relevant policy document.

The retrieval evaluation produced:

* Top-1: 3/4 relevant in-scope cases
* Top-2: 4/4 relevant in-scope cases
* Top-3: 4/4 relevant in-scope cases

One IT-policy case demonstrated that the relevant document appeared at rank 2 rather than rank 1.

### Why it mattered

A RAG system can produce a fluent answer even when the retrieved evidence is not optimal. Without measuring retrieval independently, it would have been easy to assume that the RAG layer was working simply because the final answers looked reasonable.

### What changed

The production retrieval configuration was set to Top-2 rather than Top-1.

### Lesson

**Measure retrieval quality separately from final answer quality.**

Future RAG projects should evaluate retrieval before spending significant time tuning agent prompts or response formatting.

---

## 3. Mistake 2 - Running the Evaluation Script the Wrong Way

### What happened

The evaluation script initially failed when executed directly:

```text
python evals/evaluate_routing.py
```

The application package was not resolved correctly and produced:

```text
ModuleNotFoundError: No module named 'app'
```

### Why it happened

The evaluation code expected the project to be executed as a Python module from the repository root.

### What changed

The correct command became:

```text
python -m evals.evaluate_routing
```

### Lesson

**Execution context is part of reproducibility.**

A script that works only under a particular working directory or module invocation should document the required execution method clearly.

This was incorporated into the Handover Pack.

---

## 4. Mistake 3 - Testing Approval Execution with Incomplete Arguments

### What happened

The first manual approval-execution test attempted to execute an employee-record update without providing the required `field` argument.

The operation therefore failed with a missing argument error.

### Why it mattered

The approval state machine itself was working, but the test data did not match the actual risky-tool function signature.

This demonstrated that testing only the approval status transitions was insufficient. The final execution step also needed realistic tool arguments.

### What changed

The test was repeated using the correct arguments:

* `employee_id`
* `field`
* `new_value`

The complete lifecycle then succeeded:

```text
PENDING
   |
   v
APPROVED
   |
   v
EXECUTED
```

The audit trail also showed the approval and execution events.

### Lesson

**Test the complete workflow with valid end-to-end inputs.**

State-machine tests should verify both state transitions and the real operation executed at the final state.

---

## 5. Mistake 4 - Hitting the Provider Rate Limit During Evaluation

### What happened

A large evaluation run encountered a Groq rate limit on the configured small model.

The provider reported that the token-per-day limit had effectively been reached.

### Why it mattered

The application logic itself was not necessarily failing, but the external dependency prevented the evaluation from completing normally.

This demonstrated that evaluation infrastructure also needs to account for provider limits.

### What changed

Evaluation was rerun with appropriate rate-limit handling and after the provider allowance became available.

The final evaluation completed successfully.

### Lesson

**External dependencies must be treated as part of the system's failure surface.**

Production evaluation should record provider failures separately from application-quality failures so that a rate-limit event is not incorrectly interpreted as a retrieval or routing regression.

---

## 6. Mistake 5 - Underestimating Cold-Start Latency

### What happened

The first embedding/model initialization was significantly slower than subsequent warm requests.

The production startup logs showed a long embedding initialization period before the application became ready.

### Why it mattered

Without separating cold and warm performance, the latency numbers could have been misleading.

### What changed

The application added startup retrieval/embedding warm-up, and the evaluation process measures warm latency separately.

The final evaluation gate reported a warm P95 latency of approximately 1080 ms.

### Lesson

**Latency needs operational context.**

For systems using local ML models or large initialization steps, cold-start and warm-request latency should be measured separately.

---

## 7. Mistake 6 - Assuming an Approval Queue Could Be Shared Across Processes

### What happened

The approval queue was implemented as an in-memory structure.

During verification, an approval created in one application process could not be resolved from a separate Python process.

### Why it mattered

This exposed an important production limitation: process-local state is not suitable for a multi-process or multi-replica approval workflow.

### What changed

The limitation was documented rather than hidden because replacing the approval queue with persistent infrastructure would expand the current project scope.

### Lesson

**State ownership must be explicit in production architecture.**

For a larger deployment, approval state should be stored in persistent shared storage and exposed through an appropriate approval API or workflow service.

---

## 8. What Went Well

Several engineering decisions produced useful results.

### Automated gates

The evaluation suite became a release gate rather than a manually reviewed report. This made quality criteria executable.

### Explicit safety boundaries

Risky operations were separated from normal retrieval and protected by human approval.

### Auditability

Tool calls and approval events were recorded, making workflow behavior observable.

### Production verification

The application was tested in its Dockerized environment rather than relying only on local development behavior.

### Documentation of limitations

Known limitations were documented in the README, SECURITY.md, FAILURE_MODES.md, and HANDOVER_PACK.md instead of being presented as solved problems.

---

## 9. What I Would Do Differently

If starting the project again, I would:

1. Define the evaluation dataset before implementing extensive agent logic.
2. Establish retrieval-quality metrics earlier.
3. Design approval state persistence before implementing multi-process deployment.
4. Test tool signatures with complete realistic arguments from the beginning.
5. Add provider-rate-limit handling to evaluation planning earlier.
6. Separate cold-start and warm latency measurements from the first performance test.
7. Create the handover and failure-mode documentation earlier rather than near project completion.

---

## 10. Final Lessons

The most important lessons from the project are:

### Lesson 1

**An agent is a system, not just a model call.**

Reliable behavior requires routing, retrieval, safety, tools, state, observability, and evaluation around the model.

### Lesson 2

**Evaluation should influence architecture.**

The Top-1 versus Top-2 retrieval result directly changed the production retrieval configuration.

### Lesson 3

**Failures are useful engineering evidence.**

The module-path issue, provider rate limit, incomplete approval test arguments, and process-local approval state all exposed assumptions that would otherwise have remained hidden.

### Lesson 4

**Production readiness includes knowing what is not solved.**

A documented limitation is more useful than an unsupported claim that the system is production-safe.

### Lesson 5

**Verification must be repeatable.**

The final project includes documented commands for tests, linting, evaluation, API health, and readiness so another person can verify the system without relying on the original developer.

---

## 11. Closing

The project improved through repeated cycles of implementation, failure, measurement, correction, and verification.

The final result is not presented as a system without limitations. Instead, it provides a documented production-oriented baseline with measurable quality gates, safety controls, auditability, deployment evidence, and a clear record of remaining limitations.
