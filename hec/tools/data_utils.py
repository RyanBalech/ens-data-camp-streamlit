from pathlib import Path

import numpy as np
import pandas as pd


DATE_COLUMN = "TS"
TARGET_COLUMN = "target"


def load_dataset(features_path: str | Path, target_path: str | Path) -> pd.DataFrame:
    """Load feature and target CSVs and join them safely by ROW_ID."""
    features = pd.read_csv(features_path)
    target = pd.read_csv(target_path)
    if not {"ROW_ID", "GROUP"}.issubset(features.columns) or not {"ROW_ID", TARGET_COLUMN}.issubset(target.columns):
        raise ValueError("Features need ROW_ID and GROUP; targets need ROW_ID and target.")
    if features.empty or target.empty:
        raise ValueError("Both input files must contain observations.")
    if {"target", "label"}.intersection(features.columns):
        raise ValueError("Upload the original feature file without target or label columns.")
    for frame in (features, target):
        if frame["ROW_ID"].isna().any() or frame["ROW_ID"].duplicated().any():
            raise ValueError("ROW_ID must be unique and non-missing in each file.")
    if set(features["ROW_ID"]) != set(target["ROW_ID"]):
        raise ValueError("Feature and target ROW_ID sets must match; no rows are silently dropped.")
    if features["GROUP"].isna().any():
        raise ValueError("Every observation needs an allocation GROUP.")
    target[TARGET_COLUMN] = pd.to_numeric(target[TARGET_COLUMN], errors="coerce")
    if not np.isfinite(target[TARGET_COLUMN]).all():
        raise ValueError("Targets must be finite numbers with no missing values.")
    data = features.merge(target[["ROW_ID", TARGET_COLUMN]], on="ROW_ID", how="left", validate="one_to_one")
    data["label"] = (data[TARGET_COLUMN] > 0).astype(int)
    return data


def filter_dataset(data: pd.DataFrame, group: int | None = None, label: int | None = None) -> pd.DataFrame:
    """Filter rows by allocation group and/or return label."""
    if label not in (None, 0, 1):
        raise ValueError("Return label must be 0 or 1.")
    filtered = data
    if group is not None:
        filtered = filtered[filtered["GROUP"] == group]
    if label is not None:
        filtered = filtered[filtered["label"] == label]
    return filtered.copy()
