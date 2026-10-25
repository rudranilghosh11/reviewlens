import pandas as pd
from src.pipeline import clean_reviews, extract_aspects, find_issues

def _df(texts):
    return pd.DataFrame(dict(review_id=[f"r{i}" for i in range(len(texts))], brand="B", rating=3,
                             date="2026-09-01", review_text=texts))

def test_duplicates_and_short_are_flagged():
    d = clean_reviews(_df(["Battery is great and lasts long", "Battery is great and lasts long", "ok"]))
    assert d.flagged.tolist() == [False, True, True]

def test_mixed_sentiment_split_by_clause():
    a = extract_aspects(clean_reviews(_df(["Sound is crisp with deep bass but battery drains within two hours."])))
    got = dict(zip(a.aspect, a.sentiment))
    assert got["sound"] == "pos" and got["battery"] == "neg"

def test_hinglish_terms():
    a = extract_aspects(clean_reviews(_df(["Delivery bahut late thi, bekar experience for me."])))
    assert (a[a.aspect == "delivery"].sentiment == "neg").all()

def test_issue_ranking_runs():
    d = clean_reviews(_df([f"Delivery was late by over a week, case {i}" for i in range(60)]))
    assert not find_issues(extract_aspects(d), d).empty
