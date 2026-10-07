"""Pure research calculations shared by offline evaluation and the app."""
import numpy as np
import pandas as pd

RETURNS = [f"RET_{i}" for i in range(20, 0, -1)]
VOLUMES = [f"SIGNED_VOLUME_{i}" for i in range(20, 0, -1)]
DESCRIPTIONS = {
    "mean_ret": "Mean return over the 20-day window.",
    "volatility": "Sample standard deviation of the 20 historical returns.",
    "momentum": "Sum of the latest five returns minus the earliest five.",
    "ewma_ret": "Weighted mean return, with span 10 and larger weights on recent days.",
    "max_drawdown": "Worst decline from a previous peak along the compounded history.",
    "win_rate": "Fraction of historical days with a positive return.",
    "mean_volume": "Mean signed-volume measure over the historical window.",
    "volume_volatility": "Sample standard deviation of signed volume.",
    "return_volume_corr": "Within-observation correlation between return and signed volume.",
    "turnover": "Median daily turnover supplied by the challenge.",
    "GROUP": "Anonymized allocation family, treated as a category.",
}


def engineer_features(data):
    """Row-local features; no population statistics or target values are used.

    Missing/nonfinite return and volume entries use zero, matching the original
    notebook convention. Turnover stays missing for fold-fitted median imputation.
    Group-relative ranks/clipping are deliberately omitted from this new experiment.
    """
    missing = set(RETURNS + VOLUMES + ["GROUP", "MEDIAN_DAILY_TURNOVER"]) - set(data.columns)
    if missing:
        raise ValueError("Missing required feature columns: " + ", ".join(sorted(missing)))
    r = data[RETURNS].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0).to_numpy()
    v = data[VOLUMES].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0).to_numpy()
    weights = (1 - 2 / 11) ** np.arange(19, -1, -1)
    weights /= weights.sum()
    wealth = np.cumprod(1 + r, axis=1)
    peaks = np.maximum.accumulate(np.column_stack([np.ones(len(r)), wealth]), axis=1)[:, 1:]
    rc, vc = r - r.mean(axis=1, keepdims=True), v - v.mean(axis=1, keepdims=True)
    result = pd.DataFrame({
        "mean_ret": r.mean(axis=1), "volatility": r.std(axis=1, ddof=1),
        "momentum": r[:, -5:].sum(axis=1) - r[:, :5].sum(axis=1),
        "ewma_ret": r @ weights,
        "max_drawdown": ((wealth - peaks) / np.maximum(peaks, 1e-12)).min(axis=1),
        "win_rate": (r > 0).mean(axis=1), "mean_volume": v.mean(axis=1),
        "volume_volatility": v.std(axis=1, ddof=1),
        "return_volume_corr": (rc * vc).mean(axis=1) / (rc.std(axis=1) * vc.std(axis=1) + 1e-12),
        "turnover": pd.to_numeric(data.MEDIAN_DAILY_TURNOVER, errors="coerce").to_numpy(),
        "GROUP": data.GROUP.astype(str).to_numpy(),
    }, index=data.index)
    return result.replace([np.inf, -np.inf], np.nan)


def classification_metrics(y, probability, threshold=0.5):
    y, probability = np.asarray(y), np.asarray(probability, dtype=float)
    if y.ndim != 1 or probability.ndim != 1 or len(y) == 0 or y.shape != probability.shape or not np.isin(y, [0, 1]).all():
        raise ValueError("Non-empty aligned binary labels and probabilities are required.")
    if not np.isfinite(probability).all() or ((probability < 0) | (probability > 1)).any() or not 0 <= threshold <= 1:
        raise ValueError("Probabilities and threshold must be between zero and one.")
    predicted = probability >= threshold
    tp = int(((y == 1) & predicted).sum())
    tn = int(((y == 0) & ~predicted).sum())
    fp = int(((y == 0) & predicted).sum())
    fn = int(((y == 1) & ~predicted).sum())
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {"threshold": float(threshold), "tp": tp, "tn": tn, "fp": fp, "fn": fn,
            "accuracy": (tp + tn) / len(y), "precision": precision, "recall": recall,
            "f1": 2 * precision * recall / (precision + recall) if precision + recall else 0.0,
            "predicted_positive": float(predicted.mean())}
