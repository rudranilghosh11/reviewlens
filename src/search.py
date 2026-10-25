"""'Ask your reviews': lightweight TF-IDF retrieval (no API needed). Swap for embeddings + LLM for full RAG."""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

def build_index(reviews):
    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
    return vec, vec.fit_transform(reviews.review_text)

def search(query, reviews, vec, X, k=8):
    sims = linear_kernel(vec.transform([query]), X).ravel()
    idx = sims.argsort()[::-1][:k]
    return reviews.iloc[idx].assign(match=sims[idx].round(2)).query("match > 0")
