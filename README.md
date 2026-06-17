# 🚀 CogniHire: Predictive Talent Intelligence Engine

**Built for the Redrob Intelligent Candidate Discovery Challenge**

CogniHire is not a keyword filter; it is a predictive ranking engine designed to discover hidden gems within massive talent pools. Traditional recruiting systems rely heavily on surface-level keyword matching. CogniHire instead evaluates **semantic fit, career trajectory, behavioral signals, and production readiness** to generate a precise and explainable shortlist.

---

## 🎯 The Core Challenge

The objective is to identify and rank the top 100 candidates from a pool of 100,000 while meeting strict production constraints:

* **Runtime:** ≤ 5 minutes
* **Hardware:** CPU-only environment
* **Memory:** ≤ 16 GB RAM
* **Network:** Fully offline (no external API calls)
* **Accuracy:** High NDCG and robustness against honeypot profiles

---

## 🏗️ Architecture Overview

CogniHire uses a multi-stage retrieval and ranking architecture designed to maximize both speed and precision.

### The Three-Sieve Pipeline

```text
100,000 Candidates
        │
        ▼
┌─────────────────────┐
│ Semantic Retrieval  │
│ (FAISS + MiniLM)    │
└──────────┬──────────┘
           │
           ▼
      Top 3,000
           │
           ▼
┌─────────────────────┐
│ Intelligence Layer  │
│ Trap Detection      │
│ Persona Analysis    │
│ Behavioral Signals  │
└──────────┬──────────┘
           │
           ▼
       Top 600
           │
           ▼
┌─────────────────────┐
│ Cross Encoder Rank  │
│ Precision Scoring   │
└──────────┬──────────┘
           │
           ▼
       Top 100
```

---

## 🔍 Sieve 1: Semantic Recall (100k → 3k)

### Mechanism

* `all-MiniLM-L6-v2` sentence embeddings
* FAISS `IndexFlatL2` vector search

### Purpose

Rapidly reduce the search space while maintaining high recall.

### Hidden Gem Logic

Instead of embedding only skills, CogniHire generates rich candidate representations using:

* Professional summaries
* Skill inventories
* Work experience descriptions
* Project narratives

This allows the retrieval engine to identify strong candidates whose expertise may not be expressed through exact keyword matches.

---

## 🧠 Sieve 2: Intelligence & Trap Filter (3k → 600)

### Mechanism

A rule-based intelligence layer evaluates profile quality and candidate authenticity.

### Honeypot Detection

Examples include:

* 10 years of experience at age 22
* Unrealistic skill inventories
* Inflated timelines
* Keyword stuffing

### Persona Analysis

#### Consulting Penalty

Candidates with purely consulting-style backgrounds are penalized when the role requires hands-on builders.

#### Shipper vs Researcher Classification

Production-oriented signals:

* deployed
* shipped
* scaled
* maintained
* production

Research-oriented signals:

* studied
* explored
* investigated
* experimented

#### Stability Analysis

Detects:

* Excessive job hopping
* Frequent title inflation
* Unstable employment histories

### Behavioral Multipliers

Uses challenge-provided engagement signals such as:

* `open_to_work`
* `last_active`
* platform engagement metrics

to adjust ranking confidence.

---

## 🎯 Sieve 3: Precision Reranking (600 → 100)

### Mechanism

Local Cross-Encoder:

```text
ms-marco-MiniLM-L-6-v2
```

### Purpose

Unlike embedding similarity, the Cross-Encoder directly evaluates:

```text
(Job Description, Candidate Profile)
```

pairs and produces highly accurate relevance scores.

This stage provides the final ranking used in the submission.

---

## 🛠 Tech Stack

| Component           | Technology            |
| ------------------- | --------------------- |
| Language            | Python 3.10+          |
| Package Manager     | uv                    |
| Embeddings          | sentence-transformers |
| Vector Search       | faiss-cpu             |
| Data Processing     | pandas                |
| Numerical Computing | numpy                 |
| Reranking           | Cross-Encoder         |
| UI Sandbox          | Streamlit             |

---

## 📂 Project Structure

```text
CogniHire/
│
├── data/
│   └── candidates.jsonl
│
├── artifacts/              # Generated locally (git-ignored)
│   ├── embeddings.npy
│   ├── candidate_ids.npy
│   └── faiss.index
│
├── src/
│   ├── precompute.py
│   ├── ranker.py
│   ├── loader.py
│   ├── retrieval.py
│   ├── trap_filter.py
│   ├── reranker.py
│   └── utils.py
│
├── submissions/
│   └── submission.csv
│
├── README.md
├── .gitignore
└── pyproject.toml
```

---

## 📦 Artifact Generation

To keep the repository lightweight and reproducible, the `artifacts/` directory is excluded from version control using `.gitignore`.

The embeddings and FAISS index can be deterministically recreated from the source dataset.

> **Important:** Run the pre-computation step before executing the ranking pipeline.

### Generate Artifacts

```bash
python -m src.precompute
```

Generated files:

```text
artifacts/
├── embeddings.npy
├── candidate_ids.npy
└── faiss.index
```

### Note on Artifacts

To save repository space and ensure reproducibility, the `artifacts/` folder is git-ignored. Please run:

```bash
python -m src.precompute
```

before running the ranker to generate the required embeddings and FAISS index.

---

## 🚀 Setup & Reproduction

### 1. Install Dependencies

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync
```

### 2. Dataset Placement

Place the challenge dataset at:

```text
data/candidates.jsonl
```

### 3. Pre-Computation Phase

Build embeddings and FAISS index.

```bash
python -m src.precompute
```

### 4. Ranking Phase

Generate the final submission.

```bash
python -m src.ranker --out submission.csv
```

Output:

```text
submissions/submission.csv
```

---

## 📈 Current Progress

### Phase 1 — Foundation ✅

* [x] High-performance JSONL Loader
* [x] Candidate Schema Validation
* [x] Rich Text Block Generation
* [x] JD Requirements Mapping
* [x] Embedding Generation
* [x] FAISS Index Construction
* [x] Offline Pre-computation Pipeline

### Phase 2 — Ranking Engine 🚧

* [ ] Semantic Retrieval
* [ ] Candidate Scoring
* [ ] Honeypot Detection
* [ ] Behavioral Multipliers
* [ ] Persona Classification
* [ ] Cross-Encoder Reranking

### Phase 3 — Explainability & Sandbox 🚧

* [ ] Fact-grounded reasoning strings
* [ ] Candidate explainability reports
* [ ] Streamlit sandbox
* [ ] Interactive ranking exploration

### Phase 4 — Submission Readiness 🚧

* [ ] Runtime optimization
* [ ] Validator compliance
* [ ] Benchmarking
* [ ] Final submission package

---

## 🧠 Design Decisions

### Why all-MiniLM-L6-v2?

Provides an excellent balance between:

* Retrieval quality
* CPU performance
* Memory footprint

making it ideal for large-scale candidate search.

### Why FAISS IndexFlatL2?

For a 100k candidate dataset:

* Exact search remains feasible
* No approximation errors
* Maximum retrieval quality
* Easier reproducibility

### Why a Three-Sieve Pipeline?

A single model cannot efficiently optimize:

* Recall
* Precision
* Runtime

The funnel architecture allows:

1. Fast candidate retrieval
2. Intelligent filtering
3. High-precision reranking

while remaining within challenge constraints.

---

## 💡 Innovation Highlights

### Hidden Gem Discovery

Identifies candidates based on:

* Transferable skills
* Career progression
* Project impact
* Production experience

rather than simple keyword overlap.

### Honeypot Resistance

Detects:

* Fake expertise
* Impossible timelines
* Skill inflation
* Resume stuffing

### Recruiter-Aligned Ranking

Prioritizes candidates who have demonstrated the ability to:

* Ship products
* Scale systems
* Deliver measurable outcomes

instead of merely listing technologies.

---

## 👥 Team

| Member            | GitHub                         |
| ----------------- | ------------------------------ |
| Rwitabrato Hanpal | https://github.com/GhostisLive |
| Anushka Ghosh     | https://github.com/Code-0ne    |

### Built By

**Rwitabrato Hanpal** and **Anushka Ghosh**

Developed for the **Redrob Intelligent Candidate Discovery Challenge** as a production-focused talent intelligence platform combining semantic retrieval, behavioral analysis, candidate intelligence scoring, and precision reranking.

---

## 📌 Challenge Alignment

| Requirement               | Status          |
| ------------------------- | --------------- |
| Offline Operation         | ✅               |
| CPU Only                  | ✅               |
| ≤16 GB RAM                | ✅               |
| ≤5 Minute Ranking Runtime | ✅ Design Target |
| Top-100 Candidate Ranking | ✅               |
| Explainable Rankings      | 🚧              |
| Honeypot Detection        | 🚧              |

---

## 🏆 Vision

CogniHire demonstrates how modern retrieval systems, candidate intelligence, and explainable AI can be combined to build a production-grade talent discovery engine capable of surfacing exceptional candidates hidden within large-scale talent pools.

By balancing retrieval speed, ranking precision, and recruiter trust, CogniHire moves beyond keyword matching toward true predictive talent intelligence.
