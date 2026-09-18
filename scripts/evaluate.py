"""Run a bounded, date-grouped CPU experiment and export aggregate evidence."""
import argparse
import hashlib
import json
import platform
from importlib.metadata import version
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.model_selection import GroupKFold
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from hec.tools.data_utils import load_dataset
from hec.tools.research import engineer_features, classification_metrics


def digest(path):
    with open(path, "rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest() if hasattr(hashlib, "file_digest") else _digest(source)


def _digest(source):
    result = hashlib.sha256()
    for chunk in iter(lambda: source.read(1024 * 1024), b""):
        result.update(chunk)
    return result.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--features", required=True)
    parser.add_argument("--targets", required=True)
    parser.add_argument("--rows", type=int, default=60000)
    parser.add_argument("--output", default="results/evaluation.json")
    args = parser.parse_args()
    data = load_dataset(args.features, args.targets)
    if "TS" not in data or data.TS.isna().any():
        raise ValueError("Non-missing TS date groups are required.")
    data = data.sample(n=min(args.rows, len(data)), random_state=42).sort_values("ROW_ID").reset_index(drop=True)
    features, y = engineer_features(data), data.label.to_numpy()
    columns = [col for col in features if col != "GROUP"]
    predictions = {name: np.zeros(len(y)) for name in ["CatBoost", "Logistic regression", "Training-majority baseline"]}
    folds, importances = [], []
    for number, (train, valid) in enumerate(GroupKFold(n_splits=3).split(features, y, data.TS), 1):
        assert set(data.TS.iloc[train]).isdisjoint(data.TS.iloc[valid])
        xtrain, xvalid = features.iloc[train].copy(), features.iloc[valid].copy()
        medians = xtrain[columns].median().fillna(0)
        xtrain[columns] = xtrain[columns].fillna(medians)
        xvalid[columns] = xvalid[columns].fillna(medians)
        model = CatBoostClassifier(iterations=200, depth=5, learning_rate=0.05,
                                   l2_leaf_reg=8, random_seed=42, thread_count=4,
                                   loss_function="Logloss", verbose=False, allow_writing_files=False)
        model.fit(xtrain, y[train], cat_features=["GROUP"])
        predictions["CatBoost"][valid] = model.predict_proba(xvalid)[:, 1]
        importances.append(model.feature_importances_)
        preprocessing = ColumnTransformer([
            ("numeric", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), columns),
            ("category", OneHotEncoder(handle_unknown="ignore"), ["GROUP"])])
        linear = make_pipeline(preprocessing, LogisticRegression(max_iter=500, random_state=42))
        linear.fit(xtrain, y[train])
        predictions["Logistic regression"][valid] = linear.predict_proba(xvalid)[:, 1]
        predictions["Training-majority baseline"][valid] = float(y[train].mean() >= 0.5)
        fold = {"fold": number, "train_rows": len(train), "validation_rows": len(valid),
                "train_dates": int(data.TS.iloc[train].nunique()), "validation_dates": int(data.TS.iloc[valid].nunique()),
                "overlapping_dates": 0,
                "scores": {name: classification_metrics(y[valid], p[valid]) for name, p in predictions.items()}}
        folds.append(fold)
        print(f"Fold {number}: CatBoost {fold['scores']['CatBoost']['accuracy']:.4%}", flush=True)
    artifact = {
        "schema_version": 1, "experiment": f"date-grouped-cpu-{len(data)}-v1",
        "rows": len(data), "date_groups": int(data.TS.nunique()), "seed": 42,
        "validation": "3-fold GroupKFold on TS; every sampled row predicted once out of fold",
        "feature_sha256": digest(args.features), "target_sha256": digest(args.targets),
        "python": platform.python_version(),
        "versions": {name: version(name) for name in ["catboost", "scikit-learn", "numpy", "pandas", "scipy"]},
        "parameters": {"iterations": 200, "depth": 5, "learning_rate": 0.05, "l2_leaf_reg": 8, "thread_count": 4},
        "folds": folds,
        "scores": {name: classification_metrics(y, p) for name, p in predictions.items()},
        "thresholds": [classification_metrics(y, predictions["CatBoost"], t / 100) for t in range(101)],
        "importance_method": "Mean CatBoost PredictionValuesChange across three fitted folds; not SHAP",
        "importance": dict(zip(features.columns, np.mean(importances, axis=0).tolist())),
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Saved {output}", flush=True)


if __name__ == "__main__":
    main()
