import streamlit as st
from groq import Groq

def generate_sap(study_data: dict) -> str:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    prompt = f"""
You are a senior biostatistician at a Contract Research Organization (CRO).
Write a formal Statistical Analysis Plan (SAP) following ICH E9 guidelines.
Use precise clinical and statistical terminology. Number all sections clearly.

Study Details:
- Study Title: {study_data['title']}
- Study Phase: {study_data['phase']}
- Study Design: {study_data['design']}
- Study Population: {study_data['population']}
- Treatment Arms: {study_data['treatments']}
- Primary Endpoint: {study_data['endpoint']}
- Statistical Method: {study_data['stat_method']}

Generate these sections:
1. Study Objectives
2. Study Design Summary
3. Analysis Populations (ITT, PP, Safety)
4. Statistical Methods for Primary Endpoint
5. Handling of Missing Data
6. Sensitivity Analyses
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
