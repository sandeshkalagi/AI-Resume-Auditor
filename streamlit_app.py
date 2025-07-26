import streamlit as st
import spacy
from collections import Counter
import re

# ✅ Use lightweight English pipeline (no download needed)
nlp = spacy.blank("en")

# ✅ Add POS tagger to extract nouns/verbs
if "tagger" not in nlp.pipe_names:
    from spacy.pipeline import Tagger
    tagger = Tagger(nlp.vocab)
    nlp.add_pipe("tagger")

# 🔍 Filter technical keywords
def extract_technical_keywords(text):
    doc = nlp(text)
    keywords = [token.text.lower() for token in doc if token.pos_ in ["NOUN", "PROPN", "VERB"] and len(token.text) > 2]
    filtered = [word for word in keywords if word.isalpha() and word not in common_words]
    return Counter(filtered)

# 🛑 Stop words: not considered technical
common_words = set("""
i me my myself we our ours you your yours he him his she her hers they them their what which who whom this that these those am is are was were be been being have has had do does did a an the and but if or because as until while of at by for with about against between into through during before after to from in out on off over under again further then once here there all any both each few more most other some such no nor not only own same so than too very can will just ok okay
""".split())

# 🌐 Streamlit Interface
st.title("🧠 AI-Powered Resume Auditor")
st.markdown("Upload your resume (.txt) to receive smart keyword analysis.")

uploaded_file = st.file_uploader("📄 Upload your .txt resume", type=["txt"])

if uploaded_file is not None:
    content = uploaded_file.read().decode("utf-8")
    st.subheader("🔍 Analysis Summary")

    keywords = extract_technical_keywords(content)
    most_common = keywords.most_common(15)

    if most_common:
        st.markdown("*Top Technical Keywords Detected:*")
        for word, freq in most_common:
            st.write(f"🔹 {word} — {freq} times")
    else:
        st.warning("No strong technical keywords found. Try adding more domain-specific skills.")

# Footer with your name
st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 13px;'>Crafted with by <b>Sandesh Kalagi</b></p>", unsafe_allow_html=True)
