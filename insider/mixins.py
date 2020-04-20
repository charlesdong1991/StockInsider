from constants import MOVING_COLS


class BaseMixin:
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


class MovingIndicatorMixin:
    def ma(self, n=5):
        df_ma = self._df.loc[:, MOVING_COLS]
        df_ma.loc[:, "close"] = self._ma(col="close", n=n)
        return df_ma

    def md(self, n=5):
        df_md = self._df.loc[:, MOVING_COLS]
        df_md.loc[:, "close"] = self._md(col="close", n=n)
        return df_md

    def ema(self, n=5):
        df_ema = self._df.loc[:, MOVING_COLS]
        df_ema.loc[:, "close"] = self._ema(col="close", n=n)
        return df_ema

    def macd(self, n=12, m=26, k=9):
        df_macd = self._df.loc[:, MOVING_COLS]
        df_macd.loc[:, "diff"] = self._ema(col="close", n=n) - self._ema(col="close", n=m)
        df_macd.loc[:, "dea"] = self._ema(col="diff", n=k, df=df_macd)
        df_macd.loc[:, "macd"] = 2 * (df_macd["diff"] - df_macd["dea"])
        return df_macd
