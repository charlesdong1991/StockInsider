from insider.constants import MOVING_COLS, KDJ_COLS, RSI_COLS


class BaseMixin:
    """Base Mixins used in different Indicator Mixins"""

    def _ma(self, col, n, df=None):
        if df is None:
            df = self._df
        return df[col].rolling(n).mean()

    def _md(self, col, n, df=None):
        if df is None:
            df = self._df
        return df[col].rolling(n).std(ddof=0)

    def _ema(self, col, n, df=None):
        if df is None:
            df = self._df
        return df[col].ewm(ignore_na=False, span=n, min_periods=0, adjust=False).mean()

    def _sma(self, col, n, df=None):
        assert n != 0, "Cannot set n to 0 for SMA."

        if df is None:
            df = self._df
        ser = df[col].fillna(0)
        return ser.ewm(min_periods=0, ignore_na=False, adjust=False, alpha=1 / n).mean()


class MovingIndicatorMixin(BaseMixin):
    """Moving Indicator Mixin (移动指标混合)"""

    def ma(self, n=5):
        """Moving Average Calculation (移动平均值计算)"""
        df_ma = self._df.loc[:, MOVING_COLS]
        df_ma.loc[:, "close"] = self._ma(col="close", n=n)
        return df_ma

    def md(self, n=5):
        """Moving Deviation Calculation (移动标准差值计算)"""
        df_md = self._df.loc[:, MOVING_COLS]
        df_md.loc[:, "close"] = self._md(col="close", n=n)
        return df_md

    def ema(self, n=5):
        """Exponential Moving Average Calculation (指数移动平均值计算)"""
        df_ema = self._df.loc[:, MOVING_COLS]
        df_ema.loc[:, "close"] = self._ema(col="close", n=n)
        return df_ema

    def macd(self, n=12, m=26, k=9):
        """Moving Average Convergence Divergence Calculation (平滑异同移动平均计算)"""
        df_macd = self._df.loc[:, MOVING_COLS]
        df_macd.loc[:, "diff"] = self._ema(col="close", n=n) - self._ema(
            col="close", n=m
        )
        df_macd.loc[:, "dea"] = self._ema(col="diff", n=k, df=df_macd)
        df_macd.loc[:, "macd"] = 2 * (df_macd["diff"] - df_macd["dea"])
        return df_macd


class KDJIndicatorMixin(BaseMixin):
    """KDJ Indicator Mixin (KDJ指标混合)"""

    def kdj(self, n: int = 9, smooth_type: str = "sma"):
        if smooth_type == "sma":
            func = self._sma
        elif smooth_type == "ema":
            func = self._ema
        else:
            raise ValueError(
                "Invalid smooth average method is given, only sma and ema are allowed."
            )

        df_kdj = self._df.loc[:, KDJ_COLS]
        close_minus_low = df_kdj["close"] - df_kdj["low"].rolling(n).min()
        high_minus_low = (
            df_kdj["high"].rolling(n).max() - df_kdj["low"].rolling(n).min()
        )

        df_kdj.loc[:, "K"] = (close_minus_low / high_minus_low) * 100
        df_kdj.loc[:, "K"] = func("K", 3, df=df_kdj)
        df_kdj.loc[:, "D"] = func("K", 3, df=df_kdj)
        df_kdj.loc[:, "J"] = 3 * df_kdj["K"] - 2 * df_kdj["D"]

        # Cap it between 0 and 100 as shown in THS.
        df_kdj.loc[:, ["K", "D", "J"]] = df_kdj.loc[:, ["K", "D", "J"]].clip(0, 100)
        return df_kdj


class RSIIndicatorMixin(BaseMixin):
    """RSI and VRSI Indicator Mixin (RSI和VRSI指标混合)"""

    def _rsi(self, col: str, n: int = 6):
        df_rsi = self._df.loc[:, RSI_COLS]
        ser_shift_diff = df_rsi[col] - df_rsi[col].shift(1)

        df_rsi["shift_diff"] = ser_shift_diff.clip(lower=0)
        df_rsi["shift_diff_abs"] = ser_shift_diff.abs()
        df_rsi["rsi"] = (
            self._sma("shift_diff", n=n, df=df_rsi)
            / self._sma("shift_diff_abs", n=n, df=df_rsi)
            * 100
        )

        return df_rsi

    def rsi(self, n: int = 6):
        return self._rsi("close", n=n)

    def vrsi(self, n: int = 6):
        return self._rsi("volumn", n=n)
