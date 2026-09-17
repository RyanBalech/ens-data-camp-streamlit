from pathlib import Path

import pandas as pd


DATE_COLUMN = "TS"
TARGET_COLUMN = "target"


def load_dataset(features_path: str | Path, target_path: str | Path) -> pd.DataFrame:
    """Load feature and target CSVs and join them safely by ROW_ID."""
    features = pd.read_csv(features_path)
    target = pd.read_csv(target_path)
    required = {"ROW_ID"}
    if not required.issubset(features.columns) or not required.union({TARGET_COLUMN}).issubset(target.columns):
        raise ValueError("Input files must contain ROW_ID; target file must also contain target")
    data = features.merge(target[["ROW_ID", TARGET_COLUMN]], on="ROW_ID", how="inner", validate="one_to_one")
    data["label"] = (data[TARGET_COLUMN] > 0).astype(int)
    return data


def filter_dataset(data: pd.DataFrame, group: int | None = None, label: int | None = None) -> pd.DataFrame:
    """Filter rows by allocation group and/or return label."""
    filtered = data
    if group is not None:
        filtered = filtered[filtered["GROUP"] == group]
    if label is not None:
        filtered = filtered[filtered["label"] == label]
    return filtered.copy()
