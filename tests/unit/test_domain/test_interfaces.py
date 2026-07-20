import pytest

from alpharadar.domain.interfaces.data_provider import DataProvider
from alpharadar.domain.interfaces.analyzer import (
    TechnicalAnalyzer,
    FundamentalAnalyzer,
    SentimentAnalyzer,
)
from alpharadar.domain.interfaces.notifier import Notifier


def test_data_provider_is_abstract():
    with pytest.raises(TypeError):
        DataProvider()


def test_notifier_is_abstract():
    with pytest.raises(TypeError):
        Notifier()


def test_technical_analyzer_is_abstract():
    with pytest.raises(TypeError):
        TechnicalAnalyzer()


def test_fundamental_analyzer_is_abstract():
    with pytest.raises(TypeError):
        FundamentalAnalyzer()


def test_sentiment_analyzer_is_abstract():
    with pytest.raises(TypeError):
        SentimentAnalyzer()
