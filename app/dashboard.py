import sys, pathlib, html, inspect
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import pandas as pd, plotly.express as px, plotly.graph_objects as go, streamlit as st
import streamlit.components.v1 as components
from src.pipeline import (clean_reviews, extract_aspects, aspect_summary, find_issues, emerging, weekly_net)
from src.search import build_index, search
from src.brief import make_brief

st.set_page_config(page_title="ReviewLens", page_icon=None, layout="wide", initial_sidebar_state="expanded")

# ----------------------------------------------------------------------------------------------
# Design tokens. Glass surfaces over a living background. Four semantic colours only:
# green = positive, amber = warning/emerging, red = critical, blue = informational.
# The background hue drifts with scroll (see SCRIPT); panels stay neutral so data colours keep meaning.
# ----------------------------------------------------------------------------------------------
GREEN, AMBER, RED, BLUE = "#3FB68B", "#E3A62F", "#E5484D", "#4C8DF6"
LINE, TEXT, MUTED = "rgba(255,255,255,.09)", "#E8ECF4", "#94A0B5"
SERIES = [BLUE, "#A78BFA", "#2DD4BF", "#94A3B8", "#7DD3FC", "#C4B5FD", "#5EEAD4", "#CBD5E1"]  # non-semantic

NAV = [("home", "Home"), ("overview", "Overview"), ("fixes", "Top fixes"), ("sentiment", "Sentiment"),
       ("compare", "Compare"), ("reviews", "Reviews"), ("brief", "Brief")]

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&display=swap');
:root{--bg:#070B14;--glass:rgba(16,24,42,.55);--glass2:rgba(24,34,58,.62);--line:rgba(255,255,255,.09);--line2:rgba(255,255,255,.17);
--text:#E8ECF4;--soft:#C3CBD9;--muted:#94A0B5;--green:#3FB68B;--amber:#E3A62F;--red:#E5484D;--blue:#4C8DF6;
--mx:0;--my:0;--p:0;--h1:218;--h2:262;--h3:196;}
html,body{background:var(--bg)!important;}
.stApp, .stApp *:not([data-testid="stIconMaterial"]):not(.material-icons){font-family:'DM Sans',system-ui,-apple-system,'Segoe UI',sans-serif;}
.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"],header[data-testid="stHeader"]{background:transparent!important;color:var(--text);}
[data-testid="stMain"]{scroll-behavior:smooth;}
/* Streamlit's transparent header would swallow clicks meant for the navigator: let clicks pass through it */
header[data-testid="stHeader"]{pointer-events:none;}
header[data-testid="stHeader"] *{pointer-events:none;}
header[data-testid="stHeader"] button, header[data-testid="stHeader"] a, header[data-testid="stHeader"] [role="button"]{pointer-events:auto;}
#MainMenu, footer, [data-testid="stAppDeployButton"], [data-testid="stDeployButton"], .stDeployButton{display:none!important;}
.block-container{max-width:1500px;padding:5.2rem 2.25rem 4rem;}

/* ---------- living background (fixed, behind everything) ---------- */
.rl-bg{position:fixed;inset:0;z-index:0;overflow:hidden;pointer-events:none;
background:radial-gradient(1100px 620px at 50% -8%,hsl(var(--h1) 55% 13%),transparent 72%),var(--bg);}
.rl-grid{position:absolute;inset:-70px;background-image:linear-gradient(rgba(255,255,255,.04) 1px,transparent 1px),
linear-gradient(90deg,rgba(255,255,255,.04) 1px,transparent 1px);background-size:58px 58px;
-webkit-mask-image:radial-gradient(ellipse 80% 70% at 50% 35%,#000 15%,transparent 75%);mask-image:radial-gradient(ellipse 80% 70% at 50% 35%,#000 15%,transparent 75%);
transform:translate3d(calc(var(--mx)*-16px),calc(var(--my)*-12px + var(--p)*-140px),0);will-change:transform;}
.rl-orb{position:absolute;border-radius:50%;will-change:transform;}
.o1{width:60vmax;height:60vmax;left:-14vmax;top:-22vmax;background:radial-gradient(circle,hsl(var(--h1) 85% 58%/.44),transparent 62%);
transform:translate3d(calc(var(--mx)*-46px),calc(var(--my)*-34px + var(--p)*-26vh),0);}
.o2{width:52vmax;height:52vmax;right:-16vmax;top:12vh;background:radial-gradient(circle,hsl(var(--h2) 80% 60%/.36),transparent 62%);
transform:translate3d(calc(var(--mx)*70px),calc(var(--my)*46px + var(--p)*36vh),0);}
.o3{width:46vmax;height:46vmax;left:26vw;bottom:-26vmax;background:radial-gradient(circle,hsl(var(--h3) 80% 52%/.32),transparent 62%);
transform:translate3d(calc(var(--mx)*-30px),calc(var(--my)*-60px + var(--p)*-20vh),0);}
@media (prefers-reduced-motion:reduce){.rl-orb,.rl-grid,.tilt{transform:none!important;}[data-testid="stMain"]{scroll-behavior:auto;}}

/* ---------- floating navigator ---------- */
.rl-nav{position:fixed;top:14px;left:50%;transform:translateX(-50%);z-index:60;display:flex;align-items:center;gap:6px;
padding:6px 8px 6px 14px;border-radius:999px;background:rgba(12,18,32,.62);border:1px solid var(--line2);
backdrop-filter:blur(18px) saturate(140%);-webkit-backdrop-filter:blur(18px) saturate(140%);box-shadow:0 8px 30px rgba(0,0,0,.35);max-width:calc(100vw - 120px);}
.rl-nav .brand{display:flex;align-items:center;gap:8px;font-weight:700;font-size:14px;color:var(--text)!important;text-decoration:none;margin-right:8px;white-space:nowrap;}
.rl-nav .mark{width:10px;height:10px;border-radius:3px;background:hsl(var(--h1) 85% 62%);box-shadow:0 0 0 3px hsl(var(--h1) 85% 62%/.18);}
.rl-nav .links{display:flex;gap:2px;overflow-x:auto;scrollbar-width:none;}
.rl-nav .links::-webkit-scrollbar{display:none;}
.rl-nav a.lk{color:var(--muted)!important;text-decoration:none;font-size:13px;font-weight:500;padding:6px 12px;border-radius:999px;white-space:nowrap;transition:background .15s,color .15s;}
.rl-nav a.lk:hover{color:var(--text)!important;background:rgba(255,255,255,.06);}
.rl-nav a.lk.active{color:var(--text)!important;background:rgba(255,255,255,.12);}
@media(max-width:820px){.rl-nav .brand span:last-child{display:none;}}

/* ---------- hero ---------- */
.anchor{scroll-margin-top:84px;height:0;}
.hero{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:48px;align-items:center;min-height:calc(100vh - 150px);padding:8px 0 24px;}
@media(max-width:1000px){.hero{grid-template-columns:1fr;min-height:0;gap:28px;padding-top:24px;}}
.tag{display:inline-flex;align-items:center;gap:8px;padding:5px 12px;border-radius:999px;border:1px solid var(--line2);background:rgba(255,255,255,.05);
font-size:12.5px;color:var(--soft);margin-bottom:20px;}
.tag .dot{width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 0 3px rgba(63,182,139,.2);}
.hero h1{font-size:clamp(32px,3.5vw,48px);line-height:1.08;letter-spacing:-.025em;font-weight:700;margin:0 0 16px;padding:0;color:var(--text);max-width:16ch;}
.hero p.lead{font-size:16.5px;line-height:1.6;color:var(--soft);max-width:52ch;margin:0 0 28px;}
.cta{display:flex;gap:12px;flex-wrap:wrap;}
a.btn{display:inline-flex;align-items:center;padding:11px 20px;border-radius:10px;font-size:14px;font-weight:600;text-decoration:none;color:var(--text)!important;
border:1px solid var(--line2);background:rgba(255,255,255,.06);transition:background .15s,border-color .15s;}
a.btn:hover{background:rgba(255,255,255,.12);}
a.btn.primary{background:var(--blue);border-color:transparent;color:#fff!important;}
a.btn.primary:hover{background:#6AA3FA;}
.hero-r{perspective:1000px;}
.tilt{background:var(--glass2);border:1px solid var(--line2);border-radius:18px;padding:22px;
backdrop-filter:blur(20px) saturate(140%);-webkit-backdrop-filter:blur(20px) saturate(140%);
box-shadow:0 30px 70px rgba(0,0,0,.45),inset 0 1px 0 rgba(255,255,255,.08);
transform:rotateY(calc(var(--mx)*9deg)) rotateX(calc(var(--my)*-7deg));transform-style:preserve-3d;will-change:transform;}
.tilt-h{display:flex;justify-content:space-between;align-items:center;font-size:13px;color:var(--muted);margin-bottom:14px;}
.tilt-t{font-size:20px;font-weight:600;line-height:1.3;margin-bottom:14px;transform:translateZ(24px);}
.tilt-row{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;margin-top:6px;}
.tilt-n{font-size:44px;font-weight:700;line-height:1;font-variant-numeric:tabular-nums;transform:translateZ(36px);}
.tilt-n small{font-size:15px;color:var(--muted);font-weight:500;margin-left:3px;}
.tilt-f{margin-top:18px;padding-top:14px;border-top:1px solid var(--line);display:flex;gap:18px;flex-wrap:wrap;font-size:13px;color:var(--muted);}
.tilt-f b{color:var(--text);font-weight:600;}

/* ---------- sections, KPI, alert ---------- */
.sec{display:flex;align-items:flex-end;justify-content:space-between;gap:12px;flex-wrap:wrap;margin:44px 0 14px;}
.sec-t{font-size:22px;font-weight:700;letter-spacing:-.01em;}
.sec-s{color:var(--muted);font-size:13.5px;margin-top:3px;}
.chips{display:flex;gap:8px;flex-wrap:wrap;}
.chip{border:1px solid var(--line);background:rgba(255,255,255,.05);color:var(--soft);font-size:12.5px;padding:4px 11px;border-radius:999px;}
.panel-t{font-size:15px;font-weight:600;}
.panel-s{color:var(--muted);font-size:12.5px;margin:2px 0 6px;}
.kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-bottom:14px;}
@media(max-width:1100px){.kpis{grid-template-columns:repeat(2,minmax(0,1fr));}}
.kpi{background:var(--glass);border:1px solid var(--line);border-radius:14px;padding:16px 18px;min-height:116px;
backdrop-filter:blur(14px) saturate(130%);-webkit-backdrop-filter:blur(14px) saturate(130%);box-shadow:inset 0 1px 0 rgba(255,255,255,.05);}
.kpi-l{color:var(--muted);font-size:13px;font-weight:500;display:flex;align-items:center;gap:8px;}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block;flex:none;}
.kpi-v{font-size:28px;font-weight:700;line-height:1.15;margin:8px 0 4px;font-variant-numeric:tabular-nums;}
.kpi-v small{font-size:14px;color:var(--muted);font-weight:500;margin-left:4px;}
.kpi-s{color:var(--muted);font-size:12.5px;line-height:1.4;}
.alert{display:flex;gap:16px;align-items:center;border:1px solid rgba(227,166,47,.38);border-left:4px solid var(--amber);
background:rgba(227,166,47,.09);border-radius:14px;padding:12px 18px;margin-bottom:10px;backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);}
.alert.red{border-color:rgba(229,72,77,.42);border-left-color:var(--red);background:rgba(229,72,77,.09);}
.alert-b{flex:1;min-width:0;}.alert-t{font-weight:600;font-size:14px;}.alert-d{color:var(--soft);font-size:13px;margin-top:2px;}
.alert-x{text-align:right;white-space:nowrap;font-size:20px;font-weight:700;color:var(--amber);font-variant-numeric:tabular-nums;line-height:1.1;}
.alert.red .alert-x{color:var(--red);}
.alert-x small{display:block;font-size:12px;color:var(--muted);font-weight:500;margin-top:2px;}

/* ---------- top-5 fix cards ---------- */
.fix{background:var(--glass);border:1px solid var(--line);border-radius:14px;margin-bottom:10px;overflow:hidden;
backdrop-filter:blur(14px) saturate(130%);-webkit-backdrop-filter:blur(14px) saturate(130%);box-shadow:inset 0 1px 0 rgba(255,255,255,.05);transition:border-color .15s;}
.fix:hover{border-color:var(--line2);}
.fix-main{display:grid;grid-template-columns:34px minmax(0,1fr) 200px;gap:16px;align-items:center;padding:16px 18px;}
@media(max-width:900px){.fix-main{grid-template-columns:34px minmax(0,1fr);}.score{grid-column:2;text-align:left!important;}}
.rank{width:28px;height:28px;border-radius:8px;background:rgba(255,255,255,.06);border:1px solid var(--line);display:flex;align-items:center;justify-content:center;font-weight:600;font-size:13px;color:var(--soft);}
.fix-title{font-size:16px;font-weight:600;line-height:1.3;}
.fix-meta{display:flex;flex-wrap:wrap;align-items:center;gap:6px 14px;margin-top:9px;color:var(--muted);font-size:13px;}
.pill{padding:2px 9px;border-radius:6px;background:rgba(76,141,246,.14);color:#8DB4FA;font-size:12px;font-weight:500;}
.badge{padding:2px 9px;border-radius:6px;font-size:12px;font-weight:600;}
.badge.crit{background:rgba(229,72,77,.17);color:#FF8A8E;}.badge.high{background:rgba(227,166,47,.17);color:#F2C060;}.badge.med{background:rgba(76,141,246,.17);color:#8DB4FA;}
.trend{font-weight:600;font-size:13px;}.trend.up{color:#FF8A8E;}.trend.down{color:#5FD3A8;}.trend.flat{color:var(--muted);}
.score{text-align:right;}
.score-n{font-size:26px;font-weight:700;line-height:1;font-variant-numeric:tabular-nums;}
.score-n small{font-size:13px;color:var(--muted);font-weight:500;margin-left:2px;}
.bar{height:6px;background:rgba(255,255,255,.08);border-radius:999px;margin:9px 0 5px;overflow:hidden;}
.bar i{display:block;height:100%;border-radius:999px;}
.score-l{font-size:12px;color:var(--muted);}
details.ev{border-top:1px solid var(--line);}
details.ev summary{cursor:pointer;padding:10px 18px;font-size:13px;color:#8DB4FA;font-weight:500;list-style:none;}
details.ev summary::-webkit-details-marker{display:none;}
details.ev summary:before{content:"\\25B8";margin-right:8px;display:inline-block;transition:transform .15s;}
details.ev[open] summary:before{transform:rotate(90deg);}
details.ev summary:hover{background:rgba(76,141,246,.07);}
.ev-b{padding:2px 18px 16px;}.ev-h{font-size:12.5px;color:var(--muted);margin:8px 0 2px;font-weight:500;}
.quote{border-left:2px solid var(--line2);padding:2px 0 2px 12px;margin:8px 0;color:var(--soft);font-size:13.5px;line-height:1.5;}
.next{margin-top:12px;padding:10px 12px;border-radius:8px;background:rgba(255,255,255,.05);font-size:13px;color:var(--soft);line-height:1.5;}
.next b{color:var(--text);font-weight:600;}

/* ---------- sidebar (glass) ---------- */
section[data-testid="stSidebar"]{background:rgba(8,13,24,.68)!important;backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border-right:1px solid var(--line);z-index:70;}
section[data-testid="stSidebar"] .block-container,section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]{padding-top:1.4rem;}
section[data-testid="stSidebar"] label p{font-size:13px;color:var(--soft);font-weight:500;}
.side-h{font-size:13px;font-weight:600;margin:18px 0 8px;}
.dq{border:1px solid var(--line);background:rgba(255,255,255,.04);border-radius:12px;padding:14px;}
.dq-top{display:flex;justify-content:space-between;align-items:baseline;}
.dq-v{font-size:22px;font-weight:700;font-variant-numeric:tabular-nums;}.dq-l{font-size:12.5px;color:var(--muted);}
.dq-r{display:flex;justify-content:space-between;font-size:13px;padding:6px 0;border-top:1px solid var(--line);color:var(--soft);}
.dq-r b{font-weight:600;color:var(--text);font-variant-numeric:tabular-nums;}

/* ---------- review search + streamlit widgets ---------- */
.rv{background:var(--glass);border:1px solid var(--line);border-radius:14px;padding:12px 16px;margin-bottom:8px;backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);}
.rv-h{display:flex;gap:10px;align-items:center;font-size:12.5px;color:var(--muted);margin-bottom:6px;}.rv-h b{color:var(--text);font-weight:600;}
.rv-t{font-size:14px;line-height:1.55;color:var(--soft);}
div[data-testid="stVerticalBlockBorderWrapper"]{background:var(--glass)!important;border:1px solid var(--line)!important;border-radius:14px!important;
backdrop-filter:blur(14px) saturate(130%);-webkit-backdrop-filter:blur(14px) saturate(130%);box-shadow:inset 0 1px 0 rgba(255,255,255,.05);}
div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stVerticalBlockBorderWrapper"]{background:transparent!important;border:none!important;box-shadow:none;backdrop-filter:none;}
div[data-testid="stExpander"]{border:1px solid var(--line);border-radius:14px;background:var(--glass);backdrop-filter:blur(12px);}
.stDownloadButton button{border-radius:8px;border:1px solid var(--line2);background:rgba(255,255,255,.06);}
</style>
"""

# Cursor "gyro" + scroll-driven background. Runs once; re-running replaces the previous instance.
SCRIPT = """
<script>
(function(){
  const P = window.frameElement ? window.parent : window, D = P.document, root = D.documentElement;
  if (P.__rl && P.__rl.destroy) P.__rl.destroy();
  const reduce = P.matchMedia && P.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const stops = [218, 250, 276, 196, 226, 206];            // background hue along the page
  const clamp = (v,a,b) => Math.max(a, Math.min(b, v));
  const hueAt = p => { const x = clamp(p,0,1)*(stops.length-1), i = Math.floor(x), f = x-i;
                       return stops[i] + ((stops[Math.min(i+1,stops.length-1)] - stops[i]) * f); };
  let tx=0, ty=0, cx=0, cy=0, tp=0, cp=0, raf=0;
  const scroller = () => { const m = D.querySelector('[data-testid="stMain"]') || D.querySelector('section.main');
                           return (m && m.scrollHeight > m.clientHeight) ? m : (D.scrollingElement || D.documentElement); };
  const readScroll = () => { const s = scroller(), max = s.scrollHeight - s.clientHeight; tp = max > 0 ? s.scrollTop / max : 0; };
  const frame = () => {
    cx += (tx-cx)*.07; cy += (ty-cy)*.07; cp += (tp-cp)*.09;
    const h = hueAt(cp);
    root.style.setProperty('--mx', cx.toFixed(4)); root.style.setProperty('--my', cy.toFixed(4));
    root.style.setProperty('--p', cp.toFixed(4));
    root.style.setProperty('--h1', h.toFixed(1)); root.style.setProperty('--h2', (h+44).toFixed(1)); root.style.setProperty('--h3', (h-24).toFixed(1));
    raf = (Math.abs(tx-cx)+Math.abs(ty-cy)+Math.abs(tp-cp) > .0008) ? requestAnimationFrame(frame) : 0;
  };
  const kick = () => { if (!raf) raf = requestAnimationFrame(frame); };
  const spy = () => {
    const links = D.querySelectorAll('a.lk[data-nav]'); if (!links.length) return;
    let active = links[0].dataset.nav;
    links.forEach(a => { const el = D.getElementById(a.dataset.nav); if (el && el.getBoundingClientRect().top <= 150) active = a.dataset.nav; });
    const s = scroller(); if (s.scrollHeight - s.clientHeight - s.scrollTop < 6) active = links[links.length-1].dataset.nav;
    links.forEach(a => a.classList.toggle('active', a.dataset.nav === active));
  };
  const onScroll = () => { readScroll(); spy(); kick(); };
  const onMove = e => { if (reduce) return; tx = (e.clientX / P.innerWidth - .5) * 2; ty = (e.clientY / P.innerHeight - .5) * 2; kick(); };
  const onTilt = e => { if (reduce || e.gamma == null) return; tx = clamp(e.gamma/30,-1,1); ty = clamp((e.beta-45)/30,-1,1); kick(); };
  const onClick = e => { const a = e.target.closest && e.target.closest('a[data-nav]'); if (!a) return; e.preventDefault();
    const t = D.getElementById(a.dataset.nav); if (t) t.scrollIntoView({behavior: reduce ? 'auto' : 'smooth', block: 'start'}); };
  D.addEventListener('scroll', onScroll, true); D.addEventListener('mousemove', onMove, {passive:true});
  D.addEventListener('click', onClick); P.addEventListener('deviceorientation', onTilt);
  const timer = P.setInterval(onScroll, 500);              // Streamlit re-renders: keep nav + scroll state in sync
  onScroll();
  P.__rl = { destroy(){ D.removeEventListener('scroll', onScroll, true); D.removeEventListener('mousemove', onMove);
    D.removeEventListener('click', onClick); P.removeEventListener('deviceorientation', onTilt); P.clearInterval(timer); } };
})();
</script>
"""

st.markdown(CSS, unsafe_allow_html=True)
st.markdown('<div class="rl-bg" aria-hidden="true"><div class="rl-grid"></div><div class="rl-orb o1"></div>'
            '<div class="rl-orb o2"></div><div class="rl-orb o3"></div></div>', unsafe_allow_html=True)
st.markdown('<nav class="rl-nav"><a class="brand" data-nav="home" href="#home"><span class="mark"></span><span>ReviewLens</span></a>'
            '<div class="links">' + "".join(f'<a class="lk" data-nav="{k}" href="#{k}">{v}</a>' for k, v in NAV) + '</div></nav>',
            unsafe_allow_html=True)
if "unsafe_allow_javascript" in inspect.signature(st.html).parameters:
    st.html(SCRIPT, unsafe_allow_javascript=True)
else:
    components.html(SCRIPT, height=0)


# ------------------------------------------------------------------------------- helpers
def esc(s):
    """HTML-escape and neutralise '$' (Streamlit would otherwise try to render it as maths)."""
    return html.escape(str(s)).replace("$", "&#36;")


def section(anchor, title, sub="", right=""):
    st.markdown(f'<div id="{anchor}" class="anchor"></div><div class="sec"><div><div class="sec-t">{esc(title)}</div>'
                f'<div class="sec-s">{esc(sub)}</div></div>{right}</div>', unsafe_allow_html=True)


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


def hero(n_reviews, issues, alerts, scope):
    if issues.empty:
        card = ('<div class="tilt"><div class="tilt-h"><span>Highest priority right now</span></div>'
                '<div class="tilt-t">Not enough negative feedback in this selection to rank issues.</div></div>')
    else:
        r = next(issues.head(1).itertuples())
        label, cls, color = severity(r.priority)
        n_al = len(alerts)
        card = (
            f'<div class="tilt"><div class="tilt-h"><span>Highest priority right now</span><span class="badge {cls}">{label}</span></div>'
            f'<div class="tilt-t">{esc(r.issue)}</div>'
            f'<div class="tilt-row"><div class="tilt-n">{r.priority}<small>/100</small></div>'
            f'<div class="fix-meta" style="margin:0"><span class="pill">{esc(str(r.aspect).capitalize())}</span>{trend_tag(r.trend)}</div></div>'
            f'<div class="bar" style="height:7px;margin:14px 0 0"><i style="width:{r.priority}%;background:{color}"></i></div>'
            f'<div class="tilt-f"><span><b>{r.pct_reviews}%</b> of reviews affected</span><span>Owner: <b>{esc(r.owner)}</b></span>'
            f'<span><b>{n_al}</b> emerging {"alert" if n_al == 1 else "alerts"}</span></div></div>')
    return (
        '<section class="hero"><div>'
        f'<div class="tag"><span class="dot"></span>Analysing {n_reviews:,} reviews: {esc(scope)}</div>'
        '<h1>Know what to fix before the next review lands</h1>'
        '<p class="lead">ReviewLens reads every customer review, groups complaints into concrete issues, '
        'and ranks them by impact, so your team starts with the problem that matters most.</p>'
        '<div class="cta"><a class="btn primary" data-nav="fixes" href="#fixes">See top fixes</a>'
        '<a class="btn" data-nav="sentiment" href="#sentiment">Explore sentiment</a></div></div>'
        f'<div class="hero-r">{card}</div></section>')


def style_fig(fig, height=340, legend=True):
    fig.update_layout(
        height=height, margin=dict(l=4, r=4, t=4, b=4), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#B7C0CF", size=12), showlegend=legend,
        legend=dict(orientation="h", y=1.1, x=0, title=None, bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor="#17223A", bordercolor="rgba(255,255,255,.2)", font_color=TEXT))
    fig.update_xaxes(gridcolor="rgba(255,255,255,.07)", zerolinecolor="rgba(255,255,255,.12)", linecolor="rgba(255,255,255,.1)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,.07)", zerolinecolor="rgba(255,255,255,.12)", linecolor="rgba(255,255,255,.1)")
    return fig


PLOT_CFG = {"displayModeBar": False}


@st.cache_data(show_spinner="Analysing reviews...")
def analyse(raw: pd.DataFrame):
    rev = clean_reviews(raw); return rev, extract_aspects(rev)


# ------------------------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown('<div style="font-size:18px;font-weight:700">ReviewLens</div>'
                '<div style="font-size:13px;color:#94A0B5">Customer voice insights</div>', unsafe_allow_html=True)
    st.markdown('<div class="side-h">Data</div>', unsafe_allow_html=True)
    up = st.file_uploader("Upload reviews CSV", type="csv",
                          help="Columns: review_id, brand, date, rating, review_text")
    raw = pd.read_csv(up) if up else pd.read_csv(pathlib.Path(__file__).resolve().parents[1] / "data/reviews.csv")
    reviews, asp = analyse(raw)
    st.markdown('<div class="side-h">Filters</div>', unsafe_allow_html=True)
    brands = sorted(reviews.brand.unique())
    brand = st.selectbox("Brand", ["All brands"] + brands)
    lo, hi = reviews.date.min().date(), reviews.date.max().date()
    dr = st.date_input("Date range", (lo, hi), min_value=lo, max_value=hi)

    total, flagged = len(reviews), int(reviews.flagged.sum())
    usable_pct = 100 * (total - flagged) / max(total, 1)
    st.markdown('<div class="side-h">Data quality</div>', unsafe_allow_html=True)
    qcolor = GREEN if usable_pct >= 95 else AMBER if usable_pct >= 85 else RED
    st.markdown(
        '<div class="dq"><div class="dq-top">'
        f'<div class="dq-v">{usable_pct:.1f}%</div><div class="dq-l">usable reviews</div></div>'
        f'<div class="bar"><i style="width:{usable_pct:.1f}%;background:{qcolor}"></i></div>'
        f'<div class="dq-r"><span>Loaded</span><b>{total:,}</b></div>'
        f'<div class="dq-r"><span>Excluded</span><b>{flagged:,}</b></div>'
        f'<div class="dq-r"><span>&nbsp;&nbsp;Duplicates</span><b>{int(reviews.is_duplicate.sum()):,}</b></div>'
        f'<div class="dq-r"><span>&nbsp;&nbsp;Too short</span><b>{int(reviews.is_too_short.sum()):,}</b></div>'
        f'<div class="dq-r"><span>&nbsp;&nbsp;Repetitive</span><b>{int(reviews.is_repetitive.sum()):,}</b></div>'
        f'<div class="dq-r"><span>Star/text mismatches</span><b>{int(reviews.rating_mismatch.sum()):,}</b></div></div>',
        unsafe_allow_html=True)
    st.caption("Exclusion reasons can overlap. Excluded reviews are left out of every chart and score.")

# ------------------------------------------------------------------------------- filtering (unchanged logic)
rv, a = reviews, asp
if brand != "All brands": rv, a = rv[rv.brand == brand], a[a.brand == brand]
if len(dr) == 2:
    d0, d1 = map(pd.Timestamp, dr); rv, a = rv[rv.date.between(d0, d1)], a[a.date.between(d0, d1)]
good = rv[~rv.flagged]

scope_from, scope_to = (dr[0], dr[1]) if len(dr) == 2 else (lo, hi)
if good.empty or a.empty:
    st.markdown('<div id="home" class="anchor"></div>', unsafe_allow_html=True)
    st.warning("No reviews match these filters. Widen the date range.")
    st.stop()

issues, alerts = find_issues(a, rv), emerging(asp if brand == "All brands" else asp[asp.brand == brand])
summ = aspect_summary(a)

# ------------------------------------------------------------------------------- home
st.markdown('<div id="home" class="anchor"></div>', unsafe_allow_html=True)
st.markdown(hero(len(good), issues, alerts, brand), unsafe_allow_html=True)

# ------------------------------------------------------------------------------- overview
chips = (f'<div class="chips"><span class="chip">{esc(brand)}</span>'
         f'<span class="chip">{scope_from:%d %b %Y} to {scope_to:%d %b %Y}</span></div>')
section("overview", "Overview", "The state of customer feedback for the current selection", chips)
avg = good.rating.mean()
weak, weak_net, weak_neg = summ.index[0], summ.net.iloc[0], int(summ.neg.iloc[0])
mism = int(good.rating_mismatch.sum()); mism_pct = 100 * mism / len(good)
st.markdown('<div class="kpis">' + "".join([
    kpi("Reviews", f"{len(good):,}", f"{int(rv.flagged.sum()):,} excluded as duplicate or spam-like", BLUE),
    kpi("Average rating", f"{avg:.2f}", "Mean star rating of usable reviews",
        GREEN if avg >= 4 else AMBER if avg >= 3.5 else RED, unit="/ 5"),
    kpi("Weakest aspect", str(weak).capitalize(), f"Net sentiment {weak_net:+.2f}, {weak_neg:,} negative mentions",
        RED if weak_net < 0 else AMBER if weak_net < 0.4 else GREEN),
    kpi("Star/text mismatches", f"{mism:,}", f"{mism_pct:.1f}% of reviews: high stars with negative text, or the reverse",
        AMBER if mism_pct > 5 else BLUE),
]) + "</div>", unsafe_allow_html=True)
if len(alerts):
    st.markdown("".join(alert_card(r) for r in alerts.itertuples()), unsafe_allow_html=True)

# ------------------------------------------------------------------------------- top 5 fixes
section("fixes", "Top 5 things to fix", "Ranked by customers affected, severity, recent growth and rating impact")
if issues.empty:
    st.info("Not enough negative feedback in this selection to rank issues. Widen the date range or brand filter.")
else:
    st.markdown("".join(fix_card(i, r) for i, r in enumerate(issues.head(5).itertuples(), 1)), unsafe_allow_html=True)
with st.expander("How is priority calculated?"):
    st.markdown("`priority = share of reviews affected x (0.5 + severity) x (1 + recent growth) x (1 + rating drag / 2)`, "
                "scaled so the top issue is 100. Issues are clusters of negative review clauses within an aspect. "
                "Badges: **Critical** 70 and above, **High** 40 to 69, **Medium** below 40.")

# ------------------------------------------------------------------------------- sentiment
section("sentiment", "Customer sentiment", "Net sentiment runs from -1 (all negative) to +1 (all positive)")
left, right = st.columns([5, 6], gap="medium")

with left, st.container(border=True):
    st.markdown('<div class="panel-t">Sentiment by topic</div>'
                '<div class="panel-s">Share of mentions, weakest topic first. Net score on the right.</div>',
                unsafe_allow_html=True)
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
        fig.add_annotation(x=1.0, xref="paper", y=nm, text=f"<b>{summ.loc[k, 'net']:+.2f}</b>", showarrow=False,
                           xanchor="left", xshift=8, font=dict(color=GREEN if summ.loc[k, "net"] >= 0.4 else
                                                              AMBER if summ.loc[k, "net"] >= 0 else RED, size=12))
    fig.update_layout(barmode="stack", bargap=0.35)
    style_fig(fig, 360); fig.update_layout(margin=dict(l=4, r=48, t=4, b=4))
    fig.update_xaxes(range=[0, 100], showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False)
    st.plotly_chart(fig, width="stretch", config=PLOT_CFG)

with right, st.container(border=True):
    st.markdown('<div class="panel-t">Sentiment trend</div>'
                '<div class="panel-s">Weekly net sentiment. Above the dashed line is net positive.</div>',
                unsafe_allow_html=True)
    w = weekly_net(a)
    sel = st.multiselect("Topics", sorted(w.aspect.unique()), default=list(summ.index[:3]),
                         format_func=lambda x: x.capitalize(), label_visibility="collapsed")
    wsel = w[w.aspect.isin(sel)].assign(Topic=lambda d: d.aspect.str.capitalize())
    if wsel.empty:
        st.info("Select at least one topic to see its trend.")
    else:
        tf = px.line(wsel, x="week", y="net", color="Topic", markers=True, color_discrete_sequence=SERIES,
                     labels={"net": "Net sentiment", "week": ""})
        tf.update_traces(line=dict(width=2.2), marker=dict(size=5),
                         hovertemplate="%{fullData.name}: %{y:+.2f}<extra></extra>")
        tf.add_hline(y=0, line_dash="dash", line_color=MUTED, line_width=1)
        style_fig(tf, 306); tf.update_layout(hovermode="x unified")
        tf.update_yaxes(range=[-1.05, 1.05], tickformat="+.1f", title=None)
        tf.update_xaxes(tickformat="%d %b", title=None, showgrid=False)
        st.plotly_chart(tf, width="stretch", config=PLOT_CFG)

# ------------------------------------------------------------------------------- compare brands
section("compare", "Brand comparison", "Net sentiment by brand and topic across all dates. Green is better, red is worse.")
with st.container(border=True):
    h = asp.groupby(["brand", "aspect"]).apply(
        lambda g: (g.sentiment.eq("pos").sum() - g.sentiment.eq("neg").sum()) / len(g), include_groups=False).unstack()
    h.columns = [c.capitalize() for c in h.columns]
    hf = px.imshow(h, text_auto=".2f", aspect="auto", zmin=-1, zmax=1,
                   color_continuous_scale=[[0, RED], [0.5, "#1B2740"], [1, GREEN]])
    style_fig(hf, 120 + 70 * len(h), legend=False)
    hf.update_layout(coloraxis_colorbar=dict(title="Net", thickness=10, len=0.8, outlinewidth=0, tickfont=dict(size=11)))
    hf.update_xaxes(side="top", showgrid=False, title=None); hf.update_yaxes(showgrid=False, title=None)
    st.plotly_chart(hf, width="stretch", config=PLOT_CFG)

# ------------------------------------------------------------------------------- ask the reviews
section("reviews", "Ask the reviews", "Search what customers wrote, in their own words")
q = st.text_input("Search reviews", label_visibility="collapsed",
                  placeholder="Try: why do customers return it, or bluetooth disconnecting")
if q:
    vec, X = build_index(good); hits = search(q, good, vec, X)
    if len(hits):
        st.caption(f"{len(hits)} matching reviews")
        cards = []
        for r in hits.itertuples():
            rc = GREEN if r.rating >= 4 else AMBER if r.rating == 3 else RED
            cards.append(f'<div class="rv"><div class="rv-h"><b>{esc(r.brand)}</b>'
                         f'<span class="dot" style="background:{rc}"></span><span>{r.rating} stars</span>'
                         f'<span>{r.date:%d %b %Y}</span></div><div class="rv-t">{esc(r.review_text)}</div></div>')
        st.markdown("".join(cards), unsafe_allow_html=True)
    else:
        st.info("No matches. Try different words.")

# ------------------------------------------------------------------------------- brief and data
section("brief", "Brief and data", "A shareable summary and the full ranked issue table")
brief = make_brief(brand, rv, a, issues, alerts)
b1, b2 = st.columns([3, 2], gap="medium")
with b1, st.container(border=True):
    st.markdown('<div class="panel-t">PM brief</div><div class="panel-s">Ready to paste into a doc or email.</div>',
                unsafe_allow_html=True)
    st.markdown(brief)
    st.download_button("Download PM brief (.md)", brief, file_name="reviewlens_brief.md")
with b2, st.container(border=True):
    st.markdown('<div class="panel-t">Issue table</div><div class="panel-s">All ranked issues in this selection.</div>',
                unsafe_allow_html=True)
    st.dataframe(issues.drop(columns=["quotes", "action"], errors="ignore"), width="stretch", hide_index=True)
