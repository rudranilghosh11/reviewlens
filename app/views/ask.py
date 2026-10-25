import streamlit as st
import ui, state
from src.search import build_index, search

ctx = state.require()
good = ctx["good"]
ui.page_header("Ask the reviews", "Search what customers wrote, in their own words.", state.scope_chips(ctx))

EXAMPLES = ["bluetooth disconnecting", "refund not processed", "arrived damaged", "ear tips hurt"]
def _set(x): st.session_state["q"] = x

q = st.text_input("Search reviews", key="q", label_visibility="collapsed",
                  placeholder="Try: why do customers return it, or bluetooth disconnecting")
cols = st.columns(len(EXAMPLES) + 2)
for c, ex in zip(cols, EXAMPLES):
    c.button(ex, on_click=_set, args=(ex,), key=f"ex_{ex}", width="stretch")

if q:
    vec, X = build_index(good); hits = search(q, good, vec, X)
    if len(hits):
        st.caption(f"{len(hits)} matching reviews")
        cards = []
        for r in hits.itertuples():
            rc = ui.GREEN if r.rating >= 4 else ui.AMBER if r.rating == 3 else ui.RED
            cards.append(f'<div class="rv"><div class="rv-h"><b>{ui.esc(r.brand)}</b><span class="dot" style="background:{rc}"></span>'
                         f'<span>{r.rating} stars</span><span>{r.date:%d %b %Y}</span></div>'
                         f'<div class="rv-t">{ui.esc(r.review_text)}</div></div>')
        st.markdown("".join(cards), unsafe_allow_html=True)
    else:
        st.info("No matches. Try different words.")
