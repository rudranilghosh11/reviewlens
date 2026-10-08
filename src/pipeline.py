"""ReviewLens core: clean -> aspect extraction -> aspect sentiment -> issues -> priority."""
import re
import numpy as np, pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from .config import ASPECT_RE, DOMAIN_LEXICON, OWNERS, ACTIONS

_sia = SentimentIntensityAnalyzer()
_sia.lexicon.update(DOMAIN_LEXICON)
# phrases whose words flip meaning in context ("zero lag", "without any issue")
_PHRASES = {r"\b(zero|no) lag\b": "smooth", r"\bwithout any (issue|problem)s?\b": "smoothly", r"\bno (issue|problem)s?\b": "smoothly", r"\btook ages\b": "was awful and terrible"}


def _score(text):
    for pat, rep in _PHRASES.items():
        text = re.sub(pat, rep, text, flags=re.I)
    return _sia.polarity_scores(text)["compound"]


_SPLIT = re.compile(r"(?<=[.!?])\s+|;|\s+but\s+|\s+however\s+|\s+though\s+", re.I)


def load_reviews(path="data/reviews.csv"):
    df = pd.read_csv(path)
    need = {"review_id", "brand", "date", "rating", "review_text"}
    if missing := need - set(df.columns):
        raise ValueError(f"CSV is missing columns: {sorted(missing)}")
    return df


def clean_reviews(df):
    """Normalise, flag duplicates / spam-like text, score overall sentiment, flag star-text mismatch."""
    d = df.copy()
    d["date"] = pd.to_datetime(d["date"])
    d["review_text"] = d["review_text"].fillna("").astype(str).str.strip()
    norm = d["review_text"].str.lower().str.replace(r"[^a-z0-9 ]", "", regex=True)
    words = norm.str.split()
    d["is_duplicate"] = norm.duplicated()
    d["is_too_short"] = words.str.len() < 4
    d["is_repetitive"] = words.apply(lambda w: len(w) > 6 and len(set(w)) / len(w) < 0.5)
    d["flagged"] = d[["is_duplicate", "is_too_short", "is_repetitive"]].any(axis=1)
    d["overall"] = d["review_text"].apply(_score)
    d["rating_mismatch"] = ((d.rating >= 4) & (d.overall <= -0.3)) | ((d.rating <= 2) & (d.overall >= 0.4))
    return d


def extract_aspects(d):
    """One row per (review, clause, aspect) with a sentiment label."""
    rows = []
    for r in d[~d.flagged].itertuples():
        for s in filter(None, (x.strip() for x in _SPLIT.split(r.review_text) if x)):
            hit = [a for a, p in ASPECT_RE.items() if p.search(s)]
            if not hit:
                continue
            comp = _score(s)
            rows += [(r.review_id, r.brand, r.date, r.rating, a, s, comp) for a in hit]
    a = pd.DataFrame(rows, columns=["review_id", "brand", "date", "rating", "aspect", "sentence", "compound"])
    a["sentiment"] = np.select([a.compound >= 0.15, a.compound <= -0.15], ["pos", "neg"], "neu")
    return a


def aspect_summary(a):
    """Share of pos / neu / neg per aspect and a net sentiment score in [-1, 1]."""
    t = a.groupby(["aspect", "sentiment"]).size().unstack(fill_value=0)
    for c in ("pos", "neu", "neg"):
        t[c] = t.get(c, 0)
    t["mentions"] = t[["pos", "neu", "neg"]].sum(axis=1)
    t["net"] = (t.pos - t.neg) / t.mentions
    return t.sort_values("net")


def find_issues(a, reviews, now=None, window=28, top=None):
    """Cluster negative clauses within each aspect into concrete issues and rank them.
    priority = share_of_reviews * (0.5 + severity) * (1 + trend_growth) * (1 + rating_drag/2), scaled 0-100."""
    base = reviews[~reviews.flagged]
    now = now or a.date.max()
    mean_rating, n_rev, out = base.rating.mean(), max(len(base), 1), []
    for asp, g in a[a.sentiment == "neg"].groupby("aspect"):
        if len(g) < 10:
            continue
        vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=2)
        try:
            X = vec.fit_transform(g.sentence)
        except ValueError:
            continue
        k = max(1, min(3, len(g) // 40))
        km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(X)
        dist = km.transform(X)
        g = g.assign(cluster=km.labels_)
        for c in range(k):
            m = (g.cluster == c).values
            gc = g[m]
            if len(gc) < 5:
                continue
            ids = gc.review_id.unique()
            sev = float((-gc.compound).clip(0, 1).mean())
            drag = max(mean_rating - base[base.review_id.isin(ids)].rating.mean(), 0)
            recent = int((gc.date > now - pd.Timedelta(days=window)).sum())
            prior = int(((gc.date <= now - pd.Timedelta(days=window)) &
                         (gc.date > now - pd.Timedelta(days=2 * window))).sum())
            growth = float(np.clip((recent - prior) / max(prior, 5), -1, 2))
            share = len(ids) / n_rev
            raw = share * (0.5 + sev) * (1 + max(growth, 0)) * (1 + drag / 2)
            order = np.argsort(dist[m, c])
            cand = gc.sentence.iloc[order].str.strip().str.rstrip(".!? ")
            quotes = cand.loc[~cand.str.lower().duplicated()].head(3).tolist()
            out.append(dict(aspect=asp, issue=quotes[0], mentions=len(gc), reviews=len(ids),
                            pct_reviews=round(100 * share, 1), severity=round(sev, 2),
                            rating_drag=round(drag, 2), recent=recent, prior=prior,
                            trend=round(growth, 2), raw=raw, quotes=quotes,
                            owner=OWNERS.get(asp, "Product"), action=ACTIONS.get(asp, "Investigate.")))
    df = pd.DataFrame(out)
    if df.empty:
        return df
    df["priority"] = (100 * df.raw / df.raw.max()).round(0).astype(int)
    df = df.drop(columns="raw").sort_values("priority", ascending=False).reset_index(drop=True)
    return df.head(top) if top else df


def emerging(a, now=None, recent_days=14, base_days=56, min_recent=8, ratio=1.6):
    """Flag brand x aspect pairs whose negative mentions spiked vs. their recent baseline."""
    now = now or a.date.max()
    neg, res = a[a.sentiment == "neg"], []
    for (b, asp), g in neg.groupby(["brand", "aspect"]):
        r = int((g.date > now - pd.Timedelta(days=recent_days)).sum())
        p = int(((g.date <= now - pd.Timedelta(days=recent_days)) &
                 (g.date > now - pd.Timedelta(days=recent_days + base_days))).sum())
        expected = p / base_days * recent_days
        x = (r + 1) / (expected + 1)
        if r >= min_recent and x >= ratio:
            res.append(dict(brand=b, aspect=asp, recent=r, expected=round(expected, 1), spike=round(x, 1)))
    return pd.DataFrame(res).sort_values("spike", ascending=False) if res else pd.DataFrame(
        columns=["brand", "aspect", "recent", "expected", "spike"])


def weekly_net(a):
    """Weekly net sentiment per aspect (for trend charts)."""
    w = a.assign(week=a.date.dt.to_period("W").dt.start_time)
    t = w.groupby(["week", "aspect"]).apply(
        lambda g: (g.sentiment.eq("pos").sum() - g.sentiment.eq("neg").sum()) / len(g), include_groups=False)
    return t.rename("net").reset_index()


def run_all(path="data/reviews.csv"):
    reviews = clean_reviews(load_reviews(path))
    a = extract_aspects(reviews)
    return reviews, a
