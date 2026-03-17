from dotenv import load_dotenv
load_dotenv()

from sap_generator import generate_sap
from table_interpreter import interpret_table
from csr_generator import generate_csr
from docx_generator import create_docx_bytes
from pdf_generator import create_pdf_bytes
from txt_generator import create_txt_bytes
import streamlit as st
import pandas as pd
import io
import os

# ── Example data ──────────────────────────────────────────────────────────────
EXAMPLE_DATA = {
    "title":       "A Phase III Trial of DrugX for Hypertension",
    "phase":       "Phase III",
    "design":      "Randomized double-blind placebo-controlled parallel-group study",
    "population":  "Adults aged 18-65 with stage 2 hypertension (SBP 140-179 mmHg)",
    "treatments":  "DrugX 10mg once daily, DrugY 20mg once daily, Placebo once daily",
    "endpoint":    "Blood pressure reduction (mmHg) from baseline after 12 weeks",
    "stat_method": "ANCOVA with baseline blood pressure as covariate",
}

EXAMPLE_CSV = """Treatment,N,Mean_BP_Reduction,StdDev
Placebo,50,2.3,1.1
DrugX,52,8.7,2.4
DrugY,48,9.5,2.1
"""

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TrialDocAI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: #0a0e1a;
    color: #c9d1e0;
}
section[data-testid="stSidebar"] {
    background-color: #0d1220;
    border-right: 1px solid #1e2d4a;
}
section[data-testid="stSidebar"] * { color: #8a9bb5 !important; }
.main .block-container { padding: 2rem 3rem; max-width: 1100px; }

.step-card {
    background: #0f1629;
    border: 1px solid #1e2d4a;
    border-left: 3px solid #3b82f6;
    border-radius: 8px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
}
.step-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem; font-weight: 600;
    letter-spacing: 0.15em; color: #3b82f6;
    text-transform: uppercase; margin-bottom: 0.3rem;
}
.step-title { font-size: 1.2rem; font-weight: 600; color: #e2e8f0; margin-bottom: 1.2rem; }

.stat-box {
    background: #0a0e1a; border: 1px solid #1e2d4a;
    border-radius: 6px; padding: 1rem 1.2rem; text-align: center;
}
.stat-value { font-family: 'IBM Plex Mono', monospace; font-size: 1.6rem; font-weight: 600; color: #3b82f6; }
.stat-label { font-size: 0.72rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 0.2rem; }

.badge {
    display: inline-block; padding: 0.25rem 0.7rem; border-radius: 999px;
    font-size: 0.72rem; font-weight: 600; letter-spacing: 0.05em;
    font-family: 'IBM Plex Mono', monospace;
}
.badge-green  { background: #052e16; color: #4ade80; border: 1px solid #166534; }
.badge-red    { background: #2d0a0a; color: #f87171; border: 1px solid #7f1d1d; }
.badge-blue   { background: #0c1a3a; color: #60a5fa; border: 1px solid #1e3a8a; }
.badge-yellow { background: #2d2006; color: #fbbf24; border: 1px solid #78350f; }

.output-box {
    background: #080c18; border: 1px solid #1e2d4a; border-radius: 8px;
    padding: 1.5rem 2rem; font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem; line-height: 1.8; color: #94a3b8;
    white-space: pre-wrap; max-height: 400px; overflow-y: auto;
}

.sample-box {
    background: #0a1628; border: 1px dashed #1e3a5f; border-radius: 8px;
    padding: 1rem 1.5rem; margin-bottom: 1rem;
}
.sample-box code {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.8rem;
    color: #60a5fa; line-height: 1.8;
}
.sample-label {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem;
    color: #3b82f6; letter-spacing: 0.12em; text-transform: uppercase;
    margin-bottom: 0.5rem;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background-color: #0d1220 !important; border: 1px solid #1e2d4a !important;
    color: #c9d1e0 !important; border-radius: 6px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}
.stButton > button {
    background: #1d4ed8; color: #fff; border: none; border-radius: 6px;
    padding: 0.55rem 1.4rem; font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem; font-weight: 600; letter-spacing: 0.08em;
    text-transform: uppercase; transition: background 0.2s;
}
.stButton > button:hover { background: #2563eb; }
.stDownloadButton > button {
    background: #052e16; color: #4ade80; border: 1px solid #166534;
    border-radius: 6px; font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem; font-weight: 600; letter-spacing: 0.08em;
}
hr { border-color: #1e2d4a; margin: 2rem 0; }
.stDataFrame { border: 1px solid #1e2d4a; border-radius: 6px; }
label, .stSelectbox label { color: #8a9bb5 !important; font-size: 0.82rem !important; }
.stSuccess { background: #052e16 !important; border: 1px solid #166534 !important; }
.stError   { background: #2d0a0a !important; border: 1px solid #7f1d1d !important; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0a0e1a; }
::-webkit-scrollbar-thumb { background: #1e2d4a; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def clean_text(text):
    return " ".join(text.strip().split())

def badge(text, color="blue"):
    return f'<span class="badge badge-{color}">{text}</span>'


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧬 TrialDocAI")
    st.markdown("---")
    st.markdown("""
**Pipeline**

`01` Enter study metadata  
`02` Generate SAP draft  
`03` Upload results table  
`04` Generate CSR + download  

---

**Supported CSV format**
```
Treatment, N,
Mean_BP_Reduction, StdDev
```

---

**Output formats**  
`.txt` · `.docx` · `.pdf`
""")
    st.markdown("---")
    st.markdown('<span style="font-size:0.7rem; color:#334155;">Powered by Groq · LLaMA 3.3 70B</span>', unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom: 2rem;">
  <div style="font-family:'IBM Plex Mono',monospace; font-size:0.7rem; color:#3b82f6;
              letter-spacing:0.15em; text-transform:uppercase; margin-bottom:0.4rem;">
    Clinical Research Automation
  </div>
  <h1 style="font-size:2rem; font-weight:600; color:#e2e8f0; margin:0;">
    TrialDocAI
  </h1>
  <p style="color:#64748b; margin-top:0.4rem; font-size:0.9rem;">
    AI pipeline for SAP, table interpretation, and CSR generation
  </p>
</div>
""", unsafe_allow_html=True)


# ── Example button ────────────────────────────────────────────────────────────
ex_col1, ex_col2 = st.columns([5, 1])
with ex_col2:
    if st.button("🧪 Load Example", help="Auto-fill all fields with a demo hypertension trial"):
        st.session_state["example_loaded"] = True

if st.session_state.get("example_loaded"):
    for k, v in EXAMPLE_DATA.items():
        st.session_state[f"field_{k}"] = v
    example_df = pd.read_csv(io.StringIO(EXAMPLE_CSV))
    st.session_state["structured_results"] = interpret_table(example_df)
    st.session_state["example_csv"] = EXAMPLE_CSV
    st.session_state["example_loaded"] = False
    st.success("✅ Example loaded — click Generate SAP Draft, then upload the sample CSV in Step 02!")


# ── Step 1: Metadata ──────────────────────────────────────────────────────────
st.markdown("""
<div class="step-card">
  <div class="step-header">Step 01</div>
  <div class="step-title">Study Metadata</div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])
with col1:
    study_title = st.text_input("Study Title",
        value=st.session_state.get("field_title", ""),
        placeholder="e.g. A Phase III Trial of DrugX for Hypertension")
with col2:
    phase_options = ["Phase I", "Phase II", "Phase III"]
    default_phase = st.session_state.get("field_phase", "Phase III")
    study_phase = st.selectbox("Study Phase", phase_options,
        index=phase_options.index(default_phase) if default_phase in phase_options else 0)

col3, col4 = st.columns(2)
with col3:
    study_design = st.text_area("Study Design",
        value=st.session_state.get("field_design", ""),
        placeholder="e.g. Randomized double-blind placebo-controlled", height=90)
    population = st.text_area("Study Population",
        value=st.session_state.get("field_population", ""),
        placeholder="e.g. Adults aged 18-65 with stage 2 hypertension", height=90)
with col4:
    treatments = st.text_area("Treatment Arms",
        value=st.session_state.get("field_treatments", ""),
        placeholder="e.g. DrugX 10mg, DrugY 20mg, Placebo", height=90)
    endpoint = st.text_area("Primary Endpoint",
        value=st.session_state.get("field_endpoint", ""),
        placeholder="e.g. Blood pressure reduction after 12 weeks", height=90)

stat_method = st.text_input("Statistical Method",
    value=st.session_state.get("field_stat_method", ""),
    placeholder="e.g. ANCOVA with baseline as covariate")

st.markdown("<br>", unsafe_allow_html=True)

if st.button("⚡ Generate SAP Draft"):
    if not study_title:
        st.error("Please enter a study title.")
    else:
        study_data = {
            "title":       clean_text(study_title),
            "phase":       clean_text(study_phase),
            "design":      clean_text(study_design),
            "population":  clean_text(population),
            "treatments":  clean_text(treatments),
            "endpoint":    clean_text(endpoint),
            "stat_method": clean_text(stat_method),
        }
        with st.spinner("Generating SAP via AI..."):
            sap_text = generate_sap(study_data)
            st.session_state["sap_text"] = sap_text
            st.session_state["study_data"] = study_data

if "sap_text" in st.session_state:
    st.markdown("**Generated SAP**")
    st.markdown(f'<div class="output-box">{st.session_state["sap_text"]}</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button("↓ Download SAP (.txt)", data=st.session_state["sap_text"], file_name="sap_draft.txt")


# ── Step 2: Results Table ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div class="step-card">
  <div class="step-header">Step 02</div>
  <div class="step-title">Upload Statistical Results Table</div>
</div>
""", unsafe_allow_html=True)

# ── Sample CSV download ───────────────────────────────────────────────────────
st.markdown("**Don't have a file? Download the sample CSV first:**")
st.download_button(
    "↓ Download Sample CSV",
    data=EXAMPLE_CSV,
    file_name="sample_results.csv",
    mime="text/csv",
    help="Download this file, then upload it below"
)

st.markdown("<br>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload your CSV results file", type=["csv"])

if uploaded_file is not None:
    try:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file)
        st.dataframe(df, use_container_width=True)

        structured_results = interpret_table(df)
        st.session_state["structured_results"] = structured_results

        # ── Stats dashboard ───────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Interpretation Summary**")

        m1, m2, m3, m4 = st.columns(4)
        conclusion_color = "green" if structured_results["conclusion"] == "positive" else "red"

        with m1:
            st.markdown(f"""
            <div class="stat-box">
              <div class="stat-value">{structured_results["confidence_score"]}</div>
              <div class="stat-label">Confidence Score</div>
            </div>""", unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="stat-box">
              <div class="stat-value" style="font-size:1.1rem; padding-top:0.3rem;">
                {badge(structured_results["conclusion"].upper(), conclusion_color)}
              </div>
              <div class="stat-label" style="margin-top:0.6rem;">Conclusion</div>
            </div>""", unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="stat-box">
              <div class="stat-value" style="font-size:1rem; padding-top:0.4rem; color:#e2e8f0;">
                {structured_results["best_treatment"]}
              </div>
              <div class="stat-label" style="margin-top:0.4rem;">Best Treatment</div>
            </div>""", unsafe_allow_html=True)
        with m4:
            w = structured_results["warning"]
            warning_color = "red" if "Low" in w else ("yellow" if "Moderate" in w else "green")
            st.markdown(f"""
            <div class="stat-box">
              <div class="stat-value" style="font-size:0.85rem; padding-top:0.5rem;">
                {badge(w, warning_color)}
              </div>
              <div class="stat-label" style="margin-top:0.5rem;">Effect Size</div>
            </div>""", unsafe_allow_html=True)

        # ── Pairwise stats table ──────────────────────────────────────────────
        if structured_results.get("pairwise_stats"):
            st.markdown("<br>**Pairwise Statistics vs Placebo**", unsafe_allow_html=True)
            rows = []
            for ps in structured_results["pairwise_stats"]:
                rows.append({
                    "Treatment":   ps["treatment"],
                    "vs":          ps["vs"],
                    "t-statistic": ps["t_statistic"],
                    "p-value":     ps["p_value"],
                    "Significance":ps["significance"],
                    "Cohen's d":   ps["cohens_d"],
                    "Effect Size": ps["effect_size_label"],
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True)

    except Exception as e:
        st.error(f"Error reading file: {e}")


# ── Step 3: CSR ───────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div class="step-card">
  <div class="step-header">Step 03</div>
  <div class="step-title">Generate Clinical Study Report</div>
</div>
""", unsafe_allow_html=True)

if "structured_results" not in st.session_state:
    st.markdown('<span style="color:#475569; font-size:0.85rem;">⚠ Upload a results table in Step 02 first.</span>', unsafe_allow_html=True)
else:
    if st.button("⚡ Generate CSR"):
        study_data = st.session_state.get("study_data", {
            "title":       clean_text(study_title),
            "phase":       clean_text(study_phase),
            "design":      clean_text(study_design),
            "population":  clean_text(population),
            "treatments":  clean_text(treatments),
            "endpoint":    clean_text(endpoint),
            "stat_method": clean_text(stat_method),
        })
        with st.spinner("Generating CSR via AI..."):
            csr_text = generate_csr(study_data, st.session_state["structured_results"])
            st.session_state["csr_text"] = csr_text

if "csr_text" in st.session_state:
    st.markdown("**Generated CSR**")
    st.markdown(f'<div class="output-box">{st.session_state["csr_text"]}</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    dl1, dl2, dl3 = st.columns(3)
    with dl1:
        txt_output = create_txt_bytes(
            st.session_state["csr_text"],
            st.session_state["structured_results"]
        )
        st.download_button(
            "↓ Download CSR (.txt)",
            data=txt_output,
            file_name="csr_report.txt"
        )
    with dl2:
        docx_file = create_docx_bytes(
            st.session_state["csr_text"],
            st.session_state["structured_results"]
        )
        st.download_button(
            "↓ Download CSR (.docx)",
            data=docx_file,
            file_name="csr_report.docx"
        )
    with dl3:
        pdf_file = create_pdf_bytes(
            st.session_state["csr_text"],
            st.session_state["structured_results"]
        )
        st.download_button(
            "↓ Download CSR (.pdf)",
            data=pdf_file,
            file_name="csr_report.pdf",
            mime="application/pdf"
        )