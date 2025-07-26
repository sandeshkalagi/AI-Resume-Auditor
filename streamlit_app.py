import streamlit as st
import spacy
import fitz  # PyMuPDF
from collections import Counter
from io import BytesIO
from reportlab.pdfgen import canvas
import openai
import os
from dotenv import load_dotenv

# Load .env file and OpenAI key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    st.error("⚠️ spaCy model not found. Install it using: `python -m spacy download en_core_web_sm`")
    st.stop()

# Common non-technical words
common_words = set("""
i me my myself we our ours you your yours he him his she her hers they them their what which who whom this that these those am is are was were be been being have has had do does did a an the and but if or because as until while of at by for with about against between into through during before after to from in out on off over under again further then once here there all any both each few more most other some such no nor not only own same so than too very can will just ok okay
""".split())

# Extract keywords
def extract_technical_keywords(text):
    doc = nlp(text)
    keywords = [token.text.lower() for token in doc if token.pos_ in ["NOUN", "PROPN", "VERB"] and len(token.text) > 2]
    filtered = [word for word in keywords if word.isalpha() and word not in common_words]
    return Counter(filtered)

# Read PDF text
def extract_text_from_pdf(file):
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        return "\n".join([page.get_text() for page in doc])

# Generate GPT feedback
def generate_feedback(resume_text, job_text):
    prompt = f"""
You are a cybersecurity resume expert.
Analyze this resume and job description.
Suggest improvements (skills to add, clarity, buzzwords, etc.)

Resume:
{resume_text[:1500]}

Job Description:
{job_text[:1500]}

Give concise feedback (max 100 words).
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "⚠️ Error generating GPT feedback. Check your API key or usage limit."

# Create a PDF report
def create_pdf_report(name, keywords, missing, percent, feedback):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 800, "AI Resume Audit Report")

    p.setFont("Helvetica", 12)
    y = 770
    p.drawString(50, y, f"Name: {name}")
    y -= 20
    p.drawString(50, y, f"Match Score: {percent}%")
    y -= 30

    p.drawString(50, y, "Top Keywords in Resume:")
    for word, freq in keywords:
        y -= 15
        p.drawString(60, y, f"{word} — {freq} times")

    y -= 30
    p.drawString(50, y, "Missing Keywords from JD:")
    for word in list(missing)[:10]:
        y -= 15
        p.drawString(60, y, f"{word}")

    y -= 30
    p.drawString(50, y, "GPT Feedback:")
    lines = feedback.split('\n')
    for line in lines:
        for chunk in [line[i:i+80] for i in range(0, len(line), 80)]:
            y -= 15
            p.drawString(60, y, chunk)

    p.save()
    buffer.seek(0)
    return buffer

# --- UI START ---
st.title("🧠 AI-Powered Resume Auditor")
st.markdown("Upload your resume and job description to receive smart keyword analysis and GPT feedback.")

uploaded_file = st.file_uploader("📄 Upload Resume (.pdf or .txt)", type=["pdf", "txt"])
st.subheader("📌 Paste Job Description")
job_desc = st.text_area("Enter job description:", height=200)

if uploaded_file is not None:
    if uploaded_file.name.endswith(".pdf"):
        resume_text = extract_text_from_pdf(uploaded_file)
    else:
        resume_text = uploaded_file.read().decode("utf-8")

    st.subheader("🔍 Resume Keyword Analysis")
    resume_keywords = extract_technical_keywords(resume_text)
    top_keywords = resume_keywords.most_common(15)

    if top_keywords:
        st.markdown("**Top Technical Keywords:**")
        for word, freq in top_keywords:
            st.write(f"🔹 {word} — {freq} times")
    else:
        st.warning("No strong technical keywords found.")

    if job_desc:
        jd_keywords = extract_technical_keywords(job_desc)
        resume_set = set(resume_keywords.keys())
        jd_set = set(jd_keywords.keys())
        missing = jd_set - resume_set
        matched = jd_set & resume_set
        match_percent = round((len(matched) / len(jd_set)) * 100, 2) if jd_set else 0.0

        st.subheader("🤝 Match with Job Description")
        if missing:
            st.warning("Missing terms from JD:")
            for word in list(missing)[:10]:
                st.write(f"➕ {word}")
        else:
            st.success("✅ Resume covers all key job terms.")

        st.subheader("📊 Resume Match Score")
        st.progress(int(match_percent))
        st.info(f"✅ Your resume matches **{match_percent}%** of the job description.")

        st.subheader("🧠 GPT Feedback")
        with st.spinner("Analyzing with GPT..."):
            feedback = generate_feedback(resume_text, job_desc)
        st.success(feedback)

        # 🎯 PDF Report Button
        st.subheader("📥 Download PDF Report")
        pdf = create_pdf_report("Sandesh Kalagi", top_keywords, missing, match_percent, feedback)
        st.download_button("Download Report", data=pdf, file_name="resume_audit_report.pdf", mime="application/pdf")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 13px;'>Built with  by <b>Sandesh Kalagi</b></p>", unsafe_allow_html=True)
