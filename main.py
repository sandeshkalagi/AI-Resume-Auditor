import re
import spacy
import nltk

nltk.download('stopwords')
from nltk.corpus import stopwords

# Load NLP model
nlp = spacy.load("en_core_web_sm")
stop_words = set(stopwords.words('english'))
custom_ignored = {"ok", "hello", "sure", "im", "thanks", "hi", "and", "the", "like", "yes", "no"}

# Clean and extract keywords
def get_keywords(text):
    doc = nlp(text)
    keywords = []
    for token in doc:
        word = token.lemma_.lower()
        if (
            token.pos_ in ["NOUN", "PROPN", "VERB", "ADJ"] and
            word not in stop_words and
            word not in custom_ignored and
            len(word) > 2 and
            token.is_alpha
        ):
            keywords.append(word)
    return keywords

# Input from user
resume_text = input("Paste your Resume:\n")
job_desc = input("\nPaste Job Description:\n")

# Processing
res_keywords = get_keywords(resume_text)
jd_keywords = get_keywords(job_desc)

matched = set(res_keywords) & set(jd_keywords)
missing = set(jd_keywords) - set(res_keywords)
score = (len(matched) / len(set(jd_keywords))) * 100 if jd_keywords else 0

# Output
print(f"\n✅ Match Score: {score:.2f}%")
print(f"\n✅ Matched Keywords: {', '.join(sorted(matched)) if matched else 'None'}")
print(f"\n⚠️ Missing Keywords: {', '.join(sorted(missing)) if missing else 'None'}")
