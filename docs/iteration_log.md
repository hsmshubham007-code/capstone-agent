# Iteration Log — Company Policy Agent

## Project

**Project:** `week2day5proj1`
**System:** Company Policy Agent
**Purpose:** Track the engineering iteration from identified risk to measured result.

---

## Iteration 1 — Retrieval Quality Investigation

### 1. Risk Identified

The highest-risk assumption was **retrieval quality**.

The main concern was whether the RAG system could:

* retrieve relevant policy documents,
* provide evidence for in-scope questions,
* return appropriate sources,
* avoid producing unsupported answers for out-of-scope questions.

The investigation focused on retrieval quality before making changes to the agent architecture.

### 2. Baseline

The baseline system used the existing production RAG pipeline:

1. User question
2. Tool routing
3. `search_documents`
4. Chroma retrieval
5. Retrieved policy context
6. Groq-hosted `openai/gpt-oss-20b`
7. Answer with source attribution

The main evaluation set contained **5 cases**:

* 2 HR cases
* 1 Company case
* 1 IT case
* 1 Out-of-scope case

### 3. Baseline Results

| Metric                              |      Result |
| ----------------------------------- | ----------: |
| Total evaluation cases              |           5 |
| Passed                              |           5 |
| Failed                              |           0 |
| Errors                              |           0 |
| Completion rate                     |        100% |
| Pass rate                           |        100% |
| Source hit rate                     |        100% |
| In-scope cases with evidence        |         4/4 |
| Out-of-scope cases with no evidence |         1/1 |
| Average documents retrieved         |        3.00 |
| Average retrieval distance          |      0.8194 |
| Average cost/query                  | $0.00013641 |

The main quality evaluation therefore passed all five cases.

### 4. Investigation Finding

The investigation showed that retrieval was successfully finding evidence for the evaluated in-scope questions.

The main evaluation produced:

* **4/4 in-scope cases with evidence**
* **1/1 out-of-scope case correctly handled**
* **100% source hit rate**

The retrieval system was therefore not changed merely to address the evaluation result.

### 5. Evaluation Failure Investigation

One earlier evaluation issue involved the IT case:

> "How should company information be protected?"

The answer was semantically consistent with the expected policy content, but the evaluator originally relied on a literal keyword that did not match the wording used in the generated answer.

The evaluation criterion was therefore corrected so that the expected keyword reflected the intended answer characteristic.

After the correction:

**IT evaluation: PASS**

The complete five-case evaluation then produced:

**5/5 passed — 100% pass rate.**

This change should be understood as an **evaluation-quality correction**, not evidence of a model-quality improvement.

### 6. Latency Investigation

The evaluation showed a large difference between cold-start and warm performance.

| Latency metric       |       Result |
| -------------------- | -----------: |
| Cold-start latency   | 31,171.76 ms |
| Warm average latency |    758.43 ms |
| Warm P50             |    950.93 ms |
| Warm P95             |  1,080.27 ms |
| Overall P95          | 25,156.06 ms |

The cold-start latency was associated with initialization of the local embedding model.

Because production requests should not repeatedly initialize the embedding model, the retrieval model was warmed during API startup.

The evaluation gate was subsequently changed to use **warm P95 latency** for the performance threshold.

### 7. Measured Result After Iteration

The current evaluation results are:

| Metric                      |      Result |
| --------------------------- | ----------: |
| Overall pass rate           |        100% |
| Completion rate             |        100% |
| Source hit rate             |        100% |
| In-scope retrieval evidence |         4/4 |
| Out-of-scope no-evidence    |         1/1 |
| Warm P50 latency            |   950.93 ms |
| Warm P95 latency            | 1,080.27 ms |
| Average cost/query          | $0.00013641 |
| Total evaluation cost       | $0.00054562 |

The evaluation gate currently passes.

### 8. Routing Evaluation Findings

A separate routing evaluation contains **32 cases**.

The results should not be interpreted as a single clean routing-accuracy score because some failures were caused by external/model availability and test-fixture problems.

Observed failures include:

* multiple cases failing with `The Groq LLM service is currently unavailable.`
* `approval_001` failing because an employee ID could not be identified
* `approval_002` failing because an employee ID could not be identified

The routing suite also contains successful cases demonstrating:

* correct document-search routing,
* correct `no_tool` routing for out-of-scope questions,
* prompt-injection guardrail behavior.

All five prompt-injection cases shown in the routing results passed.

The approval failures indicate that the approval evaluation fixtures should provide valid employee identifiers when testing employee-record operations.

### 9. Current Risk

The main remaining evaluation risks are:

1. The primary quality dataset contains only **5 cases**.
2. Keyword matching does not provide full semantic answer evaluation.
3. Cold-start latency is significantly higher than warm latency.
4. The routing suite contains infrastructure/test-fixture failures that should be separated from actual routing failures.
5. Cost projections assume the evaluation average represents production traffic.
6. Retrieval distance is specific to the embedding model and should not be treated as a universal relevance threshold.

### 10. Next Iteration

The next iteration should focus on **evaluation coverage and reliability**, rather than changing the RAG pipeline without evidence.

Planned improvements:

* Expand the quality evaluation set beyond 5 cases.
* Separate infrastructure failures from routing failures.
* Add valid employee IDs to approval test cases.
* Add stronger semantic answer evaluation.
* Continue monitoring warm P50/P95 latency.
* Compare measured production cost against modeled cost projections.

### 11. Iteration Conclusion

The retrieval investigation did not identify a need for a fundamental RAG redesign.

The current evidence shows that the system successfully retrieved evidence for the evaluated in-scope cases and correctly rejected the evaluated out-of-scope case.

The highest-value next improvement is therefore **evaluation depth and reliability**, not an unmeasured change to retrieval.
