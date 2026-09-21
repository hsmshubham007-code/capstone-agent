# Signed-Off Success Metrics & Human-in-the-Loop Boundary

## Project

**Company Policy Agent**

**Project:** `week2day5proj1`

---

# 1. Purpose

This document defines the measurable success criteria and human-in-the-loop boundaries agreed upon for the Company Policy Agent.

The purpose is to ensure that the system is evaluated using measurable targets rather than subjective statements such as "the system should be fast" or "the answers should be accurate."

---

# 2. Signed-Off Success Metrics

The following targets are proposed as the project acceptance criteria.

| Metric                         |          Target | Measurement                                             |
| ------------------------------ | --------------: | ------------------------------------------------------- |
| Policy answer accuracy         |       **≥ 90%** | Correct answers / total evaluated questions             |
| Source attribution             |       **≥ 90%** | Answers with correct supporting policy sources          |
| p50 latency                    | **≤ 2 seconds** | Median end-to-end response latency                      |
| p95 latency                    | **≤ 5 seconds** | 95th-percentile end-to-end response latency             |
| Cost per query                 |     **≤ $0.01** | Estimated model/API cost per request                    |
| Prompt-injection resistance    |       **≥ 95%** | Percentage of injection tests correctly blocked/handled |
| High-risk approval enforcement |        **100%** | All defined risky actions require human approval        |
| Audit coverage                 |        **100%** | High-risk requests generate an audit record             |

> **Note:** These targets are project acceptance targets and should be confirmed by the stakeholder and mentor before being treated as final production requirements.

---

# 3. Primary Success Metric

The primary functional success metric is:

> **At least 90% of evaluated company-policy questions must receive a correct answer.**

The evaluation dataset should contain representative questions covering the supported policy categories, such as:

* HR policy
* IT policy
* Company policy

The pass rate is calculated as:

```text
Pass Rate = Correct Answers / Total Evaluated Questions × 100
```

Example:

```text
90 correct answers
------------------ × 100 = 90%
100 total questions
```

---

# 4. Latency Requirement

The system should provide responses within an acceptable time.

The target is:

```text
p50 latency ≤ 2 seconds
p95 latency ≤ 5 seconds
```

This means the system should be responsive for normal users while also limiting unusually slow requests.

Latency should be measured from the beginning of the request until the final response is returned.

---

# 5. Cost Requirement

The target cost is:

```text
Maximum cost per query ≤ $0.01
```

The project should also track projected cost at different usage volumes.

Example:

```text
10,000 queries/month × $0.01
= $100/month maximum model cost
```

Actual cost should be measured using the model/API pricing applicable to the deployed configuration.

---

# 6. Source Attribution Requirement

Because the system answers questions using company policy documents, the response should identify the supporting sources.

Target:

```text
≥ 90% of evaluated policy answers
must provide the correct supporting source(s).
```

This helps users verify where the answer came from.

---

# 7. Prompt-Injection Safety Requirement

The system should be tested against prompt-injection attempts.

Target:

```text
≥ 95% of defined prompt-injection tests
must be correctly blocked or safely handled.
```

The evaluation should include examples attempting to:

* Override system instructions
* Bypass safety controls
* Access unauthorized information
* Force unauthorized tool execution
* Circumvent approval requirements

---

# 8. Human-in-the-Loop Boundary

The following boundary is agreed for the system:

> **The AI may retrieve information, answer policy questions, and prepare proposed actions. It must not independently execute defined high-risk or destructive actions. Those actions require explicit human approval before execution.**

---

# 9. Actions That Do Not Require Approval

The following activities can be performed automatically:

```text
✓ Search authorized policy documents
✓ Retrieve relevant document sections
✓ Answer policy questions
✓ Provide supporting sources
✓ Summarize policy information
✓ Prepare a proposed action for human review
```

These activities are informational or reversible and do not directly modify sensitive records.

---

# 10. Actions That Require Human Approval

The following actions require explicit human approval:

```text
✗ Update employee records
✗ Delete employee information
✗ Perform destructive operations
✗ Send sensitive emails or communications
✗ Execute other defined high-risk actions
```

The approval workflow is:

```text
User Request
     ↓
AI identifies risky action
     ↓
Approval Request Created
     ↓
Status = PENDING
     ↓
Human Reviews Request
     ↓
   ┌───────────────┐
   ↓               ↓
APPROVED         REJECTED
   ↓               ↓
Execute          Block
   ↓
Record Execution
```

---

# 11. Approval States

The approval system uses explicit states.

| State      | Meaning                       |
| ---------- | ----------------------------- |
| `PENDING`  | Waiting for human decision    |
| `APPROVED` | Human has approved the action |
| `REJECTED` | Human has rejected the action |
| `EXECUTED` | Approved action was executed  |

An action must not execute while it is in the `PENDING` or `REJECTED` state.

---

# 12. Audit Requirement

Every high-risk request should be traceable.

The system should record information such as:

* Request ID
* Tool/action requested
* Request status
* Approval decision
* Execution status
* Relevant timestamps

Target:

```text
100% of high-risk requests
must have an audit record.
```

---

# 13. Example: Employee Record Update

### User request

```text
"Update the employee's salary to ₹80,000."
```

The system should **not** immediately execute the change.

Instead:

```text
User Request
     ↓
Router identifies employee-record update
     ↓
Approval request created
     ↓
Human reviews proposed change
     ↓
APPROVE / REJECT
```

If approved:

```text
APPROVED
   ↓
Execute update
   ↓
Record execution in audit log
```

If rejected:

```text
REJECTED
   ↓
Do not execute
   ↓
Record rejection
```

---

# 14. Stakeholder Sign-Off

The stakeholder should review and confirm the following:

### Success Metrics

* [ ] ≥ 90% policy answer accuracy
* [ ] ≥ 90% correct source attribution
* [ ] p50 latency ≤ 2 seconds
* [ ] p95 latency ≤ 5 seconds
* [ ] Cost per query ≤ $0.01
* [ ] ≥ 95% prompt-injection test pass rate
* [ ] 100% high-risk actions require approval
* [ ] 100% high-risk requests are audited

### Human-in-the-Loop

* [ ] Policy search can be automated.
* [ ] Policy question answering can be automated.
* [ ] Source retrieval can be automated.
* [ ] High-risk employee-record changes require approval.
* [ ] Destructive actions require approval.
* [ ] Sensitive communication requires approval.
* [ ] Rejected actions must not execute.
* [ ] Approved actions must be auditable.

---

# 15. Sign-Off

## Intern

**Name:** ______________________________

**Signature:** ___________________________

**Date:** _______________________________

## Stakeholder

**Name:** ______________________________

**Role:** _______________________________

**Signature:** ___________________________

**Date:** _______________________________

---

# 16. Final Agreement

By signing this document, the intern and stakeholder confirm that:

1. The success criteria are measurable.
2. The numerical targets are understood.
3. The evaluation method is understood.
4. The human-in-the-loop boundary is clearly defined.
5. High-risk actions require explicit human approval.
6. High-risk actions must be auditable.
7. The AI system must not bypass the agreed approval boundary.

---

## Summary

```text
SUCCESS
    ↓
≥ 90% answer accuracy
≥ 90% source attribution
p50 ≤ 2 seconds
p95 ≤ 5 seconds
≤ $0.01/query
≥ 95% injection-test pass rate

SAFETY BOUNDARY
    ↓
Informational tasks → Automated
        ↓
High-risk actions → Human approval
        ↓
Approved → Execute + Audit
Rejected → Block + Audit
```
