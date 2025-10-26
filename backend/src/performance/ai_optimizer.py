import time
from typing import Dict

class AIOptimizer:
    def analyze_complexity(self, n_values: list, times: list) -> Dict[str, str]:
        if len(n_values) < 3:
            return {"complexity": "O(n)", "reason": "insufficient data"}
        ratios = [times[i+1]/times[i] for i in range(len(times)-1)]
        if all(1.0 <= r <= 1.3 for r in ratios):
            return {"complexity": "O(n)", "reason": "linear growth"}
        elif any(r > 2.0 for r in ratios):
            return {"complexity": "O(n²)", "reason": "super-linear growth"}
        else:
            return {"complexity": "O(n log n)", "reason": "moderate growth"}