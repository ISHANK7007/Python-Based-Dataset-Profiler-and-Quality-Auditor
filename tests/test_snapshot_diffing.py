from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Union

class DriftSeverity(Enum):
    NONE = "none"           # No significant drift
    MINOR = "minor"         # Minor drift, within acceptable thresholds
    MAJOR = "major"         # Major drift, requires attention
    CRITICAL = "critical"   # Critical drift, immediate action needed

@dataclass
class DriftPoint:
    """Represents a single point in the drift timeline."""
    snapshot_id: str
    timestamp: datetime
    severity: DriftSeverity
    score: float  # Normalized drift score (0-1)
    metrics: Dict[str, float]  # Individual metric drift scores
    column_details: Dict[str, Dict]  # Column-specific drift details
    
@dataclass
class DriftTimeline:
    """A collection of drift points forming a timeline."""
    dataset_id: str
    points: List[DriftPoint]
    start_date: datetime
    end_date: datetime
    metadata: Dict = None