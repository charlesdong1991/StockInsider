import numpy as np

from insider.mixins.base import BaseMixin
from insider.constants import MOVING_COLS, HIGH_LOW_COLS, ADTM_COLS


class PriceIndicatorMixin(BaseMixin):
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

    def kdj(self, n: int = 9, smooth_type: str = "sma"):
        if smooth_type == "sma":
            func = self._sma
        elif smooth_type == "ema":
            func = self._ema
        else:
            raise ValueError(
                "Invalid smooth average method is given, only sma and ema are allowed."
            )

        df_kdj = self._df.loc[:, HIGH_LOW_COLS]
        close_minus_low = df_kdj["close"] - df_kdj["low"].rolling(n).min()
        high_minus_low = (
            df_kdj["high"].rolling(n).max() - df_kdj["low"].rolling(n).min()
        )

        df_kdj.loc[:, "K"] = (close_minus_low / high_minus_low) * 100
        df_kdj.loc[:, "K"] = func(col="K", n=3, df=df_kdj)
        df_kdj.loc[:, "D"] = func(col="K", n=3, df=df_kdj)
        df_kdj.loc[:, "J"] = 3 * df_kdj["K"] - 2 * df_kdj["D"]

        # Cap it between 0 and 100 as shown in THS.
        df_kdj.loc[:, ["K", "D", "J"]] = df_kdj.loc[:, ["K", "D", "J"]].clip(0, 100)
        return df_kdj

    def rsi(self, n: int = 6):
        return self._rsi("close", n=n)

    def env(self, n: int = 14):
        df_env = self._df.loc[:, MOVING_COLS]

        df_env.loc[:, "up"] = self._ma(col="close", n=n) * 1.06
        df_env.loc[:, "down"] = self._ma(col="close", n=n) * 0.94
        return df_env

    def mi(self, n=12):
        """Calculate MI indicator."""
        df_mi = self._df.loc[:, MOVING_COLS]

        ser = df_mi["close"] - df_mi["close"].shift(n)
        df_mi.loc[:, "mi"] = self._sma(n=n, use_ser=ser)
        return df_mi

    def mike(self, n: int = 12):
        """Calculate MIKE indicator"""
        df_mike = self._df.loc[:, HIGH_LOW_COLS]

        # typ price = avg(high + low + close)
        typ = df_mike[["high", "low", "close"]].mean(axis=1)
        # hv price = highest price in a window
        hv = df_mike["high"].rolling(n).max()
        # lv price = lowest price in a window
        lv = df_mike["low"].rolling(n).min()

        df_mike.loc[:, "wr"] = typ * 2 - lv
        df_mike.loc[:, "mr"] = typ + hv - lv
        df_mike.loc[:, "sr"] = 2 * hv - lv
        df_mike.loc[:, "ws"] = typ * 2 - hv
        df_mike.loc[:, "ms"] = typ - hv + lv
        df_mike.loc[:, "ss"] = 2 * lv - hv

        return df_mike

    def adtm(self, n: int = 23, m: int = 8):
        """动态买卖气指数
        (https://bkso.baidu.com/item/%E5%8A%A8%E6%80%81%E4%B9%B0%E5%8D%96%E6%B0%94%E6%8C%87%E6%A0%87)

        规则：
        1.如果开盘价≤昨日开盘价，DTM=0
          如果开盘价>昨日开盘价，DTM=(最高价-开盘价)和(开盘价-昨日开盘价)的较大值
        2.如果开盘价≥昨日开盘价，DBM=0
          如果开盘价<昨日开盘价，DBM=(开盘价-最低价)和(开盘价-昨日开盘价)的较大值
        3.STM=DTM在N日内的和
        4.SBM=DBM在N日内的和
        5.如果STM>SBM,ADTM=(STM-SBM)/STM
          如果STM<SBM,ADTM=(STM-SBM)/SBM
          如果STM=SBM,ADTM=0
        6.ADTMMA=ADTM的M日简单移动平均
        7.参数N设置为23日，参数M设置为8日

        参考值：
        1.ADTM指标在+1到-1之间波动。
        2.低于-0.5时为低风险区,高于+0.5时为高风险区，需注意风险。
        3.ADTM上穿ADTMMA时，买入股票；ADTM跌穿ADTMMA时，卖出股票。
        """
        df_adtm = self._df.loc[:, ADTM_COLS]

        df_adtm.loc[:, "open_diff"] = df_adtm["open"] - df_adtm["open"].shift(1)
        df_adtm.loc[:, "high_open_diff"] = df_adtm["high"] - df_adtm["open"]
        df_adtm.loc[:, "open_low_diff"] = df_adtm["open"] - df_adtm["low"]

        df_adtm = (
            df_adtm.assign(
                dtm=lambda x: np.where(
                    x["open_diff"] > 0,
                    np.where(
                        x["high_open_diff"] >= x["open_low_diff"],
                        x["high_open_diff"],
                        x["open_low_diff"],
                    ),
                    0,
                )
            )
        ).assign(dbm=lambda x: np.where(x["open_diff"] >= 0, 0, x["open_low_diff"]))

        df_adtm.loc[:, "stm"] = df_adtm["dtm"].rolling(n).sum()
        df_adtm.loc[:, "sbm"] = df_adtm["dbm"].rolling(n).sum()

        df_adtm = df_adtm.assign(
            adtm=lambda x: np.select(
                condlist=[
                    x["stm"] > x["sbm"],
                    x["stm"] < x["sbm"],
                    x["stm"] == x["sbm"],
                ],
                choicelist=[
                    (x["stm"] - x["sbm"]) / x["stm"],
                    (x["stm"] - x["sbm"]) / x["sbm"],
                    0,
                ],
            )
        )

        df_adtm.loc[:, "adtmma"] = self._ma(col="adtm", n=m, df=df_adtm)
        return df_adtm
