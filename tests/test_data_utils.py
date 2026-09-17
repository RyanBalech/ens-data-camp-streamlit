import pandas as pd
import pytest

from hec.tools.data_utils import filter_dataset, load_dataset


def test_load_dataset_joins_and_creates_label(tmp_path):
    features = tmp_path / "features.csv"
    target = tmp_path / "target.csv"
    pd.DataFrame({"ROW_ID": [1, 2], "GROUP": [1, 2]}).to_csv(features, index=False)
    pd.DataFrame({"ROW_ID": [1, 2], "target": [0.2, -0.1]}).to_csv(target, index=False)

    result = load_dataset(features, target)

    assert result["label"].tolist() == [1, 0]


def test_load_dataset_rejects_missing_columns(tmp_path):
    features = tmp_path / "features.csv"
    target = tmp_path / "target.csv"
    pd.DataFrame({"wrong": [1]}).to_csv(features, index=False)
    pd.DataFrame({"ROW_ID": [1], "target": [0.2]}).to_csv(target, index=False)

    with pytest.raises(ValueError):
        load_dataset(features, target)


def test_filter_dataset_by_group_and_label():
    data = pd.DataFrame({"GROUP": [1, 1, 2], "label": [1, 0, 1]})

    result = filter_dataset(data, group=1, label=1)

    assert len(result) == 1
    assert result.iloc[0]["GROUP"] == 1
