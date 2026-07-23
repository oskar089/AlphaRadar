from alpharadar.infrastructure.analyzers.sentiment import TextBlobSentimentAnalyzer


async def test_symbol_sentiment_defaults_to_neutral() -> None:
    assert await TextBlobSentimentAnalyzer().analyze("AAPL") == 0.0


def test_text_sentiment_distinguishes_polarity() -> None:
    analyzer = TextBlobSentimentAnalyzer()
    positive = analyzer.analyze_text("Great earnings and excellent growth")
    negative = analyzer.analyze_text("Terrible losses and awful outlook")
    assert positive > negative
