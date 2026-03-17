import streamlit as st
from groq import Groq

def generate_sap(study_data: dict) -> str:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    results_summary = "\n".join([
        f"  - {r['treatment']}: N={r['sample_size']}, Mean={r['mean']}, SD={r['std_dev']}"
        for r in structured_data["results"]
    ])

    conclusion_context = (
        "The study met its primary endpoint and shows a positive treatment effect."
        if structured_data["conclusion"] == "positive"
        else
        "The study did not demonstrate a meaningful treatment effect over placebo."
    )

    prompt = f"""
You are a senior medical writer at a CRO.
Write a complete Clinical Study Report (CSR) following ICH E3 guidelines.
Use formal regulatory language for FDA/EMA submission. Number all sections.

--- STUDY METADATA ---
Study Title: {study_data['title']}
Phase: {study_data['phase']}
Design: {study_data['design']}
Population: {study_data['population']}
Treatments: {study_data['treatments']}
Endpoint: {study_data['endpoint']}
Statistical Method: {study_data['stat_method']}

--- RESULTS ---
Endpoint: {structured_data['endpoint']}
{results_summary}
Best Treatment: {structured_data['best_treatment']}
Conclusion: {conclusion_context}
Effect: {structured_data['warning']}
Confidence Score: {structured_data['confidence_score']}

Generate sections 1-10:
1. Title Page
2. Synopsis
3. Ethics and Compliance
4. Study Objectives
5. Study Design
6. Study Population
7. Efficacy Results
8. Safety Analysis
9. Discussion
10. Conclusion
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
