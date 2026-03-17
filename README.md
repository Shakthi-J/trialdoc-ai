# 🧬 TrialDocAI

An AI-powered clinical trial document automation pipeline built for Contract Research Organizations (CROs).

## 🔗 Live Demo
https://trialdoc-ai.streamlit.app/

---

## What it does

TrialDocAI automates three core CRO documents using AI:

1. **Statistical Analysis Plan (SAP)** — Generated following ICH E9 guidelines
2. **Table Interpretation** — Real statistical analysis using Welch's t-test, p-values, and Cohen's d effect sizes
3. **Clinical Study Report (CSR)** — Generated following ICH E3 guidelines, downloadable in PDF, DOCX, and TXT

---

## Features

- AI-generated SAP and CSR narratives using Groq LLaMA 3.3 70B
- Welch's t-test with p-values and Cohen's d for pairwise comparisons
- Professional PDF output with cover page and styled tables
- Professional DOCX output with dark cover and formatted tables
- Structured TXT report
- One-click example data for instant demo
- Dark clinical UI

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| AI Model | Groq LLaMA 3.3 70B |
| Statistical Analysis | SciPy, NumPy |
| Document Generation | ReportLab (PDF), python-docx (DOCX) |
| Deployment | Streamlit Community Cloud |
| Language | Python 3.x |

---

## How to Run Locally
```bash
git clone https://github.com/Shakthi-J/trialdoc-ai.git
cd trialdoc-ai
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.streamlit/secrets.toml` file:
```toml
GROQ_API_KEY = "your-groq-key-here"
```

Run the app:
```bash
streamlit run app.py
```

---

## CSV Format

The app accepts a CSV file with the following columns:
```
Treatment, N, Mean_BP_Reduction, StdDev
Placebo, 50, 2.3, 1.1
DrugX, 52, 8.7, 2.4
DrugY, 48, 9.5, 2.1
```

---

## Author

Built by Shakthi J as a prototype for AI & automation in clinical research documentation.
