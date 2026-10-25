"""Discover product-specific topics from the reviews themselves, so ReviewLens works for any category
(air coolers, phones, shoes, ...) and not only the built-in earbud topics."""
import re
import numpy as np, pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from .config import ASPECT_RE
from .pipeline import _SPLIT, _score, _sia

GENERIC = set("""product products item items one get got buy bought purchase purchased order ordered use used using day days week weeks
month months year years time hour hours thing things lot much even still make made look looks looking amazon flipkart seller
company brand price quality delivery review reviews rating stars star money rupees rs bit little thank thanks guys sir
people person customer customers service work works worked working experience sale overall honest sharing shared recommend recommended
took came went said told gave come take taking going gone left want wanted need needed asked called tried try keeps kept says
hai bhi hain nahi bahut thi tha hota kar kya yeh aur ekdum bilkul mein hai""".split())
_LEXICON = {w.lower() for w in _sia.lexicon}


def discover_aspects(texts, ratings=None, k=6, max_reviews=8000, max_clauses=15000, seed=42):
    """Return {topic name: compiled regex} for up to k frequent product nouns/phrases that are not already covered by the
    built-in topics. A word qualifies if it shows up in opinionated clauses with some negative evidence, OR if reviews that
    mention it have a clearly different star rating (this catches topics the sentiment lexicon cannot read, e.g. 'too loud').
    Opinion words (good, poor, excellent) are excluded."""
    if k <= 0:
        return {}
    d = pd.DataFrame({"t": list(texts), "r": list(ratings) if ratings is not None else np.nan}).dropna(subset=["t"])
    if len(d) > max_reviews:
        d = d.sample(max_reviews, random_state=seed)
    clauses, crate = [], []
    for t, r in zip(d.t.astype(str), d.r):
        for c in _SPLIT.split(t):
            if c and len(c.split()) >= 2:
                clauses.append(c.strip()); crate.append(r)
    if len(clauses) > max_clauses:
        keep = np.random.default_rng(seed).choice(len(clauses), max_clauses, replace=False)
        clauses, crate = [clauses[i] for i in keep], [crate[i] for i in keep]
    if len(clauses) < 300:
        return {}
    comp = np.array([_score(c) for c in clauses]); absc, crate = np.abs(comp), np.array(crate, dtype=float)
    has_r, mean_r = not np.isnan(crate).all(), np.nanmean(crate) if not np.isnan(crate).all() else 0
    cv = CountVectorizer(stop_words="english", ngram_range=(1, 2), binary=True, lowercase=True,
                         min_df=max(8, int(0.004 * len(clauses))), token_pattern=r"(?u)\b[a-z]{3,}\b")
    X = cv.fit_transform(clauses).tocsc()
    terms, df = cv.get_feature_names_out(), np.asarray(X.sum(axis=0)).ravel()
    unigram_df = {t: n for t, n in zip(terms, df) if " " not in t}
    cands = []
    for j, t in enumerate(terms):
        toks = t.split()
        if any(w in GENERIC or w in _LEXICON or w.endswith("ed") for w in toks) or any(p.search(t) for p in ASPECT_RE.values()):
            continue
        if len(toks) == 2 and df[j] < 0.5 * min(unigram_df.get(w, 0) for w in toks):
            continue  # a bigram must be a real phrase, not two unrelated common words
        rows = X[:, j].nonzero()[0]
        ev, neg = absc[rows].mean(), int((comp[rows] <= -0.15).sum())
        dev = (mean_r - np.nanmean(crate[rows])) if has_r else 0.0   # > 0: reviews mentioning it rate lower than average
        if (ev >= 0.2 and neg >= 3) or dev >= 0.15:
            cands.append((df[j] * max(ev, dev), t, toks))
    picked, used = {}, set()
    for _, t, toks in sorted(cands, reverse=True):
        if used & set(toks):
            continue
        picked[t] = re.compile(r"\b" + r"\W+".join(re.escape(w) for w in toks) + r"s?\b", re.I)
        used |= set(toks)
        if len(picked) >= k:
            break
    return picked
