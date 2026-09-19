import json
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from hec.tools.research import engineer_features, DESCRIPTIONS, RETURNS, VOLUMES
from ui.charts import show_chart

ROOT = Path(__file__).resolve().parents[1]
MINT, VIOLET, CORAL = "#7EE8C5", "#B29AFF", "#FFA88E"


def model_lab():
    st.subheader("Evidence, before confidence.")
    path = ROOT / "results/evaluation.json"
    if not path.exists():
        st.info("Run scripts/evaluate.py to generate verified evaluation results.")
        return
    report = json.loads(path.read_text())
    st.info(f"Fixed research experiment · {report['rows']:,} sampled real observations · three disjoint date folds. Dataset filters do not change this evaluation.")
    performance, thresholds, importance, card = st.tabs(["Validation", "Threshold lab", "Feature importance", "Model card"])
    with performance:
        score = report["scores"]["CatBoost"]["accuracy"]
        baseline = report["scores"]["Training-majority baseline"]["accuracy"]
        a, b, c = st.columns(3)
        a.metric("CATBOOST · OUT OF FOLD", f"{score:.2%}")
        b.metric("TRAINING-MAJORITY BASELINE", f"{baseline:.2%}")
        c.metric("ACCURACY DIFFERENCE", f"{(score - baseline) * 100:+.2f} pp")
        st.caption("The baseline chooses the majority class using each training fold only. Both methods are evaluated on exactly the same held-out rows.")
        comparison = pd.DataFrame([{"Model": name, "Accuracy": value["accuracy"]} for name, value in report["scores"].items()])
        chart = alt.Chart(comparison).mark_bar(color=VIOLET).encode(
            y=alt.Y("Model:N", sort="-x", title=None), x=alt.X("Accuracy:Q", scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(format="%")),
            x2=alt.X2(datum=0),
            tooltip=["Model", alt.Tooltip("Accuracy:Q", format=".2%")])
        show_chart(chart, "Out-of-fold model comparison", "comparison")
        folds = pd.DataFrame([{"Fold": str(f["fold"]), "Model": name, "Accuracy": metrics["accuracy"]}
                              for f in report["folds"] for name, metrics in f["scores"].items()])
        show_chart(alt.Chart(folds).mark_line(point=True).encode(
            x=alt.X("Fold:N"), y=alt.Y("Accuracy:Q", axis=alt.Axis(format="%"), scale=alt.Scale(zero=False)),
            color=alt.Color("Model:N", scale=alt.Scale(range=[MINT, VIOLET, CORAL])),
            tooltip=["Fold", "Model", alt.Tooltip("Accuracy:Q", format=".2%")]), "Validation stability", "folds")
        st.caption("Small differences can be noise. Grouped validation reduces same-date leakage but is not chronological validation or evidence of profitability.")
        with st.expander("Original report: historical results, not reproduced scores"):
            st.write("The original report gives CatBoost ~53.03% CV accuracy and 52.03% public leaderboard accuracy. It also lists Logistic Regression 50.95%, LightGBM 51.37% and XGBoost 50.70% in its comparison. These came from a different workflow and must not be ranked against this experiment.")
            st.warning("The supplied report describes both grouped and stratified validation. The notebook uses stratified random folds. This discrepancy is documented, not silently treated as a verified protocol.")
        st.download_button("Download evaluation evidence", path.read_bytes(), "evaluation.json", "application/json")
    with thresholds:
        st.subheader("Change the decision, see the trade-off.")
        threshold = st.slider("Positive-return probability threshold", 0, 100, 50, 1, format="%d%%", key="threshold")
        row = report["thresholds"][threshold]
        a, b, c, d = st.columns(4)
        a.metric("ACCURACY", f"{row['accuracy']:.2%}")
        b.metric("PRECISION", f"{row['precision']:.2%}")
        c.metric("RECALL", f"{row['recall']:.2%}")
        d.metric("PREDICTED POSITIVE", f"{row['predicted_positive']:.1%}")
        st.caption("A prediction is positive when probability ≥ threshold. Precision is reported as zero if no positives are predicted.")
        matrix = pd.DataFrame([
            {"Actual": "Positive", "Predicted": "Positive", "Count": row["tp"]},
            {"Actual": "Positive", "Predicted": "Zero / negative", "Count": row["fn"]},
            {"Actual": "Zero / negative", "Predicted": "Positive", "Count": row["fp"]},
            {"Actual": "Zero / negative", "Predicted": "Zero / negative", "Count": row["tn"]}])
        base = alt.Chart(matrix).encode(x=alt.X("Predicted:N"), y=alt.Y("Actual:N"), tooltip=["Actual", "Predicted", "Count"])
        heatmap = base.mark_rect(cornerRadius=5).encode(color=alt.Color("Count:Q", scale=alt.Scale(range=["#26223C", "#7257C5"]), legend=None))
        text = base.mark_text(color="white", fontSize=22).encode(text=alt.Text("Count:Q", format=","))
        show_chart(heatmap + text, "Out-of-fold confusion matrix", "confusion")
        st.dataframe(matrix, hide_index=True, width="stretch")
        curve = pd.DataFrame(report["thresholds"]).melt(id_vars="threshold", value_vars=["accuracy", "precision", "recall"], var_name="Metric", value_name="Score")
        show_chart(alt.Chart(curve).mark_line().encode(
            x=alt.X("threshold:Q", title="Decision threshold", axis=alt.Axis(format="%")),
            y=alt.Y("Score:Q", axis=alt.Axis(format="%")),
            color=alt.Color("Metric:N", scale=alt.Scale(range=[MINT, VIOLET, CORAL])),
            tooltip=["Metric", alt.Tooltip("threshold:Q", format=".0%"), alt.Tooltip("Score:Q", format=".2%")]), "Threshold sensitivity", "threshold_curve")
        st.warning("This slider explores validation predictions. Selecting a threshold here and reporting its best score would reuse validation data. Confirm any chosen threshold on a separate untouched test set.")
    with importance:
        st.subheader("What the model uses")
        st.caption(report["importance_method"] + ". Importance describes model behavior, not causality.")
        table = pd.DataFrame({"Feature": list(report["importance"]), "Importance": list(report["importance"].values())}).sort_values("Importance", ascending=False)
        show_chart(alt.Chart(table).mark_bar(color=MINT).encode(
            y=alt.Y("Feature:N", sort="-x", title=None), x=alt.X("Importance:Q", title="Relative importance (%)"),
            x2=alt.X2(datum=0),
            tooltip=["Feature", alt.Tooltip("Importance:Q", format=".2f")]), "CatBoost feature importance", "importance", height=420)
        feature = st.selectbox("Explain a feature", table.Feature.tolist())
        st.info(DESCRIPTIONS[feature])
        st.download_button("Download feature importance", table.to_csv(index=False), "feature-importance.csv", "text/csv")
    with card:
        st.markdown("#### Purpose")
        st.write("Educational classification of next-day allocation return direction. This bounded CPU experiment is a reproducible extension of the original project, not the original final GPU model.")
        st.markdown("#### Evaluation contract")
        st.write(report["validation"])
        st.write(f"Sample: {report['rows']:,} rows, selected with seed {report['seed']}; {report['date_groups']} date identifiers. Preprocessing medians and logistic scaling are fitted using each training fold only.")
        st.write("Features are calculated independently per observation. Group-relative ranks and population winsorization are omitted to avoid importing the notebook's preprocessing leakage.")
        st.dataframe(pd.DataFrame([{k: v for k, v in fold.items() if k != "scores"} for fold in report["folds"]]), hide_index=True)
        st.markdown("#### Limits")
        st.write("Date identifiers are anonymized, so this is not a forward-time backtest. Allocations may recur across dates. The bounded sample and reduced tree count limit comparison with the original report. No transaction costs, profit simulation, causal claim, calibration guarantee or statistical significance claim is made.")
        st.markdown("#### Reproducibility")
        st.json({k: report[k] for k in ["seed", "parameters", "versions", "python", "feature_sha256", "target_sha256"]})
        st.code("python scripts/evaluate.py --features /data/X_train_9xQjqvZ.csv --targets /data/y_train_Ppwhaz8.csv")
        st.markdown("**Pipeline:** Validate IDs → deterministic sample → date-group folds → row-local features → train-fold preprocessing → fit models → held-out probabilities → aggregate evidence.")


def feature_explorer(selected):
    st.subheader("One observation. Twenty days of context.")
    required = set(RETURNS + VOLUMES + ["MEDIAN_DAILY_TURNOVER"])
    if not required.issubset(selected.columns):
        st.info("This file is missing some of the 20 return or volume lags, or turnover. Use Demo dataset to try this explorer, or upload the full training feature file.")
        return
    position = st.number_input("Observation position in filtered data", 1, len(selected), 1, key="observation")
    raw = selected.iloc[[int(position) - 1]]
    st.caption(f"ROW_ID {raw.ROW_ID.iloc[0]} · Group {raw.GROUP.iloc[0]} · observed target {raw.target.iloc[0] * 10000:+.2f} bp")
    history = pd.DataFrame({"Day": list(range(-20, 0)),
                           "Return (bp)": pd.to_numeric(raw[RETURNS].iloc[0], errors="coerce").to_numpy() * 10000,
                           "Signed volume": pd.to_numeric(raw[VOLUMES].iloc[0], errors="coerce").to_numpy()})
    for field, color, key in [("Return (bp)", MINT, "observation_returns"), ("Signed volume", VIOLET, "observation_volume")]:
        show_chart(alt.Chart(history).mark_line(point=True, color=color).encode(
            x=alt.X("Day:Q", title="Lag relative to target day"), y=alt.Y(f"{field}:Q"),
            tooltip=["Day", alt.Tooltip(f"{field}:Q", format=".4f")]), field, key)
    result = engineer_features(raw).iloc[0]
    table = pd.DataFrame({"Feature": result.index, "Value": result.astype(str).values,
                          "Definition": [DESCRIPTIONS[name] for name in result.index]})
    st.dataframe(table, hide_index=True, width="stretch")
    st.caption("Historical plots show raw missing values as gaps. Feature calculations replace missing return/volume entries with zero, as documented. No target value is used to construct features.")
    st.download_button("Download this observation's features", table.to_csv(index=False), "observation-features.csv", "text/csv")
