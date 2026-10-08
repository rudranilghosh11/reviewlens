import streamlit as st
import ui, state
from src.brief import make_brief

ctx = state.require()
ui.page_header("Reports", "A one-page brief and the full ranked issue list.", state.scope_chips(ctx))
brief = make_brief(ctx["brand"], ctx["rv"], ctx["a"], ctx["issues"], ctx["alerts"])

b1, b2 = st.columns([3, 2], gap="medium")
with b1, st.container(border=True):
    st.markdown('<div class="panel-t">PM brief</div><div class="panel-s">Ready to paste into a doc or email.</div>', unsafe_allow_html=True)
    st.markdown(brief)
    st.download_button("Download PM brief (.md)", brief, file_name="reviewlens_brief.md")
with b2, st.container(border=True):
    st.markdown('<div class="panel-t">Issue table</div><div class="panel-s">All ranked issues in this selection.</div>', unsafe_allow_html=True)
    st.dataframe(ctx["issues"].drop(columns=["quotes", "action"], errors="ignore"), width="stretch", hide_index=True)
