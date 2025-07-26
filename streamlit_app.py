import streamlit as st
import spacy
import fitz  # PyMuPDF
from collections import Counter

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    st.error("⚠️ spaCy model not found. Please install it using:\n`python -m spacy download en_core_web_sm`")
    st.stop()

# Common words to ignore
common_words = set("""
i me my myself we our ours you your yours he him his she her hers they them their what which who whom this that these those am is are was were be been being have has had do does did a an the and but if or because as until while of at by for with about against between into through during before after to from in out on off over under again further then once here there all any both each few more most other some such no nor not only own same so than too very can will just ok okay
""".split())

# Extract technical keywords
def extract_technical_keywords(text):
    doc = nlp(text)
    keywords = [token.text.lower() for token in doc if token.pos_ in ["NOUN", "PROPN", "VERB"] and len(token.text) > 2]
    filtered = [word for word in keywords if word.isalpha() and word not in common_words]
    return Counter(filtered)

# Extract text from PDF
def extract_text_from_pdf(file):
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        return "\n".join([page.get_text() for page in doc])

# ---- Streamlit Interface ----
st.title("🧠 AI-Powered Resume Auditor")
st.markdown("Upload your resume and job description to get smart keyword suggestions.")

# 📄 Upload Resume
uploaded_file = st.file_uploader("📄 Upload your Resume (.pdf or .txt)", type=["txt", "pdf"])

# 📌 Paste Job Description
st.subheader("📌 Paste Job Description")
job_desc = st.text_area("Enter the job description for the role you're applying to:", height=200)

if uploaded_file is not None:
    if uploaded_file.name.endswith(".pdf"):
        content = extract_text_from_pdf(uploaded_file)
    else:
        content = uploaded_file.read().decode("utf-8")

    # 🔍 Resume Analysis
    st.subheader("🔍 Resume Keyword Analysis")
    keywords = extract_technical_keywords(content)
    most_common = keywords.most_common(15)

    if most_common:
        st.markdown("**Top Technical Keywords Detected:**")
        for word, freq in most_common:
            st.write(f"🔹 {word} — {freq} times")
    else:
        st.warning("No strong technical keywords found. Try adding more domain-specific skills.")

    # 🤖 Compare with Job Description
    if job_desc:
        jd_keywords = extract_technical_keywords(job_desc)
        resume_words = set(keywords.keys())
        jd_words = set(jd_keywords.keys())
        missing_keywords = jd_words - resume_words

        st.subheader("🤝 Match with Job Description")
        if missing_keywords:
            st.warning("⚠️ Your resume may be missing some key terms from the job description:")
            for word in list(missing_keywords)[:10]:
                st.write(f"➕ Consider adding: **{word}**")
        else:
            st.success("✅ Great! Your resume covers most of the job description's keywords.")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 13px;'>Built by <b>Sandesh Kalagi</b> ⚙️</p>", unsafe_allow_html=True)
