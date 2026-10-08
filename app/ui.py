"""Shared look & feel: design tokens, glass CSS, animated background loader, HTML component helpers, charts."""
import hashlib, html, json, pathlib
import pandas as pd, plotly.express as px, plotly.graph_objects as go, streamlit as st

ASSETS = pathlib.Path(__file__).resolve().parent / "assets"

GREEN, AMBER, RED, BLUE = "#3FB68B", "#E3A62F", "#E5484D", "#4C8DF6"
BORDER, TEXT, MUTED = "rgba(255,255,255,.10)", "#E6EAF2", "#8A96AA"
SERIES = [BLUE, "#A78BFA", "#2DD4BF", "#94A3B8", "#7DD3FC", "#C4B5FD", "#5EEAD4", "#CBD5E1"]  # non-semantic
PLOT_CFG = {"displayModeBar": False}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&family=Sora:wght@500;600;700&display=swap');
:root{--bg:#070B14;--glass:rgba(15,23,42,.50);--glass2:rgba(255,255,255,.045);--edge:rgba(255,255,255,.09);--edge2:rgba(255,255,255,.17);
--text:#E6EAF2;--soft:#C3CBD9;--muted:#8A96AA;--green:#3FB68B;--amber:#E3A62F;--red:#E5484D;--blue:#4C8DF6;--blur:blur(14px) saturate(130%);}
.stApp :where(*:not([data-testid="stIconMaterial"]):not(.material-icons)){font-family:'DM Sans',system-ui,-apple-system,'Segoe UI',sans-serif;}
html,body{background:var(--bg)!important;}
.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"],[data-testid="stBottom"]{background:transparent!important;color:var(--text);}
#MainMenu,footer{visibility:hidden;}
.block-container{max-width:1560px;padding:1.6rem 2.25rem 4rem;}

/* animated background (created by assets/background.js) */
#rl-bg{position:fixed;inset:0;z-index:-1;overflow:hidden;pointer-events:none;background:var(--bg);
--mx:0;--my:0;--sp:0;--sx:50;--sy:40;--c1:rgb(37,99,235);--c2:rgb(124,58,237);--c3:rgb(8,145,178);perspective:1400px;}
#rl-bg .rl-stage{position:absolute;inset:-8%;transform-style:preserve-3d;will-change:transform;
transform:rotateX(calc(var(--my)*-3.2deg)) rotateY(calc(var(--mx)*4.2deg));}
#rl-bg .rl-orb{position:absolute;border-radius:50%;will-change:transform;}
#rl-bg .rl-o1{width:62vmax;height:62vmax;left:-14%;top:-22%;opacity:.36;background:radial-gradient(circle,var(--c1) 0%,transparent 64%);
transform:translate3d(calc(var(--mx)*-70px),calc(var(--my)*-46px + var(--sp)*-260px),60px);}
#rl-bg .rl-o2{width:54vmax;height:54vmax;right:-16%;top:6%;opacity:.30;background:radial-gradient(circle,var(--c2) 0%,transparent 64%);
transform:translate3d(calc(var(--mx)*54px),calc(var(--my)*38px + var(--sp)*-420px),-40px);}
#rl-bg .rl-o3{width:50vmax;height:50vmax;left:22%;bottom:-34%;opacity:.28;background:radial-gradient(circle,var(--c3) 0%,transparent 64%);
transform:translate3d(calc(var(--mx)*-34px),calc(var(--my)*-24px + var(--sp)*-560px),20px);}
#rl-bg .rl-grid{position:absolute;inset:-6%;
background-image:linear-gradient(rgba(255,255,255,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.04) 1px,transparent 1px);
background-size:68px 68px;-webkit-mask-image:radial-gradient(ellipse at 50% 28%,#000 8%,transparent 72%);mask-image:radial-gradient(ellipse at 50% 28%,#000 8%,transparent 72%);
transform:translate3d(calc(var(--mx)*-16px),calc(var(--my)*-12px + var(--sp)*-140px),30px);}
#rl-bg .rl-spot{position:absolute;inset:0;background:radial-gradient(520px circle at calc(var(--sx)*1%) calc(var(--sy)*1%),rgba(255,255,255,.055),transparent 62%);}
@media(prefers-reduced-motion:reduce){#rl-bg .rl-stage,#rl-bg .rl-orb,#rl-bg .rl-grid{transition:none;}}

/* glass surfaces */
header[data-testid="stHeader"]{background:rgba(7,11,20,.55);backdrop-filter:var(--blur);-webkit-backdrop-filter:var(--blur);border-bottom:1px solid var(--edge);}
section[data-testid="stSidebar"]{background:rgba(9,14,26,.55)!important;backdrop-filter:var(--blur);-webkit-backdrop-filter:var(--blur);border-right:1px solid var(--edge);}
section[data-testid="stSidebar"] > div,[data-testid="stSidebarContent"]{background:transparent!important;}
section[data-testid="stSidebar"] .block-container{padding:1.4rem 1.1rem;}
section[data-testid="stSidebar"] label p{font-size:13px;color:var(--soft);font-weight:500;}
.kpi,.fix,.alert,.dq,.rv,.stat,.step,.feat,.hero-card,.chip,div[data-testid="stExpander"],div[data-testid="stVerticalBlockBorderWrapper"]{
background:var(--glass);border:1px solid var(--edge);backdrop-filter:var(--blur);-webkit-backdrop-filter:var(--blur);border-radius:14px;}
div[data-testid="stExpander"] details{background:transparent;}
div[data-baseweb="select"] > div,div[data-baseweb="input"],div[data-baseweb="base-input"]{background:rgba(255,255,255,.04)!important;border-color:var(--edge)!important;}
.stDownloadButton button,.stButton button{border-radius:10px;border:1px solid var(--edge2);background:var(--glass2);color:var(--text);}
.stDownloadButton button:hover,.stButton button:hover{border-color:var(--blue);color:#fff;}

/* top navigator */
a[data-testid="stTopNavLink"]{border-radius:10px;color:var(--soft);font-weight:500;}
a[data-testid="stTopNavLink"]:hover{background:var(--glass2);color:#fff;}
a[data-testid="stTopNavLink"][aria-current="page"]{background:rgba(76,141,246,.16);color:#fff;}
a[data-testid="stPageLink-NavLink"]{border:1px solid var(--edge2);background:var(--glass2);border-radius:10px;padding:8px 14px;color:var(--text);}
a[data-testid="stPageLink-NavLink"]:hover{border-color:var(--blue);background:rgba(76,141,246,.12);}
.st-key-cta1 a[data-testid="stPageLink-NavLink"]{background:var(--blue);border-color:var(--blue);color:#fff;font-weight:600;}
.st-key-cta1 a[data-testid="stPageLink-NavLink"]:hover{background:#6AA2FA;}
.st-key-bgloader{position:absolute;height:0;overflow:hidden;margin:0;}

/* page header */
.hdr{display:flex;justify-content:space-between;align-items:flex-end;gap:16px;flex-wrap:wrap;margin-bottom:18px;}
.hdr-t{font-family:'Sora',sans-serif;font-size:24px;font-weight:600;letter-spacing:-.015em;line-height:1.2;}
.hdr-s{color:var(--muted);font-size:14px;margin-top:3px;}
.chips{display:flex;gap:8px;flex-wrap:wrap;}
.chip{color:var(--soft);font-size:12.5px;padding:4px 11px;border-radius:999px;}

/* KPI */
.kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-bottom:16px;}
@media(max-width:1100px){.kpis{grid-template-columns:repeat(2,minmax(0,1fr));}}
.kpi{padding:16px 18px;min-height:116px;}
.kpi-l{color:var(--muted);font-size:13px;font-weight:500;display:flex;align-items:center;gap:8px;}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block;flex:none;}
.kpi-v{font-family:'Sora',sans-serif;font-size:28px;font-weight:600;line-height:1.15;margin:8px 0 4px;font-variant-numeric:tabular-nums;}
.kpi-v small{font-family:'DM Sans',sans-serif;font-size:14px;color:var(--muted);font-weight:500;margin-left:4px;}
.kpi-s{color:var(--muted);font-size:12.5px;line-height:1.4;}

/* alert */
.alert{display:flex;gap:16px;align-items:center;border-left:4px solid var(--amber);background:rgba(227,166,47,.09);padding:12px 18px;margin-bottom:10px;}
.alert.red{border-left-color:var(--red);background:rgba(229,72,77,.09);}
.alert-b{flex:1;min-width:0;}
.alert-t{font-weight:600;font-size:14px;}
.alert-d{color:var(--soft);font-size:13px;margin-top:2px;}
.alert-x{text-align:right;white-space:nowrap;font-size:20px;font-weight:700;color:var(--amber);font-variant-numeric:tabular-nums;line-height:1.1;}
.alert.red .alert-x{color:var(--red);}
.alert-x small{display:block;font-size:12px;color:var(--muted);font-weight:500;margin-top:2px;}

/* headings */
.sec{display:flex;align-items:baseline;justify-content:space-between;gap:12px;flex-wrap:wrap;margin:28px 0 12px;}
.sec-t{font-family:'Sora',sans-serif;font-size:18px;font-weight:600;letter-spacing:-.01em;}
.sec-s{color:var(--muted);font-size:13px;}
.panel-t{font-size:15px;font-weight:600;}
.panel-s{color:var(--muted);font-size:12.5px;margin:2px 0 6px;}

/* top-5 fix cards */
.fix{margin-bottom:10px;overflow:hidden;}
.fix-main{display:grid;grid-template-columns:34px minmax(0,1fr) 200px;gap:16px;align-items:center;padding:16px 18px;}
@media(max-width:900px){.fix-main{grid-template-columns:34px minmax(0,1fr);}.score{grid-column:2;text-align:left!important;}}
.rank{width:28px;height:28px;border-radius:8px;background:var(--glass2);border:1px solid var(--edge);display:flex;align-items:center;justify-content:center;font-weight:600;font-size:13px;color:var(--soft);}
.fix-title{font-size:16px;font-weight:600;line-height:1.3;}
.fix-meta{display:flex;flex-wrap:wrap;align-items:center;gap:6px 14px;margin-top:9px;color:var(--muted);font-size:13px;}
.pill{padding:2px 9px;border-radius:6px;background:rgba(76,141,246,.14);color:#8DB4FA;font-size:12px;font-weight:500;}
.badge{padding:2px 9px;border-radius:6px;font-size:12px;font-weight:600;}
.badge.crit{background:rgba(229,72,77,.18);color:#FF8A8E;}
.badge.high{background:rgba(227,166,47,.18);color:#F2C060;}
.badge.med{background:rgba(76,141,246,.18);color:#8DB4FA;}
.trend{font-weight:600;font-size:13px;}
.trend.up{color:#FF8A8E;}.trend.down{color:#5FD3A8;}.trend.flat{color:var(--muted);}
.score{text-align:right;}
.score-n{font-family:'Sora',sans-serif;font-size:26px;font-weight:600;line-height:1;font-variant-numeric:tabular-nums;}
.score-n small{font-family:'DM Sans',sans-serif;font-size:13px;color:var(--muted);font-weight:500;margin-left:2px;}
.bar{height:6px;background:rgba(255,255,255,.08);border-radius:999px;margin:9px 0 5px;overflow:hidden;}
.bar i{display:block;height:100%;border-radius:999px;}
.score-l{font-size:12px;color:var(--muted);}
details.ev{border-top:1px solid var(--edge);}
details.ev summary{cursor:pointer;padding:10px 18px;font-size:13px;color:#8DB4FA;font-weight:500;list-style:none;}
details.ev summary::-webkit-details-marker{display:none;}
details.ev summary:before{content:"\\25B8";margin-right:8px;display:inline-block;transition:transform .15s;}
details.ev[open] summary:before{transform:rotate(90deg);}
details.ev summary:hover{background:rgba(76,141,246,.07);}
.ev-b{padding:2px 18px 16px 18px;}
.ev-h{font-size:12.5px;color:var(--muted);margin:8px 0 2px;font-weight:500;}
.quote{border-left:2px solid var(--edge2);padding:2px 0 2px 12px;margin:8px 0;color:var(--soft);font-size:13.5px;line-height:1.5;}
.next{margin-top:12px;padding:10px 12px;border-radius:8px;background:var(--glass2);font-size:13px;color:var(--soft);line-height:1.5;}
.next b{color:var(--text);font-weight:600;}

/* sidebar */
.dq{padding:14px;}
.dq-top{display:flex;justify-content:space-between;align-items:baseline;}
.dq-v{font-family:'Sora',sans-serif;font-size:22px;font-weight:600;font-variant-numeric:tabular-nums;}
.dq-l{font-size:12.5px;color:var(--muted);}
.dq-r{display:flex;justify-content:space-between;font-size:13px;padding:6px 0;border-top:1px solid var(--edge);color:var(--soft);}
.dq-r b{font-weight:600;color:var(--text);font-variant-numeric:tabular-nums;}
.side-h{font-size:13px;font-weight:600;color:var(--text);margin:18px 0 8px;}

/* search results / lists */
.rv{padding:12px 16px;margin-bottom:8px;}
.rv-h{display:flex;gap:10px;align-items:center;font-size:12.5px;color:var(--muted);margin-bottom:6px;}
.rv-h b{color:var(--text);font-weight:600;}
.rv-t{font-size:14px;line-height:1.55;color:var(--soft);}

/* home */
.hero-h{font-family:'Sora',sans-serif;font-size:clamp(34px,4vw,54px);line-height:1.08;font-weight:600;letter-spacing:-.025em;margin:56px 0 18px;}
.hero-p{font-size:17px;line-height:1.6;color:var(--soft);max-width:54ch;margin:0 0 26px;}
.hero-card{padding:18px 20px;margin-top:44px;}
.hc-h{display:flex;align-items:center;gap:8px;font-size:13px;color:var(--muted);font-weight:500;margin-bottom:12px;}
.hc-alert{display:flex;justify-content:space-between;gap:12px;font-size:13px;padding:9px 12px;border-radius:10px;margin-bottom:12px;background:rgba(227,166,47,.10);border:1px solid rgba(227,166,47,.30);color:#F2C060;}
.hc-alert b{font-weight:700;white-space:nowrap;}
.mini{display:grid;grid-template-columns:minmax(0,1fr) 44px;gap:4px 12px;padding:11px 0;border-top:1px solid var(--edge);}
.mini-t{font-size:14px;font-weight:600;line-height:1.3;}
.mini-n{font-family:'Sora',sans-serif;font-weight:600;font-size:15px;text-align:right;grid-row:1;grid-column:2;}
.mini-s{display:flex;gap:10px;align-items:center;font-size:12.5px;color:var(--muted);}
.mini .bar{grid-column:1 / span 2;margin:4px 0 0;}
.hc-f{font-size:12px;color:var(--muted);margin-top:6px;}
.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin:36px 0 8px;}
@media(max-width:1000px){.stats{grid-template-columns:repeat(2,minmax(0,1fr));}}
.stat{padding:18px 20px;}
.stat-v{font-family:'Sora',sans-serif;font-size:30px;font-weight:600;font-variant-numeric:tabular-nums;line-height:1.1;}
.stat-l{color:var(--muted);font-size:13px;margin-top:6px;}
.steps{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;}
@media(max-width:1100px){.steps{grid-template-columns:repeat(2,minmax(0,1fr));}}
.step{padding:18px 20px;min-height:150px;}
.step-n{width:26px;height:26px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:600;background:rgba(76,141,246,.16);color:#8DB4FA;margin-bottom:12px;}
.step-t{font-size:15px;font-weight:600;margin-bottom:6px;}
.step-d{font-size:13.5px;color:var(--muted);line-height:1.55;}
.feat{padding:18px 20px 14px;min-height:132px;margin-bottom:10px;}
.feat-t{font-size:15px;font-weight:600;margin-bottom:6px;}
.feat-d{font-size:13.5px;color:var(--muted);line-height:1.55;}
.gap{display:flex;justify-content:space-between;gap:12px;padding:10px 0;border-top:1px solid var(--edge);font-size:14px;color:var(--soft);}
.gap b{color:var(--text);font-weight:600;}
.gap span:last-child{color:var(--amber);font-weight:600;font-variant-numeric:tabular-nums;white-space:nowrap;}

/* tabs / misc */
button[data-baseweb="tab"]{font-size:14px;font-weight:500;color:var(--muted);}
button[data-baseweb="tab"][aria-selected="true"]{color:var(--text);}
[data-baseweb="tab-highlight"]{background:var(--blue)!important;}
[data-baseweb="tab-border"]{background:var(--edge)!important;}
</style>
"""


def inject():
    """Inject CSS and (once per browser session) the animated background script."""
    st.markdown(CSS, unsafe_allow_html=True)
    js = (ASSETS / "background.js").read_text(encoding="utf-8")
    js = js.replace("__RL_VERSION__", hashlib.sha1(js.encode()).hexdigest()[:10])
    with st.container(key="bgloader"):
        try:
            st.html(f"<script>{js}</script>", unsafe_allow_javascript=True)
        except TypeError:  # older Streamlit: run it from a component iframe instead, in the parent page
            import streamlit.components.v1 as components
            components.html("<script>(function(){var p=window.parent,s=p.document.createElement('script');"
                            f"s.textContent={json.dumps(js)};p.document.head.appendChild(s);}})();</script>", height=0)


# --------------------------------------------------------------------------- html helpers
def esc(s):
    """HTML-escape and neutralise '$' (Streamlit would otherwise try to render it as maths)."""
    return html.escape(str(s)).replace("$", "&#36;")


def section(title, sub=""):
    st.markdown(f'<div class="sec"><div class="sec-t">{esc(title)}</div><div class="sec-s">{esc(sub)}</div></div>',
                unsafe_allow_html=True)


def page_header(title, sub, chips=()):
    c = "".join(f'<span class="chip">{esc(x)}</span>' for x in chips)
    st.markdown(f'<div class="hdr"><div><div class="hdr-t">{esc(title)}</div><div class="hdr-s">{esc(sub)}</div></div>'
                f'<div class="chips">{c}</div></div>', unsafe_allow_html=True)


def kpi(label, value, sub, color, unit=""):
    u = f"<small>{esc(unit)}</small>" if unit else ""
    return (f'<div class="kpi"><div class="kpi-l"><span class="dot" style="background:{color}"></span>{esc(label)}</div>'
            f'<div class="kpi-v">{esc(value)}{u}</div><div class="kpi-s">{esc(sub)}</div></div>')


def severity(priority):
    if priority >= 70: return "Critical", "crit", RED
    if priority >= 40: return "High", "high", AMBER
    return "Medium", "med", BLUE


def trend_tag(t):
    if t > .15: return '<span class="trend up">&#9650; Rising</span>'
    if t < -.15: return '<span class="trend down">&#9660; Falling</span>'
    return '<span class="trend flat">&#9679; Stable</span>'


def fix_card(i, r):
    label, cls, color = severity(r.priority)
    quotes = "".join(f'<div class="quote">&ldquo;{esc(q)}&rdquo;</div>' for q in r.quotes)
    return (
        '<div class="fix"><div class="fix-main">'
        f'<div class="rank">{i}</div>'
        f'<div><div class="fix-title">{esc(r.issue)}</div>'
        f'<div class="fix-meta"><span class="pill">{esc(str(r.aspect).capitalize())}</span>'
        f'<span class="badge {cls}">{label}</span>{trend_tag(r.trend)}'
        f'<span>{r.pct_reviews}% of reviews</span>'
        f'<span>{r.recent} mentions in last 28 days (prior {r.prior})</span>'
        f'<span>Owner: {esc(r.owner)}</span></div></div>'
        f'<div class="score"><div class="score-n">{r.priority}<small>/100</small></div>'
        f'<div class="bar"><i style="width:{r.priority}%;background:{color}"></i></div>'
        '<div class="score-l">Priority score</div></div></div>'
        '<details class="ev"><summary>Evidence and next step</summary><div class="ev-b">'
        f'<div class="ev-h">What customers say</div>{quotes}'
        f'<div class="next"><b>Next step.</b> {esc(r.action)}</div></div></details></div>')


def alert_card(r):
    red = r.spike >= 3
    return (f'<div class="alert{" red" if red else ""}"><div class="alert-b">'
            f'<div class="alert-t">Emerging issue: {esc(r.brand)}, {esc(r.aspect)}</div>'
            f'<div class="alert-d">{r.recent} negative mentions in the last 14 days against about {r.expected} expected. '
            'Review before it reaches the top of the fix list.</div></div>'
            f'<div class="alert-x">{r.spike}&times;<small>vs. baseline</small></div></div>')


# --------------------------------------------------------------------------- charts
def style_fig(fig, height=340, legend=True):
    fig.update_layout(
        height=height, margin=dict(l=4, r=4, t=4, b=4), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#B7C0CF", size=12), showlegend=legend,
        legend=dict(orientation="h", y=1.1, x=0, title=None, bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor="#17223A", bordercolor="rgba(255,255,255,.15)", font_color=TEXT))
    fig.update_xaxes(gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER)
    fig.update_yaxes(gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER)
    return fig


def topic_sentiment_fig(a, summ):
    cnt = a.groupby(["aspect", "sentiment"]).size().unstack(fill_value=0).reindex(columns=["neg", "neu", "pos"], fill_value=0)
    share = cnt.div(cnt.sum(axis=1), axis=0) * 100
    order = list(summ.index)[::-1]  # plotly draws the first category at the bottom
    names = [x.capitalize() for x in order]
    fig = go.Figure()
    for key, label, color in [("neg", "Negative", RED), ("neu", "Neutral", "#4A5873"), ("pos", "Positive", GREEN)]:
        vals = share.loc[order, key]
        fig.add_bar(y=names, x=vals, name=label, orientation="h", marker_color=color,
                    text=[f"{v:.0f}%" if v >= 9 else "" for v in vals], textposition="inside", insidetextanchor="middle",
                    textfont=dict(color="#0B1220" if key != "neu" else "#E6EAF2", size=11),
                    hovertemplate="%{y}: %{x:.1f}% " + label.lower() + "<extra></extra>")
    for nm, k in zip(names, order):
        net = summ.loc[k, "net"]
        fig.add_annotation(x=1.0, xref="paper", y=nm, text=f"<b>{net:+.2f}</b>", showarrow=False, xanchor="left", xshift=8,
                           font=dict(color=GREEN if net >= 0.4 else AMBER if net >= 0 else RED, size=12))
    fig.update_layout(barmode="stack", bargap=0.35)
    style_fig(fig, 360); fig.update_layout(margin=dict(l=4, r=48, t=4, b=4))
    fig.update_xaxes(range=[0, 100], showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False)
    return fig


def trend_fig(wsel):
    tf = px.line(wsel, x="week", y="net", color="Topic", markers=True, color_discrete_sequence=SERIES,
                 labels={"net": "Net sentiment", "week": ""})
    tf.update_traces(line=dict(width=2.2), marker=dict(size=5), hovertemplate="%{fullData.name}: %{y:+.2f}<extra></extra>")
    tf.add_hline(y=0, line_dash="dash", line_color=MUTED, line_width=1)
    style_fig(tf, 306); tf.update_layout(hovermode="x unified")
    tf.update_yaxes(range=[-1.05, 1.05], tickformat="+.1f", title=None)
    tf.update_xaxes(tickformat="%d %b", title=None, showgrid=False)
    return tf
