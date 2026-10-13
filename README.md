# Resume Skill Extractor

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Database SQLite](https://img.shields.io/badge/database-SQLite-lightgrey.svg)](https://www.sqlite.org/)
[![Tests PyTest](https://img.shields.io/badge/tests-4%20passed-brightgreen.svg)](https://docs.pytest.org/)
[![License MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

An end-to-end data and AI pipeline that ingests sample resumes, extracts a controlled taxonomy of technical skills through an isolated model interface, persists structured results into a relational SQLite database, and quantitatively evaluates extraction fidelity against human-annotated ground truth.

---

## Candidate Information
* **Candidate Name**: Shivam Mishra
* **Candidate ID**: DAI-027
* **Track**: AI + Data
* **Repository**: [https://github.com/shiv9918/Resume-skill-Extractor](https://github.com/shiv9918/Resume-skill-Extractor)
* **Demo Video**: [Click to Watch Demo Video](#demo-video) *(link below)*
* **Design & Decision Note**: Included as a 1-page PDF submission document (`DESIGN_NOTE.md`)

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture & Design Principles](#architecture--design-principles)
3. [Relational Data Model](#relational-data-model)
4. [Clean Setup & Installation](#clean-setup--installation)
5. [Running the Pipeline & Validation](#running-the-pipeline--validation)
6. [Accuracy Evaluation Results](#accuracy-evaluation-results)
7. [Edge-Case & Failure Resilience](#edge-case--failure-resilience)
8. [Automated Test Suite](#automated-test-suite)
9. [Ethical Design: No Candidate Ranking](#ethical-design-no-candidate-ranking)
10. [Demo Video & Presentation Script](#demo-video--presentation-script)
11. [5-Day Development Roadmap](#5-day-development-roadmap)

---

## Project Overview
Automated resume screening often suffers from two major pitfalls:
1. **Unbounded AI Hallucination & Vocabulary Drift**: Generative models without strict taxonomies extract non-standard skill terms ("pythonic coding", "py-lang", "expert python developer"), fragmenting data consistency.
2. **Algorithmic Bias via Ranking**: Unchecked scoring algorithms penalize candidates based on formatting or keyword stuffing.

This project addresses these challenges by:
- Enforcing a **controlled vocabulary of 27 technical skills**.
- Isolating extraction logic behind an abstract interface (`SkillExtractorInterface`).
- Storing normalized data into a **relational SQL schema**.
- Measuring **Precision, Recall, and F1-score** against a human-labeled ground truth set.
- Operating strictly as an **extraction pipeline without ranking or scoring individuals**.

---

## Architecture & Design Principles

```
+--------------------------------------------------------------------------+
|                            1. INGESTION LAYER                            |
|             Reads UTF-8 text files from `sample_data/*.txt`              |
+--------------------------------------------------------------------------+
                                     |
                                     v
+--------------------------------------------------------------------------+
|                     2. AI INTERFACE ABSTRACTION                          |
|                     (SkillExtractorInterface)                            |
|     +----------------------------+-----------------------------+         |
|     |     MockLocalExtractor     |      LLMSkillExtractor      |         |
|     |  Boundary Regex Matching   |    Cloud / Local LLM Hook   |         |
|     | (Zero-Cost / Clean Setup)  |   (Gemini, OpenAI, Ollama)  |         |
|     +----------------------------+-----------------------------+         |
+--------------------------------------------------------------------------+
                                     |
                                     v
+--------------------------------------------------------------------------+
|                      3. RELATIONAL PERSISTENCE (SQL)                     |
|           SQLite Database: `resumes` <-> `extracted_skills`              |
|        - Foreign keys with ON DELETE CASCADE                             |
|        - Unique constraint on (resume_id, skill_name)                    |
|        - Transactional upsert (ON CONFLICT DO UPDATE)                    |
+--------------------------------------------------------------------------+
                                     |
             +-----------------------+-----------------------+
             v                                               v
+--------------------------+                       +-----------------------+
|  4. EVALUATION ENGINE    |                       |   5. QUALITY SUITE    |
|   (Precision, Recall,    |                       |  4 PyTest Unit Tests  |
|    F1 vs Ground Truth)   |                       |  Edge-Case Scenarios  |
+--------------------------+                       +-----------------------+
```

### Directory Structure
```
ByteSpoke-Assesment/
├── .gitignore               # Ignores __pycache__, SQLite DBs, venv
├── README.md                # Main documentation
├── DESIGN_NOTE.md           # 1-page architecture and decision document
├── DEMO_SCRIPT.md           # 5-8 minute walkthrough presentation script
├── requirements.txt         # Minimal dependency list (pytest)
├── skills_list.py           # Controlled taxonomy of technical skills
├── extractor.py             # SkillExtractorInterface & MockLocalExtractor
├── database.py              # SQLite DDL, CRUD operations, transactions
├── pipeline.py              # End-to-end ingestion and persistence pipeline
├── evaluate.py              # Quantitative accuracy evaluation engine
├── demo_edge_case.py        # Failure mode and boundary collision demo
├── data/
│   ├── ground_truth.json    # Human-annotated evaluation set
│   └── resume_skills.db     # SQLite database (auto-generated at runtime)
├── sample_data/
│   ├── resume_1.txt         # Software Engineer profile
│   ├── resume_2.txt         # Data Scientist profile
│   └── resume_edge_case.txt # Non-tech / noisy profile with special chars
└── tests/
    └── test_pipeline.py     # 4 automated unit tests
```

---

## Relational Data Model

The relational model is built with SQLite to guarantee zero-configuration portability, ACID transactions, and standard SQL compliance.

```sql
-- Resumes Table
CREATE TABLE IF NOT EXISTS resumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT UNIQUE NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Extracted Skills Table
CREATE TABLE IF NOT EXISTS extracted_skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id INTEGER NOT NULL,
    skill_name TEXT NOT NULL,
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(resume_id) REFERENCES resumes(id) ON DELETE CASCADE,
    UNIQUE(resume_id, skill_name)
);
```

### Key Schema Characteristics
- **Referential Integrity**: Cascading deletes ensure orphan skill rows are removed if a parent resume is deleted.
- **Compound Uniqueness**: `UNIQUE(resume_id, skill_name)` guarantees a resume cannot register duplicate skill entries.
- **Idempotency**: Re-ingesting resumes uses `ON CONFLICT(filename) DO UPDATE` in an atomic transaction to ensure safe re-runs.

---

## Clean Setup & Installation

The solution is designed to run completely offline from a fresh environment without requiring API keys or payment accounts.

### Prerequisites
- Python 3.10 or higher
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/shiv9918/Resume-skill-Extractor.git
cd Resume-skill-Extractor
```

### 2. Create and Activate Virtual Environment
* On **Windows (PowerShell)**:
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
* On **macOS / Linux**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
*(Dependencies are strictly minimal: `pytest>=7.0.0`; all SQLite and regex modules are built into standard Python).*

---

## Running the Pipeline & Validation

### Step 1: Run End-to-End Ingestion Pipeline
Processes all resumes in `sample_data/`, extracts skills, and saves structured records into SQLite:
```bash
python pipeline.py
```
**Sample Output:**
```text
2026-10-13 00:06:57 [INFO] Initializing database at: data/resume_skills.db
2026-10-13 00:06:57 [INFO] Discovered 3 resume file(s) for processing.
2026-10-13 00:06:57 [INFO] Processed 'resume_1.txt' -> Extracted 9 skills: ['AWS', 'CSS', 'Django', 'Docker', 'HTML', 'JavaScript', 'MySQL', 'PostgreSQL', 'Python']
2026-10-13 00:06:57 [INFO] Processed 'resume_2.txt' -> Extracted 8 skills: ['Data Analysis', 'Git', 'Machine Learning', 'Python', 'SQL', 'TensorFlow', 'pandas', 'scikit-learn']
Pipeline finished processing resumes successfully.
```

### Step 2: Run Accuracy Evaluation
Compares extraction output with human-verified ground truth in `data/ground_truth.json`:
```bash
python evaluate.py
```

### Step 3: Run Edge-Case & Failure Demonstration
Demonstrates boundary isolation, noisy text parsing, and idempotent database re-ingestion:
```bash
python demo_edge_case.py
```

### Step 4: Run Automated Unit Tests
Runs the automated test suite verifying database CRUD, word boundary regex, and end-to-end directory parsing:
```bash
python -m pytest tests/
```

---

## Accuracy Evaluation Results

Evaluation is performed using standard Information Retrieval metrics (Precision, Recall, F1):

$$\text{Precision} = \frac{\text{True Positives}}{\text{Predicted}}, \quad \text{Recall} = \frac{\text{True Positives}}{\text{Ground Truth}}, \quad F_1 = \frac{2 \cdot P \cdot R}{P + R}$$

| Document | Ground Truth Skills | Extracted Skills | Precision | Recall | F1-Score |
|---|---|---|---|---|---|
| **resume_1.txt** | 9 skills (Python, Django, PostgreSQL, MySQL, Docker, AWS, HTML, CSS, JavaScript) | 9 skills | **100.00%** | **100.00%** | **100.00%** |
| **resume_2.txt** | 6 skills (Python, SQL, pandas, scikit-learn, TensorFlow, Git) | 8 skills (+ Machine Learning, Data Analysis) | **75.00%** | **100.00%** | **85.71%** |
| **Overall Micro-Average** | **15 Skills** | **17 Skills** | **88.24%** | **100.00%** | **93.75%** |

*Note: In `resume_2.txt`, the extra skills detected were "Machine Learning" and "Data Analysis" which were explicitly written in the summary section of the resume.*

---

## Edge-Case & Failure Resilience

The suite in `demo_edge_case.py` demonstrates resilience against 5 critical edge cases:

1. **Empty / Whitespace Input**:
   - `""` and `"   \n\t  "` return `[]` gracefully without crashes.
2. **Non-Technical Resumes**:
   - Profiles with unlisted creative tools (Photoshop, Figma, Copywriting) return `[]` without error.
3. **Substring Collision & Boundary Isolation**:
   - Ensures compound terms such as `"JavaScript"` do **not** trigger a false positive for `"Java"`.
   - Uses negative lookarounds: `rf'(?<!\w){escaped_skill}(?!\w)'`.
4. **Database Idempotence**:
   - Re-running the pipeline on existing filenames updates records cleanly using SQLite transactions without unique constraint violations.
5. **Noisy Text & Special Characters**:
   - Resumes containing noisy symbols (`@#$%^&!`, `null`, `undefined`, `NaN`, `C++`) are parsed safely.

---

## Automated Test Suite

The test suite in `tests/test_pipeline.py` contains 4 unit tests run via `pytest`:
- **`test_database_crud`**: Verifies database initialization, table creation, foreign key constraints, and record retrieval.
- **`test_extractor_boundary_and_case_matching`**: Asserts boundary isolation (e.g. `Java` vs `JavaScript`) and case-insensitive matching.
- **`test_extractor_edge_cases`**: Validates handling of empty strings, whitespace, and non-technical inputs.
- **`test_end_to_end_pipeline`**: Creates temporary resume files, runs `run_pipeline()`, and verifies database persistence.

**Test Execution:**
```bash
python -m pytest tests/
```
Output:
```text
tests/test_pipeline.py ....                                              [100%]
4 passed in 0.31s
```

---

## Ethical Design: No Candidate Ranking

In strict accordance with project specifications and ethical AI hiring guidelines:
- **No Ranking Algorithm**: This system does **not** score, tier, sort, or rank candidates.
- **Rationale**: Keyword frequency does not equate to candidate competence. Automatic ranking introduces systemic bias against diverse resume formats. The pipeline strictly functions as an extraction and data normalization utility for human recruiters.

---

## Demo Video & Presentation Script

* **Demo Video Link**: `https://youtu.be/your-demo-video-link` *(Record and insert your YouTube/Loom link here)*
* **Demo Script**: A complete 5–8 minute spoken presentation script with minute-by-minute visual guidance is prepared locally in `DEMO_SCRIPT.md`.

---

## 5-Day Development Roadmap

| Day | Milestone | Key Deliverables | Status |
|:---:|---|---|:---:|
| **Day 1** | **Foundation & Data Model** | Git repo setup, SQLite schema (`database.py`), synthetic resumes, ground truth JSON | ✅ Completed |
| **Day 2** | **AI Interface & Extraction** | `SkillExtractorInterface`, `MockLocalExtractor`, `CONTROLLED_SKILLS` vocabulary | ✅ Completed |
| **Day 3** | **Database Integration** | Pipeline connection (`pipeline.py`), transactional persistence, logging | ✅ Completed |
| **Day 4** | **Testing & Evaluation** | Evaluation suite (`evaluate.py`), 4 PyTest tests, edge-case demo script | ✅ Completed |
| **Day 5** | **Documentation & Final Polish** | 1-page `DESIGN_NOTE.md`, polished `README.md`, `DEMO_SCRIPT.md`, final push | ✅ Completed |

---

## License
This project is open-source and available under the [MIT License](LICENSE).
