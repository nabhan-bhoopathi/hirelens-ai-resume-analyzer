import streamlit as st
from pypdf import PdfReader
from google import genai
from google.genai import types
import json
import re

st.set_page_config(page_title="HireLens AI | Resume Intelligence", page_icon="✦", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root{--bg:#080b12;--panel:#101622;--line:#253044;--muted:#8e9aaf;--purple:#9b8cff;--cyan:#62e5d2}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}
.stApp{background:radial-gradient(ellipse at 12% 0%,rgba(111,83,255,.17),transparent 35%),radial-gradient(ellipse at 88% 8%,rgba(43,213,194,.10),transparent 28%),var(--bg);color:#f5f7fb}
.block-container{max-width:1180px;padding-top:2.3rem;padding-bottom:4rem}
h1,h2,h3{font-family:'Space Grotesk',sans-serif!important;letter-spacing:-.04em}
.hero{padding:1.4rem 0 2rem}
.eyebrow{color:var(--cyan);font-size:.75rem;font-weight:700;letter-spacing:.18em;text-transform:uppercase}
.hero h1{font-size:clamp(2.8rem,6vw,5rem);line-height:1.02;margin:.7rem 0}
.gradient{background:linear-gradient(100deg,#fff 10%,#a99bff 55%,#63e6d5 100%);-webkit-background-clip:text;background-clip:text;color:transparent}
.sub{color:#aab5c7;font-size:1.08rem;max-width:650px;line-height:1.7}
.panel{background:linear-gradient(145deg,rgba(20,29,44,.96),rgba(13,18,29,.96));border:1px solid var(--line);border-radius:22px;padding:1.35rem}
.panel-title{font-family:'Space Grotesk';font-size:1.18rem;font-weight:600;margin-bottom:.25rem}
.small{color:var(--muted);font-size:.88rem}
div[data-testid="stFileUploader"]{background:#0b111d;border:1px dashed #46516b;border-radius:16px;padding:1rem}
.stTextArea textarea{background:#0b111d!important;color:#f5f7fb!important;border:1px solid #303b50!important;border-radius:14px!important}
.stButton>button{background:linear-gradient(100deg,#9b8cff,#66dcca);color:#071018;border:0;border-radius:12px;padding:.75rem 1.4rem;font-weight:800;min-height:3rem}
.stButton>button:hover{filter:brightness(1.08);color:#071018}
div[data-testid="stMetric"]{background:#111a29;border:1px solid #28364c;border-radius:16px;padding:1rem}
div[data-testid="stMetricValue"]{color:#a99bff}
hr{border-color:#263247}
.skill{display:inline-block;padding:.38rem .7rem;border-radius:99px;background:#172b32;color:#70e3d2;border:1px solid #28524f;margin:.2rem;font-size:.83rem}
.missing{display:inline-block;padding:.38rem .7rem;border-radius:99px;background:#2b2028;color:#ff9caa;border:1px solid #633341;margin:.2rem;font-size:.83rem}
footer{visibility:hidden}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
 <div class="eyebrow">✦ AI-powered career intelligence</div>
 <h1>Make your resume<br><span class="gradient">impossible to overlook.</span></h1>
 <p class="sub">A smarter way to understand your fit for the role. Upload your resume, add the job description, and get a clear, actionable match report.</p>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([.92,1.08], gap="large")
with left:
    st.markdown('<div class="panel"><div class="panel-title">01 / Your resume</div><div class="small">Upload your latest resume in PDF format.</div></div>', unsafe_allow_html=True)
    resume = st.file_uploader("Upload resume (PDF)", type=["pdf"], label_visibility="collapsed")
    if resume:
        st.success(f"Ready to analyze · {resume.name}")
    st.markdown('<div class="panel" style="margin-top:1rem"><div class="panel-title">02 / Target role</div><div class="small">Paste the job description you want to match.</div></div>', unsafe_allow_html=True)
    jd = st.text_area("Job description", height=260, placeholder="Paste the complete job description here...", label_visibility="collapsed")
    analyze = st.button("✦  Analyze my resume", use_container_width=True)

with right:
    st.markdown('<div class="panel"><div class="panel-title">Your analysis, at a glance</div><div class="small">A focused report to help you apply with confidence.</div><hr>', unsafe_allow_html=True)
    st.markdown("""
    <div style="display:flex;gap:1rem;align-items:center;margin:1.2rem 0">
      <div style="font-size:2rem">◎</div><div><b>ATS match score</b><div class="small">See how closely your profile aligns with the role.</div></div>
    </div>
    <div style="display:flex;gap:1rem;align-items:center;margin:1.2rem 0">
      <div style="font-size:2rem">⌁</div><div><b>Skills intelligence</b><div class="small">Identify relevant strengths and missing keywords.</div></div>
    </div>
    <div style="display:flex;gap:1rem;align-items:center;margin:1.2rem 0">
      <div style="font-size:2rem">✧</div><div><b>Actionable improvements</b><div class="small">Get five practical suggestions to strengthen your resume.</div></div>
    </div>
    <hr><div class="small">Your resume is analyzed for this session only. Add your Gemini API key in Streamlit Secrets to enable AI analysis.</div></div>
    """, unsafe_allow_html=True)

if analyze:
    if not resume or not jd.strip():
        st.warning("Please upload a PDF resume and paste the job description.")
        st.stop()
    try:
        reader = PdfReader(resume)
        resume_text = "\n".join(page.extract_text() or "" for page in reader.pages)
        if not resume_text.strip():
            st.error("I couldn't extract readable text from this PDF. Try an exported/searchable PDF.")
            st.stop()
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        if not api_key:
            st.error("Gemini API key is not configured yet. Open App settings → Secrets and add GEMINI_API_KEY = \"your-key\".")
            st.stop()
        with st.spinner("Reading your resume and comparing it with the role..."):
            client = genai.Client(api_key=api_key)
            prompt = f"""
You are an expert ATS resume reviewer. Compare the resume to the job description.
Return ONLY valid JSON with these keys:
match_score (integer 0-100), matched_skills (array of strings), missing_skills (array of strings),
summary (2-3 sentences), suggestions (array of exactly 5 practical strings).
Be honest and base claims only on provided text. Do not invent experience.
RESUME:
{resume_text[:24000]}
JOB DESCRIPTION:
{jd[:12000]}
"""
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.2)
            )
            data = json.loads(response.text)
        st.markdown("---")
        st.markdown("## Your resume intelligence report")
        st.markdown(f"**{data.get('summary','')}**")
        score = max(0,min(100,int(data.get("match_score",0))))
        c1,c2,c3 = st.columns(3)
        c1.metric("ATS match score", f"{score}/100")
        c2.metric("Matched skills", len(data.get("matched_skills",[])))
        c3.metric("Skills to build", len(data.get("missing_skills",[])))
        st.progress(score/100)
        a,b = st.columns(2)
        with a:
            st.markdown("### ✓ Matched skills")
            vals=data.get("matched_skills",[])
            st.markdown("".join(f'<span class="skill">{s}</span>' for s in vals) if vals else "_No clear matches identified._",unsafe_allow_html=True)
        with b:
            st.markdown("### + Missing keywords")
            vals=data.get("missing_skills",[])
            st.markdown("".join(f'<span class="missing">{s}</span>' for s in vals) if vals else "_No major gaps identified._",unsafe_allow_html=True)
        st.markdown("### ✧ Five ways to improve")
        for i,item in enumerate(data.get("suggestions",[])[:5],1):
            st.markdown(f"**{i:02d}**  {item}")
        report = {"match_score":score,"summary":data.get("summary"),"matched_skills":data.get("matched_skills"),"missing_skills":data.get("missing_skills"),"suggestions":data.get("suggestions")}
        st.download_button("↓ Download analysis (JSON)",json.dumps(report,indent=2),"hirelens_analysis.json","application/json")
    except Exception as e:
        st.error(f"Analysis failed: {e}")
        st.info("Check that your Gemini API key is valid and that the uploaded PDF contains selectable text.")

st.markdown("---")
st.markdown('<div class="small" style="text-align:center">HIRELENS AI · Built for smarter career decisions</div>',unsafe_allow_html=True)
