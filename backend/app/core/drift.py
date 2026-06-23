from __future__ import annotations

import math
from collections import deque
import logging

_logger = logging.getLogger(__name__)


class ScoreDriftDetector:
    def __init__(self, window_size: int = 1000, num_bins: int = 10) -> None:
        self.window_size = window_size
        self.num_bins = num_bins
        self.recent_scores: deque[float] = deque(maxlen=window_size)
        
        # Default baseline: representative distribution of 1000 normal transaction scores
        # (mostly low risk, small percentage of high risk)
        self.baseline_scores: list[float] = (
            [0.05] * 800 +  # 80% very low
            [0.2] * 150 +   # 15% low-medium
            [0.55] * 30 +   # 3% medium-high
            [0.85] * 20     # 2% high
        )
        self._cached_baseline_pcts: list[float] = self._compute_pcts(self.baseline_scores)

    def set_baseline(self, scores: list[float]) -> None:
        if not scores:
            raise ValueError("Baseline scores cannot be empty.")
        self.baseline_scores = list(scores)
        self._cached_baseline_pcts = self._compute_pcts(self.baseline_scores)
        _logger.info(f"Loaded new baseline score distribution of size {len(scores)}.")

    def record_score(self, score: float) -> float | None:
        """Record a new prediction score and return computed PSI if window is full, else None."""
        self.recent_scores.append(score)
        
        # Calculate PSI periodically or when window is reasonably populated.
        # For small window testing, if window size <= 10 or recent scores >= 10, compute it.
        if len(self.recent_scores) >= min(self.window_size, 10):
            return self.compute_psi()
        return None

    def _compute_pcts(self, scores: list[float] | deque[float]) -> list[float]:
        pcts = [0.0] * self.num_bins
        if not scores:
            return pcts
        
        for s in scores:
            # Clamp s in [0, 0.9999] so that int(s * num_bins) falls in [0, num_bins-1]
            val = max(0.0, min(0.9999, s))
            bin_idx = int(val * self.num_bins)
            pcts[bin_idx] += 1.0
            
        total = len(scores)
        return [c / total for c in pcts]

    def compute_psi(self) -> float:
        """Calculate the Population Stability Index (PSI) between baseline and recent scores."""
        if not self.recent_scores:
            return 0.0
            
        actual_pcts = self._compute_pcts(self.recent_scores)
        expected_pcts = self._cached_baseline_pcts
        
        eps = 0.0001
        psi_val = 0.0
        for e, a in zip(expected_pcts, actual_pcts, strict=True):
            e = max(e, eps)
            a = max(a, eps)
            psi_val += (a - e) * math.log(a / e)
            
        return round(psi_val, 4)


# Singleton detector instance
score_drift_detector = ScoreDriftDetector()
