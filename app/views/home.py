import streamlit as st
import ui, state

reviews, asp = st.session_state["base"]
pages = st.session_state["pages"]
good = reviews[~reviews.flagged]
issues, alerts = state.ranked(asp, reviews), state.spikes(asp)

# ---- hero ----------------------------------------------------------------------------------
left, right = st.columns([11, 9], gap="large")
with left:
    st.markdown('<div class="hero-h">Hear every customer.<br>Fix what matters first.</div>'
                '<p class="hero-p">ReviewLens turns thousands of product reviews into a ranked, evidence-backed '
                'fix list, so brand and product teams know what to act on this week.</p>', unsafe_allow_html=True)
    b1, b2, _ = st.columns([3, 3, 4])
    with b1, st.container(key="cta1"):
        st.page_link(pages["overview"], label="Open dashboard")
    with b2:
        st.page_link(pages["ask"], label="Ask the reviews")

with right:
    rows = ""
    for r in issues.head(3).itertuples():
        label, cls, color = ui.severity(r.priority)
        rows += (f'<div class="mini"><div class="mini-t">{ui.esc(r.issue)}</div><div class="mini-n">{r.priority}</div>'
                 f'<div class="mini-s"><span class="badge {cls}">{label}</span><span>{ui.esc(str(r.aspect).capitalize())}</span>'
                 f'{ui.trend_tag(r.trend)}</div><div class="bar"><i style="width:{r.priority}%;background:{color}"></i></div></div>')
    alert = ""
    if len(alerts):
        a0 = alerts.iloc[0]
        alert = (f'<div class="hc-alert"><span>Emerging: {ui.esc(a0.brand)}, {ui.esc(a0.aspect)}</span>'
                 f'<b>{a0.spike}&times; baseline</b></div>')
    st.markdown('<div class="hero-card"><div class="hc-h"><span class="dot" style="background:#3FB68B"></span>'
                f'Live from your data</div>{alert}{rows}'
                '<div class="hc-f">Top issues across all brands and dates</div></div>', unsafe_allow_html=True)

# ---- numbers -------------------------------------------------------------------------------
stats = [(f"{len(good):,}", "Reviews analysed"), (str(reviews.brand.nunique()), "Brands compared"),
         (str(asp.aspect.nunique()), "Topics tracked"), (str(len(issues)), "Issues ranked by priority")]
st.markdown('<div class="stats">' + "".join(
    f'<div class="stat"><div class="stat-v">{v}</div><div class="stat-l">{l}</div></div>' for v, l in stats) + "</div>",
    unsafe_allow_html=True)

# ---- how it works --------------------------------------------------------------------------
ui.section("How it works", "From raw reviews to a decision in four steps")
steps = [("Clean", "Duplicates, spam-like text and too-short reviews are removed. Star ratings that contradict the text are flagged."),
         ("Find topics", "Each review is split into clauses and matched to price, quality, delivery, service, battery, sound, comfort and connectivity."),
         ("Score sentiment", "Every topic mention gets its own sentiment, so a review that praises sound but slams battery counts both."),
         ("Rank and recommend", "Negative comments are grouped into concrete issues, ranked by impact, and paired with an owner and a next step.")]
st.markdown('<div class="steps">' + "".join(
    f'<div class="step"><div class="step-n">{i}</div><div class="step-t">{t}</div><div class="step-d">{d}</div></div>'
    for i, (t, d) in enumerate(steps, 1)) + "</div>", unsafe_allow_html=True)

# ---- explore -------------------------------------------------------------------------------
ui.section("Explore", "Jump straight to the part you need")
feats = [("overview", "Overview", "KPIs, emerging-issue alerts, the Top 5 things to fix and sentiment by topic."),
         ("competitors", "Competitors", "See how brands compare on every topic and where the biggest gaps are."),
         ("ask", "Ask the reviews", "Search what customers actually wrote, in their own words."),
         ("reports", "Reports", "A one-page PM brief to download, plus the full ranked issue table.")]
cols = st.columns(4, gap="medium")
for col, (key, title, desc) in zip(cols, feats):
    with col:
        st.markdown(f'<div class="feat"><div class="feat-t">{title}</div><div class="feat-d">{desc}</div></div>', unsafe_allow_html=True)
        st.page_link(pages[key], label=f"Open {title.lower()}")
