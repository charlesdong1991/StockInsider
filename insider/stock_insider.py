from typing import Callable, List, Optional

import plotly.graph_objects as go
import pandas as pd
import numpy as np

from insider.indicators.price import PriceIndicatorMixin
from insider.indicators.volume import VolumnIndicatorMixin
from insider.indicators.sar import SARIndicatorMixin
from insider.stock import Stock
from insider.utils import set_layout
from insider.constants import (
    MA_N,
    MD_N,
    EXPMA_N,
    RSI_N,
    MIKE_COLS,
    CDP_COLS,
    EXTERNAL_COLS,
)


class StockInsider(Stock, PriceIndicatorMixin, VolumnIndicatorMixin, SARIndicatorMixin):
    """Plot daily trading indicators."""

    def __init__(self, code, ktype="D", df=None):
        """
        Parameters:
            code: Full stock code，(e.g. 'sz002156')，股票完整代码
            ktype: Data frequency, valid input is `D`, `W`, or `M`. 股票数据的频率
        """
        if df is not None and isinstance(df, pd.DataFrame):
            self._df = df
            self.stock_code = code
        else:
            super().__init__(code, ktype)

    @classmethod
    def from_external_csv_data(cls, fpath: str, code=None):
        """Allow the StockInsider class serve for external stock data (other than
        default Chinese stock data) to visualize stock trading indicators.
        如果你有已经下载好的或者是非中国股市股票的数据想要来计算和绘出交易指标，你可以选择
        用这个classmethod来初始化。

        Parameters:
            fpath: the path to the external stock data in CSV. 外部数据的路径
            code: the stock code you would like to show in each visualization, the default
                is None which will have `external data` shown as stock name.
                股票代码，这个没有必要是真实的代码，你选择的结果将会被以股票代码的形式展示。
        """
        df = pd.read_csv(fpath)
        if not set(EXTERNAL_COLS).issubset(df.columns):
            raise ValueError(
                f"{EXTERNAL_COLS} are mandatory in external data so as to plot"
                f" all trading indicators."
            )
        if code is None:
            code = "external data"
        return cls(code=code, df=df)

    @staticmethod
    def _plot_line(df: pd.DataFrame, head: int, line_name: str, y: str = "close"):
        if head:
            df = df.tail(head)
        plot_data = go.Scatter(x=df["day"], y=df[y], name=line_name)
        return plot_data

    def _plot_moving_lines(
        self,
        func: Callable,
        verbose_func: Callable,
        name: str,
        y: str = "close",
        head: int = 90,
        ns: Optional[List] = None,
        verbose: bool = False,
    ):

        plot_data = []
        for n in ns:
            df = func(n=n)
            line_name = name + str(n)
            plot_data.append(self._plot_line(df, head, line_name, y=y))

        if verbose:
            df = self._df.copy()
            verbose_data = verbose_func(df, head)
            plot_data.append(verbose_data)

        layout = set_layout()
        fig = go.Figure(data=plot_data, layout=layout)
        if verbose:
            fig.update_layout(xaxis_rangeslider_visible=False)
        fig.update_layout(title_text=f"{name.upper()} Chart ({self.stock_code})")
        fig.show()

    def _plot(self, df, head, title, lines, verbose: bool = False):
        """General plot functions shared across the class."""
        fig = go.Figure(layout=set_layout())

        if isinstance(lines, str):
            lines = [lines]
        elif not isinstance(lines, list):
            raise ValueError("Only string or list is valid type for lines.")

        for n in lines:
            fig.add_trace(self._plot_line(df, head=head, y=n, line_name=n.upper()))

        if verbose:
            fig.add_trace(self._plot_stock_data(self._df, head))

        fig.update_layout(
            title_text=f"{title} Chart ({self.stock_code})",
            xaxis_rangeslider_visible=False,
        )
        fig.show()

    def plot_ma(
        self, head: int = 90, ns: Optional[List[int]] = None, verbose: bool = False
    ):
        """Plot Moving Average Indicator. 绘出MA曲线

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。
            ns: Select which trading lines to plot, default is to plot 5, 10, 20, 60-day lines
            选择曲线的种类，e.g. [5, 10], 默认会绘出5, 10, 20, 60日曲线
            verbose: If to include stock price or not, default is False.
            选择是否将股票价格曲线一起绘出，默认是False，将会只绘出指标曲线。
        """
        if ns is None:
            ns = MA_N

        func = self.ma
        verbose_func = self._plot_stock_data
        self._plot_moving_lines(
            func=func,
            verbose_func=verbose_func,
            name="ma",
            head=head,
            ns=ns,
            verbose=verbose,
        )

    def plot_md(
        self, head: int = 90, ns: Optional[List[int]] = None, verbose: bool = False
    ):
        """Plot Moving Deviation Indicator. 绘出MD曲线

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。
            ns: Select which trading lines to plot, default is to plot 5, 10, 20-day lines
            选择曲线的种类，e.g. [5, 10], 默认会绘出5, 10, 20日曲线
            verbose: If to include stock price or not, default is False.
            选择是否将股票价格曲线一起绘出，默认是False，将会只绘出指标曲线。
        """
        if ns is None:
            ns = MD_N

        func = self.md
        verbose_func = self._plot_stock_data
        self._plot_moving_lines(
            func=func,
            verbose_func=verbose_func,
            name="md",
            head=head,
            ns=ns,
            verbose=verbose,
        )

    def plot_ema(
        self, head: int = 90, ns: Optional[List[int]] = None, verbose: bool = False
    ):
        """Plot Exponential Moving Average Indicator. 绘出EMA曲线

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。
            ns: Select which trading lines to plot, default is to plot 5, 10, 20, 60-day lines
            选择曲线的种类，e.g. [5, 10, 20, 60], 默认会绘出5, 10, 20, 60日曲线
            verbose: If to include stock price or not, default is False.
            选择是否将股票价格曲线一起绘出，默认是False，将会只绘出指标曲线。
        """
        if ns is None:
            ns = EXPMA_N

        func = self.ema
        verbose_func = self._plot_stock_data
        self._plot_moving_lines(
            func=func,
            verbose_func=verbose_func,
            name="ema",
            head=head,
            ns=ns,
            verbose=verbose,
        )

    def plot_macd(self, head: int = 90):
        """Plot MACD (Moving Average Convergence and Divergence) Indicator. 绘出MACD曲线

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。

        A mixed chart will be plotted, including a bar chart to visualize MACD, and line charts
        to visualize DIFF and DEA.
        将会绘出差值柱形图来表示MACD, 以及表示差离值和讯号线的线性图。
        """
        df_macd = self.macd()
        if head:
            df_macd = df_macd.tail(head)

        df_macd.loc[:, "color"] = df_macd["macd"].apply(
            lambda x: "red" if x >= 0 else "green"
        )

        layout = set_layout()
        fig = go.Figure(layout=layout)

        fig.add_trace(
            go.Bar(
                x=df_macd["day"],
                y=df_macd["macd"],
                base=0,
                marker_color=df_macd["color"],
                name="MACD",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df_macd["day"], y=df_macd["dea"], marker_color="orange", name="DEA"
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df_macd["day"], y=df_macd["diff"], marker_color="black", name="DIFF"
            )
        )
        fig.update_layout(title_text=f"MACD Chart ({self.stock_code})")
        fig.show()

    def plot_kdj(self, head: int = 90, n: int = 9, smooth_type="sma"):
        """Plot KDJ Indicator. 绘出KDJ曲线。

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。
            n: The size of moving average period for K, default is 9. 平移平均曲线的窗口大小，默认
            是9个交易日。
            smooth_type: The metric to calculate moving average, default is `sma`, the other
            option is `ema`. 选择计算平移平均曲线的方式，默认是SMA, 另一个选择是EMA。
        """
        df_kdj = self.kdj(n=n, smooth_type=smooth_type)
        if head:
            df_kdj = df_kdj.tail(head)

        plot_data = []
        for col in ["K", "D", "J"]:
            plot_data.append(self._plot_line(df_kdj, head, col, y=col))

        layout = set_layout()
        fig = go.Figure(data=plot_data, layout=layout)
        fig.update_layout(title_text=f"KDJ Chart ({self.stock_code})")
        fig.show()

    def plot_rsi(self, head: int = 90, ns: Optional[List] = None):
        """Plot RSI (Relative Strength Index) Indicator. 绘出RSI曲线。

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。
            ns: Select which trading lines to plot, default is to plot 6, 12, 24-day lines
            选择曲线的种类，e.g. [6, 12], 默认会绘出6, 12, 24日曲线
        """
        if ns is None:
            ns = RSI_N

        func = self.rsi
        verbose_func = self._plot_stock_data
        self._plot_moving_lines(
            func=func,
            verbose_func=verbose_func,
            y="rsi",
            name="RSI",
            head=head,
            ns=ns,
            verbose=False,
        )

    def plot_vrsi(self, head: int = 90, ns: Optional[List] = None):
        """Plot VRSI (Volumn Relative Strength Index) Indicator. 绘出VRSI曲线。

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。
            ns: Select which trading lines to plot, default is to plot 6, 12, 24-day lines
            选择曲线的种类，e.g. [6, 12], 默认会绘出6, 12, 24日曲线
        """
        if ns is None:
            ns = RSI_N

        func = self.vrsi
        verbose_func = self._plot_stock_data
        self._plot_moving_lines(
            func=func,
            verbose_func=verbose_func,
            y="rsi",
            name="VRSI",
            head=head,
            ns=ns,
            verbose=False,
        )

    @staticmethod
    def _plot_volumn_data(df, head):
        df_volumn = df.copy()
        if head:
            df_volumn = df_volumn.tail(head)

        df_volumn = df_volumn.assign(
            color=lambda x: np.where(x["open"] < x["close"], "red", "green")
        )

        data = go.Bar(
            x=df_volumn["day"],
            y=df_volumn["volumn"],
            base=0,
            marker_color=df_volumn["color"],
            name="Volumn",
        )
        return data

    def plot_volumn(self, head: int = 90):
        """Plot Volumn over time. 绘出交易量能柱状图。

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的交易量能柱状图。
        """
        df_volumn = self._df.copy()
        data = self._plot_volumn_data(df_volumn, head)

        layout = set_layout()
        fig = go.Figure(data=[data], layout=layout)
        fig.update_layout(title_text=f"Volumn Chart ({self.stock_code})")
        fig.show()

    def plot_vma(
        self, head: int = 90, ns: Optional[List] = None, verbose: bool = False
    ):
        """Plot VMA over time. 绘出交易能量MA图曲线

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。
            ns: Select which trading lines to plot, default is to plot 5, 10, 20-day lines
            选择曲线的种类，e.g. [5, 10], 默认会绘出5, 10, 20日曲线
            verbose: If to include volumn change bar chart or not, default is False.
            选择是否将能量变化柱状图一起绘出，默认是False，将会只绘出指标曲线。
        """
        if ns is None:
            ns = MA_N

        func = self.vma
        verbose_func = self._plot_volumn_data
        self._plot_moving_lines(
            func=func,
            verbose_func=verbose_func,
            y="volumn",
            name="vma",
            head=head,
            ns=ns,
            verbose=verbose,
        )

    def plot_vmacd(self, head: int = 90):
        """Plot VMACD (Volumn Moving Average Convergence and Divergence)
        Indicator. 绘出VMACD曲线

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。

        A mixed chart will be plotted, including a bar chart to visualize VMACD, and line charts
        to visualize DIFF and DEA.
        将会绘出量能差值柱形图来表示VMACD, 以及表示差离值和讯号线的线性图。
        """
        df_vmacd = self.vmacd()
        if head:
            df_vmacd = df_vmacd.tail(head)

        df_vmacd.loc[:, "color"] = df_vmacd["macd"].apply(
            lambda x: "red" if x >= 0 else "green"
        )

        layout = set_layout()
        fig = go.Figure(layout=layout)

        fig.add_trace(
            go.Bar(
                x=df_vmacd["day"],
                y=df_vmacd["macd"],
                base=0,
                marker_color=df_vmacd["color"],
                name="VMACD",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df_vmacd["day"], y=df_vmacd["dea"], marker_color="orange", name="DEA"
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df_vmacd["day"], y=df_vmacd["diff"], marker_color="black", name="DIFF"
            )
        )
        fig.update_layout(title_text=f"VMACD Chart ({self.stock_code})")
        fig.show()

    def plot_vstd(self, head: int = 90, ns: Optional[List] = None):
        """Plot VSTD chart. 绘出VSTD曲线

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。
            ns: Select which trading lines to plot, default is to plot 5, 10, 20-day lines
            选择曲线的种类，e.g. [5, 10], 默认会绘出5, 10, 20日曲线
        """
        if ns is None:
            ns = MD_N

        func = self.vstd
        verbose_func = self._plot_volumn_data
        self._plot_moving_lines(
            func=func,
            verbose_func=verbose_func,
            y="vstd",
            name="vstd",
            head=head,
            ns=ns,
            verbose=False,
        )

    def plot_env(self, head: int = 90, n: int = 14, verbose: bool = False):
        """Plot ENV indicator. 绘出ENV曲线。

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。
            n: The size of moving average period for K, default is 14. 平移平均曲线的窗口大小，默认
            是14个交易日。
            verbose: If to include stock price or not, default is False.
            选择是否将股票价格曲线一起绘出，默认是False，将会只绘出指标曲线。
        """

        df_env = self.env(n=n)
        self._plot(
            df=df_env, head=head, title="ENV", lines=["up", "down"], verbose=verbose
        )

    def plot_vosc(self, head: int = 90):
        """Plot Volumn Oscillator Indicator 绘出成交量震荡指标

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。
        """
        df_vosc = self.vosc()
        self._plot(df=df_vosc, head=head, title="VOSC", lines=["vosc"])

    def plot_mi(self, head: int = 90, n: int = 12):
        """Plot Momentum Indicator. 绘出动量指标

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。
            n: The size of moving average period for K, default is 12. 平移平均曲线的窗口大小，默认
            是12个交易日。
        """
        df_mi = self.mi(n=n)
        self._plot(df=df_mi, head=head, title="MI", lines=["mi"])

    def plot_mike(
        self,
        head: int = 90,
        n: int = 12,
        ns: Optional[List] = None,
        verbose: bool = False,
    ):
        """Plot Mike Base Indicator. 绘出Mike指标

        压力线解释：
        初级压力线（WR)
        中级压力线（MR)
        强力压力线（SR）
        初级支撑线（WS）
        中级支撑线（MS）
        强力支撑线（SS）

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。
            n: The size of moving average period for K, default is 12. 平移平均曲线的窗口大小，默认
            是12个交易日。
            ns: Choose the lines to be plotted, default is None, which will plot all six lines.
            选择压力线来绘出，默认会绘出所有六条压力线。
            verbose: If to include stock price or not, default is False.
            选择是否将股票价格曲线一起绘出，默认是False，将会只绘出指标曲线。
        """
        if ns is None:
            ns = MIKE_COLS
        elif isinstance(ns, str):
            ns = [ns]
        else:
            ns = [n.lower() for n in ns]
            if [n for n in ns if n not in MIKE_COLS]:
                raise ValueError(
                    "Invalid input for ns, valid values are wr, sr, ws, ms and ss."
                )

        df_mike = self.mike(n=n)
        self._plot(df=df_mike, head=head, title="MIKE", lines=ns, verbose=verbose)

    def plot_adtm(self, head: int = 90):
        """Plot ADTM(23,8) indicator. 绘出动态买卖气指标 (ADTM(23, 8))

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。
        """
        df_adtm = self.adtm()
        self._plot(df=df_adtm, head=head, title="ADTM", lines=["adtm", "adtmma"])

    def plot_obv(self, head: int = 90):
        """Plot OBV (On Balance Volumn) Indicator。绘出能量指标

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。
        """
        df_obv = self.obv()
        self._plot(df=df_obv, head=head, title="OBV", lines=["obv"])

    def plot_rc(self, head: int = 90, n: int = 30):
        """Plot RC (Price rate of Change) Indicator 绘出价格变化率指标

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。
            n: The size of moving average period for K, default is 30. 平移平均曲线的窗口大小，默认
            是30个交易日。
        """
        df_rc = self.rc(n=n)
        self._plot(df=df_rc, head=head, title="RC", lines=["arc"])

    def plot_boll(self, head: int = 90, n: int = 26, verbose: bool = False):
        """Plot BOLL line indicator 绘出布林线。

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。
            n: The size of moving average period for K, default is 26. 平移平均曲线的窗口大小，默认
            是26个交易日。
            verbose: If to include stock price or not, default is False.
            选择是否将股票价格曲线一起绘出，默认是False，将会只绘出指标曲线。
        """
        df_boll = self.boll(n=n)
        self._plot(
            df=df_boll,
            head=head,
            title="BOLL",
            lines=["up", "middle", "down"],
            verbose=verbose,
        )

    def plot_bbiboll(
        self, head: int = 90, n: int = 11, m: int = 6, verbose: bool = False
    ):
        """Plot BOLL line indicator 绘出布林线。

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。
            n: The size of moving average period for K, default is 6. 平移平均曲线的窗口大小，默认
            是6个交易日。
            m: The number to decide the width of up/down lines. 上下压力线的带宽倍数。
            verbose: If to include stock price or not, default is False.
            选择是否将股票价格曲线一起绘出，默认是False，将会只绘出指标曲线。
        """
        df_boll = self.bbiboll(n=n, m=m)
        self._plot(
            df=df_boll,
            head=head,
            title="BBIBOLL",
            lines=["upr", "bbiboll", "dwn"],
            verbose=verbose,
        )

    def plot_atr(self, head: int = 90, n: int = 14):
        """Plot Average True Ranger indicator. 绘出真实变化率曲线

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。
            n: The size of moving average period for K, default is 14. 平移平均曲线的窗口大小，默认
            是14个交易日。
        """
        df_atr = self.atr(n=n)
        self._plot(df=df_atr, head=head, title="ATR", lines=["tr", "atr"])

    def plot_cdp(
        self,
        head: int = 90,
        n: int = 1,
        ns: Optional[List] = None,
        verbose: bool = False,
    ):
        """Plot Contrarian Operation Indicator. 绘出逆势操作曲线

        压力线解释：
        CDP: 需求值
        AH: 最高值
        NH：近高值
        AL：最低值
        NL：近低值

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。
            n: The size of moving average period for K, default is 1. 平移平均曲线的窗口大小，默认
            是1个交易日。
            ns: Choose the lines to be plotted, default is None, which will plot all five lines.
            选择压力线来绘出，默认会绘出所有五条条压力线。
            verbose: If to include stock price or not, default is False.
            选择是否将股票价格曲线一起绘出，默认是False，将会只绘出指标曲线。
        """
        if ns is None:
            ns = CDP_COLS
        elif isinstance(ns, str):
            ns = [ns]
        else:
            ns = [n.lower() for n in ns]
            if [n for n in ns if n not in CDP_COLS]:
                raise ValueError(
                    "Invalid input for ns, valid values are ah, al, cdp, nh, nl."
                )

        df_cdp = self.cdp(n=n)
        self._plot(df=df_cdp, head=head, title="CDP", lines=ns, verbose=verbose)

    def plot_sar(self, head: int = 90, verbose: bool = False):
        """Plot Stop And Reverse (SAR) indicator. 绘出止损反转指标

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。
            verbose: If to include stock price or not, default is False.
            选择是否将股票价格曲线一起绘出，默认是False，将会只绘出指标曲线。
        """
        df_sar = self.sar()

        if head:
            df_sar = df_sar.tail(head)

        fig = go.Figure(layout=set_layout())
        fig.add_trace(
            go.Scatter(
                x=df_sar["day"],
                y=df_sar["sar"],
                marker=dict(color=df_sar["color"], size=3),
                mode="markers",
                name="SAR",
            )
        )

        if verbose:
            fig.add_trace(self._plot_stock_data(self._df, head))

        fig.update_layout(
            title_text=f"SAR Chart ({self.stock_code})",
            xaxis_rangeslider_visible=False,
        )
        fig.show()

    def plot_mtm(self, head: int = 90):
        """Plot MTM indicator. 绘出动量指标

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。
        """
        df_mtm = self.mtm()
        self._plot(df=df_mtm, head=head, title="MTM", lines=["mtm", "mtmma"])

    def plot_dmi(self, head: int = 90, n: int = 14):
        """Plot DMI (Directional Movement Index) indicator. 绘出动向指标

            Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。
            n: The size of moving average period for K, default is 14. 平移平均曲线的窗口大小，默认
            是14个交易日。
        """
        df_dmi = self.dmi(n=n)

        self._plot(
            df=df_dmi, head=head, title="DMI", lines=["pdi", "mdi", "adx", "adxr"]
        )
