"""Compact orientation for first-time research reviewers."""
from base64 import b64encode

import streamlit as st


def welcome(source):
    demo = source == "Demo dataset"
    exploration = "Synthetic demo" if demo else "Your training files"
    detail = "360 illustrative observations" if demo else "Upload X_train + y_train in the sidebar"
    paths = [
        '<path d="M4 19V5m0 14h16M8 15v-4m5 4V7m5 8v-6"/>',
        '<path d="m4 16 5-5 4 3 7-9M15 5h5v5"/><path d="M4 20h16"/>',
        '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9zM14 3v6h6M8 13h8M8 17h5"/>',
    ]
    steps = [
        ("Explore the patterns", "See how returns vary across allocation groups and trace an observation's 20-day history.", "Overview · Historical signals"),
        ("Put the models to the test", "Compare predictions with a simple baseline. Adjust the threshold and see what changes.", "Model Lab"),
        ("Look behind the results", "Inspect the rows, download the evidence and understand how the experiment was validated.", "Data explorer · Research & methods"),
    ]
    icons = [
        b64encode((f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">{path}</svg>').encode()).decode()
        for color, path in zip(["#7ee8c5", "#bbaaff", "#a6cbff"], paths)
    ]
    cards = "".join(
        f'<article class="tour-card tour-card-{i}"><div class="tour-card-top">'
        f'<span class="tour-icon"><img src="data:image/svg+xml;base64,{icon}" width="23" height="23" alt="" /></span>'
        f'<span class="tour-number" aria-label="Step {i}">{i:02}</span></div>'
        f'<h3>{title}</h3><p>{body}</p><div class="tour-destination">{destination}</div></article>'
        for i, (icon, (title, body, destination)) in enumerate(zip(icons, steps), 1)
    )
    st.html(
        '<section class="research-tour" aria-labelledby="tour-title">'
        '<div class="tour-heading"><div><span class="tour-kicker">YOUR RESEARCH GUIDE</span>'
        '<h2 id="tour-title">The project, at a glance.</h2></div>'
        '<span class="tour-duration">2 min to get oriented</span></div>'
        '<p class="tour-summary">Twenty days of investment history. One question: '
        '<strong>will the next day finish positive?</strong></p>'
        f'<div class="tour-grid">{cards}</div>'
        '<div class="tour-sources" aria-label="Data sources">'
        '<div class="tour-source"><span class="tour-source-dot"></span><div>'
        f'<span class="tour-source-label">EXPLORATION</span><strong>{exploration}</strong><span>{detail}</span>'
        '</div></div><div class="tour-source"><span class="tour-source-dot real"></span><div>'
        '<span class="tour-source-label">MODEL LAB</span><strong>Real project data</strong>'
        '<span>60,000 observations · fixed experiment</span></div></div></div></section>'
    )
    with st.expander("About the data & key terms"):
        st.markdown("**Getting started:** the synthetic demo is ready to explore, with no upload required. Each row represents one investment allocation, its previous 20 days of returns and trading activity, and its actual next-day outcome. Upload your training files in the sidebar to explore the original data.\n\n**Model Lab:** results come from a separate, fixed experiment on 60,000 real project observations. Changing demo data, uploads or filters does not retrain the models or change that experiment.\n\n**Return:** the change in investment value. Positive means a gain; zero or negative means no gain or a loss.\n\n**Allocation group:** an anonymized category of investment allocations. Group numbers are identifiers, not rankings.\n\n**Basis point (bp):** 0.01 percentage points; 100 bp = 1%.\n\n**Accuracy:** the share of correct direction predictions on held-out observations. The baseline always predicts the training fold's most common class.")
