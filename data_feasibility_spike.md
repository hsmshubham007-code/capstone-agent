# Data & Feasibility Spike

## Project

**Company Policy Agent**

**Project:** `week2day5proj1`

---

## 1. Purpose

The purpose of this feasibility spike is to determine whether the available company-policy data is sufficient to support a retrieval-based AI system.

The spike answers two questions:

1. **Can the required information actually be retrieved from the available documents?**
2. **What is the maximum practical coverage we can expect from the current data?**

The investigation is timeboxed to approximately **2 hours**.

---

# 2. Available Data

The current knowledge base contains company policy documents:

| Document             | Type | Coverage                 |
| -------------------- | ---- | ------------------------ |
| `hr_policy.pdf`      | PDF  | HR policies              |
| `company_policy.pdf` | PDF  | General company policies |
| `it_policy.pdf`      | PDF  | IT policies              |

The documents are stored locally in:

```text
data/
├── hr_policy.pdf
├── company_policy.pdf
└── it_policy.pdf
```

---

# 3. Data Access

The documents are locally accessible by the application.

The ingestion pipeline uses:

```text
PyPDFLoader
```

to extract text from the PDF files.

The documents were successfully processed, indicating that the source data is technically accessible to the application.

---

# 4. Data Quality

The available documents are sufficiently readable and structured for the initial retrieval prototype.

### Observed results

```text
PDF pages processed: 21
Document chunks created: 39
```

The documents can therefore be:

```text
PDF
 ↓
Text extraction
 ↓
Chunking
 ↓
Embedding
 ↓
Vector storage
```

---

# 5. Retrieval Setup

The feasibility test uses:

### Embedding model

```text
sentence-transformers/all-MiniLM-L6-v2
```

### Vector database

```text
Chroma
```

### Collection

```text
capstone_documents
```

### Retrieval

```text
Top-k = 4
```

The retrieval pipeline searches the policy documents using semantic similarity.

---

# 6. 2-Hour Feasibility Spike

The spike focused only on determining whether relevant policy information could be retrieved.

### Activities completed

* Identified available policy documents.
* Verified local document access.
* Loaded PDF files.
* Extracted text.
* Split documents into chunks.
* Generated embeddings.
* Created the Chroma vector store.
* Indexed the document chunks.
* Tested policy questions against the vector store.
* Inspected retrieved document content.

The full agent was not required to determine basic retrieval feasibility.

---

# 7. Retrieval Test

A representative policy question was tested:

```text
"What does the company say about professional conduct?"
```

The expected retrieval behavior is:

```text
User Question
      ↓
Semantic Search
      ↓
Relevant Policy Chunks
      ↓
HR / Company Policy Documents
      ↓
Relevant Policy Information
```

The retrieval pipeline can search the indexed company-policy corpus and return relevant document chunks.

This demonstrates that the required information is **retrievable in principle** from the available corpus.

---

# 8. Feasibility Result

## Result: RETRIEVABLE FOR THE CURRENT PROTOTYPE CORPUS

The spike established that the current data can support a RAG-based prototype.

The basic retrieval path works:

```text
Policy PDFs
     ↓
Text extraction
     ↓
39 chunks
     ↓
Embeddings
     ↓
Chroma
     ↓
Semantic retrieval
     ↓
Relevant policy content
```

Therefore, there is sufficient technical evidence to proceed with the Company Policy Agent.

---

# 9. What Is the Ceiling?

The **retrieval ceiling** is determined by the quality and coverage of the available documents.

The AI cannot reliably answer questions about information that does not exist in the indexed corpus.

Therefore:

```text
Answer quality
      ≤
Quality and coverage of available policy data
```

For example:

```text
Question covered by policy documents
        ↓
Potentially retrievable
        ↓
Can be answered using retrieved evidence
```

But:

```text
Question not covered by policy documents
        ↓
No reliable source available
        ↓
System should not invent an answer
```

---

# 10. Current Data Ceiling

The current prototype has a limited corpus:

```text
3 primary policy documents
21 PDF pages
39 indexed chunks
```

Therefore, the system's knowledge coverage is limited to the information contained in these documents.

It should not be considered a complete company knowledge base.

---

# 11. Important Limitations

### Limited document coverage

Only the currently available HR, company, and IT policy documents are indexed.

Questions about policies that are not present cannot be reliably answered.

### Retrieval is not the same as correctness

Retrieving a relevant chunk does not guarantee that the final LLM-generated answer is correct.

The system therefore requires separate answer evaluation.

### Document freshness

If company policies change, the indexed data must be updated.

Otherwise, the system could retrieve outdated policy information.

### Ambiguous questions

Questions that are vague or refer to concepts not explicitly described in the documents may produce weaker retrieval results.

### Missing evidence

If the retrieval system cannot find sufficient supporting evidence, the system should avoid inventing an answer.

---

# 12. Feasibility Decision

| Question                                      | Result                                 |
| --------------------------------------------- | -------------------------------------- |
| Do usable documents exist?                    | **Yes**                                |
| Can the application access them?              | **Yes**                                |
| Can PDF text be extracted?                    | **Yes**                                |
| Can the text be chunked?                      | **Yes**                                |
| Can embeddings be generated?                  | **Yes**                                |
| Can chunks be indexed?                        | **Yes**                                |
| Can semantic retrieval be performed?          | **Yes**                                |
| Can relevant policy information be retrieved? | **Yes, for the tested/current corpus** |
| Is the corpus complete?                       | **No**                                 |
| Does retrieval guarantee answer correctness?  | **No**                                 |

---

# 13. Feasibility Conclusion

The 2-hour spike provides sufficient evidence that the Company Policy Agent is **data-feasible as a prototype**.

The current policy documents can be successfully processed, indexed, and searched.

The main limitation is not basic technical accessibility of the data. The main limitation is **coverage**: the system can only reliably answer questions supported by the documents available in the knowledge base.

Therefore:

> **The project can proceed to full agent development, but answer quality will be bounded by the coverage, freshness, and quality of the indexed policy documents.**

---

# 14. Next Step

After confirming feasibility, development can continue with:

```text
Data Feasibility
       ↓
RAG Evaluation
       ↓
Agent / Router
       ↓
Safety Guardrails
       ↓
Human Approval
       ↓
Audit Trail
       ↓
Async Execution
       ↓
Evaluation
       ↓
Deployment
```

---

# 15. Final Feasibility Statement

> **The available company-policy documents are accessible, processable, and retrievable through the RAG pipeline. The feasibility spike confirms that relevant policy information can be retrieved from the current corpus. However, the system's answer ceiling is bounded by the coverage and freshness of the indexed documents; information absent from the corpus cannot be reliably retrieved and should not be fabricated by the AI.**
