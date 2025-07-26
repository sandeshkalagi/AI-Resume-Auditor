import streamlit as st
import spacy
from spacy.cli import download
from collections import Counter
import re

# Auto-download SpaCy model if missing (Streamlit Cloud safe)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Define common non-technical words to ignore
common_words = set("""
i me my myself we our ours you your yours he him his she her hers they them their what which who whom this that these those am is are was were be been being have has had do does did a an the and but if or because as until while of at by for with about against between into through during before after to from in out on off over under again further then once here there all any both each few more most other some such no nor not only own same so than too very can will just don should now ok okay
""".split())

# Function to extract meaningful keywords
def extract_technical_keywords(text):
    doc = nlp(text)
    keywords = [token.text.lower() for token in doc if token.pos_ in ["NOUN", "PROPN", "VERB"] and len(token.text) > 2]
    filtered = [word for word in keywords if word.isalpha() and word not in common_words]
    return Counter(filtered)

# Streamlit UI
st.title("🧠 AI-Powered Resume Auditor")
st.markdown("Upload your resume (.txt only) to get keyword insights!")

uploaded_file = st.file_uploader("📄 Upload Resume (.txt)", type=["txt"])

if uploaded_file:
    content = uploaded_file.read().decode("utf-8")
    st.subheader("🔍 Top Technical Keywords")

    keywords = extract_technical_keywords(content)
    top_keywords = keywords.most_common(15)

    if top_keywords:
        for word, count in top_keywords:
            st.write(f"🔹 {word} — {count} time(s)")
    else:
        st.warning("No strong keywords found. Try a more technical resume.")

# Footer with your name
st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 13px;'>Built by <b>Sandesh Kalagi</b> 🛠️</p>", unsafe_allow_html=True)
