import pandas as pd
import streamlit as st
from pathlib import Path

from hec.tools.data_utils import filter_dataset, load_dataset


st.set_page_config(page_title="ENS Data Camp Explorer", layout="wide")
st.title("ENS Data Camp — Return Explorer")
st.write("Explore the relationship between allocation groups, historical returns, and next-day return labels.")

features_file = st.file_uploader("Upload X_train CSV (optional)", type="csv")
target_file = st.file_uploader("Upload y_train CSV (optional)", type="csv")

if features_file and target_file:
    data = load_dataset(features_file, target_file)
    st.success(f"Loaded {len(data):,} aligned observations.")
else:
    sample_dir = Path(__file__).parent / "sample_data"
    data = load_dataset(sample_dir / "X_train_sample.csv", sample_dir / "y_train_sample.csv")
    st.info("Showing the included sample dataset. Upload both full training files for the complete analysis.")

    groups = sorted(data["GROUP"].dropna().unique().tolist())
    selected_group = st.selectbox("Allocation group", ["All"] + groups)
    selected_label = st.selectbox("Return label", ["All", 0, 1], format_func=lambda x: {"All": "All labels", 0: "Negative or zero", 1: "Positive"}[x])

    filtered = filter_dataset(
        data,
        group=None if selected_group == "All" else selected_group,
        label=None if selected_label == "All" else selected_label,
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", f"{len(filtered):,}")
    c2.metric("Positive-return share", f"{filtered['label'].mean():.1%}" if len(filtered) else "—")
    c3.metric("Mean target", f"{filtered['target'].mean():.4f}" if len(filtered) else "—")
    st.subheader("Target distribution")
    st.bar_chart(filtered["label"].value_counts().sort_index())
    st.subheader("Sample")
    st.dataframe(filtered.head(100), use_container_width=True)
else:
    st.info("Upload both training files to begin. The files are intentionally kept outside Git because they are large.")
