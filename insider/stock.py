from typing import Optional
import re

import requests
from requests.exceptions import Timeout
import pandas as pd
import plotly.graph_objects as go

from insider.constants import (
    STOCK_URL,
    KTYPE_CONVERSION,
    KTYPES,
    DAY_COL,
    NUMERIC_COLUMNS,
    MA_COLORS,
    MA_COLS,
)
from insider.utils import set_layout


class Stock:
    """
    Stock Class which collects historical stock trading data and plots the basic
    stock price and k-lines
    """

    def __init__(self, code: str, ktype: str = "D"):
        """
        code: Full stock code，(e.g. 'sz002156')，股票完整代码
        ktype: freq, valid values are `D`, `W`, and `M`，股票趋势频率
        """
        self.code = self._check_code(code)
        self.stock_code = re.findall(r"\d+", self.code)[0]
        self.ktype, self.converted_ktype = self._check_ktype(ktype)
        self.url = STOCK_URL.format(ktype=self.converted_ktype, code=self.code)

        self._df = self._get_stock_data()

    def _check_code(self, code: str) -> str:
        if not code.startswith("sz") and not code.startswith("sh"):
            raise ValueError("Stock code needs to be either sz or sh.")
        elif len(code) != 8:
            raise ValueError(f"Invalid code length: requires 8, but get {len(code)}")
        elif not code[2:].isdigit():
            raise ValueError("Code must be all digits after sh or sz.")
        return code

    def _check_ktype(self, ktype: str) -> (str, str):
        upper_ktype = ktype.upper()
        if upper_ktype not in KTYPES:
            raise ValueError(f"Invalid ktype is given, valid inputs are {KTYPES}")
        converted_ktype = KTYPE_CONVERSION[upper_ktype]
        return upper_ktype, converted_ktype

    @property
    def full_data(self):
        df = self._df.copy()
        return df

    def _get_stock_data(self):
        try:
            r = requests.get(self.url, timeout=10)
        except Timeout:
            raise ValueError("The request timed out. Please try again.")
        else:
            data = r.json()["record"]
            if data:
                df = pd.DataFrame(data, columns=DAY_COL + NUMERIC_COLUMNS)
                df[NUMERIC_COLUMNS] = (
                    df[NUMERIC_COLUMNS]
                    .applymap(lambda x: x.replace(",", ""))
                    .astype("float64")
                )
                self._df = df
                return df
            else:
                raise ValueError(
                    "No data about the stock is found. Please check if the stock code is correct."
                )

    @staticmethod
    def _choose_date(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
        if start_date:
            df = df[df["day"] >= start_date]
        if end_date:
            df = df[df["day"] <= end_date]
        return df

    def show_data(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ):
        """Return the data in Pandas DataFrame，以DataFrame的形式显示历史数据。

        Parameters:
            start_date: start date of data to show, e.g. '2019-01-01'，起始时间
            end_date: end date of data to show, e.g. '2020-01-01'，终止时间

        Returns:
            Truncated DataFrame based on the dates, default is to show
            the full data.
            根据定义的起止时间而截取的历史数据，默认将会返回所有下载的数据。
        """
        df = self._df.copy()
        return self._choose_date(df, start_date, end_date)

    @staticmethod
    def _plot_stock_data(df: pd.DataFrame, head: int):
        if head:
            df = df.tail(head)

        stock_data = go.Candlestick(
            x=df["day"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            increasing_line_color="red",
            decreasing_line_color="green",
            name="stock price",
        )
        return stock_data

    @staticmethod
    def _plot_ma_data(df: pd.DataFrame, head: int):
        if head:
            df = df.tail(head)

        ma_data = []
        for col, color in zip(MA_COLS, MA_COLORS):
            data = go.Scatter(x=df["day"], y=df[col], name=col, marker_color=color)
            ma_data.append(data)

        return ma_data

    def plot(
        self,
        head: int = 90,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        verbose: bool = True,
    ):
        """Plot the stock price over time. 绘出股票走势图。

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。
            start_date: start date, default is None, 起始时间
            end_date: end date, default is None, 终止时间
            verbose: If to plot K-line or not, default is True, 是否同时绘出k线，默认是会绘出。
        """
        df = self._df.copy()
        df = self._choose_date(df, start_date, end_date)

        stock_data = self._plot_stock_data(df, head)
        data = [stock_data]
        if verbose:
            ma_data = self._plot_ma_data(df, head)
            data.extend(ma_data)

        fig = go.Figure(data=data, layout=set_layout())
        fig.update_layout(
            xaxis_rangeslider_visible=False,
            title_text=f"Stock Price Chart ({self.stock_code})",
        )
        fig.show()
