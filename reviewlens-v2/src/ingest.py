"""Robust CSV ingestion: any encoding, any column names -> the 5 columns ReviewLens needs
(review_id, brand, date, rating, review_text). Used by the dashboard upload and the CLI."""
import io, re, json, gzip
from pathlib import Path
import numpy as np, pandas as pd

ENCODINGS = ("utf-8", "utf-8-sig", "cp1252", "latin-1")  # latin-1 never fails, so something always loads

_NONLATIN = re.compile("[\u0900-\u0DFF\u0600-\u06FF\u0400-\u04FF\u4E00-\u9FFF\u3040-\u30FF\uAC00-\uD7AF]")  # Indic, Arabic, Cyrillic, CJK


def _norm(c):
    return re.sub(r"[^a-z0-9]", "", str(c).lower())

CANDIDATES = {
    "review_text": ["reviewtext", "review", "reviews", "text", "content", "body", "comment", "comments", "reviewbody",
                    "reviewstext", "reviewcontent", "customerreview", "feedback", "reviewdescription"],
    "title": ["title", "reviewtitle", "headline", "subject", "summary"],
    "rating": ["rating", "ratings", "rate", "stars", "starrating", "overall", "score", "reviewrating", "reviewsrating",
               "reviewscore", "productrating"],
    "date": ["date", "reviewdate", "reviewtime", "timestamp", "time", "unixreviewtime", "reviewsdate", "createdat",
             "reviewedat", "datereviewed", "postdate"],
    "brand": ["brand", "brandname", "manufacturer", "productname", "product", "producttitle", "seller", "itemname", "name",
              "category", "asin"],
    "review_id": ["reviewid", "id", "srno", "index"],
}


def read_csv_robust(src):
    """src: file path or raw bytes. Returns (DataFrame, encoding_used)."""
    raw = bytes(src) if isinstance(src, (bytes, bytearray)) else open(src, "rb").read()
    encs = ("utf-16",) + ENCODINGS if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else ENCODINGS
    last = None
    for enc in encs:
        try:
            kw = dict(encoding=enc, low_memory=False, on_bad_lines="skip")
            df = pd.read_csv(io.BytesIO(raw), **kw)
            if df.shape[1] == 1:  # maybe a different delimiter
                for sep in (";", "\t", "|"):
                    alt = pd.read_csv(io.BytesIO(raw), sep=sep, **kw)
                    if alt.shape[1] > 1:
                        df = alt
                        break
            return df, enc
        except UnicodeDecodeError as e:
            last = e
    raise last


def _decode(raw):
    for enc in ENCODINGS:
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            continue


def _unwrap(obj):
    """Find the list of review records inside a JSON document."""
    if isinstance(obj, dict):
        lists = [v for v in obj.values() if isinstance(v, list) and v and isinstance(v[0], dict)]
        return max(lists, key=len) if lists else [obj]
    return obj


def _read_json(raw):
    """JSON array, {'reviews': [...]} wrapper, or JSON Lines (e.g. Amazon 5-core)."""
    text, _ = _decode(raw)
    try:
        rows = [json.loads(l) for l in text.splitlines() if l.strip()]
        if len(rows) > 1 and all(isinstance(r, dict) for r in rows):
            return pd.json_normalize(rows)
    except json.JSONDecodeError:
        pass
    return pd.json_normalize(_unwrap(json.loads(text)))


def read_table(src, name=""):
    """Read CSV/TSV/TXT, Excel, JSON/JSONL, Parquet (optionally gzipped). Returns (DataFrame, format_or_encoding)."""
    raw = bytes(src) if isinstance(src, (bytes, bytearray)) else open(src, "rb").read()
    name = name or (str(src) if isinstance(src, (str, Path)) else "")
    ext = Path(name).suffix.lower()
    if raw[:2] == b"\x1f\x8b":  # gzip
        raw = gzip.decompress(raw)
        ext = Path(name[:-3]).suffix.lower() if name.lower().endswith(".gz") else ext
    try:
        if raw[:4] == b"PK\x03\x04" or ext in (".xlsx", ".xlsm", ".xls"):
            return pd.read_excel(io.BytesIO(raw)), "Excel (first sheet)"
        if raw[:4] == b"PAR1" or ext == ".parquet":
            return pd.read_parquet(io.BytesIO(raw)), "Parquet"
        if ext in (".json", ".jsonl", ".ndjson") or raw.lstrip()[:1] in (b"{", b"["):
            return _read_json(raw), "JSON"
    except ImportError as e:
        raise ImportError(f"{e}. Install the missing package, for example: pip install openpyxl pyarrow") from e
    return read_csv_robust(raw)


def guess_columns(df):
    """Best guess for each needed column, or None."""
    norm = {}
    for c in df.columns:
        norm.setdefault(_norm(c), c)
    out = {k: next((norm[c] for c in cands if c in norm), None) for k, cands in CANDIDATES.items()}
    sample = df.head(3000)
    if out["review_text"] is None:  # longest-text column
        objs = [c for c in df.columns if sample[c].dtype == object]
        if objs:
            best = max(objs, key=lambda c: sample[c].astype(str).str.len().mean())
            if sample[best].astype(str).str.len().mean() >= 20:
                out["review_text"] = best
    if out["rating"] is None:  # numeric column within 1-5
        for c in df.columns:
            v = pd.to_numeric(sample[c], errors="coerce").dropna()
            if len(v) > 0.8 * len(sample) and v.min() >= 1 and v.max() <= 5 and c != out["review_text"]:
                out["rating"] = c
                break
    return out


def _parse_dates(s):
    if pd.api.types.is_numeric_dtype(s):
        med = s.dropna().median()
        return pd.to_datetime(s, unit="ms" if med > 1e11 else "s", errors="coerce")
    # dd/mm/yyyy vs mm/dd/yyyy: a first part above 12 proves day-first, a second part above 12 proves month-first
    parts = s.dropna().astype(str).head(5000).str.extract(r"^\s*(\d{1,2})[/\-.](\d{1,2})[/\-.]\d{2,4}")
    dayfirst = bool((pd.to_numeric(parts[0], errors="coerce") > 12).any() and not (pd.to_numeric(parts[1], errors="coerce") > 12).any())
    return pd.to_datetime(s, errors="coerce", utc=True, format="mixed", dayfirst=dayfirst).dt.tz_localize(None)


def standardize(df, mapping, max_rows=20000, top_brands=12, brand_first_word=False, seed=42):
    """mapping: {'review_text','rating','date','brand','review_id'} -> column names (None = missing).
    Returns (clean_df, notes). notes are human-readable messages about what was assumed or dropped."""
    notes = []
    text = df[mapping["review_text"]].astype(str).str.strip()
    if mapping.get("title"):
        ti = df[mapping["title"]].astype(str).str.strip().replace({"nan": ""})
        text = (pd.Series(np.where(ti.eq(""), "", ti + ". "), index=df.index) + text).str.strip()
    keep = text.ne("") & text.str.lower().ne("nan")
    if (~keep).sum():
        notes.append(f"Dropped {int((~keep).sum()):,} rows with empty review text.")
    d = df.loc[keep].copy()
    d["_text"] = text[keep]
    if max_rows and len(d) > max_rows:
        d = d.sample(max_rows, random_state=seed).sort_index()
        notes.append(f"Analysing a random sample of {max_rows:,} of {int(keep.sum()):,} reviews (change this in the sidebar).")

    estimated = not mapping.get("rating")
    if estimated:
        from .pipeline import _score
        comp = d["_text"].apply(_score)
        d["_rating"] = pd.cut(comp, [-2, -0.6, -0.2, 0.2, 0.6, 2], labels=[1, 2, 3, 4, 5]).astype(int)
        notes.append("No rating column: star ratings were estimated from the review text, so rating-based figures are approximate.")
    else:
        r = pd.to_numeric(d[mapping["rating"]].astype(str).str.extract(r"(\d+(?:\.\d+)?)")[0], errors="coerce")
        if r.max() > 5:
            if r.max() <= 10:
                r, _ = r / 2, notes.append("Ratings looked like a 1-10 scale, so they were halved to 1-5.")
            else:
                raise ValueError("Rating values go above 10. Pick the correct rating column.")
        bad = r.isna()
        if bad.sum():
            notes.append(f"Dropped {int(bad.sum()):,} rows without a usable rating.")
        d, r = d[~bad], r[~bad]
        d["_rating"] = r.round().clip(1, 5).astype(int)

    if mapping.get("date"):
        dt = _parse_dates(d[mapping["date"]])
        if dt.isna().mean() > 0.5:
            notes.append("Could not read most dates, so dates were ignored.")
            mapping = {**mapping, "date": None}
        else:
            if dt.isna().sum():
                notes.append(f"Dropped {int(dt.isna().sum()):,} rows with unreadable dates.")
            d, dt = d[dt.notna()], dt[dt.notna()]
            d["_date"] = dt.dt.normalize()
    if not mapping.get("date"):
        d["_date"] = pd.Timestamp.today().normalize()
        notes.append("No date column: trends and emerging-issue alerts need dates, so they will not be meaningful.")

    if mapping.get("brand"):
        b = d[mapping["brand"]].astype(str).str.strip().replace({"": "Unknown", "nan": "Unknown"})
        if brand_first_word:
            b = b.str.split().str[0]
        top = b.value_counts().head(top_brands).index
        d["_brand"] = b.where(b.isin(top), "Other")
        if b.nunique() > top_brands:
            notes.append(f"{b.nunique():,} distinct brand/product values: kept the top {top_brands}, grouped the rest as 'Other'.")
    else:
        d["_brand"] = "All products"

    ids = d[mapping["review_id"]].astype(str) if mapping.get("review_id") else None
    if ids is None or ids.duplicated().any():
        ids = pd.Series([f"R{i:06d}" for i in range(len(d))], index=d.index)
    out = pd.DataFrame({"review_id": ids.values, "brand": d["_brand"].values, "date": d["_date"].values,
                        "rating": d["_rating"].values, "review_text": d["_text"].values})
    if out.empty:
        raise ValueError("No usable rows left after cleaning. Check the column mapping.")
    nonlatin = out.review_text.apply(lambda t: bool(_NONLATIN.search(t))).mean()
    if nonlatin > 0.10:
        notes.append(f"{100 * nonlatin:.0f}% of reviews contain non-Latin scripts (for example Hindi or Tamil). "
                     "Sentiment scoring supports English and some Hinglish only, so results for those reviews will be weak.")
    out = out.reset_index(drop=True)
    out.attrs["rating_estimated"] = estimated
    return out, notes
