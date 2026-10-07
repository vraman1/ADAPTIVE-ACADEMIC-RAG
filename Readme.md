# Adaptive Academic RAG

## An Adaptive Retrieval-Augmented Generation Framework for Intelligent Academic Knowledge Management

This project implements an **Adaptive Retrieval-Augmented Generation (RAG) framework for academic knowledge management**.

The system retrieves relevant academic evidence, adapts evidence composition according to the educational context of a query, validates whether the retrieved evidence is sufficient, performs targeted re-retrieval when necessary, and generates a grounded academic response.

The core idea is **Adaptive Educational Evidence Composition** rather than using a fixed retrieve-then-generate pipeline.

---

## Key Idea

The system follows an adaptive pipeline:

```text
User Query
    ↓
Query & Educational Context Analysis
    ↓
Initial Retrieval
    ↓
Adaptive Evidence Composition
    ↓
Evidence Validation
    ↓
Is Evidence Sufficient?
   ↙              ↘
 No                Yes
 ↓                  ↓
Targeted           Evidence
Re-retrieval       Re-ranking
 ↓                  ↓
Compose Again       ↓
 ↓                  ↓
Validate Again      ↓
   ↘              ↙
      Generation
          ↓
   Personalized
 Academic Response
```

If the initial evidence does not adequately cover the requirements of the query, the system generates targeted retrieval queries and retrieves additional evidence before generating the final response.

---

## Main Features

- Academic PDF document ingestion
- Paragraph-aware document chunking
- Gemini-based document and query embeddings
- PostgreSQL + pgvector academic document store
- Semantic vector retrieval
- Educational query intent analysis
- Learning-context detection
- Evidence requirement detection
- Adaptive evidence composition
- Evidence coverage and sufficiency validation
- Targeted re-retrieval for missing evidence
- Evidence re-ranking
- Redundancy reduction
- Gemini-based grounded response generation
- Academic source/page citations
- Learner profile and feedback handling
- Personalized response presentation
- Streamlit-based user interface
- Retrieval history and evidence inspection

---

## Adaptive Educational Evidence Composition

The main adaptive component of the project is **Adaptive Educational Evidence Composition**.

The system adapts evidence selection according to the educational purpose and requirements of the query.

| Query Type | Evidence Adaptation |
|---|---|
| Definition | Concise evidence explaining the concept |
| Explanation | Evidence containing the concept and supporting explanation |
| Comparison | Evidence covering the concepts being compared |
| Exam Preparation | Focused notes, key points, and relevant examples |
| Research | More comprehensive and authoritative evidence |
| Multi-part Question | Evidence selected to cover the requested parts |

The system does not simply retrieve a fixed number of chunks and immediately generate an answer. It checks whether the selected evidence is sufficient and can perform targeted re-retrieval when evidence is missing.

---

## System Architecture

### Module 1 — Academic Data Ingestion & Knowledge Base

Collects and prepares academic documents for retrieval.

Main components:

- Document ingestion
- Text extraction and cleaning
- Chunking engine
- Metadata management
- Embedding generation
- Vector database/index

**Output:** Searchable academic knowledge base.

### Module 2 — Query & Educational Context Analysis

Analyzes the user's query and identifies its educational requirements.

It considers:

- Query intent
- Learning context
- Query complexity
- Multiple concepts
- Required number of items
- Evidence requirements
- Explicit requirements

**Output:** Structured educational query context.

### Module 3 — Candidate Retrieval & Ranking

Retrieves potentially relevant academic evidence and ranks the candidate documents.

The project uses:

- Gemini embeddings
- PostgreSQL
- pgvector
- Semantic retrieval
- Metadata filtering
- Candidate ranking

**Output:** Ranked candidate evidence pool.

### Module 4 — Adaptive Educational Evidence Composition

This is the core adaptive module.

It selects and combines evidence according to the query context and evidence requirements.

It attempts to:

- Cover different requirements
- Cover requested items
- Reduce duplicate evidence
- Select complementary evidence
- Build an evidence set suitable for validation and generation

**Output:** Adaptively composed evidence set.

### Module 5 — Evidence Validation & Re-ranking

Checks whether the composed evidence is sufficient for answering the query.

It evaluates:

- Evidence relevance
- Evidence coverage
- Requested-item coverage
- Supporting descriptions
- Content quality
- Structural quality
- Redundancy

If evidence is insufficient, the adaptive retrieval controller triggers targeted re-retrieval.

**Output:** Validated and re-ranked evidence.

### Module 6 — RAG Generation & Response Personalization

Generates the final response using the validated academic evidence.

The generation layer:

- Uses only supplied academic evidence
- Produces structured academic answers
- Preserves important academic terminology
- Includes source/page citations
- Adapts presentation to learner preferences

**Output:** Grounded academic response.

### Module 7 — User Profile & Feedback

Maintains learner interaction and feedback information.

It can track:

- Preferred detail level
- Preferred response format
- Preference for examples
- Preference for citations
- Learning history
- Feedback history
- Interaction count

**Output:** Updated learner profile and personalization context.

---

## Post-processing & Output

The final response can be:

- Structured
- Citation-formatted
- Quality checked
- Rendered through the Streamlit interface

The interface also provides access to evidence and adaptive retrieval information for inspection.

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
│       │   ├── evidence_reranker.py
│       │   ├── evidence_validator.py
│       │   ├── gemini_generator.py
│       │   ├── query_analyser.py
│       │   ├── retriever.py
│       │   └── user_profile.py
│       │
│       ├── pipelines/
│       │   ├── adaptive_rag_pipeline.py
│       │   ├── generation_pipeline.py
│       │   └── indexing_pipeline.py
│       │
│       ├── config.py
│       ├── haystack_store.py
│       └── main.py
│
├── data/
│   └── raw_documents/
│       └── <academic PDF files>
│
├── frontend/
│   └── streamlit_app.py
│
├── scripts/
│   ├── ingest_documents.py
│   ├── test_retrieval.py
│   ├── test_adaptive_rag.py
│   ├── ph4_trigger.py
│   ├── ph4_not_trigger.py
│   ├── ph5_reranking.py
│   ├── test_generation.py
│   └── test_user_profile.py
│
├── .env
├── .gitignore
└── README.md
```

---

## Academic PDF Documents

The academic PDF documents used by the system **must be placed inside**:

```text
data/raw_documents/
```

For example:

```text
data/
└── raw_documents/
    ├── MODULE 2.pdf
    ├── Module 4.pdf
    └── test_notes.pdf
```

The Streamlit interface automatically reads the PDF files from this folder and provides them as source-selection options.

### Important

PDF files are intentionally excluded from GitHub using:

```gitignore
data/raw_documents/*.pdf
```

Therefore:

- The `data/raw_documents/` folder is part of the project.
- The actual academic PDFs are required for local execution.
- The PDFs should be manually placed in `data/raw_documents/` after cloning the repository.
- The PDFs are not uploaded to GitHub.

After placing the PDFs in the folder, run the document ingestion pipeline before using retrieval.

---

## Technologies Used

- Python
- Streamlit
- Haystack
- Google Gemini
- Gemini Embeddings
- PostgreSQL
- pgvector
- PyMuPDF
- HNSW vector indexing

---

## Environment Setup

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd adaptive-academic-rag
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

Install the required Python packages for the project.

If a `requirements.txt` file is available:

```powershell
pip install -r requirements.txt
```

### 4. Configure the Gemini API key

Create a local `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Do not commit this file to GitHub.

### 5. Configure PostgreSQL

The application uses PostgreSQL with pgvector for storing academic document embeddings.

Ensure PostgreSQL is running and the project's database configuration is correctly set before running ingestion and retrieval.

---

## Adding Academic PDFs

After cloning the repository, place your academic PDFs inside:

```text
data/raw_documents/
```

Example:

```text
data/raw_documents/
├── MODULE 2.pdf
├── Module 4.pdf
└── another_academic_document.pdf
```

Then run the ingestion script:

```powershell
python scripts/ingest_documents.py
```

The ingestion pipeline extracts PDF text, creates chunks, generates embeddings, and stores the resulting documents in the academic vector database.

---

## Running the Application

Start the Streamlit interface:

```powershell
streamlit run frontend/streamlit_app.py
```

The application provides:

- PDF/source selection
- Academic query input
- Query analysis
- Adaptive retrieval status
- Evidence validation information
- Final generated answer
- Source/page citations
- Evidence inspection
- Adaptive retrieval history
- Learner personalization
- Feedback collection

---

## Testing

Individual pipeline stages can be tested using the scripts in `scripts/`.

Examples:

```powershell
python scripts/test_retrieval.py
python scripts/test_adaptive_rag.py
python scripts/ph4_trigger.py
python scripts/ph4_not_trigger.py
python scripts/ph5_reranking.py
python scripts/test_generation.py
python scripts/test_user_profile.py
```

The Phase 4 trigger and non-trigger tests are useful for demonstrating the adaptive behavior of the system.

---

## Example Adaptive Behavior

For a query requiring multiple academic components, the initial retrieval may not contain enough evidence.

The system can behave as follows:

```text
Initial Retrieval
       ↓
Evidence Composition
       ↓
Validation
       ↓
Insufficient Evidence
       ↓
Identify Missing Requirement
       ↓
Generate Targeted Query
       ↓
Targeted Re-retrieval
       ↓
Evidence Composition
       ↓
Validation
       ↓
Sufficient Evidence
       ↓
Evidence Re-ranking
       ↓
Grounded Generation
```

This adaptive loop is the central difference from a conventional fixed retrieval pipeline.

---

## Research Contribution

The project focuses on **adaptive educational evidence composition** for academic RAG.

Instead of treating every query with the same retrieval strategy, the framework uses the educational context and evidence requirements of the query to determine how evidence should be composed and whether additional targeted retrieval is necessary.

The framework combines:

1. Educational query understanding
2. Context-aware evidence composition
3. Evidence sufficiency validation
4. Targeted adaptive re-retrieval
5. Evidence re-ranking
6. Grounded response generation
7. Learner-oriented personalization

---

## Security and Data Considerations

- API keys must be stored in `.env` and must not be committed.
- Academic PDF files are excluded from Git by default.
- Users should only use academic documents they are permitted to process and distribute.
- Do not commit sensitive or private documents to the repository.

---

## Current Status

The project currently includes the adaptive RAG flow from:

```text
Academic PDFs
     ↓
Ingestion
     ↓
Retrieval
     ↓
Query Analysis
     ↓
Adaptive Evidence Composition
     ↓
Evidence Validation
     ↓
Targeted Re-retrieval
     ↓
Evidence Re-ranking
     ↓
Gemini Generation
     ↓
Personalized Academic Response
```

The Streamlit interface provides the main user-facing application.

---

## Future Improvements

Potential future improvements include:

- More advanced learner modeling
- Improved educational intent classification
- Additional academic source types
- More robust evidence quality evaluation
- Automated evaluation benchmarks
- Citation correctness evaluation
- Response faithfulness metrics
- Learning-outcome-aware retrieval
- More sophisticated feedback-driven adaptation
