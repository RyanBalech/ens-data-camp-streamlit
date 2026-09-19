"""Interactive descriptive adaptation of Ryan Balech's ENS Data Camp project."""
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from streamlit.components.v1 import declare_component

from hec.tools.data_utils import filter_dataset, load_dataset
from hec.tools.demo_data import make_demo_dataset
from ui.charts import show_chart
from ui.research_pages import model_lab, feature_explorer
from ui.welcome import welcome
from ui.methods import research_methods
from ui.brand import MARK, sidebar_brand

ROOT = Path(__file__).parent
TEAL, NAVY, CLAY = "#7EE8C5", "#B29AFF", "#FFA88E"
st.set_page_config(page_title="Allocation Lab | ENS Data Camp", page_icon=str(MARK), layout="wide")
st.markdown(f"<style>{(ROOT / 'assets/style.css').read_text()}</style>", unsafe_allow_html=True)


@st.cache_data(max_entries=2, show_spinner="Validating and aligning your observations…")
def read_data(features, targets):
    return load_dataset(features, targets)


with st.sidebar:
    sidebar_brand()
    st.divider()
    st.markdown("### Your workspace")
    source = st.radio("Data source", ["Demo dataset", "Upload my data"], key="source")
    features, targets = None, None
    if source == "Upload my data":
        features = st.file_uploader("Training features · X_train", type="csv", key="features")
        targets = st.file_uploader("Training targets · y_train", type="csv", key="targets")
        st.caption("Up to 500 MB per file. Files are processed by this running app and are not committed to Git.")
    else:
        st.caption("360 synthetic observations with the full 20-day schema. Illustrative only; not research results.")
    st.divider()

motion_header = declare_component("allocation_motion_header", path=str(ROOT / "assets/motion"))
motion_header(key="research_header", default=None)

welcome(source)

if source == "Upload my data" and (features is None or targets is None):
    st.info("Add both X_train and y_train in the sidebar to open your research workspace.")
    st.stop()
try:
    if source == "Demo dataset":
        data = make_demo_dataset()
    else:
        data = read_data(features, targets)
except (ValueError, pd.errors.ParserError, UnicodeError) as error:
    st.error(f"We couldn't load this dataset. {error}")
    st.stop()

with st.sidebar:
    st.markdown("### Focus your analysis")
    groups = sorted(data["GROUP"].unique().tolist(), key=str)
    group = st.selectbox("Allocation group", ["All"] + groups, format_func=lambda v: "All groups" if v == "All" else f"Group {v}", key="group")
    label = st.selectbox("Return direction", ["All", 1, 0], format_func=lambda v: {"All": "All directions", 1: "Positive", 0: "Zero or negative"}[v], key="label")
    st.caption("Filters change the demo or uploaded-data exploration. Model Lab uses its own fixed validation experiment.")
    st.slider("Chart height", 250, 700, 350, 50, key="chart_height")
    st.divider()
    st.markdown("**Research question**")
    st.caption("Can 20 days of allocation history help explain the sign of the next day's return?")
    st.caption("Individual Streamlit adaptation · 2026")

selected = filter_dataset(data, None if group == "All" else group, None if label == "All" else label)
mode = "SYNTHETIC DEMO" if source == "Demo dataset" else "UPLOADED DATA"
st.markdown(f'<div class="dataset-strip"><span class="status-dot"></span><strong>{mode}</strong><span>{len(data):,} validated observations</span><span>Aligned by ROW_ID</span></div>', unsafe_allow_html=True)
if selected.empty:
    st.info("No observations match these filters. Choose another group or return direction in the sidebar.")
    st.stop()

a, b, c, d = st.columns(4)
a.metric("OBSERVATIONS", f"{len(selected):,}", help="Number of rows after filtering.")
b.metric("POSITIVE RETURNS", f"{selected.label.mean():.1%}", help="Share of observed targets greater than zero. This is not model accuracy.")
c.metric("MEAN NEXT-DAY RETURN", f"{selected.target.mean() * 10000:+.2f} bp", help="One basis point (bp) is 0.01 percentage points.")
d.metric("ALLOCATION GROUPS", str(selected.GROUP.nunique()))
st.caption(f"Viewing {len(selected):,} of {len(data):,} observations · Metrics describe observed outcomes, not predictions.")

overview, signals, records, research, methods = st.tabs(["Overview", "Historical signals", "Data explorer", "Model Lab", "Research & methods"])

with overview:
    st.caption("Explore known outcomes here. These charts describe the selected data; open Model Lab to assess prediction quality.")
    left, right = st.columns([1.6, 1])
    with left, st.container(border=True):
        st.subheader("How much did returns vary?")
        st.caption("Each bar counts observations in a return range. Left of zero = losses; right of zero = gains. 100 bp = 1%.")
        bins = st.slider("Histogram bins", 10, 100, 40, 10)
        counts, edges = np.histogram(selected.target * 10000, bins=bins)
        histogram = pd.DataFrame({"start": edges[:-1], "end": edges[1:], "Observations": counts})
        plot = alt.Chart(histogram).mark_bar(color=TEAL, cornerRadiusTopLeft=2, cornerRadiusTopRight=2).encode(
            x=alt.X("start:Q", title="Next-day return (bp)"), x2="end:Q",
            y=alt.Y("Observations:Q", title="Observations"), y2=alt.Y2(datum=0), tooltip=[alt.Tooltip("start:Q", format=".2f"), alt.Tooltip("end:Q", format=".2f"), "Observations:Q"])
        show_chart(plot, "Next-day return distribution", "distribution")
    with right, st.container(border=True):
        st.subheader("Direction balance")
        st.caption("How many observed outcomes were gains versus zero or losses?")
        balance = pd.DataFrame({"Direction": ["Positive", "Zero or negative"], "Observations": [(selected.label == 1).sum(), (selected.label == 0).sum()]})
        plot = alt.Chart(balance).mark_bar(size=40).encode(
            y=alt.Y("Direction:N", title=None, sort=None), x=alt.X("Observations:Q", title="Observations"),
            x2=alt.X2(datum=0),
            color=alt.Color("Direction:N", scale=alt.Scale(domain=["Positive", "Zero or negative"], range=[TEAL, CLAY]), legend=None), tooltip=["Direction", "Observations"])
        show_chart(plot, "Direction balance", "balance")
        st.caption(f"Positive: {int(balance.Observations.iloc[0]):,} · Zero or negative: {int(balance.Observations.iloc[1]):,}")
        st.caption("A balanced target can still be difficult to predict. Class frequency alone is not evidence of predictive skill.")
    with st.container(border=True):
        st.subheader("Where the groups differ")
        st.caption("Average next-day return for each allocation group. Above zero = an average gain; below zero = an average loss.")
        grouped = selected.groupby("GROUP").agg(Observations=("target", "size"), Mean=("target", "mean")).reset_index()
        grouped["Mean (bp)"] = grouped.Mean * 10000
        plot = alt.Chart(grouped).mark_bar(color=NAVY).encode(
            x=alt.X("GROUP:N", title="Allocation group", axis=alt.Axis(labelAngle=0)), y=alt.Y("Mean (bp):Q", title="Mean next-day return (bp)"), y2=alt.Y2(datum=0), tooltip=["GROUP", "Observations", alt.Tooltip("Mean (bp):Q", format=".2f")])
        show_chart(plot, "Returns by allocation group", "groups")
        if len(grouped) == 1:
            st.caption("One group selected. Choose All groups in the sidebar to compare groups.")
        st.dataframe(grouped[["GROUP", "Observations", "Mean (bp)"]].rename(columns={"GROUP": "Allocation group"}), hide_index=True, width="stretch")
        st.caption("Group averages describe this selection and do not establish future performance.")

with signals:
    st.subheader("Read the history behind each observation")
    st.write("The original project summarizes return and signed-volume histories into momentum, volatility and liquidity features.")
    lag_columns = sorted([col for col in selected if col.startswith("RET_") and col[4:].isdigit()], key=lambda col: int(col[4:]), reverse=True)
    if lag_columns:
        summary = pd.DataFrame({"Days before target": [-int(col[4:]) for col in lag_columns], "Mean return (bp)": [pd.to_numeric(selected[col], errors="coerce").mean() * 10000 for col in lag_columns]})
        plot = alt.Chart(summary).mark_line(color=TEAL, point=True, strokeWidth=3).encode(x=alt.X("Days before target:Q"), y=alt.Y("Mean return (bp):Q"), tooltip=["Days before target", alt.Tooltip("Mean return (bp):Q", format=".2f")])
        show_chart(plot, "Historical return averages", "history")
        st.caption(f"Cohort average across {len(lag_columns)} available lags. Missing feature values are excluded from each mean. This is not a portfolio backtest.")
    else:
        st.info("No RET_1 … RET_20 columns found in this feature file.")
    st.divider()
    feature_explorer(selected)

with research:
    model_lab()

with records:
    st.subheader("Inspect the evidence")
    st.caption("Preview limited to 500 rows to keep the browser responsive. The metrics use every selected row.")
    st.dataframe(selected.head(500), hide_index=True, width="stretch")
    st.download_button("Download this preview · CSV", selected.head(500).to_csv(index=False), "allocation-preview.csv", "text/csv", on_click="ignore")
    missing = selected.isna().mean().sort_values(ascending=False)
    missing = missing[missing > 0].rename_axis("Feature").reset_index(name="Missing share")
    st.markdown("#### Data quality")
    if missing.empty:
        st.success("No missing feature values in this selection.")
    else:
        st.dataframe(missing, hide_index=True, width="stretch")
    st.caption("Targets and identifiers are validated on import. Missing historical features remain visible; this explorer does not impute them.")

with methods:
    research_methods()

st.divider()
st.markdown('<div class="footer">ALLOCATION LAB <span>ENS Data Camp · Individual adaptation by Ryan Balech</span></div>', unsafe_allow_html=True)
