"""Thin orchestration layer around the original Review Lens analysis modules."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.ingest import guess_columns, read_table, standardize
from src.pipeline import clean_reviews, extract_aspects, aspect_summary, find_issues, emerging, weekly_net
from src.insights import key_drivers, risk_signals, executive_summary, cooccurrence, signal_words
from src.search import build_index, search as search_reviews_engine
from src.discovery import discover_aspects
from src.brief import make_brief

_SEARCH_STATE = None


def search_reviews(query: str, limit: int = 8) -> list[dict]:
    if not query.strip() or _SEARCH_STATE is None:
        return []
    reviews, vectorizer, matrix = _SEARCH_STATE
    return _records(search_reviews_engine(query.strip(), reviews, vectorizer, matrix, k=max(1, min(limit, 50))))


def _records(frame: pd.DataFrame, limit: int | None = None) -> list[dict]:
    if frame is None or frame.empty:
        return []
    out = frame.head(limit) if limit else frame
    result = out.copy()
    for col in result.columns:
        if pd.api.types.is_datetime64_any_dtype(result[col]):
            result[col] = result[col].astype(str)
    return json.loads(result.to_json(orient="records", date_format="iso"))


def analyse_upload(file_bytes: bytes, filename: str, product_filter: str | None = None) -> dict:
    """Use existing ingestion and analysis functions; do not duplicate algorithms."""
    global _SEARCH_STATE
    raw, file_format = read_table(file_bytes, filename)
    mapping = guess_columns(raw)
    if not mapping.get("review_text"):
        raise ValueError("Could not identify a review-text column. Include a column such as review_text, reviews.text, review, or content.")
    clean, notes = standardize(raw, mapping)
    products = sorted(str(v) for v in clean["brand"].dropna().unique())
    if product_filter and product_filter != "__all__":
        clean = clean[clean["brand"].astype(str) == product_filter].copy()
        if clean.empty:
            raise ValueError(f"No reviews found for product: {product_filter}")
        notes = [*notes, f"Product filter active: {product_filter}"]
    if clean.empty:
        raise ValueError("No usable reviews remained after cleaning.")
    clean = clean_reviews(clean)
    try:
        vectorizer, matrix = build_index(clean)
        _SEARCH_STATE = (clean, vectorizer, matrix)
    except ValueError:
        # Some datasets contain no indexable English tokens; analysis should still run.
        _SEARCH_STATE = None
    try:
        extra_topics = discover_aspects(clean.review_text, clean.rating) if len(clean) >= 300 else {}
    except (ValueError, TypeError):
        extra_topics = {}
    aspects = extract_aspects(clean, extra=extra_topics)
    summary = aspect_summary(aspects) if not aspects.empty else pd.DataFrame(columns=["pos", "neu", "neg", "mentions", "net"])
    issues = find_issues(aspects, clean)
    alerts = emerging(aspects)
    drivers, driver_r2, driver_n = key_drivers(aspects, clean) if not aspects.empty else (pd.DataFrame(), 0.0, 0)
    risks = risk_signals(clean)
    pairs = cooccurrence(aspects) if not aspects.empty else pd.DataFrame()
    try:
        words = signal_words(aspects) if not aspects.empty else pd.DataFrame()
    except ValueError:
        words = pd.DataFrame()
    summary_lines = executive_summary(
        clean, aspects, summary, issues, alerts, drivers, risks,
        rating_estimated=bool(clean.attrs.get("rating_estimated", False)),
    ) if not clean.empty and not summary.empty else [
        f"{len(clean):,} usable reviews loaded. No recognised aspect mentions were found; consider adjusting the aspect lexicon."
    ]
    brand = str(clean["brand"].mode().iloc[0]) if not clean.empty else "All products"
    brief = make_brief(brand, clean, aspects, issues, alerts)
    trends = weekly_net(aspects) if not aspects.empty and aspects["date"].nunique() > 1 else pd.DataFrame()
    return {
        "filename": Path(filename).name,
        "format": str(file_format),
        "products": products,
        "selected_product": product_filter if product_filter and product_filter != "__all__" else "__all__",
        "rows_received": int(len(raw)),
        "rows_analysed": int(len(clean)),
        "rating_estimated": bool(clean.attrs.get("rating_estimated", False)),
        "notes": list(notes),
        "summary": {
            "average_rating": round(float(clean.rating.mean()), 2),
            "review_count": int(len(clean)),
            "flagged_count": int(clean.flagged.sum()),
            "brand_count": int(clean.brand.nunique()),
            "positive_share": round(float((aspects.sentiment == "pos").mean() * 100), 1) if not aspects.empty else 0,
            "negative_share": round(float((aspects.sentiment == "neg").mean() * 100), 1) if not aspects.empty else 0,
        },
        "executive_summary": summary_lines,
        "aspects": _records(summary.reset_index().sort_values("net", ascending=True) if not summary.empty else summary),
        "discovered_topics": sorted(extra_topics.keys()),
        "issues": _records(issues, 20),
        "alerts": _records(alerts, 20),
        "risks": _records(risks),
        "cooccurrence": _records(pairs),
        "signal_words": _records(words),
        "drivers": _records(drivers, 20),
        "driver_r2": round(float(driver_r2), 3),
        "driver_reviews": int(driver_n),
        "trends": _records(trends, 500),
        "reviews": _records(clean[["review_id", "brand", "date", "rating", "review_text", "flagged"]], 500),
        "brief": brief,
    }
