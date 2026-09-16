# Adaptive Academic RAG

## An Adaptive Retrieval-Augmented Generation Framework for Intelligent Academic Knowledge Management

Adaptive Academic RAG is a Retrieval-Augmented Generation (RAG) system designed for academic question answering.

The system introduces an adaptive evidence composition and validation process that changes the retrieved evidence according to the educational context and requirements of the user's query.

The framework also allows the user to select a specific academic PDF as the knowledge source. Initial retrieval and adaptive re-retrieval are restricted to the selected document.

Instead of using a fixed:

```text
Retrieve → Generate
```

pipeline, the proposed framework follows:

```text
Retrieve → Compose → Validate → Re-retrieve if necessary
→ Compose → Validate → Generate
```

---

## Project Objective

The objective of this project is to develop an adaptive RAG framework for intelligent academic knowledge management.

The system aims to:

- Retrieve relevant academic information from indexed documents.
- Allow the user to select a specific academic PDF as the knowledge source.
- Analyze the educational intent and context of a query.
- Adapt the amount and composition of evidence according to the query.
- Validate whether the retrieved evidence is sufficient.
- Perform targeted re-retrieval when evidence is insufficient.
- Restrict adaptive re-retrieval to the selected academic document.
- Generate grounded academic responses using validated evidence.
- Provide citations referring to the retrieved academic sources.

---

## Key Idea: Adaptive Educational Evidence Composition

The main adaptive component of the framework is **Adaptive Educational Evidence Composition**.

The system does not treat every query in the same way.

| Query Type | Evidence Strategy |
|---|---|
| Definition | Concise evidence from relevant sections |
| Explanation | Multiple supporting evidence chunks |
| Comparison | Evidence covering the concepts being compared |
| Summary | Key information from relevant sections |
| Examples | Evidence containing examples or applications |
| Exam Preparation | Focused and important learning content |
| Research | Broader and more authoritative evidence |

If the initial evidence does not satisfy the requirements of the query, the system performs targeted re-retrieval and composes the evidence again.

---

## Document-Specific Retrieval

The system provides interactive academic document selection.

When the system starts, the available PDF files in the academic document directory are displayed to the user.

Example:

```text
AVAILABLE ACADEMIC FILES

1. MODULE 2.pdf
2. Module 4.pdf
3. test_notes.pdf

Select a PDF number:
```

The selected document becomes the retrieval source for the current question-answering session.

The retrieval system applies a document-level filter so that evidence is retrieved only from the selected PDF. This restriction is maintained during adaptive re-retrieval.

---

## Adaptive Retrieval Mechanism

The adaptive mechanism operates in multiple stages.

### Stage 1: Query Analysis

The query is analyzed to determine:

- Query intent
- Learning context
- Query complexity
- Multi-concept requirements
- Required number of items when explicitly specified

### Stage 2: Initial Retrieval

Relevant candidate evidence is retrieved from the selected academic PDF.

### Stage 3: Evidence Composition

The retrieved candidates are composed according to the requirements of the query.

### Stage 4: Evidence Validation

The composed evidence is evaluated using factors such as:

- Evidence coverage
- Retrieval score
- Required concept coverage
- Evidence sufficiency

### Stage 5: Adaptive Re-retrieval

If the evidence is insufficient, the system generates targeted retrieval queries based on the detected requirements or missing evidence.

The additional evidence is merged with the existing candidates.

### Stage 6: Re-composition and Re-validation

The expanded candidate pool is composed again and validated.

### Stage 7: Response Generation

The validated evidence is passed to the generation component to produce a grounded academic response.

---

## System Architecture

The framework consists of the following modules:

1. **Academic Data Ingestion & Knowledge Base**
2. **Query & Educational Context Analysis**
3. **Candidate Retrieval & Ranking**
4. **Adaptive Educational Evidence Composition**
5. **Evidence Validation & Re-ranking**
6. **RAG Generation & Response Personalization**
7. **User Profile & Feedback**

Final responses are passed through a post-processing/output layer for formatting, citations, and presentation.

---

## Adaptive Pipeline

```text
User
 │
 ▼
Select Academic PDF
 │
 ▼
User Query
 │
 ▼
Query & Educational Context Analysis
 │
 ▼
Candidate Retrieval & Ranking
 │
 ▼
Adaptive Educational Evidence Composition
 │
 ▼
Evidence Validation
 │
 ▼
Is Evidence Sufficient?
 │
 ├── Yes ───────────────► RAG Generation
 │                              │
 │                              ▼
 │                       Final Response
 │
 └── No
       │
       ▼
 Targeted Re-retrieval
       │
       │  Same Selected PDF
       ▼
 Evidence Composition
       │
       ▼
 Evidence Validation
       │
       ├── Sufficient ──► RAG Generation
       │
       └── Insufficient
              │
              ▼
        Further Adaptive
        Re-retrieval
```

---

## Example of Adaptive Retrieval

For a broad question such as:

```text
Explain the complete Streaming Analytics Architecture from Collection Tier to Delivery Tier and describe how high availability and Paxos support the architecture.
```

the system may determine that the initial evidence is insufficient.

Example execution:

```text
Iteration 1: Initial Retrieval
Evidence: Insufficient
Coverage: 0.46

        ↓

Adaptive Retrieval Triggered

        ↓

Targeted Re-retrieval

        ↓

Iteration 2: Adaptive Retrieval
Evidence: Sufficient
Coverage: 0.73

        ↓

RAG Generation

        ↓

Final Academic Response
```

The system does not automatically perform additional retrieval for every query. Adaptive retrieval is triggered when the validation stage determines that the initial evidence is insufficient.

---

## Project Structure

```text
adaptive-academic-rag/
│
├── backend/
│   └── app/
│       ├── components/
│       │   ├── embedding_service.py
│       │   ├── evidence_composer.py
│       │   ├── evidence_validator.py
│       │   ├── gemini_generator.py
│       │   ├── query_analyser.py
│       │   └── retriever.py
│       │
│       ├── pipelines/
│       │   ├── adaptive_rag_pipeline.py
│       │   └── indexing_pipeline.py
│       │
│       ├── config.py
│       ├── haystack_store.py
│       └── main.py
│
├── data/
│   └── raw_documents/
│
├── frontend/
│   └── streamlit_app.py
│
├── scripts/
│   ├── ingest_documents.py
│   ├── test_retrieval.py
│   └── test_adaptive_rag.py
│
├── .env
└── README.md
```

> **Note:** `.env` contains local configuration such as API credentials and should not be committed to the repository.

---

## Technology Stack

- **Python**
- **Haystack**
- **PostgreSQL**
- **pgvector**
- **Google Gemini**
- **Streamlit**
- **PyMuPDF**

---

## Running the Adaptive RAG Test

From the project root:

```powershell
python -m scripts.test_adaptive_rag
```

The application displays the available academic PDFs and allows the user to select one document.

After selecting the document, enter an academic question.

The system displays:

- Generated answer
- Selected source
- Adaptive Retrieval status
- Query understanding
- Evidence validation
- Top evidence
- Retrieval process and iterations

---

## Adaptive RAG Status

The system can report two main states.

### Adaptive Retrieval Not Required

```text
Adaptive Retrieval: Not Required
Reason: Initial evidence was sufficient
Retrieval Iterations: 1
```

This means the initial evidence was sufficient to answer the query.

### Adaptive Retrieval Triggered

```text
Adaptive Retrieval: Triggered
Reason: Initial evidence was insufficient
Retrieval Iterations: 2
Initial Evidence: Insufficient
Adaptive Re-retrieval: Completed
Evidence Re-validation: Completed
```

This indicates that the system detected insufficient initial evidence and performed adaptive re-retrieval before generating the final response.

---

## Current Academic Documents

The project can work with multiple academic PDFs placed in:

```text
data/raw_documents/
```

The available documents are discovered dynamically by the test application rather than being hardcoded into the retrieval pipeline.

New PDF documents can therefore be added to the document collection and indexed before use.

---

## Research Contribution

The central research idea is **Adaptive Educational Evidence Composition**.

Rather than applying the same retrieval strategy to every academic question, the framework analyzes the educational requirements of the query and dynamically determines whether the retrieved evidence is sufficient.

When evidence is insufficient, the system adapts its retrieval process through targeted re-retrieval, followed by evidence composition and validation.

The framework therefore introduces an adaptive decision loop into an academic RAG system:

```text
Retrieve
   ↓
Compose
   ↓
Validate
   ↓
Adapt if necessary
   ↓
Re-retrieve
   ↓
Compose
   ↓
Validate
   ↓
Generate
```

The document-selection mechanism further provides controlled, source-specific academic retrieval by restricting retrieval and adaptive re-retrieval to the PDF selected by the user.
