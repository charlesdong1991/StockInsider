import pandas as pd

from insider.indicators.base import BaseMixin
from insider.constants import HIGH_LOW_COLS, INITIAL_AF, INITIAL_TREND


class SARIndicatorMixin(BaseMixin):
    def sar(self):
        """
        规则

        先选定一段时间判断为上涨或下跌；
        若是看涨，则第一天的SAR值必须是近期内的最低价；若是看跌，则第一天的SAR须是近期的最高价；
        第二天的SAR，则为第一天的最高价（看涨时）或是最低价（看跌时）与第一天的SAR的差距乘上加速因子，再加上第一天的SAR就可求得；

        每日的SAR都可用上述方法类推，归纳公式如下：
        SAR（n）=SAR（n-1）+AF〖EP（n-1）－SAR（n-1）〗
        SAR（n）=第n日的SAR值，SAR（n-1）即第（n-1）日之值；
        AF：加速因子；
        EP：极点价，若是看涨一段期间，则EP为这段期间的最高价，若是看跌一段时间，则EP为这段期间的最低价；
        EP（n-1）：第（n-1）日的极点价。

        加速因子第一次取0．02，假若第一天的最高价比前一天的最高价还高，则加速因子增加0．02，若无新高则加速因子沿用前一天的数值，
        但加速因子最高不能超过0．2。反之，下跌也类推；

        若是看涨期间，计算出某日的SAR比当日或前一日的最低价高，则应以当日或前一日的最低价为某日之SAR；
        若是看跌期间，计算某日之SAR比当日或前一日的最高价低，则应以当日或前一日的最高价为某日的SAR；
        """
        df_sar = self._df.loc[:, HIGH_LOW_COLS]
        trend = INITIAL_TREND
        af = INITIAL_AF

        df_sar.loc[:, "sar"] = df_sar["close"]
        df_sar.loc[:, "trend"] = pd.Series(index=df_sar["close"].index, dtype="bool")

        start_high = df_sar.loc[0, "high"]
        start_low = df_sar.loc[0, "low"]

        for i in range(1, len(df_sar)):

            reverse = False
            if trend:
                df_sar.loc[i, "sar"] = df_sar.loc[i - 1, "sar"] + (
                    af * (start_high - df_sar.loc[i - 1, "sar"])
                )
                if df_sar.loc[i, "low"] < df_sar.loc[i, "sar"]:
                    reverse = True
                    start_low = df_sar.loc[i, "low"]
                    df_sar.loc[i, "sar"] = start_high
                    af = 0.02
                elif df_sar.loc[i, "high"] > start_high:
                    start_high = df_sar.loc[i, "high"]
                    af = min(af + 0.02, 0.2)
            else:
                df_sar.loc[i, "sar"] = df_sar.loc[i - 1, "sar"] + (
                    af * (start_low - df_sar.loc[i - 1, "sar"])
                )

                if df_sar.loc[i, "high"] > df_sar.loc[i, "sar"]:
                    reverse = True
                    start_high = df_sar.loc[i, "high"]
                    df_sar.loc[i, "sar"] = start_low
                    af = 0.02
                elif df_sar.loc[i, "low"] < start_low:
                    start_low = df_sar.loc[i, "low"]
                    af = min(af + 0.02, 0.2)

            trend = trend != reverse
            df_sar.loc[i, "trend"] = trend

        df_sar.loc[:, "color"] = df_sar["trend"].apply(
            lambda x: "red" if x else "green"
        )
        return df_sar
