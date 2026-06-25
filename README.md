# 🚀 CogniHire: Predictive Talent Intelligence Engine

**Built for the Redrob Intelligent Candidate Discovery Challenge**

CogniHire is a high-performance ranking engine designed to discover "hidden gems" within massive talent pools. Moving beyond surface-level keyword matching, CogniHire evaluates **semantic fit, career trajectory, behavioral signals, and production readiness** to generate a precise, explainable, and high-confidence shortlist.

---

## 🎯 The Core Challenge

The objective was to identify and rank the top 100 candidates from a pool of 100,000 while meeting strict production constraints to ensure scalability and cost-efficiency:

* **Runtime:** $\le 5$ minutes for the ranking step.
* **Hardware:** CPU-only environment.
* **Memory:** $\le 16$ GB RAM.
* **Network:** Fully offline (no external API calls during ranking).
* **Accuracy:** High NDCG and robustness against honeypot profiles.

---

## 🏗️ Architecture Overview

CogniHire implements a multi-stage **Three-Sieve Pipeline** to balance extreme retrieval speed with deep precision.

### The Pipeline Flow

```text
100,000 Candidates
        │
        ▼
┌─────────────────────┐
│  Sieve 1: Recall    │  (FAISS + all-MiniLM-L6-v2)
│  Semantic Search    │  → Reduces 100k to Top 3,000
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Sieve 2: Intelligence│  (Rule-based Logic & Signal Weights)
│  Trap & Persona Filter│  → Reduces 3,000 to Top 200
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Sieve 3: Precision  │  (Local Cross-Encoder)
│  Deep Reranking     │  → Produces Final Top 100
└──────────┬──────────┘
           │
           ▼
       Top 100
```

---

## 🔍 Sieve Detailed Analysis

### Sieve 1: Semantic Recall
- **Mechanism:** Uses `all-MiniLM-L6-v2` embeddings and a **FAISS `IndexFlatL2`** vector search.
- **Rich Text Blocks:** Instead of embedding only skills, CogniHire generates rich representations combining professional summaries, skill inventories, and actual prose from career descriptions.
- **Purpose:** To identify candidates with the right *conceptual* fit, even if they don't use the exact keywords found in the JD.

### Sieve 2: Intelligence & Trap Filter
A logic-heavy layer that evaluates candidate authenticity and "persona" fit:
- **Honeypot Detection:** Identifies "impossible" profiles (e.g., 15 years of experience for a 22-year-old) and "keyword stuffers" (expert in 20+ skills with 0 months of usage).
- **Persona Analysis:**
    - **Consulting Penalty:** Hard-penalizes candidates with purely consulting backgrounds.
    - **Shipper vs. Researcher:** Scans for production signals (*"deployed", "scaled", "shipped"*) vs. purely theoretical signals (*"studied", "explored"*).
    - **Stability Check:** Detects "Title-Chasers" through tenure-per-company analysis.
- **Behavioral Multipliers:** Integrates `redrob_signals` (e.g., `open_to_work`, `recruiter_response_rate`, and `notice_period`) to adjust the final confidence score.

### Sieve 3: Precision Reranking
- **Mechanism:** A local **Cross-Encoder** (`ms-marco-MiniLM-L-6-v2`).
- **Purpose:** Unlike cosine similarity, the Cross-Encoder performs a deep, token-level interaction analysis between the Job Description and the candidate's profile to ensure the final top 100 are absolute fits.

---

## 🛠 Tech Stack

| Component           | Technology            |
| ------------------- | --------------------- |
| Language            | Python 3.10+          |
| Package Manager     | `uv` (Fast/Reproducible)|
| Embeddings          | `sentence-transformers` |
| Vector Search       | `faiss-cpu`             |
| Data Processing     | `pandas`, `numpy`      |
| Reranking           | `Cross-Encoder`       |
| UI Sandbox          | `streamlit`           |

---

## 📂 Project Structure

```text
CogniHire/
├── data/                   # Dataset (candidates.jsonl)
├── artifacts/              # Precomputed index & embeddings (git-ignored)
├── src/
│   ├── config.py           # Central brain (weights, constants, lists)
│   ├── loader.py           # High-performance JSONL reader
│   ├── text_builder.py     # Rich text block generator
│   ├── precompute.py       # Offline embedding & indexing pipeline
│   ├── sieve_engine.py     # Sieve 1 & 2 implementation
│   ├── res_gen.py          # Fact-grounded justification engine
│   ├── ranker.py           # Main orchestrator (The Ranking Step)
│   └── sandbox.py          # Logic for the Streamlit demo
├── app.py                  # Streamlit UI
├── requirements.txt        # Dependencies
└── .gitignore
```

---

## 🚀 Setup & Reproduction

### 1. Installation
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
```

### 2. Pre-Computation (Offline)
To meet the 5-minute ranking constraint, embeddings are precomputed.
```bash
python -m src.precompute
```

### 3. Ranking (The Submission Step)
Generates the final `submission.csv` in under 5 minutes on a CPU.
```bash
python -m src.ranker --out submission.csv
```

### 4. Sandbox Demo
Run the interactive dashboard:
```bash
streamlit run app.py
```

---

## 🌐 Sandbox & Explainability

### Fact-Grounded Reasoning
To avoid LLM hallucinations, CogniHire uses a **Fact-Extraction Engine**. The justifications in the CSV are not "generated" by a prompt, but "assembled" from actual candidate data:
- **Example:** *"Top-tier fit: Senior ML Engineer with 6.8 years of experience. Strong match based on production experience at Dream11. Key signals: Actively open to work."*

### The Sandbox Experience
The Streamlit app provides a real-time demo. To ensure a seamless experience:
- **On-the-Fly Indexing:** For small samples, the app bypasses disk artifacts and encodes candidates in RAM.
- **Smart Sampling:** For large uploads, the app samples the top 2,000 candidates to ensure response times remain under 30 seconds.

---

## 👥 Team
**Rwitabrato Hanpal** ([GitHub](https://github.com/GhostisLive)) & **Anushka Ghosh** ([GitHub](https://github.com/Code-0ne))

Developed for the **Redrob Intelligent Candidate Discovery Challenge**.