from alpharadar.domain.entities.recommendation import (
    Recommendation,
    Action,
    AnalysisScores,
)


def test_analysis_scores_creation():
    scores = AnalysisScores(technical=75.0, fundamental=60.0, sentiment=0.3)
    assert scores.technical == 75.0
    assert scores.final_score is None


def test_recommendation_creation():
    rec = Recommendation(
        symbol="AAPL",
        action=Action.BUY,
        score=78.5,
        confidence=0.82,
        reasoning="Strong technicals, solid fundamentals, positive sentiment",
    )
    assert rec.action == Action.BUY
    assert rec.score == 78.5


def test_action_enum():
    assert Action.BUY.value == "BUY"
    assert Action.SELL.value == "SELL"
    assert Action.HOLD.value == "HOLD"
