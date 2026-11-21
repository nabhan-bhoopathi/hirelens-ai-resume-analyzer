# HireLens AI — Resume Analyzer & ATS Score Checker

A Streamlit + Google Gemini prototype that compares a PDF resume with a job description and returns an ATS-style match score, matched skills, missing keywords, and five improvement suggestions.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Configure Gemini
Create `.streamlit/secrets.toml`:
```toml
GEMINI_API_KEY = "your-google-ai-studio-key"
```
Get a key from https://aistudio.google.com/app/apikey. Never commit secrets to GitHub.

## Deploy
Deploy this repository on Streamlit Community Cloud with `app.py` as the entrypoint, then add `GEMINI_API_KEY` under App settings → Secrets.

## How it works
1. Upload a searchable PDF resume.
2. Paste a target job description.
3. The app extracts PDF text using pypdf.
4. Gemini analyzes the text and returns structured JSON.
5. The app displays the match score, skill gaps, and improvement suggestions.

This is an educational prototype. ATS scores are estimates, not guarantees of hiring outcomes.
