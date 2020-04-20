import requests
from requests.exceptions import Timeout
import pandas as pd
import plotly.graph_objects as go

from constants import (
    STOCK_URL,
    KTYPE_CONVERSION,
    KTYPES,
    DAY_COL,
    NUMERIC_COLUMNS,
    MA_COLORS,
    MA_COLS,
)


class Stock:
    def __init__(self, code, ktype="D"):
        self.code = self._check_code(code)
        self.ktype, self.converted_ktype = self._check_ktype(ktype)
        self.url = STOCK_URL.format(ktype=self.converted_ktype, code=self.code)

        self._df = self._get_stock_data()

    def _check_code(self, code):
        if not code.startswith("sz") and not code.startswith("sh"):
            raise ValueError("Stock code needs to be either sz or sh.")
        elif len(code) != 8:
            raise ValueError(f"Invalid code length: requires 8, but get {len(code)}")
        return code

    def _check_ktype(self, ktype):
        upper_ktype = ktype.upper()
        if upper_ktype not in ["D", "W", "M"]:
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
    def _choose_date(df, start_date, end_date):
        if start_date:
            df = df[df["day"] >= start_date]
        if end_date:
            df = df[df["day"] <= end_date]
        return df

    def show_data(self, start_date=None, end_date=None):
        df = self._df.copy()
        return self._choose_date(df, start_date, end_date)

    @staticmethod
    def _plot_stock_data(df, head):
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
    def _plot_ma_data(df, head):
        if head:
            df = df.tail(head)

        ma_data = []
        for col, color in zip(MA_COLS, MA_COLORS):
            data = go.Scatter(x=df["day"], y=df[col], name=col, marker_color=color)
            ma_data.append(data)

        return ma_data

    @staticmethod
    def _set_layout():
        layout = go.Layout(xaxis=dict(type="category", tickangle=270))
        return layout

    def plot(self, head=90, start_date=None, end_date=None, verbose=True):
        df = self._df.copy()
        df = self._choose_date(df, start_date, end_date)

        stock_data = self._plot_stock_data(df, head)
        data = [stock_data]
        if verbose:
            ma_data = self._plot_ma_data(df, head)
            data.extend(ma_data)

        layout = self._set_layout()
        fig = go.Figure(data=data, layout=layout)
        fig.update_layout(
            xaxis_rangeslider_visible=False, title_text="Stock Price Chart"
        )
        fig.show()
