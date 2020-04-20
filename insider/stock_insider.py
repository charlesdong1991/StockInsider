import plotly.graph_objects as go

from mixins import BaseMixin, MovingIndicatorMixin
from stock import Stock
from constants import MA_N, MD_N, EXPMA_N


class StockInsider(Stock, BaseMixin, MovingIndicatorMixin):
    def __init__(self, code):
        super().__init__(code)

    @staticmethod
    def _plot_line(df, head, line_name):
        if head:
            df = df.tail(head)
        plot_data = go.Scatter(x=df["day"], y=df["close"], name=line_name)
        return plot_data

    def _plot_moving_lines(self, func, name, head=90, ns=None, verbose=False):

        plot_data = []
        for n in ns:
            df = func(n=n)
            line_name = name + str(n)
            plot_data.append(self._plot_line(df, head, line_name))

        if verbose:
            df = self._df.copy()
            stock_data = self._plot_stock_data(df, head)
            plot_data.append(stock_data)

        layout = self._set_layout()
        fig = go.Figure(data=plot_data, layout=layout)
        if verbose:
            fig.update_layout(xaxis_rangeslider_visible=False)
        fig.update_layout(title_text=f"{name.upper()} Chart")
        fig.show()

    def plot_ma(self, head=90, ns=None, verbose=False):
        if ns is None:
            ns = MA_N

        func = self.ma
        self._plot_moving_lines(func=func, name="ma", head=head, ns=ns, verbose=verbose)

    def plot_md(self, head=90, ns=None, verbose=False):
        if ns is None:
            ns = MD_N

        func = self.md
        self._plot_moving_lines(func=func, name="md", head=head, ns=ns, verbose=verbose)

    def plot_ema(self, head=90, ns=None, verbose=False):
        if ns is None:
            ns = EXPMA_N

        func = self.ema
        self._plot_moving_lines(
            func=func, name="ema", head=head, ns=ns, verbose=verbose
        )

    def plot_macd(self, head=90):
        df_macd = self.macd()
        if head:
            df_macd = df_macd.tail(head)

        df_macd.loc[:, "color"] = df_macd["macd"].apply(
            lambda x: "red" if x >= 0 else "green"
        )

        layout = self._set_layout()
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
        fig.update_layout(title_text="MACD Chart")
        fig.show()
