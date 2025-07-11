from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
import pandas as pd
import numpy as np
from profiler.data_model import ColumnProfile, DataType
from collections import Counter
import json

@dataclass
class CategoryStats:
    """Typed model for categorical column statistics."""
    column_name: str
    count: int
    null_count: int
    null_percent: float
    unique_count: int
    cardinality_ratio: float
    mode: Any
    mode_freq: int
    mode_percent: float
    is_high_cardinality: bool
    frequencies: Dict[Any, int] = field(default_factory=dict)
    frequencies_percent: Dict[Any, float] = field(default_factory=dict)
    entropy: Optional[float] = None
    is_uniform: Optional[bool] = None
    cardinality_warning: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CategoryStats':
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "column_name": self.column_name,
            "count": self.count,
            "null_count": self.null_count,
            "null_percent": self.null_percent,
            "unique_count": self.unique_count,
            "cardinality_ratio": self.cardinality_ratio,
            "mode": self.mode,
            "mode_freq": self.mode_freq,
            "mode_percent": self.mode_percent,
            "is_high_cardinality": self.is_high_cardinality,
            "frequencies": self.frequencies,
            "frequencies_percent": self.frequencies_percent,
            "entropy": self.entropy,
            "is_uniform": self.is_uniform,
            "cardinality_warning": self.cardinality_warning,
        }

    def get_top_n_categories(self, n: int = 5) -> Dict[Any, int]:
        return dict(sorted(self.frequencies.items(), key=lambda x: x[1], reverse=True)[:n])


class CategoricalProfiler:
    """Profiles categorical columns to calculate common statistics."""

    @staticmethod
    def profile_series(series: pd.Series,
                       max_categories: int = 50,
                       cardinality_threshold: float = 0.5,
                       use_typed_model: bool = False) -> Union[Dict[str, Any], CategoryStats]:

        count = len(series)
        null_count = series.isna().sum()
        null_percent = (null_count / count * 100) if count > 0 else 0
        valid_values = series.dropna()

        if len(valid_values) == 0:
            result = {
                "column_name": series.name,
                "count": count,
                "null_count": null_count,
                "null_percent": null_percent,
                "unique_count": 0,
                "cardinality_ratio": 0,
                "mode": None,
                "mode_freq": 0,
                "mode_percent": 0,
                "is_high_cardinality": False,
                "frequencies": {},
                "frequencies_percent": {},
                "entropy": None,
                "is_uniform": None,
                "cardinality_warning": None
            }
            return CategoryStats.from_dict(result) if use_typed_model else result

        unique_count = valid_values.nunique()
        cardinality_ratio = unique_count / count if count > 0 else 0
        is_high_cardinality = cardinality_ratio > cardinality_threshold
        cardinality_warning = (
            f"High cardinality: {unique_count} unique values "
            f"({cardinality_ratio:.2%}). Frequencies capped at {max_categories}."
        ) if is_high_cardinality else None

        value_counts = valid_values.value_counts()
        mode = value_counts.index[0] if not value_counts.empty else None
        mode_freq = value_counts.iloc[0] if not value_counts.empty else 0
        mode_percent = (mode_freq / count * 100) if count > 0 else 0

        frequencies = value_counts.head(max_categories).to_dict()
        frequencies_percent = {k: (v / count * 100) for k, v in frequencies.items()}

        entropy, is_uniform = None, None
        if unique_count <= 1000:
            probs = np.array(list(value_counts / len(valid_values)))
            entropy = -np.sum(probs * np.log2(probs))
            expected_prob = 1.0 / unique_count
            prob_deviation = np.abs(probs - expected_prob).mean()
            is_uniform = prob_deviation < 0.1

        result = {
            "column_name": series.name,
            "count": count,
            "null_count": null_count,
            "null_percent": null_percent,
            "unique_count": unique_count,
            "cardinality_ratio": cardinality_ratio,
            "mode": mode,
            "mode_freq": mode_freq,
            "mode_percent": mode_percent,
            "is_high_cardinality": is_high_cardinality,
            "frequencies": frequencies,
            "frequencies_percent": frequencies_percent,
            "entropy": entropy,
            "is_uniform": is_uniform,
            "cardinality_warning": cardinality_warning
        }

        return CategoryStats.from_dict(result) if use_typed_model else result
