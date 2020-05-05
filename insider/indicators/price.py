import numpy as np

from insider.indicators.base import BaseMixin
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
        """Moving Average Convergence Divergence Calculation (平滑异同移动平均计算)

        规则
        DIF = EMA12 - EMA26
        DEA = DIF的9日加权移动平均
        MACD = 2 ×（DIF-DEA）
        """
        df_macd = self._df.loc[:, MOVING_COLS]
        df_macd.loc[:, "diff"] = self._ema(col="close", n=n) - self._ema(
            col="close", n=m
        )
        df_macd.loc[:, "dea"] = self._ema(col="diff", n=k, df=df_macd)
        df_macd.loc[:, "macd"] = 2 * (df_macd["diff"] - df_macd["dea"])
        return df_macd

    def kdj(self, n: int = 9, smooth_type: str = "sma"):
        """
        规则
        n日RSV=（Cn－Ln）/（Hn－Ln）×100
        公式中，Cn为第n日收盘价；Ln为n日内的最低价；Hn为n日内的最高价。
        其次，计算K值与D值：
        * K值 = 2/3×前一日K值 + 1/3×当日RSV
        * D值 = 2/3×前一日D值 + 1/3×当日K值，若无前一日K值与D值，则可分别用50来代替
        * J值 = 3*当日K值 - 2*当日D值
        """
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
        """Calculate MI indicator.
        规则
        MI = CLOSE-REF(CLOSE,1)
        """
        df_mi = self._df.loc[:, MOVING_COLS]

        ser = df_mi["close"] - df_mi["close"].shift(n)
        df_mi.loc[:, "mi"] = self._sma(n=n, use_ser=ser)
        return df_mi

    def mike(self, n: int = 12):
        """Calculate MIKE Base indicator"""
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

    def rc(self, n: int = 30):
        """Calculate RC (Price rate of Change) indicator。 计算价格变化率"""
        df_rc = self._df.loc[:, MOVING_COLS]
        df_rc.loc[:, "rc"] = df_rc["close"] / df_rc["close"].shift(n)
        df_rc.loc[:, "arc"] = self._sma(use_ser=df_rc["rc"].shift(1), n=n)

        return df_rc

    def boll(self, n: int = 26):
        """Calculate BOLL line indicator. 计算布林线。

        规则
        中轨线 = N日的移动平均线
        上轨线 = 中轨线 + 两倍的标准差
        下轨线 = 中轨线 － 两倍的标准差
        """
        df_boll = self._df.loc[:, MOVING_COLS]
        df_boll.loc[:, "middle"] = self._ma(col="close", n=n)
        df_boll.loc[:, "up"] = df_boll["middle"] + 2 * self._md(col="close", n=n)
        df_boll.loc[:, "down"] = df_boll["middle"] - 2 * self._md(col="close", n=n)

        return df_boll

    def bbiboll(self, n: int = 11, m: int = 6):
        """Calculate BBIBOLL line indicator. 计算多空布林线.

        规则
        BBIBOLL =（3日简单移动平均价+6日简单移动平均价+12日简单移动平均价+24日简单移动平均价)/4
        UPR = BBIBOLL + M * BBIBOLL的N日估算标准差
        DWN = BBIBOLL - M * BBIBOLL的N日估算标准差
        参数N=11，M=6
        """
        df_bbiboll = self._df.loc[:, MOVING_COLS]
        df_bbiboll.loc[:, "bbiboll"] = (
            self._ma(col="close", n=3)
            + self._ma(col="close", n=6)
            + self._ma(col="close", n=12)
            + self._ma(col="close", n=24)
        ) / 4
        df_bbiboll.loc[:, "upr"] = df_bbiboll["bbiboll"] + m * self._md(
            col="bbiboll", df=df_bbiboll, n=n
        )
        df_bbiboll.loc[:, "dwn"] = df_bbiboll["bbiboll"] - m * self._md(
            col="bbiboll", df=df_bbiboll, n=n
        )
        return df_bbiboll

    def atr(self, n: int = 14):
        """Average True Ranger Indicator."""
        df_atr = self._df.loc[:, HIGH_LOW_COLS]
        df_atr.loc[:, "tr"] = np.vstack(
            [
                (df_atr["high"] - df_atr["low"]).abs(),
                (df_atr["close"].shift(1) - df_atr["high"]).abs(),
                (df_atr["close"].shift(1) - df_atr["low"]).abs(),
            ]
        ).max(axis=0)

        df_atr.loc[:, "atr"] = self._ma(col="tr", df=df_atr, n=n)
        return df_atr

    def cdp(self, n: int = 1):
        """CDP (Contrarian Operation Indicator) 逆势操作指标。

        规则
        需求值（CDP）= (前日最高价+前日最低价+前日收盘价)/3
        最高值（AH）= MA（CDP+（前日最高价-前日最低价），N）
        近高值（NH）= MA（CDP*2-前日最低价，N）
        最低值（AL）= MA（CDP-（前日最高价-前日最低价），N）
        近低值（NL）= MA（CDP*2-前日最高价，N）
        """
        df_cdp = self._df.loc[:, HIGH_LOW_COLS]

        df_cdp.loc[:, "cdp"] = (
            df_cdp.loc[:, ["high", "low", "close"]].shift(1).mean(axis=1)
        )
        df_cdp.loc[:, "ah"] = (
            (df_cdp["cdp"] + df_cdp["high"].shift(1) - df_cdp["low"].shift(1))
            .rolling(n)
            .mean()
        )
        df_cdp.loc[:, "nh"] = (
            (df_cdp["cdp"] * 2 - df_cdp["low"].shift(1)).rolling(n).mean()
        )
        df_cdp.loc[:, "al"] = (
            (df_cdp["cdp"] - df_cdp["high"].shift(1) + df_cdp["low"].shift(1))
            .rolling(n)
            .mean()
        )
        df_cdp.loc[:, "nl"] = (
            (df_cdp["cdp"] * 2 - df_cdp["high"].shift(1)).rolling(n).mean()
        )

        return df_cdp

    def mtm(self, n: int = 6, m: int = 5):
        """Momentum Index. （动量指标）

        规则
        MTM（N日）=C－CN
        C = 当日的收盘价
        CN = N日前的收盘价
        """
        df_mtm = self._df.loc[:, MOVING_COLS]

        df_mtm.loc[:, "mtm"] = df_mtm["close"] - df_mtm["close"].shift(n)
        df_mtm.loc[:, "mtmma"] = self._ma(col="mtm", df=df_mtm, n=m)
        return df_mtm

    def dmi(self, n: int = 14):
        """DMI (Directional Movement Index) 动向指标"""
        df_dmi = self._df.loc[:, HIGH_LOW_COLS]

        df_dmi.loc[:, "up"] = df_dmi["high"] - df_dmi["high"].shift(1)
        df_dmi.loc[:, "down"] = df_dmi["low"].shift(1) - df_dmi["low"]

        df_dmi = df_dmi.assign(
            pdi=lambda x: np.where((x["up"] > x["down"]) & (x["up"] > 0), x["up"], 0)
        ).assign(
            mdi=lambda x: np.where(
                (x["down"] > x["up"]) & (x["down"] > 0), x["down"], 0
            )
        )
        df_dmi.loc[:, "atr"] = self.atr(n=n)["atr"]

        df_dmi.loc[:, "pdi"] = 100 * self._ma(col="pdi", df=df_dmi, n=n) / df_dmi["atr"]
        df_dmi.loc[:, "mdi"] = 100 * self._ma(col="mdi", df=df_dmi, n=n) / df_dmi["atr"]

        df_dmi.loc[:, "adx"] = (
            100
            * (df_dmi["pdi"] - df_dmi["mdi"]).abs().rolling(n).mean()
            / (df_dmi["pdi"] + df_dmi["mdi"])
        )
        df_dmi.loc[:, "adxr"] = (df_dmi["adx"] + df_dmi["adx"].shift(n)) / 2

        return df_dmi
