import streamlit as st
import pandas as pd
import time
from datetime import datetime
from src.sandbox import CogniHireSandbox
from src.config import TARGET_JD

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CogniHire | Talent Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── GLOBAL CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Cormorant+Garamond:wght@500;600;700&display=swap');
:root {
    --bg: #f5efe6;
    --paper: #fffaf2;
    --panel: #fffdf8;
    --ink: #111111;
    --muted: #6f6a63;
    --line: rgba(17, 17, 17, 0.12);
    --line-strong: rgba(17, 17, 17, 0.2);
    --accent: #7b5c42;
    --accent-soft: rgba(123, 92, 66, 0.1);
    --warm: #d8c4ae;
    --cold: #1f1f1f;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(123, 92, 66, 0.12), transparent 22%),
        radial-gradient(circle at top right, rgba(17, 17, 17, 0.06), transparent 18%),
        linear-gradient(180deg, #f8f1e8 0%, #f3eadf 100%);
    color: var(--ink);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(255, 250, 242, 0.96), rgba(248, 239, 229, 0.98)) !important;
    border-right: 1px solid var(--line) !important;
}

[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {
    color: var(--ink) !important;
}

.shell {
    max-width: 1380px;
    margin: 0 auto;
    padding: 1rem 0 1.5rem;
}

.hero {
    display: grid;
    grid-template-columns: 1.45fr 0.75fr;
    gap: 1rem;
    align-items: stretch;
    margin-bottom: 1rem;
}

.hero-card,
.info-card,
.result-card,
.empty-card,
.sidebar-card {
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 22px;
    box-shadow: 0 18px 48px rgba(17, 17, 17, 0.06);
}

.hero-card {
    padding: 1.8rem;
}

.hero-kicker {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.4rem 0.7rem;
    margin-bottom: 1rem;
    border: 1px solid rgba(123, 92, 66, 0.18);
    border-radius: 999px;
    color: var(--accent);
    background: var(--accent-soft);
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.hero-title {
    margin: 0;
    font-size: clamp(2.8rem, 6vw, 5.6rem);
    line-height: 0.92;
    letter-spacing: -0.055em;
    font-weight: 700;
    font-family: 'Cormorant Garamond', serif;
    text-wrap: balance;
}

.hero-title span {
    color: var(--accent);
}

.hero-sub {
    max-width: 760px;
    margin: 1rem 0 1.4rem;
    color: var(--muted);
    font-size: 1.02rem;
    line-height: 1.7;
}

.pipeline-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.8rem;
}

.pipeline-step {
    padding: 1rem;
    border-radius: 18px;
    border: 1px solid var(--line);
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.9), rgba(255, 250, 242, 0.82));
}

.step-top {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.75rem;
}

.step-badge {
    width: 40px;
    height: 40px;
    border-radius: 14px;
    display: grid;
    place-items: center;
    background: rgba(123, 92, 66, 0.08);
    border: 1px solid rgba(123, 92, 66, 0.14);
    font-size: 1.05rem;
}

.step-label {
    font-size: 0.88rem;
    font-weight: 700;
}

.step-meta {
    color: var(--muted);
    font-size: 0.78rem;
    line-height: 1.5;
}

.info-card {
    padding: 1.45rem;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.info-title {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: var(--muted);
    margin-bottom: 0.75rem;
}

.info-role {
    font-size: 1.9rem;
    font-weight: 700;
    line-height: 1;
    font-family: 'Cormorant Garamond', serif;
    margin-bottom: 0.85rem;
}

.info-copy {
    color: var(--muted);
    line-height: 1.65;
    margin-bottom: 1rem;
}

.pill-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.55rem;
}

.pill {
    border-radius: 999px;
    padding: 0.42rem 0.7rem;
    border: 1px solid var(--line);
    background: rgba(123, 92, 66, 0.05);
    color: var(--ink);
    font-size: 0.78rem;
    font-weight: 600;
}

.content-grid {
    display: grid;
    grid-template-columns: 0.78fr 1.22fr;
    gap: 1rem;
    align-items: start;
}

.sidebar-card {
    padding: 1rem;
}

.sidebar-card .section-title,
.section-title {
    margin: 0 0 0.65rem;
    color: var(--muted);
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}

.sidebar-cta {
    margin-top: 0.9rem;
}

[data-testid="stFileUploader"] {
    border-radius: 18px;
}

[data-testid="stFileUploader"] section {
    padding: 0.6rem 0.1rem;
}

.stButton > button {
    width: 100%;
    background: #111111 !important;
    color: #fffaf2 !important;
    font-weight: 800 !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.8rem 1rem !important;
    box-shadow: 0 10px 24px rgba(17, 17, 17, 0.14);
}

.stButton > button:hover {
    transform: translateY(-1px);
}

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 1rem;
    margin-bottom: 1rem;
}

.metric-card {
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.95), rgba(255, 250, 242, 0.96));
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 1rem;
}

.metric-val {
    display: block;
    font-size: 1.9rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    line-height: 1;
    margin-bottom: 0.35rem;
}

.metric-lbl {
    display: block;
    font-size: 0.74rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--muted);
}

.result-card {
    padding: 1.25rem;
}

.result-head {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 1rem;
}

.result-head h3 {
    margin: 0;
    font-size: 1.2rem;
}

.result-head p {
    margin: 0.25rem 0 0;
    color: var(--muted);
}

[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
}

.empty-card {
    padding: 2rem;
    text-align: center;
}

.empty-icon {
    font-size: 2.8rem;
    margin-bottom: 0.75rem;
}

.empty-card h3 {
    margin: 0 0 0.4rem;
    font-size: 1.35rem;
}

.empty-card p {
    margin: 0;
    color: var(--muted);
    line-height: 1.6;
}

.sidebar-card .section-title {
    margin-bottom: 0.4rem;
}

[data-testid="stTextArea"] textarea {
    background: #fffdf8 !important;
    border: 1px solid var(--line) !important;
    color: var(--ink) !important;
    border-radius: 14px !important;
}

[data-testid="stFileUploader"] {
    border-radius: 18px;
}

[data-testid="stFileUploader"] section {
    padding: 0.6rem 0.1rem;
}

[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] p {
    color: var(--muted) !important;
}

[data-testid="stDataFrame"] [role="grid"] {
    font-size: 0.92rem;
}

[data-testid="stDataFrame"] div[data-testid="stDataFrameResizable"] {
    border: 1px solid var(--line);
    border-radius: 18px;
}

#MainMenu, footer { visibility: hidden; }

@media (max-width: 1100px) {
    .hero, .content-grid { grid-template-columns: 1fr; }
    .pipeline-grid, .metrics-grid { grid-template-columns: 1fr; }
}
</style>
""", unsafe_allow_html=True)

# ── ENGINE & CACHING ────────────────────────────────────────────────────────────

@st.cache_resource
def get_sandbox_engine():
    return CogniHireSandbox()

# We cache the actual processing function. 
# If the JD and content are the same, Streamlit skips the AI and returns the result instantly.
@st.cache_data(show_spinner=False)
def cached_process_pipeline(_engine, content, jd):
    return _engine.process_pipeline(content, jd)

engine = get_sandbox_engine()

# Initialize Session State to prevent results from disappearing on rerun
if "results" not in st.session_state:
    st.session_state.results = None
if "metrics" not in st.session_state:
    st.session_state.metrics = None

TARGET_SUMMARY = [
    "Production AI / ML roles",
    "Retrieval, ranking, vector search",
    "Evaluation, deployment, scale",
]

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-card" style="margin-bottom: 1rem;">
        <div class="section-title">CogniHire</div>
        <div style="font-size: 1.35rem; font-weight: 800; line-height: 1.1; margin-bottom: 0.5rem;">Talent Intelligence</div>
        <div style="color: var(--muted); line-height: 1.6;">Upload a candidate JSONL file and run the three-sieve ranking pipeline.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-card" style="margin-bottom: 1rem;">
        <div class="section-title">Target Role</div>
        <div style="font-size: 1.05rem; font-weight: 700; line-height: 1.35; margin-bottom: 0.8rem;">Senior AI Engineer, founding team</div>
        <div class="pill-row">
            <span class="pill">Production grade</span>
            <span class="pill">Retrieval + ranking</span>
            <span class="pill">5-9 years</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="section-title">Data Source</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Candidates", label_visibility="collapsed", type=["jsonl"])

    if uploaded_file:
        st.markdown(f'<div style="margin-top:0.75rem; padding:0.75rem 0.9rem; border:1px solid rgba(123,92,66,0.18); border-radius:14px; background:rgba(123,92,66,0.05); color:var(--ink); font-size:0.85rem; font-weight:600;">✓ {uploaded_file.name}</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-cta"></div>', unsafe_allow_html=True)

        if st.button("Run Pipeline", use_container_width=True):
            content = uploaded_file.getvalue().decode("utf-8")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with st.status("Running three-sieve ranking pipeline...", expanded=True) as status:
                start_time = time.time()
                st.write("Semantic recall over the full candidate set...")
                st.write("Filtering obvious mismatches and red flags...")
                st.write("Cross-encoder reranking and reasoning generation...")

                results = cached_process_pipeline(engine, content, TARGET_JD)
                duration = time.time() - start_time

                score_col = next((c for c in results.columns if "score" in c.lower()), None)
                metrics = {
                    "total": len(results),
                    "top": f"{results[score_col].max():.2f}" if score_col else "—",
                    "avg": f"{results[score_col].mean():.2f}" if score_col else "—",
                    "flagged": int((results[score_col] < 0.4).sum()) if score_col else 0,
                }

                st.session_state.results = results
                st.session_state.metrics = metrics
                st.session_state.timestamp = timestamp
                st.session_state.duration = f"{duration:.2f}s"
                status.update(label="Pipeline complete", state="complete", expanded=False)
    else:
        st.session_state.results = None

# ── MAIN CONTENT ──────────────────────────────────────────────────────────────

st.markdown(f"""
<div class="shell">
    <div class="hero">
        <div class="hero-card">
            <div class="hero-kicker">AI recruitment intelligence · editorial edition</div>
            <h1 class="hero-title">Talent ranking with <span>clarity, gravity, and speed</span>.</h1>
            <div class="hero-sub">CogniHire ranks candidates with semantic recall, signal-based filtering, and cross-encoder reranking. The layout now behaves like a polished editorial board: fewer distractions, more hierarchy, sharper contrast.</div>
            <div class="pipeline-grid">
                <div class="pipeline-step">
                    <div class="step-top"><div class="step-badge">🔍</div><div><div class="step-label">Sieve 1 · Recall</div></div></div>
                    <div class="step-meta">FAISS retrieves the strongest semantic matches from the full candidate set.</div>
                </div>
                <div class="pipeline-step">
                    <div class="step-top"><div class="step-badge">🚩</div><div><div class="step-label">Sieve 2 · Filter</div></div></div>
                    <div class="step-meta">Experience, production evidence, and red-flag checks remove weak fits early.</div>
                </div>
                <div class="pipeline-step">
                    <div class="step-top"><div class="step-badge">🎯</div><div><div class="step-label">Sieve 3 · Rank</div></div></div>
                    <div class="step-meta">A cross-encoder produces the final order, with reasoning for every candidate.</div>
                </div>
            </div>
        </div>
        <div class="info-card">
            <div>
                <div class="info-title">Fixed target role</div>
                <div class="info-role">Senior AI Engineer</div>
                <div class="info-copy">5-9 years. Production AI/ML. Retrieval, ranking, vector search, evaluation, and deployment signals are weighted into the final score.</div>
            </div>
            <div class="pill-row">
                {''.join(f'<span class="pill">{item}</span>' for item in TARGET_SUMMARY)}
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Display results if they exist in session state
if st.session_state.results is not None:
    m = st.session_state.metrics
    left_col, right_col = st.columns([0.92, 1.08], gap="large")
    with left_col:
        st.markdown(f"""
        <div class="result-card">
            <div class="section-title">Pipeline output</div>
            <div class="metrics-grid">
                <div class="metric-card"><span class="metric-val" style="color: var(--accent)">{m['total']}</span><span class="metric-lbl">Candidates ranked</span></div>
                <div class="metric-card"><span class="metric-val" style="color: var(--accent)">{m['top']}</span><span class="metric-lbl">Top score</span></div>
                <div class="metric-card"><span class="metric-val" style="color: var(--accent)">{m['avg']}</span><span class="metric-lbl">Average score</span></div>
                <div class="metric-card"><span class="metric-val" style="color: var(--accent)">{m['flagged']}</span><span class="metric-lbl">Below threshold</span></div>
            </div>
            <div style="color: var(--muted); font-size: 0.9rem;">Last run: {st.session_state.get('timestamp', 'N/A')} · Execution time: {st.session_state.get('duration', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)

    with right_col:
        st.markdown("""
        <div class="result-card">
            <div class="result-head">
                <div>
                    <h3>Ranked candidates</h3>
                    <p>Top 100 candidates with score and reasoning.</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.dataframe(st.session_state.results, use_container_width=True, hide_index=True)
        csv = st.session_state.results.to_csv(index=False).encode("utf-8")
        st.download_button(label="Export results CSV", data=csv, file_name="results.csv", mime="text/csv", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif uploaded_file:
    st.markdown("""
    <div class="empty-card">
        <div class="empty-icon">⚡</div>
        <h3>File loaded. Ready to rank.</h3>
        <p>Run the pipeline from the sidebar to generate the ranked shortlist and reasoning report.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="empty-card">
        <div class="empty-icon">📂</div>
        <h3>Awaiting candidate data</h3>
        <p>Upload a .jsonl file in the sidebar to initialize the talent intelligence sandbox.</p>
    </div>
    """, unsafe_allow_html=True)