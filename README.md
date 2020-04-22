# StockInsider


<p align="left">
    <a href="https://badge.fury.io/py/StockInsider">
        <img src="https://badge.fury.io/py/StockInsider.svg" alt="Package Version">
    </a>
    <a href="https://github.com/charlesdong1991/py-roughviz/pulls">
        <img src="https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat" alt="Contributions welcome">
    </a>
    <a href="https://opensource.org/licenses/MIT">
        <img src="https://img.shields.io/badge/License-MIT-brightgreen.svg" alt="License">
    </a>
</p>


This is a Python tool to collect Chinese stock price information, 
calculate the trading indicators for analysis and visualize stock
price and indicator lines.


## How to use the tool

### Installation

You can choose to either download it from PyPI through:

```bash
pip install StockInsider
```

or fork and clone the repo to your local device, and install 
the dependencies through:

```bash
git clone git@github.com:charlesdong1991/StockInsider.git
cd StockInsider
pip install -r requirements.txt
```


### Tool Overview

The main tool is called `StockInsider`, and it takes in two parameters:
`code` which is mandatory and an optional `ktype` argument. Once
the tool is initiated, the data is being stored under the hood.

First, you need to explicitly type the full code of the stock you
would like to analyze, e.g. `sz002156` or `sh603019`. Be aware that
only stocks traded in Shanghai and Shenzhen Stock Exchange can be 
collected, thus the code to put has to start with either `sh` or `sz`.

`ktype` is the frequency of the aggregated stock price, default is `D`
which refers to daily stock price, and other allowed values are `W` 
(weekly) and `M` (monthly).

```python
from insider import StockInsider
si = StockInsider("sz002516")
```

### Stock Price Visualization

Once initiation, you could use the tool to plot stock price and the
corresponding indicators over time.

In order to plot the stock price, you could simply do:

```python
si.plot()
```

And there are other options for you: 
- You could to select only certain number of recent trading days
 to plot by changing the `head` parameters, default is 90.
- You could choose a start/end date of stock prices to plot by defining
`start_date` and `end_date`.
- If you would like to only have the k-lines hidden in the plot, you
can set `verbose` to `False`.


### Stock Trading Indicator Visualization

Currently, there are many commonly used indicators supported in this tool:

- MA (Moving Average): `si.plot_ma()`
- MD (Moving Deviation): `si.plot_md()`
- EMA (Exponential Moving Average): `si.plot_ema()`
- MACD (Moving Average Convergence/Divergence): `si.plot_macd()`
- KDJ: `si.plot_kdj`
- RSI (Relative Strength Index): `si.plot_rsi()`
- VRSI (Volumn Relative Strength Index): `si.plot_vrsi()`

And there are several options to tune with:

- Choose to plot with the stock price by defining `verbose` to `True`
- Choose the number of recent trading days of stock information to 
plot via setting `head`.
- Choose which indicators are included in the plot, e.g. only plot `5-day`
and `60-day` line of MA indicator by setting `ns` to `[5, 60]`.

And some other more for specific indicators, please check out the docstrings.


### Get the stock data in Pandas DataFrame

If you would love to play with the data and do some other more fancy stuff,
you could also use the tool as a scrapper. Simply use `si.show_data()`
could return the data in Pandas DataFrame.

## Gallery

- Example1

```python
si = StockInsider("sh603019")
si.plot(head=120, verbose=True)
```

![Example 1](https://github.com/charlesdong1991/StockInsider/blob/master/examples/example1.png)


- Example2

```python
si = StockInsider("sz002156")
si.plot_ma(head=90, verbose=False)
```

![Example 2](https://github.com/charlesdong1991/StockInsider/blob/master/examples/example2.png)


- Example3

```python
si = StockInsider("sz002156")
si.plot_ema(ns=[5, 20, 60], verbose=True)
```

![Example 3](https://github.com/charlesdong1991/StockInsider/blob/master/examples/example3.png)


- Example4

```python
si = StockInsider("sz002156")
si.plot_macd()
```

![Example 4](https://github.com/charlesdong1991/StockInsider/blob/master/examples/example4.png)


- Example5

```python
si = StockInsider("sh603019")
si.plot_kdj(head=90, smooth_type="sma", n=7)
```

![Example 5](https://github.com/charlesdong1991/StockInsider/blob/master/examples/example5.png)

- Example6

```python
si = StockInsider("sh603019")
si.plot_rsi(head=80, ns=[6, 12])
```

![Example 6](https://github.com/charlesdong1991/StockInsider/blob/master/examples/example6.png)
