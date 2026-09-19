import pandas as pd
import pytest

from hec.tools.demo_data import make_demo_dataset
from hec.tools.research import RETURNS, VOLUMES


def test_demo_is_deterministic_balanced_and_complete():
    first = make_demo_dataset()
    second = make_demo_dataset()

    pd.testing.assert_frame_equal(first, second)
    assert len(first) == 360
    assert set(RETURNS + VOLUMES + ["ROW_ID", "GROUP", "TS", "MEDIAN_DAILY_TURNOVER", "target", "label"]) <= set(first)
    assert first["ROW_ID"].is_unique
    assert first["GROUP"].nunique() == 4
    assert 0.35 < first["label"].mean() < 0.65
    assert first[RETURNS + VOLUMES].notna().all().all()


def test_demo_requires_enough_rows_for_useful_charts():
    with pytest.raises(ValueError, match="at least 40"):
        make_demo_dataset(39)
