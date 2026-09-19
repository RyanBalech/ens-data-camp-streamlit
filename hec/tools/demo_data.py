"""Deterministic synthetic data for the app's self-contained demonstration."""
import numpy as np
import pandas as pd

from hec.tools.research import RETURNS, VOLUMES


def make_demo_dataset(rows: int = 360, seed: int = 20260918) -> pd.DataFrame:
    """Create a realistic-looking, explicitly synthetic full-schema dataset."""
    if rows < 40:
        raise ValueError("The demo needs at least 40 observations.")

    rng = np.random.default_rng(seed)
    groups = np.resize(np.array([1, 2, 3, 4]), rows)
    latent = rng.normal(0, 1, rows)
    day_profile = np.linspace(-0.0004, 0.0005, 20)
    returns = (
        rng.normal(0, 0.0065, (rows, 20))
        + latent[:, None] * np.linspace(0.0003, 0.0012, 20)
        + day_profile
        + (groups[:, None] - 2.5) * 0.00012
    )
    volumes = (
        rng.normal(0, 0.75, (rows, 20))
        + latent[:, None] * 0.18
        + np.sign(returns) * 0.12
    )
    target = (
        0.10 * returns[:, -5:].mean(axis=1)
        + 0.00008 * (groups - 2.5)
        + rng.normal(0, 0.006, rows)
    )

    data = pd.DataFrame({
        "ROW_ID": np.arange(1, rows + 1),
        "GROUP": groups,
        "TS": [f"DEMO_{index // 4:03d}" for index in range(rows)],
        "MEDIAN_DAILY_TURNOVER": rng.lognormal(-2.4, 0.45, rows),
    })
    for index, name in enumerate(RETURNS):
        data[name] = returns[:, index]
    for index, name in enumerate(VOLUMES):
        data[name] = volumes[:, index]
    data["target"] = target
    data["label"] = (target > 0).astype(int)
    return data
