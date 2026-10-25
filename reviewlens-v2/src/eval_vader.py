"""Measure VADER on YOUR data: accuracy, precision, recall, F1 (plain VADER vs. ReviewLens lexicon).
Gold labels come from a label column (positive/negative/neutral) or, if you give none, from star ratings
(4-5 = positive, 3 = neutral, 1-2 = negative). Ratings are only a proxy for true sentiment.

  python -m src.eval_vader Dataset.csv --text Review --label Sentiment
  python -m src.eval_vader Dataset.csv --text Review --rating Rate --n 20000
"""
import argparse
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, f1_score
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from .ingest import read_csv_robust, guess_columns
from .pipeline import _score  # VADER + ReviewLens domain lexicon + phrase fixes


def to_label(c, pos=0.05, neg=-0.05):
    return "positive" if c >= pos else "negative" if c <= neg else "neutral"


def run(path, text=None, label=None, rating=None, n=20000):
    df, enc = read_csv_robust(path)
    g = guess_columns(df)
    text, rating = text or g["review_text"], rating or g["rating"]
    df = df.dropna(subset=[text])
    if len(df) > n:
        df = df.sample(n, random_state=42)
    if label:
        gold = df[label].astype(str).str.lower().str.strip()
        src = f"label column '{label}'"
    else:
        r = pd.to_numeric(df[rating].astype(str).str.extract(r"(\d+(?:\.\d+)?)")[0], errors="coerce")
        gold = r.apply(lambda x: "positive" if x >= 4 else "negative" if x <= 2 else "neutral")
        src = f"star ratings from '{rating}' (a proxy)"
    keep = gold.isin(["positive", "negative", "neutral"])
    df, gold = df[keep], gold[keep]
    plain = SentimentIntensityAnalyzer()
    variants = {"Plain VADER": df[text].astype(str).apply(lambda t: plain.polarity_scores(t)["compound"]),
                "ReviewLens (VADER + lexicon)": df[text].astype(str).apply(_score)}
    print(f"File read as {enc}. {len(df):,} reviews. Gold = {src}.\n")
    for name, comp in variants.items():
        pred = comp.apply(to_label)
        print(f"=== {name} ===  accuracy {accuracy_score(gold, pred):.3f}   macro-F1 {f1_score(gold, pred, average='macro', zero_division=0):.3f}")
        print(classification_report(gold, pred, digits=3, zero_division=0))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("path"); ap.add_argument("--text"); ap.add_argument("--label")
    ap.add_argument("--rating"); ap.add_argument("--n", type=int, default=20000)
    a = ap.parse_args()
    run(a.path, a.text, a.label, a.rating, a.n)
