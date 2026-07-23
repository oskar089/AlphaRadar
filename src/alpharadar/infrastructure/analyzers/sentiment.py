from textblob import TextBlob

from alpharadar.domain.interfaces.analyzer import SentimentAnalyzer


class TextBlobSentimentAnalyzer(SentimentAnalyzer):
    """TextBlob adapter; headline acquisition is intentionally outside the MVP."""

    async def analyze(self, symbol: str) -> float:
        del symbol
        return 0.0

    def analyze_text(self, text: str) -> float:
        return float(TextBlob(text).sentiment.polarity)
