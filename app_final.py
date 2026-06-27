import streamlit as st
import pandas as pd
import time
from datetime import datetime
from src.sandbox import CogniHireSandbox
from src.config import TARGET_JD
from st_aggrid import (
    AgGrid,
    GridOptionsBuilder,
    GridUpdateMode,
    JsCode,
)

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CogniHire | Talent Intelligence",
    page_icon="⚡",
    layout="wide",
)

# ── THEME MANAGEMENT ───────────────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# KEY HACK: This key allows us to reset the file uploader instantly without a popup
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

def clear_dataset():
    st.session_state.results = None
    st.session_state.metrics = None
    st.session_state.uploader_key += 1 # Changing the key destroys the old uploader (no popup!)

if st.session_state.theme == "dark":
    colors = {
        "bg": "#0A0F1E", "card": "#111827", "border": "#1E2D45",
        "text": "#F0F4FF", "muted": "#8A9BB5", "accent": "#00D4FF",
        "glass": "rgba(255, 255, 255, 0.03)", "input_bg": "#1A2235",
        "download_bg": "#1A2235", "download_text": "#F0F4FF", "download_border": "#1E2D45", "download_hover": "#252F45",
        "upload_bg": "#1A2235", "upload_text": "#F0F4FF", "upload_hover": "#252F45",
        "pill_bg": "#1A2235", "pill_text": "#F0F4FF"
    }
else:
    colors = {
        "bg": "#F1F5F9", "card": "#FFFFFF", "border": "#CBD5E1",
        "text": "#0F172A", "muted": "#64748B", "accent": "#2563EB",
        "glass": "rgba(0, 0, 0, 0.03)", "input_bg": "#FFFFFF",
        "download_bg": "#FFFFFF", "download_text": "#0F172A", "download_border": "#CBD5E1", "download_hover": "#F8FAFC",
        "upload_bg": "#FFFFFF", "upload_text": "#0F172A", "upload_hover": "#F8FAFC",
        "pill_bg": "#FFFFFF", "pill_text": "#0F172A"
    }

# ── GLOBAL CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [data-testid="stAppViewContainer"] {{
    background-color: {colors['bg']} !important;
    color: {colors['text']} !important;
    font-family: 'Inter', sans-serif;
}}

#MainMenu, footer, header {{ visibility: hidden; }}

/* Glassmorphism Card Base */
.glass-card {{
    background: {colors['glass']};
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid {colors['border']};
    border-radius: 24px;
    padding: 2rem;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
}}

.hero-container {{
    text-align: left;
    padding: 2rem 0 4rem 0;
    margin-bottom: 3rem;
}}
.hero-eyebrow {{
    font-family: 'JetBrains Mono', monospace;
    color: {colors['accent']};
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 3px;
    margin-bottom: 1rem;
    font-weight: 600;
}}
.hero-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 4rem;
    font-weight: 700;
    background: linear-gradient(135deg, #00D4FF 0%, #7B61FF 50%, #00FF88 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1.5rem;
    line-height: 1.1;
    letter-spacing: -2px;
}}
.hero-sub {{
    color: {colors['muted']};
    font-size: 1.2rem;
    max-width: 800px;
    margin-bottom: 3rem;
    line-height: 1.6;
    font-weight: 300;
}}

.pipeline-wrapper {{
    display: flex;
    align-items: center;
    gap: 1.5rem;
    margin-top: 3rem;
}}
.pipeline-node {{
    background: {colors['glass']};
    border: 1px solid {colors['border']};
    border-radius: 16px;
    padding: 1rem 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    min-width: 220px;
    transition: all 0.3s ease;
}}
.pipeline-node:hover {{
    border-color: {colors['accent']};
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0, 212, 255, 0.1);
}}
.node-icon {{
    font-size: 1.4rem;
    background: {colors['card']};
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    border: 1px solid {colors['border']};
}}
.node-name {{ font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: 0.9rem; color: {colors['text']}; }}
.node-tech {{ font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: {colors['accent']}; }}
.pipeline-arrow {{ color: {colors['border']}; font-size: 1.8rem; font-weight: 300; }}

.metrics-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1.5rem;
    margin-bottom: 3rem;
}}
.metric-card {{
    background: {colors['card']};
    border: 1px solid {colors['border']};
    border-radius: 24px;
    padding: 2rem;
    text-align: center;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}}
.metric-card:hover {{
    border-color: {colors['accent']};
    transform: scale(1.02);
    box-shadow: 0 0 20px rgba(0, 212, 255, 0.1);
}}
.metric-val {{ font-family: 'Space Grotesk', sans-serif; font-size: 2.5rem; font-weight: 700; display: block; margin-bottom: 0.5rem; }}
.metric-lbl {{ font-size: 0.75rem; color: {colors['muted']}; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 500; }}

[data-testid="stFileUploader"] section {{
    background-color: {colors['input_bg']} !important;
    border: 1px solid {colors['border']} !important;
    border-radius: 20px !important;
    padding: 1rem !important;
}}

[data-testid="stFileUploader"] button {{
    background-color: {colors['upload_bg']} !important;
    color: {colors['upload_text']} !important;
    border: 1px solid {colors['border']} !important;
    border-radius: 12px !important;
    transition: all 0.2s ease !important;
}}
[data-testid="stFileUploader"] button:hover {{
    background-color: {colors['upload_hover']} !important;
    border-color: {colors['accent']} !important;
}}

.stButton > button {{
    background: linear-gradient(135deg, #00D4FF 0%, #7B61FF 100%) !important;
    color: #000 !important;
    font-weight: 700 !important;
    border-radius: 16px !important;
    border: none !important;
    padding: 0.75rem 1.5rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-size: 0.85rem !important;
}}
.stButton > button:hover {{ 
    transform: translateY(-3px); 
    box-shadow: 0 12px 24px rgba(0, 212, 255, 0.3); 
    filter: brightness(1.1);
}}

[data-testid="stDownloadButton"] button {{
    background-color: {colors['download_bg']} !important;
    color: {colors['download_text']} !important;
    border: 1px solid {colors['download_border']} !important;
    border-radius: 16px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}}
[data-testid="stDownloadButton"] button:hover {{
    background-color: {colors['download_hover']} !important;
    border-color: {colors['accent']} !important;
}}

</style>
""", unsafe_allow_html=True)


if st.session_state.theme == "light":
    st.markdown("""
<style>
[data-testid="stDataFrame"]{
    background:#fff !important;
    border:1px solid #dbe4ee !important;
}
[data-testid="stDataFrame"] *{
    color:#0f172a !important;
}
[data-testid="stDataFrame"] [role="grid"]{
    background:#fff !important;
}
[data-testid="stDataFrame"] [role="columnheader"]{
    background:#f8fafc !important;
    color:#0f172a !important;
}
[data-testid="stDataFrame"] [role="gridcell"]{
    background:#fff !important;
    color:#0f172a !important;
}
[data-testid="stDataFrame"] canvas{
    filter:invert(1) hue-rotate(180deg);
}
</style>
""", unsafe_allow_html=True)


# ── ENGINE & CACHING ────────────────────────────────────────────────────────────

@st.cache_resource
def get_sandbox_engine():
    return CogniHireSandbox()

@st.cache_data(show_spinner=False)
def cached_process_pipeline(_engine, content, jd):
    return _engine.process_pipeline(content, jd)

engine = get_sandbox_engine()

if "results" not in st.session_state:
    st.session_state.results = None
if "metrics" not in st.session_state:
    st.session_state.metrics = None

# ── TOP BAR ────────────────────────────────────────────────────────────────────
col_spacer, col_theme = st.columns([9, 1])
with col_theme:
    st.button("🌓 Switch Theme", on_click=toggle_theme)

# ── HERO SECTION ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-container">
    <div class="hero-eyebrow">AI-Powered Recruitment &middot; Three-Sieve Architecture</div>
    <div class="hero-title">CogniHire</div>
    <div class="hero-sub">Rank candidates at scale using semantic retrieval, red-flag filtering, and cross-encoder reranking.</div>
    <div class="pipeline-wrapper">
        <div class="pipeline-node">
            <div class="node-icon">🔍</div>
            <div class="node-text">
                <span class="node-name">Semantic Recall</span><br>
                <span class="node-tech">FAISS &middot; Sieve 1</span>
            </div>
        </div>
        <div class="pipeline-arrow">→</div>
        <div class="pipeline-node">
            <div class="node-icon">🚩</div>
            <div class="node-text">
                <span class="node-name">Intelligence Filter</span><br>
                <span class="node-tech">Red Flags &middot; Sieve 2</span>
            </div>
        </div>
        <div class="pipeline-arrow">→</div>
        <div class="pipeline-node">
            <div class="node-icon">🎯</div>
            <div class="node-text">
                <span class="node-name">Precision Rerank</span><br>
                <span class="node-tech">Cross-Encoder &middot; Sieve 3</span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── CONTROL PANEL ──────────────────────────────────────────────────────────────
with st.container():
    st.markdown(f"""
    <div class="glass-card" style="text-align: center; margin-bottom: 3rem;">
        <div style="font-family: 'Space Grotesk'; font-weight: 600; color: {colors['text']}; margin-bottom: 1.5rem; font-size: 1.2rem;">
            Candidate Pool Configuration
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    _, col_center, _ = st.columns([1, 2, 1])
    with col_center:
        jd_input = TARGET_JD 
        
        uploaded_file = st.file_uploader(
            "Upload Candidate Pool (.jsonl)", 
            type=["jsonl"], 
            label_visibility="collapsed", 
            key=f"uploader_{st.session_state.uploader_key}" 
        )
        
        btn_col1, btn_col2 = st.columns([3, 1])
        with btn_col1:
            run_pipeline = st.button("🚀 Run Intelligence Pipeline", use_container_width=True)
        with btn_col2:
            st.button("🗑️ Clear", on_click=clear_dataset, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── EXECUTION ──────────────────────────────────────────────────────────────────
if uploaded_file and run_pipeline:
    content = uploaded_file.getvalue().decode("utf-8")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    status_box = st.empty()

    status_box.markdown(f"""
    <div style="
        background:{colors['card']};
        border:1px solid {colors['border']};
        border-radius:14px;
        padding:18px 22px;
        margin-bottom:15px; 
    ">
        <h4 style="margin:0;color:{colors['text']};">
            ⚡ Executing Three-Sieve Architecture...
        </h4>
    </div>
    """, unsafe_allow_html=True)

    progress = st.empty()

    progress.markdown(f"""
    <div style="
        background:{colors['card']};
        border:1px solid {colors['border']};
        border-radius:14px;
        padding:18px 22px;
        line-height:2;
    ">
    🔍 Sieve 1: Performing Semantic Recall via FAISS...<br>
    🚩 Sieve 2: Applying Intelligence Red-Flag Filter...<br>
    🎯 Sieve 3: Precision Reranking with Cross-Encoder...
    </div>
    """, unsafe_allow_html=True)

    start_time = time.time()
    results = cached_process_pipeline(engine, content, jd_input)
    duration = time.time() - start_time
    total = len(results)

    score_col = next(
        (c for c in results.columns if "score" in c.lower()),
        None,
    )

    metrics = {
        "total": total,
        "top": f"{results[score_col].max():.2f}" if score_col else "—",
        "avg": f"{results[score_col].mean():.2f}" if score_col else "—",
        "flagged": int((results[score_col] < 0.4).sum()) if score_col else 0,
    }

    st.session_state.results = results
    st.session_state.metrics = metrics
    st.session_state.timestamp = timestamp
    st.session_state.duration = f"{duration:.2f}s"

    status_box.success("✅ Pipeline Complete!")
    progress.empty()


# ── RESULTS SECTION ────────────────────────────────────────────────────────────
if st.session_state.results is not None:
    m = st.session_state.metrics
    
    st.markdown(f"""
    <div class="metrics-grid">
        <div class="metric-card"><span class="metric-val" style="color:{colors['accent']}">{m['total']}</span><span class="metric-lbl">Candidates Ranked</span></div>
        <div class="metric-card"><span class="metric-val" style="color:#10B981">{m['top']}</span><span class="metric-lbl">Top Match Score</span></div>
        <div class="metric-card"><span class="metric-val" style="color:{colors['accent']}">{m['avg']}</span><span class="metric-lbl">Avg. Score</span></div>
        <div class="metric-card"><span class="metric-val" style="color:#F59E0B">{m['flagged']}</span><span class="metric-lbl">Below Threshold</span></div>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown(f"### 🏆 Ranked Candidates ({m['total']})")
        st.caption(f"🕒 Last Run: {st.session_state.timestamp}    •    ⚡ Execution Time: {st.session_state.duration}")

        # ---------- Custom Renderers ----------

        rank_renderer = JsCode("""
        function(params){
            const r = Number(params.value);

            if(r===1) return "🥇";
            if(r===2) return "🥈";
            if(r===3) return "🥉";

            return r;
        }
        """)

        gb = GridOptionsBuilder.from_dataframe(st.session_state.results)

        # Completely remove internal/unnecessary columns from the dataframe before building grid
        cols_to_remove = ["auto_unique_id", "__index_level_0__", "Unnamed: 0"]
        st.session_state.results = st.session_state.results.drop(columns=[c for c in cols_to_remove if c in st.session_state.results.columns])

        gb.configure_default_column(
            sortable=True,
            filter=True,
            resizable=True,
        )

        gb.configure_column("rank", width=100, pinned="left", cellRenderer=rank_renderer,)

        gb.configure_column("candidate_id", width=200, pinned="left", cellStyle={"color": "#60A5FA","fontWeight": "700","fontFamily": "JetBrains Mono, monospace",},    )  

        gb.configure_column("score", width=120, valueFormatter="Number(value).toFixed(2)",cellStyle={"fontWeight": "700","fontSize": "15px",},)

        if "reasoning" in st.session_state.results.columns:
            # Use a simple string for the renderer to avoid JsCode function issues if they persist
            # Or ensure the JsCode is perfectly formatted.
            reason_renderer = JsCode("""
            function(params) {
                var val = params.value || "";
                return val.length > 120 ? val.substring(0, 117) + "..." : val;
            }
            """)
            gb.configure_column(
                "reasoning",
                headerName="Reasoning",
                flex=1,
                minWidth=400,
                wrapText=False,
                autoHeight=False,
                tooltipField="reasoning",
                cellRenderer=reason_renderer,
                cellStyle={
                    "whiteSpace": "nowrap",
                    "lineHeight": "1.6",
                    "display": "flex",
                    "alignItems": "center",
                    "text-overflow": "ellipsis",
                },
            )

        gb.configure_grid_options(
            domLayout="normal",
            rowHeight=50,
            headerHeight=52,
            animateRows=True,
            suppressRowClickSelection=False,
            suppressRowTransform=True,
        )

        grid_options = gb.build()

        if st.session_state.theme == "light":
            custom_css = {
                ".ag-root-wrapper": {
                    "border": "1px solid #CBD5E1",
                    "border-radius": "16px",
                },
                ".ag-header": {
                    "background-color": "#F8FAFC",
                    "font-size":"14px",
                    "font-weight": "700",
                    "border-bottom":"2px solid #2563EB",
                    "box-shadow":"0 1px 0 rgba(0,0,0,.08)",
                },
                ".ag-header-cell-label":{
                    "justify-content":"center",
                },
                ".ag-header-cell":{
                    "border-right":"1px solid #D5DCE6",
                },
                ".ag-cell":{    
                    "font-size":"14px",
                    "border-right":"1px solid #E2E8F0",
                    "white-space":"normal",
                    "line-height":"1.6",
                    "padding":"10px",
                },
                ".ag-row": {
                    "border-bottom":"1px solid #EEF2F7",
                },
                ".ag-row:nth-child(even)":{
                    "background-color":"#FBFCFE",
                },
                ".ag-row-hover":{
                    "background-color":"#EFF6FF !important",
                },
            }
            theme = "balham"
        else:
            custom_css = {
                ".ag-root-wrapper": {
                    "background-color": "#111827",
                    "border": "1px solid #1F2937",
                    "border-radius": "16px",
                },
                ".ag-header": {
                    "background-color": "#162033",
                    "border-bottom": "2px solid #00D4FF",
                    "box-shadow":"0 1px 0 rgba(255,255,255,.04)",
                    "height": "52px",
                },
                ".ag-header-cell": {
                    "border-right":"1px solid #314158 !important",
                },
                ".ag-header-cell-label": {
                    "color": "#FFFFFF",
                    "font-weight": "700",
                    "font-size": "15px",
                    "justify-content": "center",
                },
                ".ag-row": {
                    "background-color": "#111827",
                    "color": "#F8FAFC",
                    "border-bottom": "1px solid #243044",
                    "transition": "all .15s ease",
                },
                ".ag-row:nth-child(even)": {
                    "background-color": "#131E31",
                },
                ".ag-row-hover": {
                    "background-color": "#213A63 !important",
                },
                ".ag-cell": {
                    "color": "#F8FAFC",
                    "font-size": "14px",
                    "line-height": "1.6",
                    "border-right":"1px solid #314158 !important",
                    "box-sizing":"border-box",
                    "white-space":"normal",
                    "padding":"10px",
                },
                ".ag-cell-focus": {
                    "border": "1px solid #00D4FF !important",
                },
                ".ag-pinned-left-cols-container": {
                    "background-color": "#111827",
                    "border-right": "1px solid #314158",
                },
                ".ag-pinned-left-header": {
                    "border-right": "1px solid #314158",
                },
                ".ag-center-cols-container": {
                    "background-color": "#111827",
                },
                ".ag-pinned-left-cols-container .ag-cell": {
                    "border-right":"1px solid #314158 !important",
                },
                ".ag-center-cols-container .ag-cell": {
                    "border-right":"1px solid #314158 !important",
                },
                ".ag-body-viewport": {
                    "background-color": "#111827",
                },
                ".ag-row-selected": {
                    "background-color": "#1E3A5F !important",
                },
                ".ag-root": {
                    "color": "#F8FAFC",
                },
                ".ag-menu": {
                    "background-color": "#1A2235",
                },
                ".ag-popup": {
                    "background-color": "#1A2235",
                },
                ".ag-tooltip": {
                    "background-color": "#1F2A40",
                    "color": "#FFFFFF",
                    "border": "1px solid #00D4FF",
                    "border-radius": "10px",
                    "padding": "12px",
                    "font-size": "14px",
                },
            }
            theme = "balham-dark"

        AgGrid(
            st.session_state.results,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.NO_UPDATE,
            fit_columns_on_grid_load=False,
            height=800,
            allow_unsafe_jscode=True,
            enable_enterprise_modules=False,
            theme=theme,
            custom_css=custom_css,
        )
    
    csv = st.session_state.results.to_csv(index=False).encode("utf-8")
    st.markdown("---")
    st.download_button(label="📥 Export Analysis to CSV", data=csv, file_name="results.csv", mime="text/csv", use_container_width=True)

elif uploaded_file:
    st.markdown(f"""
    <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; padding:80px 20px; border:2px dashed {colors['border']}; border-radius:24px; background:{colors['glass']};">
    <div style="font-size:4rem; margin-bottom:20px;">⚡</div>
    <div style="font-family:'Space Grotesk'; font-size:1.5rem; font-weight:600; color:{colors['text']}; margin-bottom:10px;">Ready for Intelligence Analysis</div>
    <div style="color:{colors['muted']}; max-width:400px; line-height:1.6;">Your candidate pool is loaded. Trigger the <b>Three-Sieve Pipeline</strong> above to begin.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; padding:80px 20px; border:2px dashed {colors['border']}; border-radius:24px; background:{colors['glass']};">
    <div style="font-size:4rem; margin-bottom:20px;">📂</div>
    <div style="font-family:'Space Grotesk'; font-size:1.5rem; font-weight:600; color:{colors['text']}; margin-bottom:10px;">Awaiting Candidate Data</div>
    <div style="color:{colors['muted']}; max-width:400px; line-height:1.6;">
    Upload a <strong>.jsonl</strong> file to initialize the Talent Intelligence sandbox.
    </div>
    """, unsafe_allow_html=True)
