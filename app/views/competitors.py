import plotly.express as px, streamlit as st
import ui, state

ctx = state.require()
asp = ctx["asp"]
ui.page_header("Competitors", "How each brand compares on every topic, across all dates.", state.scope_chips(ctx)[2:])

h = asp.groupby(["brand", "aspect"]).apply(
    lambda g: (g.sentiment.eq("pos").sum() - g.sentiment.eq("neg").sum()) / len(g), include_groups=False).unstack()
h.columns = [c.capitalize() for c in h.columns]

left, right = st.columns([3, 2], gap="medium")
with left, st.container(border=True):
    st.markdown('<div class="panel-t">Brand comparison</div>'
                '<div class="panel-s">Net sentiment by brand and topic. Green is better, red is worse.</div>', unsafe_allow_html=True)
    hf = px.imshow(h, text_auto=".2f", aspect="auto", zmin=-1, zmax=1,
                   color_continuous_scale=[[0, ui.RED], [0.5, "#1B2740"], [1, ui.GREEN]])
    ui.style_fig(hf, 150 + 70 * len(h), legend=False)
    hf.update_layout(coloraxis_colorbar=dict(title="Net", thickness=10, len=0.8, outlinewidth=0, tickfont=dict(size=11)))
    hf.update_xaxes(side="top", showgrid=False, title=None); hf.update_yaxes(showgrid=False, title=None)
    st.plotly_chart(hf, width="stretch", config=ui.PLOT_CFG)

with right, st.container(border=True):
    st.markdown('<div class="panel-t">Biggest gaps between brands</div>'
                '<div class="panel-s">Topics where the best and worst brand are furthest apart.</div>', unsafe_allow_html=True)
    if len(h) < 2:
        st.info("Add a second brand to compare.")
    else:
        gaps = (h.max() - h.min()).sort_values(ascending=False).head(5)
        rows = "".join(f'<div class="gap"><span><b>{ui.esc(t)}</b>: {ui.esc(h[t].idxmin())} trails {ui.esc(h[t].idxmax())}</span>'
                       f'<span>{g:.2f} gap</span></div>' for t, g in gaps.items())
        st.markdown(rows, unsafe_allow_html=True)
