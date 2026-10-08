"""Data loading, caching, shared filters and sidebar. Analysis logic lives in src/pipeline.py (unchanged)."""
import pathlib
import pandas as pd, streamlit as st
from src.pipeline import clean_reviews, extract_aspects, aspect_summary, find_issues, emerging
import ui

ROOT = pathlib.Path(__file__).resolve().parents[1]


@st.cache_data(show_spinner=False)
def _sample():
    return pd.read_csv(ROOT / "data/reviews.csv")


@st.cache_data(show_spinner="Analysing reviews...")
def analyse(raw: pd.DataFrame):
    rev = clean_reviews(raw); return rev, extract_aspects(rev)


@st.cache_data(show_spinner=False)
def ranked(a, rv):
    return find_issues(a, rv)


@st.cache_data(show_spinner=False)
def spikes(a):
    return emerging(a)


def base():
    """Whole dataset (uploaded file if present, else sample), analysed."""
    raw = st.session_state.get("raw_upload")
    return analyse(raw if raw is not None else _sample())


def sidebar(reviews):
    """Upload + filters + data-quality card. Filter values persist across pages in session_state."""
    with st.sidebar:
        st.markdown('<div class="hdr-t" style="font-size:18px">ReviewLens</div>'
                    '<div class="hdr-s" style="font-size:13px">Customer voice insights</div>', unsafe_allow_html=True)
        st.markdown('<div class="side-h">Data</div>', unsafe_allow_html=True)
        up = st.file_uploader("Upload reviews CSV", type="csv", help="Columns: review_id, brand, date, rating, review_text")
        if up is not None and st.session_state.get("raw_name") != up.name:
            st.session_state["raw_upload"], st.session_state["raw_name"] = pd.read_csv(up), up.name
            st.rerun()
        if st.session_state.get("raw_upload") is not None:
            st.caption(f"Using uploaded file: {st.session_state['raw_name']}")
            if st.button("Switch back to sample data", width="stretch"):
                for k in ("raw_upload", "raw_name", "f_brand", "f_dr"): st.session_state.pop(k, None)
                st.rerun()

        st.markdown('<div class="side-h">Filters</div>', unsafe_allow_html=True)
        opts = ["All brands"] + sorted(reviews.brand.unique())
        cur = st.session_state.get("f_brand", "All brands")
        brand = st.selectbox("Brand", opts, index=opts.index(cur) if cur in opts else 0)
        lo, hi = reviews.date.min().date(), reviews.date.max().date()
        dr = st.date_input("Date range", st.session_state.get("f_dr", (lo, hi)), min_value=lo, max_value=hi)
        st.session_state["f_brand"] = brand
        if len(dr) == 2: st.session_state["f_dr"] = tuple(dr)

        total, flagged = len(reviews), int(reviews.flagged.sum())
        pct = 100 * (total - flagged) / max(total, 1)
        qc = ui.GREEN if pct >= 95 else ui.AMBER if pct >= 85 else ui.RED
        st.markdown('<div class="side-h">Data quality</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="dq"><div class="dq-top">'
            f'<div class="dq-v">{pct:.1f}%</div><div class="dq-l">usable reviews</div></div>'
            f'<div class="bar"><i style="width:{pct:.1f}%;background:{qc}"></i></div>'
            f'<div class="dq-r"><span>Loaded</span><b>{total:,}</b></div>'
            f'<div class="dq-r"><span>Excluded (duplicate / spam-like)</span><b>{flagged:,}</b></div>'
            f'<div class="dq-r"><span>&nbsp;&nbsp;Duplicates</span><b>{int(reviews.is_duplicate.sum()):,}</b></div>'
            f'<div class="dq-r"><span>&nbsp;&nbsp;Too short</span><b>{int(reviews.is_too_short.sum()):,}</b></div>'
            f'<div class="dq-r"><span>&nbsp;&nbsp;Repetitive</span><b>{int(reviews.is_repetitive.sum()):,}</b></div>'
            f'<div class="dq-r"><span>Star/text mismatches</span><b>{int(reviews.rating_mismatch.sum()):,}</b></div></div>',
            unsafe_allow_html=True)
        st.caption("Exclusion reasons can overlap. Excluded reviews are left out of every chart and score.")
    return brand, (tuple(dr) if len(dr) == 2 else (lo, hi)), (lo, hi)


def build_context(reviews, asp, brand, dr):
    """Same filtering logic as the original dashboard."""
    rv, a = reviews, asp
    if brand != "All brands": rv, a = rv[rv.brand == brand], a[a.brand == brand]
    d0, d1 = map(pd.Timestamp, dr)
    rv, a = rv[rv.date.between(d0, d1)], a[a.date.between(d0, d1)]
    good = rv[~rv.flagged]
    ctx = dict(reviews=reviews, asp=asp, rv=rv, a=a, good=good, brand=brand, dr=dr, empty=good.empty or a.empty)
    if not ctx["empty"]:
        ctx["issues"] = ranked(a, rv)
        ctx["alerts"] = spikes(asp if brand == "All brands" else asp[asp.brand == brand])
        ctx["summ"] = aspect_summary(a)
    return ctx


def require():
    """Return the filtered context for data pages, or stop with a friendly message."""
    ctx = st.session_state.get("ctx")
    if ctx is None or ctx["empty"]:
        st.warning("No reviews match these filters. Widen the date range or choose All brands.")
        st.stop()
    return ctx


def scope_chips(ctx):
    f, t = ctx["dr"]
    return [ctx["brand"], f"{pd.Timestamp(f):%d %b %Y} to {pd.Timestamp(t):%d %b %Y}", f"{len(ctx['good']):,} reviews"]
