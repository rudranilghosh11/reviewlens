"""Analysis service — orchestrates src/ modules without any HTTP coupling.

Every function in this module calls REAL functions from the original ReviewLens
analysis engine.  No invented replacements.
"""
from __future__ import annotations

import uuid
from typing import Any

import pandas as pd

from src.ingest import read_table, guess_columns, standardize
from src.pipeline import clean_reviews, extract_aspects, aspect_summary, find_issues, emerging, weekly_net
from src.discovery import discover_aspects
from src.insights import key_drivers, risk_signals, cooccurrence, signal_words, executive_summary
from src.search import build_index, search as search_reviews
from src.brief import make_brief

from app.core.config import MAX_ANALYSIS_ROWS

# In-memory store for analysis sessions (local single-user app).
_sessions: dict[str, dict[str, Any]] = {}


def run_analysis(raw_bytes: bytes, filename: str, column_overrides: dict | None = None) -> dict[str, Any]:
    """Full analysis pipeline.  Returns a dict matching AnalysisResult schema."""

    # 1. Read the file
    df, fmt = read_table(raw_bytes, name=filename)
    if df.empty:
        raise ValueError("The uploaded file contains no data.")

    # 2. Guess or override column mapping
    mapping = guess_columns(df)
    if column_overrides:
        for k, v in column_overrides.items():
            if v is not None:
                mapping[k] = v

    if mapping.get("review_text") is None:
        raise ValueError(
            "No review-text column found. The dataset must contain a column "
            "with review text (e.g. 'review_text', 'Review', 'comment', 'feedback')."
        )

    # 3. Standardise
    std_df, notes = standardize(df, mapping, max_rows=MAX_ANALYSIS_ROWS)
    rating_estimated = std_df.attrs.get("rating_estimated", False)

    # 4. Clean
    reviews = clean_reviews(std_df)

    # 5. Discover new topics
    good = reviews[~reviews.flagged]
    discovered = discover_aspects(good.review_text, good.rating)

    # 6. Extract aspects
    aspects_df = extract_aspects(reviews, extra=discovered)

    # 7. Aspect summary
    summ = aspect_summary(aspects_df)

    # 8. Issues
    issues_df = find_issues(aspects_df, reviews)

    # 9. Emerging alerts
    alerts_df = emerging(aspects_df)

    # 10. Weekly trends
    has_dates = aspects_df.date.nunique() > 1
    if has_dates:
        trends_df = weekly_net(aspects_df)
    else:
        trends_df = pd.DataFrame(columns=["week", "aspect", "net"])

    # 11. Key drivers
    drivers_df, r2, _ = key_drivers(aspects_df, reviews)

    # 12. Risk signals
    risks_df = risk_signals(good)

    # 13. Co-occurrence
    cooc_df = cooccurrence(aspects_df)

    # 14. Signal words
    words_df = signal_words(aspects_df)

    # 15. Executive summary
    exec_lines = executive_summary(good, aspects_df, summ, issues_df, alerts_df, drivers_df, risks_df,
                                   rating_estimated=rating_estimated)

    # 16. Build search index
    vec, X = build_index(good)

    # Compute date range
    date_min = str(good.date.min().date()) if has_dates else ""
    date_max = str(good.date.max().date()) if has_dates else ""

    # Brands
       # Brands
    brands = sorted(good.brand.dropna().unique().tolist())

    # Products
    products = (
        sorted(good["product"].dropna().astype(str).unique().tolist())
        if "product" in good.columns
        else []
    )

    # Persist in session
    aid = uuid.uuid4().hex[:12]
    _sessions[aid] = {
        "reviews": reviews,
         "products": products,
        "aspects": aspects_df,
        "issues": issues_df,
        "alerts": alerts_df,
        "summ": summ,
        "vec": vec,
        "X": X,
        "good": good,
        "rating_estimated": rating_estimated,
    }

    # Serialise everything
    aspect_list = []
    for idx, row in summ.iterrows():
        aspect_list.append({
            "aspect": idx,
            "pos": int(row.get("pos", 0)),
            "neu": int(row.get("neu", 0)),
            "neg": int(row.get("neg", 0)),
            "mentions": int(row.get("mentions", 0)),
            "net": round(float(row.get("net", 0)), 3),
        })

    issues_list = []
    for _, row in issues_df.iterrows():
        issues_list.append({
            "aspect": row.aspect,
            "issue": row.issue,
            "mentions": int(row.mentions),
            "reviews": int(row.reviews),
            "pct_reviews": float(row.pct_reviews),
            "severity": float(row.severity),
            "dated": bool(row.dated),
            "rating_drag": float(row.rating_drag),
            "recent": int(row.recent),
            "prior": int(row.prior),
            "trend": float(row.trend),
            "priority": int(row.priority),
            "quotes": row.quotes if isinstance(row.quotes, list) else [],
            "owner": row.owner,
            "action": row.action,
        })

    alerts_list = []
    for _, row in alerts_df.iterrows():
        alerts_list.append({
            "brand": row.brand,
            "aspect": row.aspect,
            "recent": int(row.recent),
            "expected": float(row.expected),
            "spike": float(row.spike),
        })

    trends_list = []
    for _, row in trends_df.iterrows():
        trends_list.append({
            "week": str(row.week.date()) if hasattr(row.week, "date") else str(row.week),
            "aspect": row.aspect,
            "net": round(float(row.net), 3),
        })

    risks_list = []
    for _, row in risks_df.iterrows():
        risks_list.append({
            "category": row.category,
            "reviews": int(row.reviews),
            "pct": round(float(row.pct), 2),
            "color": row.color,
            "example": row.example if isinstance(row.example, str) else "",
        })

    drivers_list = []
    if not drivers_df.empty:
        for _, row in drivers_df.iterrows():
            drivers_list.append({
                "aspect": row.aspect,
                "reviews_negative": int(row.reviews_negative),
                "share_negative": round(float(row.share_negative), 4),
                "stars_effect": round(float(row.stars_effect), 4),
                "gain": round(float(row.gain), 4),
            })

    cooc_list = []
    for _, row in cooc_df.iterrows():
        cooc_list.append({
            "a": row.a,
            "b": row.b,
            "reviews": int(row.reviews),
            "lift": round(float(row.lift), 2),
        })

    words_list = []
    for _, row in words_df.iterrows():
        words_list.append({
            "word": row.word,
            "complaints": int(row.complaints),
            "times_more_common": round(float(row.times_more_common), 2),
        })

    return {
        "analysis_id": aid,
        "overview": {
            "total_reviews": len(reviews),
            "usable_reviews": len(good),
            "flagged_reviews": int(reviews.flagged.sum()),
            "avg_rating": round(float(good.rating.mean()), 2),
            "rating_estimated": rating_estimated,
            "has_dates": has_dates,
            "has_brands": len(brands) > 1 or (len(brands) == 1 and brands[0] != "All products"),
            "brands": brands,
            "products": products,
            "notes": notes,
            "date_range": [date_min, date_max],
        },
        "aspect_summary": aspect_list,
        "issues": issues_list,
        "emerging_alerts": alerts_list,
        "weekly_trends": trends_list,
        "risk_signals": risks_list,
        "key_drivers": drivers_list,
        "key_drivers_r2": round(float(r2), 3),
        "co_occurrences": cooc_list,
        "signal_words": words_list,
        "executive_summary": exec_lines,
        "discovered_topics": list(discovered.keys()),
    }


def search_session(analysis_id: str, query: str, k: int = 10) -> list[dict]:
    """Search reviews in a previous analysis session."""
    sess = _sessions.get(analysis_id)
    if sess is None:
        raise KeyError(f"Analysis session '{analysis_id}' not found. Run an analysis first.")
    results = search_reviews(query, sess["good"], sess["vec"], sess["X"], k=k)
    out = []
    for _, row in results.iterrows():
        out.append({
            "review_id": str(row.review_id),
            "brand": str(row.brand),
            "date": str(row.date.date()) if hasattr(row.date, "date") else str(row.date),
            "rating": int(row.rating),
            "review_text": str(row.review_text),
            "match": round(float(row.match), 3),
        })
    return out



def get_reviews(
    analysis_id: str,
    page: int = 1,
    per_page: int = 50,
    brand: str | None = None,
    sentiment: str | None = None,
    product: str | None = None,
) -> dict:
    """Paginated review explorer with optional product filtering."""
    sess = _sessions.get(analysis_id)
    if sess is None:
        raise KeyError(f"Analysis session '{analysis_id}' not found.")

    reviews = sess["reviews"]
    df = reviews.copy()

    if brand and brand != "All":
        df = df[df.brand == brand]

    if product and product != "All":
        if "product" in df.columns:
            df = df[df["product"].astype(str) == product]
        else:
            df = df.iloc[0:0]

    if sentiment == "positive":
        df = df[df.overall >= 0.15]
    elif sentiment == "negative":
        df = df[df.overall <= -0.15]
    elif sentiment == "neutral":
        df = df[(df.overall > -0.15) & (df.overall < 0.15)]

    total = len(df)
    start = (page - 1) * per_page
    end = start + per_page
    page_df = df.iloc[start:end]

    items = []
    for _, row in page_df.iterrows():
        items.append({
            "review_id": str(row.review_id),
            "brand": str(row.brand),
            "product": str(row.product) if "product" in df.columns else "",
            "date": str(row.date.date()) if hasattr(row.date, "date") else str(row.date),
            "rating": int(row.rating),
            "review_text": str(row.review_text),
            "overall": round(float(row.overall), 3),
            "flagged": bool(row.flagged),
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
    }



def generate_brief(analysis_id: str, brand: str = "All brands") -> str:
    """Generate PM brief markdown for a completed analysis."""
    sess = _sessions.get(analysis_id)
    if sess is None:
        raise KeyError(f"Analysis session '{analysis_id}' not found.")
    reviews = sess["reviews"]
    aspects_df = sess["aspects"]
    issues_df = sess["issues"]
    alerts_df = sess["alerts"]
    return make_brief(brand, reviews, aspects_df, issues_df, alerts_df)


def get_competitor_heatmap(analysis_id: str) -> dict:
    """Brand × aspect net sentiment matrix for the competitor heatmap."""
    sess = _sessions.get(analysis_id)
    if sess is None:
        raise KeyError(f"Analysis session '{analysis_id}' not found.")
    aspects_df = sess["aspects"]
    if aspects_df.brand.nunique() < 2:
        return {"brands": [], "aspects": [], "matrix": []}

    pivot = aspects_df.groupby(["brand", "aspect"]).apply(
        lambda g: round((g.sentiment.eq("pos").sum() - g.sentiment.eq("neg").sum()) / max(len(g), 1), 3),
        include_groups=False
    ).unstack(fill_value=0)

    return {
        "brands": pivot.index.tolist(),
        "aspects": pivot.columns.tolist(),
        "matrix": pivot.values.tolist(),
    }


def list_sessions() -> list[str]:
    """Return active analysis session IDs."""
    return list(_sessions.keys())
