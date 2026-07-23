import math

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ApiModel(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)


class PositionCreate(ApiModel):
    symbol: str = Field(min_length=1, max_length=10)
    quantity: int = Field(gt=0)
    avg_buy_price: float = Field(gt=0)

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        normalized = value.strip().upper()
        if not normalized:
            raise ValueError("symbol must not be blank")
        return normalized

    @field_validator("avg_buy_price")
    @classmethod
    def finite_price(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("price must be finite")
        return value


class PositionResponse(PositionCreate):
    id: int
    current_price: float


class StockResponse(ApiModel):
    symbol: str
    name: str
    exchange: str


class AnalysisScoresResponse(ApiModel):
    technical: float
    fundamental: float
    sentiment: float
    final_score: float


class RecommendationResponse(ApiModel):
    symbol: str
    action: str
    score: float
    confidence: float
    reasoning: str
    scores: AnalysisScoresResponse
