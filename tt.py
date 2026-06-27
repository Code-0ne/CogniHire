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

# ── GLOBAL CSS (Kept from previous version) ──────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;700&family=JetBrains+Mono:wght@400;600&display=swap');
:root { --navy: #0A0F1E; --card-bg: #111827; --card-border: #1E2D45; --accent-cyan: #00D4FF; --accent-emerald: #00FF88; --text-main: #F0F4FF; --text-muted: #8A9BB5; --glass: rgba(255, 255, 255, 0.03); }
.stApp { background-color: var(--navy); color: var(--text-main); }
[data-testid="stSidebar"] { background-color: var(--card-bg) !important; border-right: 1px solid var(--card-border) !important; }
.hero-container { text-align: left; padding: 2rem 0; border-bottom: 1px solid var(--card-border); margin-bottom: 2rem; }
.hero-eyebrow { font-family: 'JetBrains Mono', monospace; color: var(--accent-cyan); font-size: 0.7rem; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 0.5rem; }
.hero-title { font-family: 'Space Grotesk', sans-serif; font-size: 3.5rem; font-weight: 700; background: linear-gradient(135deg, #00D4FF 0%, #7B61FF 50%, #00FF88 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 1rem; line-height: 1.1; }
.hero-sub { color: var(--text-muted); font-size: 1.1rem; max-width: 700px; margin-bottom: 2rem; }
.pipeline-wrapper { display: flex; align-items: center; gap: 1rem; margin-top: 2rem; }
.pipeline-node { background: var(--glass); border: 1px solid var(--card-border); border-radius: 12px; padding: 0.75rem 1.25rem; display: flex; align-items: center; gap: 0.75rem; min-width: 200px; }
.node-icon { font-size: 1.2rem; background: var(--card-bg); width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; border-radius: 8px; border: 1px solid var(--card-border); }
.node-text { display: flex; flex-direction: column; }
.node-name { font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: 0.85rem; color: var(--text-main); }
.node-tech { font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: var(--accent-cyan); }
.pipeline-arrow { color: var(--card-border); font-size: 1.5rem; }
.metrics-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 2rem; }
.metric-card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 16px; padding: 1.5rem; text-align: center; }
.metric-val { font-family: 'Space Grotesk', sans-serif; font-size: 2rem; font-weight: 700; display: block; }
.metric-lbl { font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; }
[data-testid="stTextArea"] textarea { background-color: var(--card-bg) !important; border: 1px solid var(--card-border) !important; color: var(--text-main) !important; border-radius: 12px !important; }
.stButton > button { background: linear-gradient(135deg, #00D4FF 0%, #7B61FF 100%) !important; color: #000 !important; font-weight: 700 !important; border-radius: 12px !important; border: none !important; }
#MainMenu, footer { visibility: hidden; }
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

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:30px; padding-bottom:20px; border-bottom:1px solid #1E2D45;">
        <div style="width:40px; height:40px; background:linear-gradient(135deg, #00D4FF, #7B61FF); border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:20px;">⚡</div>
        <div>
            <div style="font-family:'Space Grotesk'; font-weight:700; font-size:1.1rem; color:#F0F4FF;">CogniHire</div>
            <div style="font-family:'JetBrains Mono'; font-size:0.6rem; color:#8A9BB5;">TALENT INTEL v1.0</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p style="font-family:Space Grotesk; font-size:0.7rem; font-weight:600; color:#8A9BB5; text-transform:uppercase; letter-spacing:1px;">Configuration</p>', unsafe_allow_html=True)
    jd_input = st.text_area("JD", label_visibility="collapsed", value=TARGET_JD, height=200)

    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
    st.markdown('<p style="font-family:Space Grotesk; font-size:0.7rem; font-weight:600; color:#8A9BB5; text-transform:uppercase; letter-spacing:1px;">Data Source</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Candidates", label_visibility="collapsed", type=["jsonl"])

    if uploaded_file:
        st.markdown(f'<div style="background:rgba(0,255,136,0.1); border:1px solid rgba(0,255,136,0.3); border-radius:12px; padding:12px; margin-top:10px; color:#00FF88; font-size:0.8rem; font-weight:600;">✓ {uploaded_file.name}</div>', unsafe_allow_html=True)
        
        if st.button("🚀 Run Pipeline", use_container_width=True):
            # Start processing
            content = uploaded_file.getvalue().decode("utf-8")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Use st.status to provide a heartbeat (prevents browser freezing)
            with st.status("Executing Three-Sieve Architecture...", expanded=True) as status:
                start_time = time.time()
                st.write("🔍 Sieve 1: Performing Semantic Recall via FAISS...")
                # Simulate a tiny delay for visual effect
                # import time; time.sleep(0.5) 
                
                st.write("🚩 Sieve 2: Applying Intelligence Red-Flag Filter...")
                
                st.write("🎯 Sieve 3: Precision Reranking with Cross-Encoder...")
                
                # Actual cached call
                results = cached_process_pipeline(engine, content, jd_input)
                duration = time.time() - start_time
                
                # Calculate metrics
                total = len(results)
                score_col = next((c for c in results.columns if "score" in c.lower()), None)
                metrics = {
                    "total": total,
                    "top": f"{results[score_col].max():.2f}" if score_col else "—",
                    "avg": f"{results[score_col].mean():.2f}" if score_col else "—",
                    "flagged": int((results[score_col] < 0.4).sum()) if score_col else 0
                }
                
                st.session_state.results = results
                st.session_state.metrics = metrics
                st.session_state.timestamp = timestamp
                st.session_state.duration = f"{duration:.2f}s"
                status.update(label="Pipeline Complete! ✅", state="complete", expanded=False)
    else:
        st.session_state.results = None

# ── MAIN CONTENT ──────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero-container">
<div class="hero-eyebrow">AI-Powered Recruitment &middot; Three-Sieve Architecture</div>
<div class="hero-title">Talent Intelligence<br>Sandbox</div>
<div class="hero-sub">Rank candidates at scale using semantic retrieval, red-flag filtering, and cross-encoder reranking.</div>
<div class="pipeline-wrapper">
<div class="pipeline-node"><div class="node-icon">🔍</div><div class="node-text"><span class="node-name">Semantic Recall</span><span class="node-tech">FAISS &middot; Sieve 1</span></div></div>
<div class="pipeline-arrow">→</div>
<div class="pipeline-node"><div class="node-icon">🚩</div><div class="node-text"><span class="node-name">Intelligence Filter</span><span class="node-tech">Red Flags &middot; Sieve 2</span></div></div>
<div class="pipeline-arrow">→</div>
<div class="pipeline-node"><div class="node-icon">🎯</div><div class="node-text"><span class="node-name">Precision Rerank</span><span class="node-tech">Cross-Encoder &middot; Sieve 3</span></div></div>
</div>
</div>
""", unsafe_allow_html=True)

# Display results if they exist in session state
if st.session_state.results is not None:
    m = st.session_state.metrics
    st.markdown(f"""
    <div class="metrics-grid">
        <div class="metric-card"><span class="metric-val" style="color:var(--accent-cyan)">{m['total']}</span><span class="metric-lbl">Candidates Ranked</span></div>
        <div class="metric-card"><span class="metric-val" style="color:var(--accent-emerald)">{m['top']}</span><span class="metric-lbl">Top Match Score</span></div>
        <div class="metric-card"><span class="metric-val" style="color:var(--accent-cyan)">{m['avg']}</span><span class="metric-lbl">Avg. Score</span></div>
        <div class="metric-card"><span class="metric-val" style="color:#FFB800">{m['flagged']}</span><span class="metric-lbl">Below Threshold</span></div>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown(f"### 🏆 Ranked Candidates ({m['total']})")
        st.caption(f"Last run: {st.session_state.get('timestamp', 'N/A')} | Execution Time: {st.session_state.get('duration', 'N/A')}")
        st.dataframe(st.session_state.results, use_container_width=True, hide_index=True)
    
    csv = st.session_state.results.to_csv(index=False).encode("utf-8")
    st.download_button(label="📥 Export Analysis to CSV", data=csv, file_name="results.csv", mime="text/csv", use_container_width=True)

elif uploaded_file:
    st.markdown("""
    <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; padding:80px 20px; border:2px dashed #1E2D45; border-radius:24px; background:rgba(17,24,39,0.5);">
    <div style="font-size:4rem; margin-bottom:20px;">⚡</div>
    <div style="font-family:'Space Grotesk'; font-size:1.5rem; font-weight:600; color:#F0F4FF; margin-bottom:10px;">Ready for Intelligence Analysis</div>
    <div style="color:#8A9BB5; max-width:400px; line-height:1.6;">Your candidate pool is loaded. Trigger the <b>Three-Sieve Pipeline</b> from the sidebar to begin.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; padding:80px 20px; border:2px dashed #1E2D45; border-radius:24px; background:rgba(17,24,39,0.5);">
    <div style="font-size:4rem; margin-bottom:20px;">📂</div>
    <div style="font-family:'Space Grotesk'; font-size:1.5rem; font-weight:600; color:#F0F4FF; margin-bottom:10px;">Awaiting Candidate Data</div>
    <div style="color:#8A9BB5; max-width:400px; line-height:1.6;">Upload a <code>.jsonl</code> file in the sidebar to initialize the Talent Intelligence sandbox.</div>
    </div>
    """, unsafe_allow_html=True)