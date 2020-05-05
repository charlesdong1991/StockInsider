from typing import Union

import pandas as pd

from insider.constants import VOLUMN_VOLS


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

    def _sma(self, n, col=None, df=None, use_ser: Union[bool, pd.Series] = False):
        """Calculate SMA indicator

        if use_ser is assigned with a pandas.Series, then will use it to calculate
        SMA and ignore other given data, default is False which will use the default
        dataset.
        """
        assert n != 0, "Cannot set n to 0 for SMA."

        if df is None:
            df = self._df

        if isinstance(use_ser, pd.Series):
            ser = use_ser.fillna(0)
        elif use_ser is False:
            ser = df[col].fillna(0)
        else:
            raise ValueError("Only False or a Series is allowed for user_ser.")
        return ser.ewm(min_periods=0, ignore_na=False, adjust=False, alpha=1 / n).mean()

    def _rsi(self, col: str, n: int = 6):
        df_rsi = self._df.loc[:, VOLUMN_VOLS]
        ser_shift_diff = df_rsi[col] - df_rsi[col].shift(1)

        df_rsi["shift_diff"] = ser_shift_diff.clip(lower=0)
        df_rsi["shift_diff_abs"] = ser_shift_diff.abs()
        df_rsi["rsi"] = (
            self._sma(col="shift_diff", n=n, df=df_rsi)
            / self._sma(col="shift_diff_abs", n=n, df=df_rsi)
            * 100
        )

        return df_rsi
