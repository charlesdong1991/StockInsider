from insider.constants import RSI_COLS


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
