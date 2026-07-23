from alpharadar.domain.entities.stock import StockInfo
from alpharadar.domain.interfaces.analyzer import FundamentalAnalyzer


class RuleBasedFundamentalAnalyzer(FundamentalAnalyzer):
    """Apply transparent MVP rules to available fundamental metrics."""

    async def analyze(self, info: StockInfo) -> float:
        scores: list[float] = []
        if info.pe_ratio is not None:
            scores.append(self._pe_score(info.pe_ratio))
        if info.eps is not None:
            scores.append(70.0 if info.eps > 0 else 20.0)
        if info.debt_to_equity is not None:
            scores.append(
                80.0
                if info.debt_to_equity < 1
                else 60.0
                if info.debt_to_equity < 2
                else 40.0
                if info.debt_to_equity < 3
                else 20.0
            )
        if info.dividend_yield is not None:
            scores.append(
                80.0
                if info.dividend_yield > 0.04
                else 60.0
                if info.dividend_yield > 0.02
                else 40.0
                if info.dividend_yield > 0
                else 30.0
            )
        return sum(scores) / len(scores) if scores else 50.0

    @staticmethod
    def _pe_score(value: float) -> float:
        if value <= 0:
            return 20.0
        return (
            80.0 if value < 15 else 60.0 if value < 25 else 40.0 if value < 40 else 20.0
        )
