from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class Action(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass(frozen=True)
class AnalysisScores:
    technical: float  # 0-100
    fundamental: float  # 0-100
    sentiment: float  # -1 to +1
    final_score: float | None = None


@dataclass
class Recommendation:
    symbol: str
    action: Action
    score: float
    confidence: float
    reasoning: str
    scores: AnalysisScores | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = True
