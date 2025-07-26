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

# Extract keywords
def extract_technical_keywords(text):
    doc = nlp(text)
    keywords = [token.text.lower() for token in doc if token.pos_ in ["NOUN", "PROPN", "VERB"] and len(token.text) > 2]
    filtered = [word for word in keywords if word.isalpha() and word not in common_words]
    return Counter(filtered)

# Extract from PDF
def extract_text_from_pdf(file):
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        return "\n".join([page.get_text() for page in doc])

# Streamlit interface
st.title("🧠 AI-Powered Resume Auditor")
st.markdown("Upload your resume (.pdf or .txt) to receive smart keyword analysis.")

uploaded_file = st.file_uploader("📄 Upload your Resume", type=["txt", "pdf"])

if uploaded_file is not None:
    if uploaded_file.name.endswith(".pdf"):
        content = extract_text_from_pdf(uploaded_file)
    else:
        content = uploaded_file.read().decode("utf-8")

    st.subheader("🔍 Analysis Summary")
    keywords = extract_technical_keywords(content)
    most_common = keywords.most_common(15)

    if most_common:
        st.markdown("**Top Technical Keywords Detected:**")
        for word, freq in most_common:
            st.write(f"🔹 {word} — {freq} times")
    else:
        st.warning("No strong technical keywords found. Try adding more domain-specific skills.")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 13px;'>Built by <b>Sandesh Kalagi</b> ⚙️</p>", unsafe_allow_html=True)
