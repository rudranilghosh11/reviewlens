"""Deeper insights beyond sentiment: what moves the rating, risk signals, issues that travel together,
words that signal trouble, and an auto-written summary."""
import re, warnings
import numpy as np, pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

RISK_PATTERNS = {
    "Safety": r"\b(fire|burn(t|ing|s)?|smok(e|ing)|shock(ed)?|spark(s|ing)?|explod\w*|overheat\w*|melt(ed|ing)?|injur\w*|rash|allerg\w*|unsafe|danger\w*)\b",
    "Likely to churn": r"\b(never (buy|again|order)|won'?t (buy|recommend|order)|do ?n[o']?t buy|waste of (money|time)|not recommend\w*|switch(ed|ing)? to|worst|regret\w*)\b",
    "Authenticity or fraud": r"\b(fake|counterfeit|duplicate|refurbished|scam|fraud|cheat(ed|ing)?|not original|used (product|item))\b",
    "Refund or return": r"\b(refund\w*|return(ed|ing)?|replac(e|ed|ement)|money back|cancel(led|ed)?)\b",
}
RISK_COLOR = {"Safety": "red", "Likely to churn": "amber", "Authenticity or fraud": "amber", "Refund or return": "blue"}


def key_drivers(a, reviews, min_reviews=200, alpha=5.0):
    """Ridge regression of star rating on 'has a negative / positive clause about topic X'.
    Returns (table, r2, n_reviews). gain = estimated change in the AVERAGE rating if complaints about the topic vanished."""
    base = reviews[~reviews.flagged].set_index("review_id")
    flags = a.assign(neg=a.sentiment.eq("neg"), pos=a.sentiment.eq("pos")).groupby(["review_id", "aspect"])[["neg", "pos"]].max()
    neg = flags["neg"].unstack(fill_value=False).astype(float)
    pos = flags["pos"].unstack(fill_value=False).astype(float).reindex(columns=neg.columns, fill_value=0.0)
    idx = neg.index.intersection(base.index)
    if len(idx) < min_reviews:
        return pd.DataFrame(), 0.0, len(idx)
    neg, pos, y = neg.loc[idx], pos.loc[idx], base.loc[idx, "rating"].astype(float).values
    X = np.hstack([neg.values, pos.values]); Xc, yc = X - X.mean(0), y - y.mean()
    beta = np.linalg.solve(Xc.T @ Xc + alpha * np.eye(X.shape[1]), Xc.T @ yc)
    r2 = 1 - ((yc - Xc @ beta) ** 2).sum() / max((yc ** 2).sum(), 1e-9)
    k, share_cov = neg.shape[1], len(idx) / max(len(base), 1)
    out = pd.DataFrame({"aspect": neg.columns, "reviews_negative": neg.sum().astype(int).values,
                        "share_negative": neg.mean().values, "stars_effect": beta[:k]})
    out["gain"] = (-out.stars_effect).clip(lower=0) * out.share_negative * share_cov
    return out.sort_values("gain", ascending=False).reset_index(drop=True), float(max(r2, 0)), len(idx)


def risk_signals(good):
    """Count reviews mentioning safety, churn, fraud and refund/return language, with the most negative example."""
    rows = []
    for name, pat in RISK_PATTERNS.items():
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # patterns use capture groups on purpose
            m = good.review_text.str.contains(pat, flags=re.I, regex=True)
        ex = good[m].sort_values("overall").head(1).review_text
        rows.append(dict(category=name, reviews=int(m.sum()), pct=100 * m.mean(), color=RISK_COLOR[name],
                         example=(ex.iloc[0][:170] + ("..." if len(ex.iloc[0]) > 170 else "")) if len(ex) else ""))
    return pd.DataFrame(rows)


def cooccurrence(a, min_pairs=15, top=6):
    """Topic pairs whose complaints appear in the same review more often than chance (lift > 1)."""
    n = a.review_id.nunique()
    neg = a[a.sentiment == "neg"].assign(v=1).pivot_table(index="review_id", columns="aspect", values="v", aggfunc="max", fill_value=0)
    if neg.shape[1] < 2:
        return pd.DataFrame(columns=["a", "b", "reviews", "lift"])
    M, rows = neg.values, []
    for i in range(M.shape[1]):
        for j in range(i + 1, M.shape[1]):
            both = int((M[:, i] * M[:, j]).sum())
            if both >= min_pairs:
                rows.append(dict(a=neg.columns[i], b=neg.columns[j], reviews=both,
                                 lift=both * n / (M[:, i].sum() * M[:, j].sum())))
    return pd.DataFrame(rows).sort_values("lift", ascending=False).head(top).reset_index(drop=True) if rows else \
        pd.DataFrame(columns=["a", "b", "reviews", "lift"])


def signal_words(a, top=10, min_mentions=10):
    """Words far more common in negative clauses than in positive ones."""
    d = a[a.sentiment.isin(["neg", "pos"])].drop_duplicates(["review_id", "sentence"])
    cv = CountVectorizer(stop_words="english", binary=True, min_df=min_mentions, token_pattern=r"(?u)\b[a-z]{3,}\b")
    X = cv.fit_transform(d.sentence.str.lower())
    isneg = d.sentiment.eq("neg").values
    cn, cp = np.asarray(X[isneg].sum(0)).ravel(), np.asarray(X[~isneg].sum(0)).ravel()
    if isneg.sum() == 0 or (~isneg).sum() == 0:
        return pd.DataFrame(columns=["word", "complaints", "times_more_common"])
    ratio = ((cn + 1) / (isneg.sum() + 2)) / ((cp + 1) / ((~isneg).sum() + 2))
    out = pd.DataFrame({"word": cv.get_feature_names_out(), "complaints": cn.astype(int), "times_more_common": ratio})
    return out[(out.complaints >= min_mentions) & (out.times_more_common > 1.5)].sort_values("times_more_common", ascending=False).head(top).reset_index(drop=True)


def executive_summary(good, a, summ, issues, alerts, drivers, risks, rating_estimated=False):
    """A few plain-English sentences, all computed from the data."""
    out, pos_share = [], 100 * (a.sentiment == "pos").mean()
    out.append(f"{len(good):,} reviews average {good.rating.mean():.2f} stars{' (estimated from text)' if rating_estimated else ''}; "
               f"{pos_share:.0f}% of topic mentions are positive and {summ.index[0]} is the weakest topic (net {summ.net.iloc[0]:+.2f}).")
    if len(issues):
        t = issues.iloc[0]
        out.append(f"The top issue is \u201c{t.issue}\u201d ({t.aspect}), mentioned in {t.pct_reviews}% of reviews.")
    if len(drivers) and not rating_estimated and drivers.gain.iloc[0] >= 0.005:
        g = drivers.iloc[0]
        out.append(f"Eliminating {g.aspect} complaints could lift the average rating by roughly {g.gain:.2f} stars "
                   "(an estimate from patterns in the data, not a guarantee).")
    if len(alerts):
        r = alerts.iloc[0]
        out.append(f"{len(alerts)} emerging {'issue needs' if len(alerts) == 1 else 'issues need'} attention, led by {r.brand} {r.aspect} at {r.spike}x its recent baseline.")
    big = risks.sort_values("pct", ascending=False)
    big = big[(big.category.isin(["Safety", "Authenticity or fraud"])) & (big.reviews >= 3)]
    if len(big):
        r = big.iloc[0]
        out.append(f"{r.pct:.1f}% of reviews raise {r.category.lower()} concerns ({r.reviews:,} reviews): worth a manual look.")
    return out
