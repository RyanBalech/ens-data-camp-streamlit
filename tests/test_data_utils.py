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


def csv_inputs(features, targets):
    from io import StringIO
    return StringIO(features), StringIO(targets)


def test_alignment_uses_ids_not_row_position_and_zero_is_negative():
    result = load_dataset(*csv_inputs("ROW_ID,GROUP\n1,1\n2,2\n", "ROW_ID,target\n2,0\n1,0.1\n"))
    assert result.label.tolist() == [1, 0]


@pytest.mark.parametrize("features,targets", [
    ("ROW_ID,GROUP\n1,1\n1,2\n", "ROW_ID,target\n1,0.2\n"),
    ("ROW_ID,GROUP\n1,1\n", "ROW_ID,target\n1,0.2\n1,0.3\n"),
    ("ROW_ID,GROUP\n,1\n", "ROW_ID,target\n1,0.2\n"),
    ("ROW_ID,GROUP\n1,1\n", "ROW_ID,target\n2,0.2\n"),
    ("ROW_ID,GROUP\n1,\n", "ROW_ID,target\n1,0.2\n"),
    ("ROW_ID,GROUP\n1,1\n", "ROW_ID,target\n1,\n"),
    ("ROW_ID,GROUP\n1,1\n", "ROW_ID,target\n1,inf\n"),
    ("ROW_ID,GROUP\n1,1\n", "ROW_ID,target\n1,invalid\n"),
    ("ROW_ID,GROUP\n", "ROW_ID,target\n"),
    ("ROW_ID,GROUP,target\n1,1,0.1\n", "ROW_ID,target\n1,0.2\n"),
])
def test_invalid_inputs_are_rejected(features, targets):
    with pytest.raises(ValueError):
        load_dataset(*csv_inputs(features, targets))


def test_filters_preserve_input_and_allow_empty_result():
    data = pd.DataFrame({"GROUP": [1, 2], "label": [0, 1]})
    before = data.copy(deep=True)
    result = filter_dataset(data, group=1, label=1)
    assert result.empty
    pd.testing.assert_frame_equal(data, before)
    copy = filter_dataset(data)
    copy.loc[0, "label"] = 1
    pd.testing.assert_frame_equal(data, before)
    with pytest.raises(ValueError):
        filter_dataset(data, label=3)
