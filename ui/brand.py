"""Shared vector identity for the sidebar and browser tab."""
from base64 import b64encode
from pathlib import Path

import streamlit as st

MARK = Path(__file__).resolve().parents[1] / "assets/brand-mark.svg"


def sidebar_brand():
    encoded = b64encode(MARK.read_bytes()).decode()
    st.html(
        '<div class="brand-lockup" aria-label="Allocation Lab, ENS Data Camp by Ryan Balech">'
        f'<img class="brand-mark" src="data:image/svg+xml;base64,{encoded}" width="46" height="46" alt="" />'
        '<div class="brand-type"><span class="brand-name">Allocation <span>Lab</span></span>'
        '<span class="brand-project">ENS DATA CAMP</span></div></div>'
        '<div class="brand-credit">A research workspace by <strong>Ryan Balech</strong></div>'
    )
