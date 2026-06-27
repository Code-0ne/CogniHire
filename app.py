import streamlit as st
from src.sandbox import CogniHireSandbox
from src.config import TARGET_JD

# PAGE CONFIG 
st.set_page_config(page_title="CogniHire Sandbox", page_icon="🚀", layout="wide")

# CACHE LOGIC SERVICE
@st.cache_resource
def get_sandbox_engine():
    return CogniHireSandbox()

engine = get_sandbox_engine()

# UI LAYOUT
st.title("CogniHire Talent Intelligence Sandbox")
st.markdown("""
**The Three-Sieve Pipeline:**  
`Semantic Recall (FAISS)` $\rightarrow$ `Intelligence Filter (Red Flags)` $\rightarrow$ `Precision Rerank (Cross-Encoder)`
""")

st.divider()

# Sidebar for Inputs
st.sidebar.header("Configuration")
jd_input = st.sidebar.text_area(
    "Job Description", 
    value=TARGET_JD,
    height=300
)

st.sidebar.info("Upload a `.jsonl` file to test the ranking engine. Max upload size: 200 MB.")
uploaded_file = st.sidebar.file_uploader("Upload Candidates", type=["jsonl"])

# MAIN EXECUTION
if uploaded_file:
    content = uploaded_file.getvalue().decode("utf-8")
    
    with st.spinner("⚙️ Processing candidates through the Three-Sieve pipeline..."):
        try:
            df_results = engine.process_pipeline(content, jd_input)
            
            st.subheader("🏆 Top Ranked Candidates")
            st.dataframe(df_results, use_container_width=True)

            csv = df_results.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name="sandbox_results.csv",
                mime="text/csv",
            )
            
        except Exception as e:
            st.error(f"Pipeline Error: {e}")
else:
    st.warning("Please upload a `candidates.jsonl` file in the sidebar to begin.")
    st.image("https://via.placeholder.com/800x400.png?text=Upload+Data+to+See+Results") # Optional: Add a nice image/logo
