"""Consistent chart sizing, zoom, expansion and portable specification export."""
import json
import streamlit as st


@st.dialog("Expanded figure", width="large")
def expanded_chart(spec, title):
    st.subheader(title)
    st.caption("Scroll to zoom quantitative axes. Drag to pan. Double-click the chart to reset.")
    spec = dict(spec, height=600)
    st.vega_lite_chart(spec=spec, width="stretch", theme=None)


def show_chart(chart, title, key, height=None):
    height = height or st.session_state.get("chart_height", 320)
    chart = (chart.properties(height=height).interactive()
             .configure(background="transparent")
             .configure_view(strokeWidth=0)
             .configure_axis(labelColor="#B5BDD1", titleColor="#B5BDD1", gridColor="#2C334A", domain=False)
             .configure_legend(title=None, labelColor="#B5BDD1"))
    spec = chart.to_dict()
    st.altair_chart(chart, width="stretch", theme=None, key=f"figure_{key}")
    expand, export = st.columns(2)
    if expand.button("Expand chart", key=f"expand_{key}", width="stretch"):
        expanded_chart(spec, title)
    export.download_button("Export figure · JSON", json.dumps(spec), f"{key}.vl.json",
                           "application/json", key=f"export_{key}", width="stretch")
