import pandas as pd, streamlit as st
import ui, state
from src.pipeline import weekly_net

ctx = state.require()
good, rv, a, issues, alerts, summ = (ctx[k] for k in ("good", "rv", "a", "issues", "alerts", "summ"))

ui.page_header("Overview", "What customers are telling your brand, and what to fix first.", state.scope_chips(ctx))

avg = good.rating.mean()
weak, weak_net, weak_neg = summ.index[0], summ.net.iloc[0], int(summ.neg.iloc[0])
mism = int(good.rating_mismatch.sum()); mism_pct = 100 * mism / len(good)
st.markdown('<div class="kpis">' + "".join([
    ui.kpi("Reviews", f"{len(good):,}", f"{int(rv.flagged.sum()):,} excluded as duplicate or spam-like", ui.BLUE),
    ui.kpi("Average rating", f"{avg:.2f}", "Mean star rating of usable reviews",
           ui.GREEN if avg >= 4 else ui.AMBER if avg >= 3.5 else ui.RED, unit="/ 5"),
    ui.kpi("Weakest aspect", str(weak).capitalize(), f"Net sentiment {weak_net:+.2f}, {weak_neg:,} negative mentions",
           ui.RED if weak_net < 0 else ui.AMBER if weak_net < 0.4 else ui.GREEN),
    ui.kpi("Star/text mismatches", f"{mism:,}", f"{mism_pct:.1f}% of reviews: high stars with negative text, or the reverse",
           ui.AMBER if mism_pct > 5 else ui.BLUE),
]) + "</div>", unsafe_allow_html=True)

if len(alerts):
    st.markdown("".join(ui.alert_card(r) for r in alerts.itertuples()), unsafe_allow_html=True)

ui.section("Top 5 things to fix", "Ranked by customers affected, severity, recent growth and rating impact")
if issues.empty:
    st.info("Not enough negative feedback in this selection to rank issues. Widen the date range or brand filter.")
else:
    st.markdown("".join(ui.fix_card(i, r) for i, r in enumerate(issues.head(5).itertuples(), 1)), unsafe_allow_html=True)
with st.expander("How is priority calculated?"):
    st.markdown("`priority = share of reviews affected x (0.5 + severity) x (1 + recent growth) x (1 + rating drag / 2)`, "
                "scaled so the top issue is 100. Issues are clusters of negative review clauses within an aspect. "
                "Badges: **Critical** 70 and above, **High** 40 to 69, **Medium** below 40.")

ui.section("Customer sentiment", "Net sentiment runs from -1 (all negative) to +1 (all positive)")
left, right = st.columns([5, 6], gap="medium")
with left, st.container(border=True):
    st.markdown('<div class="panel-t">Sentiment by topic</div>'
                '<div class="panel-s">Share of mentions, weakest topic first. Net score on the right.</div>', unsafe_allow_html=True)
    st.plotly_chart(ui.topic_sentiment_fig(a, summ), width="stretch", config=ui.PLOT_CFG)
with right, st.container(border=True):
    st.markdown('<div class="panel-t">Sentiment trend</div>'
                '<div class="panel-s">Weekly net sentiment. Above the dashed line is net positive.</div>', unsafe_allow_html=True)
    w = weekly_net(a)
    sel = st.multiselect("Topics", sorted(w.aspect.unique()), default=list(summ.index[:3]),
                         format_func=lambda x: x.capitalize(), label_visibility="collapsed")
    wsel = w[w.aspect.isin(sel)].assign(Topic=lambda d: d.aspect.str.capitalize())
    if wsel.empty:
        st.info("Select at least one topic to see its trend.")
    else:
        st.plotly_chart(ui.trend_fig(wsel), width="stretch", config=ui.PLOT_CFG)
