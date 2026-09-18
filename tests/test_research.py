import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from hec.tools.research import engineer_features, classification_metrics, RETURNS, VOLUMES


def test_features_known_constant_history_and_target_independence():
    data = pd.DataFrame({**{c: [0.01] for c in RETURNS}, **{c: [2.0] for c in VOLUMES},
                         "GROUP": [1], "MEDIAN_DAILY_TURNOVER": [0.2], "target": [100.0]})
    first = engineer_features(data)
    assert first.mean_ret.iloc[0] == pytest.approx(0.01)
    assert first.ewma_ret.iloc[0] == pytest.approx(0.01)
    assert first.momentum.iloc[0] == pytest.approx(0)
    assert first.max_drawdown.iloc[0] == 0
    assert first.win_rate.iloc[0] == 1
    assert first.return_volume_corr.iloc[0] == 0
    data["target"] = -100
    pd.testing.assert_frame_equal(first, engineer_features(data))


def test_drawdown_includes_initial_capital_and_missing_values_are_finite():
    data = pd.DataFrame({**{c: [0.0] for c in RETURNS}, **{c: [np.nan] for c in VOLUMES},
                         "GROUP": [1], "MEDIAN_DAILY_TURNOVER": [np.nan]})
    data["RET_20"] = -0.1
    result = engineer_features(data)
    assert result.max_drawdown.iloc[0] == pytest.approx(-0.1)
    assert result.mean_volume.iloc[0] == 0
    assert np.isnan(result.turnover.iloc[0])
    with pytest.raises(ValueError):
        engineer_features(data.drop(columns="RET_1"))


def test_confusion_metrics_and_threshold_boundaries():
    result = classification_metrics([0, 0, 1, 1], [0.1, 0.8, 0.4, 0.9])
    assert [result[k] for k in ["tp", "tn", "fp", "fn"]] == [1, 1, 1, 1]
    assert result["f1"] == 0.5
    assert classification_metrics([0, 1], [0.3, 0.8], 0)["predicted_positive"] == 1
    none = classification_metrics([0, 1], [0.3, 0.8], 1)
    assert none["precision"] == none["recall"] == none["f1"] == 0
    assert classification_metrics([1], [0.5], 0.5)["tp"] == 1


@pytest.mark.parametrize("y,p,t", [([], [], .5), ([0], [.1, .2], .5), ([2], [.1], .5),
                                  ([0], [np.nan], .5), ([0], [1.1], .5), ([0], [.1], -1)])
def test_invalid_metrics_rejected(y, p, t):
    with pytest.raises(ValueError):
        classification_metrics(y, p, t)


def test_committed_evidence_is_consistent():
    evidence = json.loads((Path(__file__).parents[1] / "results/evaluation.json").read_text())
    assert sum(f["validation_rows"] for f in evidence["folds"]) == evidence["rows"]
    assert all(f["overlapping_dates"] == 0 for f in evidence["folds"])
    for row in evidence["thresholds"]:
        assert sum(row[k] for k in ["tp", "tn", "fp", "fn"]) == evidence["rows"]
        assert row["accuracy"] == pytest.approx((row["tp"] + row["tn"]) / evidence["rows"])
    assert evidence["scores"]["CatBoost"] == evidence["thresholds"][50]
    assert sum(evidence["importance"].values()) == pytest.approx(100)
