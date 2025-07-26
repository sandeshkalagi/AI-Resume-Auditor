import streamlit as st
import spacy
import subprocess
import sys
from collections import Counter
import re

# Auto-download SpaCy model if missing
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

# Function to extract only technical nouns and verbs
def extract_technical_keywords(text):
    doc = nlp(text)
    keywords = [token.text.lower() for token in doc if token.pos_ in ["NOUN", "PROPN", "VERB"] and len(token.text) > 2]
    filtered = [word for word in keywords if word.isalpha() and word not in common_words]
    return Counter(filtered)

# Minimal stoplist of non-technical common words
common_words = set("""
i me my myself we our ours you your yours he him his she her hers they them their what which who whom this that these those am is are was were be been being have has had do does did a an the and but if or because as until while of at by for with about against between into through during before after to from in out on off over under again further then once here there all any both each few more most other some such no nor not only own same so than too very can will just don don should now ok okay
""".split())

# Streamlit app interface
st.title("🧠 AI-Powered Resume Auditor")
st.markdown("Upload your resume (text only) to get smart keyword analysis.")

uploaded_file = st.file_uploader("Upload your .txt resume", type=["txt"])

if uploaded_file is not None:
    content = uploaded_file.read().decode("utf-8")
    st.subheader("🔍 Analysis Summary")

    keywords = extract_technical_keywords(content)
    most_common = keywords.most_common(15)

    if most_common:
        st.markdown("*Top Technical Keywords Found:*")
        for word, freq in most_common:
            st.write(f"🔹 {word} — {freq} times")
    else:
        st.warning("No strong technical keywords detected.")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 13px;'>Crafted with by <b>Sandesh Kalagi</b></p>", unsafe_allow_html=True)