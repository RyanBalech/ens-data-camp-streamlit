"""Interactive descriptive adaptation of Ryan Balech's ENS Data Camp project."""
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from hec.tools.data_utils import filter_dataset, load_dataset

ROOT = Path(__file__).parent
TEAL, NAVY, CLAY = "#087F75", "#142D45", "#B65D44"
st.set_page_config(page_title="Allocation Lab | ENS Data Camp", layout="wide")
st.markdown(f"<style>{(ROOT / 'assets/style.css').read_text()}</style>", unsafe_allow_html=True)


@st.cache_data(max_entries=2, show_spinner="Validating and aligning your observations…")
def read_data(features, targets):
    return load_dataset(features, targets)


def chart_style(chart):
    return (chart.configure_view(strokeWidth=0)
            .configure_axis(labelColor="#526577", titleColor="#526577", gridColor="#E7EBEC", domain=False)
            .configure_legend(title=None, labelColor="#526577"))


with st.sidebar:
    st.markdown('<div class="wordmark">AL<span>/</span> Allocation Lab</div>', unsafe_allow_html=True)
    st.caption("ENS DATA CAMP · RYAN BALECH")
    st.divider()
    st.markdown("### Your workspace")
    source = st.radio("Data source", ["Demo dataset", "Upload my data"], key="source")
    features, targets = None, None
    if source == "Upload my data":
        features = st.file_uploader("Training features · X_train", type="csv", key="features")
        targets = st.file_uploader("Training targets · y_train", type="csv", key="targets")
        st.caption("Up to 500 MB per file. Files are processed by this running app and are not committed to Git.")
    else:
        st.caption("Six synthetic observations for a quick walkthrough. These are illustrative, not research results.")
    st.divider()

st.markdown('<div class="eyebrow">RESEARCH WORKSPACE / 01</div>', unsafe_allow_html=True)
st.title("Inside the allocation signal.")
st.markdown('<div class="intro">Explore return direction, allocation groups and the historical signals behind the ENS Data Camp project.</div>', unsafe_allow_html=True)

if source == "Upload my data" and (features is None or targets is None):
    st.info("Add both X_train and y_train in the sidebar to open your research workspace.")
    st.stop()
try:
    if source == "Demo dataset":
        data = read_data(ROOT / "sample_data/X_train_sample.csv", ROOT / "sample_data/y_train_sample.csv")
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
    st.caption("Filters apply to every chart and table in the workspace.")
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

overview, signals, records, methods = st.tabs(["Overview", "Historical signals", "Data explorer", "Research & methods"])

with overview:
    left, right = st.columns([1.6, 1])
    with left, st.container(border=True):
        st.subheader("The shape of tomorrow's return")
        st.caption("Observed next-day returns · all selected rows · basis points")
        counts, edges = np.histogram(selected.target * 10000, bins=40)
        histogram = pd.DataFrame({"start": edges[:-1], "end": edges[1:], "Observations": counts})
        plot = alt.Chart(histogram).mark_bar(color=TEAL, cornerRadiusTopLeft=2, cornerRadiusTopRight=2).encode(
            x=alt.X("start:Q", title="Next-day return (bp)"), x2="end:Q",
            y=alt.Y("Observations:Q", title="Observations"), y2=alt.Y2(datum=0), tooltip=[alt.Tooltip("start:Q", format=".2f"), alt.Tooltip("end:Q", format=".2f"), "Observations:Q"])
        st.altair_chart(chart_style(plot.properties(height=275)), width="stretch")
    with right, st.container(border=True):
        st.subheader("Direction balance")
        st.caption("Actual outcomes in the selected cohort")
        balance = pd.DataFrame({"Direction": ["Positive", "Zero or negative"], "Observations": [(selected.label == 1).sum(), (selected.label == 0).sum()]})
        plot = alt.Chart(balance).mark_bar(cornerRadiusEnd=5, size=40).encode(
            y=alt.Y("Direction:N", title=None, sort=None), x=alt.X("Observations:Q", title="Observations"),
            color=alt.Color("Direction:N", scale=alt.Scale(domain=["Positive", "Zero or negative"], range=[TEAL, CLAY]), legend=None), tooltip=["Direction", "Observations"])
        st.altair_chart(chart_style(plot.properties(height=190)), width="stretch")
        st.caption("A balanced target can still be difficult to predict. Class frequency alone is not evidence of predictive skill.")
    with st.container(border=True):
        st.subheader("Where the groups differ")
        st.caption("Mean observed return by allocation family · descriptive comparison")
        grouped = selected.groupby("GROUP").agg(Observations=("target", "size"), Mean=("target", "mean")).reset_index()
        grouped["Mean (bp)"] = grouped.Mean * 10000
        plot = alt.Chart(grouped).mark_bar(color=NAVY, cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
            x=alt.X("GROUP:N", title="Allocation group"), y=alt.Y("Mean (bp):Q", title="Mean next-day return (bp)"), tooltip=["GROUP", "Observations", alt.Tooltip("Mean (bp):Q", format=".2f")])
        st.altair_chart(chart_style(plot.properties(height=220)), width="stretch")

with signals:
    st.subheader("Read the history behind each observation")
    st.write("The original project summarizes return and signed-volume histories into momentum, volatility and liquidity features.")
    lag_columns = sorted([col for col in selected if col.startswith("RET_") and col[4:].isdigit()], key=lambda col: int(col[4:]), reverse=True)
    if lag_columns:
        summary = pd.DataFrame({"Days before target": [-int(col[4:]) for col in lag_columns], "Mean return (bp)": [pd.to_numeric(selected[col], errors="coerce").mean() * 10000 for col in lag_columns]})
        plot = alt.Chart(summary).mark_line(color=TEAL, point=True, strokeWidth=3).encode(x=alt.X("Days before target:Q"), y=alt.Y("Mean return (bp):Q"), tooltip=["Days before target", alt.Tooltip("Mean return (bp):Q", format=".2f")])
        st.altair_chart(chart_style(plot.properties(height=300)), width="stretch")
        st.caption(f"Cohort average across {len(lag_columns)} available lags. Missing feature values are excluded from each mean. This is not a portfolio backtest.")
    else:
        st.info("No RET_1 … RET_20 columns found in this feature file.")

with records:
    st.subheader("Inspect the evidence")
    st.caption("Preview limited to 500 rows to keep the browser responsive. The metrics use every selected row.")
    st.dataframe(selected.head(500), hide_index=True, width="stretch")
    st.download_button("Download this preview · CSV", selected.head(500).to_csv(index=False), "allocation-preview.csv", "text/csv")
    missing = selected.isna().mean().sort_values(ascending=False)
    missing = missing[missing > 0].rename_axis("Feature").reset_index(name="Missing share")
    st.markdown("#### Data quality")
    if missing.empty:
        st.success("No missing feature values in this selection.")
    else:
        st.dataframe(missing, hide_index=True, width="stretch")
    st.caption("Targets and identifiers are validated on import. Missing historical features remain visible; this explorer does not impute them.")

with methods:
    st.subheader("From a research project to an interactive app")
    st.write("This is Ryan Balech's individual Streamlit adaptation of the ENS Data Camp / QRT asset-allocation project. The original research was conducted with Omar Karim, Hitaishi Dhoowooah, Gabriel Dreik and Korouhanba Khuman Laikhuram.")
    st.markdown("#### 01 / The question")
    st.write("The original task predicts whether the next-day return is positive using 20 return lags, 20 signed-volume lags, turnover and allocation group. A label of 1 means target > 0; 0 includes zero and negative returns.")
    st.markdown("#### 02 / This application")
    st.write("Upload matching training feature and target CSVs to explore distributions, group differences, historical signals and missingness. The application is an exploratory adaptation: it does not train CatBoost or generate predictions. X_test and submission.csv are not inputs to this labeled-data explorer.")
    st.markdown("#### 03 / Original model & limitations")
    st.write("The supplied notebook engineers statistical, momentum and liquidity features and trains CatBoost on a GPU. Its stratified random cross-validation may place observations from the same anonymized date in both partitions. The report also describes grouped validation elsewhere; those descriptions are inconsistent, so the app does not claim to reproduce its reported scores.")
    st.write("Anonymized TS values are identifiers, not calendar dates. These plots show associations and observed outcomes; they do not establish out-of-sample predictive performance.")
    st.markdown("#### 04 / Reproduce this workspace")
    st.write("The repository includes Docker instructions, a frozen dependency environment, import/filter tests, UI smoke tests and GitLab CI. The bundled six-row dataset is synthetic and only demonstrates the interface. Use the original challenge training files to reproduce the full analysis.")

st.divider()
st.markdown('<div class="footer">ALLOCATION LAB <span>ENS Data Camp · Individual adaptation by Ryan Balech</span></div>', unsafe_allow_html=True)
