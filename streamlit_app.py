import streamlit as st
import spacy
import PyPDF2
import openai
import re
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from dotenv import load_dotenv
import os

# Load environment variable
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

nlp = spacy.load("en_core_web_sm")

st.set_page_config(page_title="AI-Powered Resume Auditor", page_icon="🧠")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .reportview-container .main footer {visibility: hidden;}
    .css-1rs6os.edgvbvh3 {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.title("🧠 AI-Powered Resume Auditor")
st.markdown("Upload your **.txt** or **.pdf** resume and a job description to see keyword match and get smart suggestions!")
st.markdown("___")

with st.sidebar:
    st.subheader("📌 Instructions")
    st.write("- Upload resume file (`.pdf` or `.txt`)")
    st.write("- Paste job description")
    st.write("- View keyword match %")
    st.write("- Get GPT feedback & download report")
    st.markdown("---")
    st.markdown("Built by **Sandesh Kalagi** 🔧")

# File uploader
uploaded_file = st.file_uploader("📄 Upload Resume", type=["pdf", "txt"])
job_desc = st.text_area("💼 Paste Job Description")

def extract_text_from_file(file):
    if file.type == "application/pdf":
        reader = PyPDF2.PdfReader(file)
        return " ".join(page.extract_text() or "" for page in reader.pages)
    elif file.type == "text/plain":
        return file.read().decode("utf-8")
    return ""

def extract_keywords(text):
    doc = nlp(text)
    keywords = [token.lemma_.lower() for token in doc if token.pos_ in ["NOUN", "PROPN", "VERB"] and not token.is_stop and token.is_alpha]
    return list(set(keywords))

def compare_keywords(resume_kw, job_kw):
    matched = set(resume_kw) & set(job_kw)
    if len(job_kw) == 0:
        return 0, []
    percent = round((len(matched) / len(job_kw)) * 100, 2)
    return percent, matched

def get_gpt_feedback(resume, job_desc):
    try:
        prompt = f"""You are an expert resume auditor for cybersecurity roles. Given the following resume and job description, provide specific feedback to improve the resume for better job matching.

Resume:
{resume}

Job Description:
{job_desc}

Your feedback:"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return "⚠️ Error generating GPT feedback. Check your API key or usage limit."

def generate_pdf_report(resume_kw, job_kw, match_percent, feedback):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    p.setFont("Helvetica", 12)

    y = height - 40
    p.drawString(50, y, "AI Resume Auditor Report")
    y -= 30

    p.drawString(50, y, f"Keyword Match: {match_percent}%")
    y -= 20

    p.drawString(50, y, "Matched Keywords:")
    y -= 20
    for word in set(resume_kw) & set(job_kw):
        p.drawString(60, y, f"- {word}")
        y -= 15
        if y < 50:
            p.showPage()
            y = height - 40

    p.drawString(50, y, "GPT Feedback:")
    y -= 20
    for line in feedback.split('\n'):
        for chunk in re.findall('.{1,90}(?:\s+|$)', line):
            p.drawString(60, y, chunk.strip())
            y -= 15
            if y < 50:
                p.showPage()
                y = height - 40

    p.save()
    buffer.seek(0)
    return buffer

if uploaded_file and job_desc:
    resume_text = extract_text_from_file(uploaded_file)
    resume_keywords = extract_keywords(resume_text)
    job_keywords = extract_keywords(job_desc)

    st.subheader("🔍 Keyword Analysis")
    percent_match, matched_keywords = compare_keywords(resume_keywords, job_keywords)
    st.write(f"✅ **Keyword Match: {percent_match}%**")
    st.write(f"🧠 Matched Keywords: {', '.join(matched_keywords)}")

    st.subheader("💡 GPT Suggestions")
    feedback = get_gpt_feedback(resume_text, job_desc)
    st.info(feedback)

    st.subheader("📄 Download Report")
    pdf = generate_pdf_report(resume_keywords, job_keywords, percent_match, feedback)
    st.download_button(label="📥 Download PDF Report", data=pdf, file_name="resume_audit_report.pdf", mime="application/pdf")
