import numpy as np

from insider.mixins.base import BaseMixin
from insider.constants import MOVING_VOLUMN_COLS, VOLUMN_VOLS


class VolumnIndicatorMixin(BaseMixin):
    """Volumn Indicator Mixin (量能相关指标混合)"""

    def vma(self, n=5):
        """Volumn Moving Average Calculation (量能移动平均值计算)"""
        df_vma = self._df.loc[:, MOVING_VOLUMN_COLS]
        df_vma.loc[:, "volumn"] = self._ma(col="volumn", n=n)
        return df_vma

    def vmacd(self, n=12, m=26, k=9):
        """Volumn Moving Average Convergence Divergence Calculation (量能平滑异同移动平均计算)"""
        df_vmacd = self._df.loc[:, MOVING_VOLUMN_COLS]
        df_vmacd.loc[:, "diff"] = self._ema(col="volumn", n=n) - self._ema(
            col="volumn", n=m
        )
        df_vmacd.loc[:, "dea"] = self._ema(col="diff", n=k, df=df_vmacd)
        df_vmacd.loc[:, "macd"] = 2 * (df_vmacd["diff"] - df_vmacd["dea"])
        return df_vmacd

    def vstd(self, n=5):
        df_vstd = self._df.loc[:, MOVING_VOLUMN_COLS]
        df_vstd.loc[:, "vstd"] = self._md(col="volumn", n=n, df=df_vstd)
        return df_vstd

    def vrsi(self, n: int = 6):
        return self._rsi("volumn", n=n)

    def vosc(self, n=12, m=26):
        """Volume Oscillator Indicator (成交量震荡指标)

        规则
        SHORT = N周期中成交量的总和/N；
        LONG = M周期中成交量的总和/M；
        VOSC =（SHORT－LONG）÷SHORT×100
        """

        df_vosc = self._df.loc[:, MOVING_VOLUMN_COLS]
        df_vosc.loc[:, "vosc"] = (
            (self._ma(col="volumn", n=n) - self._ma(col="volumn", n=m))
            / self._ma(col="volumn", n=n)
            * 100
        )
        return df_vosc

    def obv(self):
        """On Balance Volumn Indicator (平衡能量指标)

        规则：
        若当日收盘价＞上日收盘价，则当日OBV=前一日OBV＋今日成交量
        若当日收盘价＜上日收盘价，则当日OBV=前一日OBV－今日成交量
        若当日收盘价＝上日收盘价，则当日OBV=前一日OBV
        """
        df_obv = self._df.loc[:, VOLUMN_VOLS]

        df_obv.loc[:, "close_diff"] = df_obv["close"] - df_obv["close"].shift()
        df_obv = df_obv.assign(
            v=lambda x: np.select(
                condlist=[
                    x["close_diff"] > 0,
                    x["close_diff"] < 0,
                    x["close_diff"] == 0,
                ],
                choicelist=[x["volumn"], -x["volumn"], 0],
            )
        )
        df_obv.loc[:, "obv"] = df_obv["v"].expanding(1).sum()
        return df_obv
