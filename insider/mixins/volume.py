from insider.mixins.base import BaseMixin
from insider.constants import MOVING_VOLUMN_COLS


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
