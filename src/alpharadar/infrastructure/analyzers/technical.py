from collections.abc import Sequence
from dataclasses import dataclass
from statistics import fmean, pstdev

from alpharadar.domain.entities.stock import OHLCV, Stock
from alpharadar.domain.interfaces.analyzer import TechnicalAnalyzer


@dataclass(frozen=True)
class TechnicalIndicators:
    sma20: float | None = None
    sma50: float | None = None
    sma200: float | None = None
    ema12: float | None = None
    ema26: float | None = None
    rsi: float | None = None
    macd: float | None = None
    macd_signal: float | None = None
    macd_histogram: float | None = None
    stoch_k: float | None = None
    stoch_d: float | None = None
    bb_upper: float | None = None
    bb_middle: float | None = None
    bb_lower: float | None = None
    atr: float | None = None
    obv: float | None = None
    volume_ratio: float | None = None
    doji: bool = False
    hammer: bool = False
    bullish_engulfing: bool = False
    bearish_engulfing: bool = False


class TrendMomentumTechnicalAnalyzer(TechnicalAnalyzer):
    """Calculate deterministic pandas-ta-style indicators for the MVP."""

    async def analyze(self, stock: Stock) -> float:
        if len(stock.history) < 50:
            return 50.0

        indicators = self.calculate_indicators(stock)
        signals = self._signals(stock.history, indicators)
        if not signals:
            return 50.0

        total_weight = sum(weight for _, weight in signals)
        weighted_signal = sum(signal * weight for signal, weight in signals)
        score = 50.0 + 50.0 * weighted_signal / total_weight
        return max(0.0, min(100.0, score))

    def calculate_indicators(self, stock: Stock) -> TechnicalIndicators:
        candles = stock.history
        closes = [candle.close for candle in candles]
        highs = [candle.high for candle in candles]
        lows = [candle.low for candle in candles]
        volumes = [float(candle.volume) for candle in candles]
        macd, macd_signal = self._macd(closes)
        bb_middle, bb_upper, bb_lower = self._bollinger_bands(closes)
        patterns = self._candlestick_patterns(candles)

        return TechnicalIndicators(
            sma20=self._sma(closes, 20),
            sma50=self._sma(closes, 50),
            sma200=self._sma(closes, 200),
            ema12=self._ema(closes, 12),
            ema26=self._ema(closes, 26),
            rsi=self._rsi(closes, 14),
            macd=macd,
            macd_signal=macd_signal,
            macd_histogram=(
                macd - macd_signal
                if macd is not None and macd_signal is not None
                else None
            ),
            stoch_k=self._stochastic_k(closes, highs, lows, 14),
            stoch_d=self._stochastic_d(closes, highs, lows, 14, 3),
            bb_upper=bb_upper,
            bb_middle=bb_middle,
            bb_lower=bb_lower,
            atr=self._atr(candles, 14),
            obv=self._obv(candles),
            volume_ratio=self._volume_ratio(volumes, 20),
            doji=patterns[0],
            hammer=patterns[1],
            bullish_engulfing=patterns[2],
            bearish_engulfing=patterns[3],
        )

    @staticmethod
    def _signals(
        candles: list[OHLCV], indicators: TechnicalIndicators
    ) -> list[tuple[float, float]]:
        close = candles[-1].close
        signals: list[tuple[float, float]] = []

        def add_direction(reference: float | None, weight: float) -> None:
            if reference is None:
                return
            signal = 1.0 if close > reference else -1.0 if close < reference else 0.0
            signals.append((signal, weight))

        for reference in (
            indicators.sma20,
            indicators.sma50,
            indicators.sma200,
            indicators.ema12,
            indicators.ema26,
        ):
            add_direction(reference, 1.0)

        if indicators.rsi is not None:
            rsi_signal = (
                1.0
                if indicators.rsi < 30.0
                else -1.0
                if indicators.rsi > 70.0
                else 0.0
            )
            signals.append((rsi_signal, 1.0))

        if indicators.macd is not None and indicators.macd_signal is not None:
            macd_signal = (
                1.0
                if indicators.macd > indicators.macd_signal
                else -1.0
                if indicators.macd < indicators.macd_signal
                else 0.0
            )
            signals.append((macd_signal, 1.0))

        if indicators.stoch_k is not None:
            stoch_signal = (
                1.0
                if indicators.stoch_k < 20.0
                else -1.0
                if indicators.stoch_k > 80.0
                else 0.0
            )
            signals.append((stoch_signal, 0.75))

        if indicators.bb_lower is not None and indicators.bb_upper is not None:
            band_signal = (
                1.0
                if close < indicators.bb_lower
                else -1.0
                if close > indicators.bb_upper
                else 0.0
            )
            signals.append((band_signal, 0.75))

        if indicators.atr is not None and len(candles) > 1:
            previous_close = candles[-2].close
            latest_range = TrendMomentumTechnicalAnalyzer._true_range(
                candles[-1], previous_close
            )
            direction = (
                1.0
                if close > previous_close
                else -1.0
                if close < previous_close
                else 0.0
            )
            signals.append((direction if latest_range > indicators.atr else 0.0, 0.5))

        if len(candles) > 1:
            previous_obv = TrendMomentumTechnicalAnalyzer._obv(candles[:-1])
            if indicators.obv is not None and previous_obv is not None:
                obv_signal = (
                    1.0
                    if indicators.obv > previous_obv
                    else -1.0
                    if indicators.obv < previous_obv
                    else 0.0
                )
                signals.append((obv_signal, 0.75))

            if indicators.volume_ratio is not None and indicators.volume_ratio > 1.5:
                signals.append((direction, 0.75))

        if indicators.hammer or indicators.bullish_engulfing:
            signals.append((1.0, 1.0))
        if indicators.bearish_engulfing:
            signals.append((-1.0, 1.0))
        if indicators.doji:
            signals.append((0.0, 0.5))
        return signals

    @staticmethod
    def _sma(values: Sequence[float], period: int) -> float | None:
        if len(values) < period:
            return None
        return fmean(values[-period:])

    @classmethod
    def _ema(cls, values: Sequence[float], period: int) -> float | None:
        series = cls._ema_series(values, period)
        return series[-1] if series else None

    @staticmethod
    def _ema_series(values: Sequence[float], period: int) -> list[float | None]:
        if len(values) < period:
            return [None] * len(values)

        result: list[float | None] = [None] * (period - 1)
        current = fmean(values[:period])
        result.append(current)
        multiplier = 2.0 / (period + 1.0)
        for value in values[period:]:
            current = (value - current) * multiplier + current
            result.append(current)
        return result

    @staticmethod
    def _rsi(values: Sequence[float], period: int) -> float | None:
        if len(values) <= period:
            return None

        changes = [
            current - previous
            for previous, current in zip(values, values[1:], strict=False)
        ]
        gains = [max(change, 0.0) for change in changes[:period]]
        losses = [max(-change, 0.0) for change in changes[:period]]
        average_gain = fmean(gains)
        average_loss = fmean(losses)
        for change in changes[period:]:
            average_gain = (average_gain * (period - 1) + max(change, 0.0)) / period
            average_loss = (average_loss * (period - 1) + max(-change, 0.0)) / period

        if average_loss == 0.0:
            return 100.0 if average_gain > 0.0 else 50.0
        return 100.0 - 100.0 / (1.0 + average_gain / average_loss)

    @classmethod
    def _macd(
        cls, values: Sequence[float]
    ) -> tuple[float | None, float | None]:
        fast = cls._ema_series(values, 12)
        slow = cls._ema_series(values, 26)
        macd_values = [
            fast_value - slow_value
            for fast_value, slow_value in zip(fast, slow, strict=True)
            if fast_value is not None and slow_value is not None
        ]
        if not macd_values:
            return None, None
        signal_values = cls._ema_series(macd_values, 9)
        signal = signal_values[-1] if signal_values else None
        return macd_values[-1], signal

    @staticmethod
    def _stochastic_k(
        closes: Sequence[float],
        highs: Sequence[float],
        lows: Sequence[float],
        period: int,
    ) -> float | None:
        if len(closes) < period:
            return None
        highest = max(highs[-period:])
        lowest = min(lows[-period:])
        spread = highest - lowest
        return 50.0 if spread == 0.0 else (closes[-1] - lowest) / spread * 100.0

    @classmethod
    def _stochastic_d(
        cls,
        closes: Sequence[float],
        highs: Sequence[float],
        lows: Sequence[float],
        period: int,
        smooth: int,
    ) -> float | None:
        if len(closes) < period + smooth - 1:
            return None
        values = [
            cls._stochastic_k(
                closes[:index], highs[:index], lows[:index], period
            )
            for index in range(period, len(closes) + 1)
        ]
        valid = [value for value in values if value is not None]
        return fmean(valid[-smooth:]) if len(valid) >= smooth else None

    @staticmethod
    def _bollinger_bands(
        values: Sequence[float], period: int = 20, deviations: float = 2.0
    ) -> tuple[float | None, float | None, float | None]:
        if len(values) < period:
            return None, None, None
        window = values[-period:]
        middle = fmean(window)
        deviation = pstdev(window)
        return middle, middle + deviations * deviation, middle - deviations * deviation

    @classmethod
    def _atr(cls, candles: Sequence[OHLCV], period: int) -> float | None:
        if len(candles) < period:
            return None
        true_ranges = [cls._true_range(candles[0], None)]
        true_ranges.extend(
            cls._true_range(candle, candles[index - 1].close)
            for index, candle in enumerate(candles[1:], start=1)
        )
        return cls._rma(true_ranges, period)

    @staticmethod
    def _true_range(candle: OHLCV, previous_close: float | None) -> float:
        if previous_close is None:
            return candle.high - candle.low
        return max(
            candle.high - candle.low,
            abs(candle.high - previous_close),
            abs(candle.low - previous_close),
        )

    @staticmethod
    def _rma(values: Sequence[float], period: int) -> float | None:
        if len(values) < period:
            return None
        current = fmean(values[:period])
        for value in values[period:]:
            current = (current * (period - 1) + value) / period
        return current

    @staticmethod
    def _obv(candles: Sequence[OHLCV]) -> float | None:
        if not candles:
            return None
        current = 0.0
        for previous, candle in zip(candles, candles[1:], strict=False):
            if candle.close > previous.close:
                current += candle.volume
            elif candle.close < previous.close:
                current -= candle.volume
        return current

    @staticmethod
    def _volume_ratio(values: Sequence[float], period: int) -> float | None:
        if len(values) < period:
            return None
        average = fmean(values[-period:])
        return values[-1] / average if average else None

    @staticmethod
    def _candlestick_patterns(
        candles: Sequence[OHLCV],
    ) -> tuple[bool, bool, bool, bool]:
        if not candles:
            return False, False, False, False

        current = candles[-1]
        current_body = abs(current.close - current.open)
        current_range = current.high - current.low
        upper_shadow = current.high - max(current.open, current.close)
        lower_shadow = min(current.open, current.close) - current.low
        doji = current_range > 0.0 and current_body <= current_range * 0.1
        hammer = (
            current_body > 0.0
            and current_range > 0.0
            and current_body <= current_range * 0.4
            and lower_shadow >= current_body * 2.0
            and upper_shadow <= current_body
        )

        if len(candles) < 2:
            return doji, hammer, False, False

        previous = candles[-2]
        bullish_engulfing = (
            previous.close < previous.open
            and current.close > current.open
            and current.open <= previous.close
            and current.close >= previous.open
        )
        bearish_engulfing = (
            previous.close > previous.open
            and current.close < current.open
            and current.open >= previous.close
            and current.close <= previous.open
        )
        return doji, hammer, bullish_engulfing, bearish_engulfing


TechnicalAnalyzerImpl = TrendMomentumTechnicalAnalyzer
