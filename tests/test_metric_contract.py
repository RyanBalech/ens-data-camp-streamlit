import numpy as np
import pytest
from hec.tools.research import classification_metrics

@pytest.mark.parametrize("labels,probabilities", [(0, 0.5), ([[0, 1]], [[0.2, 0.8]])])
def test_metrics_require_one_dimensional_samples(labels, probabilities):
    with pytest.raises(ValueError, match="aligned binary"):
        classification_metrics(labels, probabilities)
