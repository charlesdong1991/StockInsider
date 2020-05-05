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
    <a href="https://badge.fury.io/py/py-roughviz">
        <img src="https://travis-ci.org/charlesdong1991/py-roughviz.svg?branch=master" alt="build">
    </a>
</p>


这是一个用来获取中国上市股票价格相关的信息，计算交易指标，并将交易指标绘出的Python工具。指标的计算大多是根据这个博客里
列出的技术分析指标总结: [By woojean](http://www.woojean.com/2018/03/09/%E6%8A%80%E6%9C%AF%E5%88%86%E6%9E%90%E6%8C%87%E6%A0%87%E6%80%BB%E7%BB%93/）
以及同花顺给出的公式。

This is a Python tool to calculate the trading indicators for analysis and visualize stock
price and indicator lines. This tool provides a simple API for the collection stock information 
from Chinese stock market, but you could also use it to get the stock data from your saved
stock information in CSV format. 


## How to use the tool （如何使用这个工具）

### Installation （安装）

You can choose to either download it from PyPI through: （你可以选择从PyPI上下载）

```bash
pip install StockInsider
```

or to install the latest version: （也可以安装最新的Github版本）
```bash
pip install -U git+https://github.com/charlesdong1991/StockInsider
```

or fork and clone the repo to your local device, and install 
the dependencies through: （或者克隆这个项目到你本地电脑，然后安装所需包）

```bash
git clone git@github.com:charlesdong1991/StockInsider.git
cd StockInsider
pip install -r requirements.txt
```


### Tool Overview （工具简介）

主要工具是`StockInsider`，它需要两个参数：必要参数是`code`，它代表股票在交易
所的代码，另一个是可选参数`ktype`，它代表股票数据类型。

首先，值得注意的是你需要输入完整的股票代码，我只试过上海和深圳股票交易所的代码，所以
可以肯定的是这两个交易所上市的公司的股票信息是支持的，比如`sz002156`或者`sh603019`，
目前的工具只支持股票代码以`sh`或者`sz`开头。

其次，股票数据类型是以何种频率股票价格等信息会汇总，默认是D，表示是日线。也可以选择
W（周线），M（月线）。

值得注意的是，所有的指标都是以日线为基准的。

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

### Calculate and Plot Trading Indicators on your Saved Stock Data (利用你已有的股票数据来计算和绘出曲线)
如果你想利用这个工具来计算和绘出其他的（非中国）股票数据，可以利用以下来初始化工具.

Other than calculating and plotting trading indicators for Chinese stock data (default), you could 
also use this tool to do the same for any of your saved stock data in CSV. You could initialize
your StockInsider by `from_external_csv_data`, and then use the initialized tool to do the rest.

```python
from insider import StockInsider
fpath = "path/to/your/stock/data/in/CSV"
si = StockInsider.from_external_csv_data(fapth=fpath, code="my stock")
```


### Stock Price Visualization （股票价格图）

如果想用这个工具单纯的画出股票K线，只需要输入 `si.plot()`, 就会得到K线走势。

这也有一些选择，比如可以选择`head`来决定只绘出近N日的股票价格而不是所有的，也可以
选择开始和截止日期内的股票价格；如果想画出向同花顺软件类似的MA曲线，可以选择`verbose=True`来
做到。

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


### Stock Trading Indicator Visualization （股票交易指标图）
 
Currently, there are many commonly used indicators supported in this tool 
（目前，这个工具支持画出以下的指标）:

- MA (Moving Average， 移动平均线): `si.plot_ma()`
- MD (Moving Deviation， 移动标准差曲线): `si.plot_md()`
- EMA (Exponential Moving Average， 指数移动平均线): `si.plot_ema()`
- MACD (Moving Average Convergence/Divergence，指数平滑移动均线): `si.plot_macd()`
- KDJ （随机指标）: `si.plot_kdj`
- RSI (Relative Strength Index，相对强弱指标): `si.plot_rsi()`
- VRSI (Volumn Relative Strength Index，量相对强弱指标): `si.plot_vrsi()`
- Volumn change（量变指标）: `si.plot_volumn()`
- VMA (Volumn Moving Average，量移动平均线): `si.plot_vma()`
- VSTD（成交量标准差）: `si.plot_vstd()`
- VMACD (Volumn Moving Average Convergence/Divergence，量指数平滑异同平均线): `si.plot_vmacd()`
- ENV（轨道线）: `si.plot_env()`
- VOSC (Volumn Oscillator，量震荡指标): `si.plot_vosc()`
- MI (Momentum Indicator，动力指标): `si.plot_mi()`
- MIKE（麦克指标）: `si.plot_mike()`
- ADTM（动态买卖气指标）: `si.plot_adtm()`
- OBV (On Balance Volumn，能量潮曲线): `si.plot_obv()`
- RC (Price rate of Change，变化率指标): `si.plot_rc()`
- BOLL (BOLL line，布林线): `si.plot_boll()`
- BBIBOLL (BBI BOLL line，多空布林线): `si.plot_bbiboll()`
- ATR (Average True Ranger，真实波幅): `si.plot_atr()`
- CDP (Contrarian Operation，逆势操作指标): `si.plot_cdp()`
- SAR (Stop And Reverse，停损点转向指标): `si.plot_sar()`
- MTM (Momentum Index，动量指标): `si.plot_mtm()`
- DMI (Directional Movement Index, 动向指标): `si.plot_dmi()`


And there are several options to tune with（一些可以其他的选项）:

- Choose to plot with the stock price by defining `verbose` to `True` （是否将股票价格一并绘出）
- Choose the number of recent trading days of stock information to 
plot via setting `head`. （选择最近N日的股票价格来绘出）
- Choose which indicators are included in the plot, e.g. only plot `5-day`
and `60-day` line of MA indicator by setting `ns` to `[5, 60]`. （当有多条指标线绘出时，可以选择
只绘出其中的指定的线而不是全部绘出）

And some other more for specific indicators, please check out the docstrings （每个指标可能都有
一些自己独有的参数，可以查看公式注释）.


### Get the original stock data in Pandas DataFrame （以Pandas DataFrame的形式得到原始数据）

如果你想利用原始数据自己做一些有意思的项目，可以选择`si.show_data()`来得到原始股票数据，这些数据将以
Pandas DataFrame的形式返回。

If you would love to play with the data and do some other more fancy stuff,
you could also use the tool as a scrapper. Simply use `si.show_data()`
could return the data in Pandas DataFrame.


### Get the calculated indicator data in Pandas DataFrame (以Pandas DataFrame的形式得到计算出来的指标数据)

你也可以得到计算好的指标数据，你只需要用指标名称即可，而不需要绘出，比如`si.macd()`。

If you do not like the plot, and want to do other fancy analysis or visualization,
it is certainly okay! And you just need to call the indicator name, e.g. `si.vosc()`, 
or `si.macd()`, then it will return the subset with those indicators in it.

## Gallery （样例）

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


- Example7

```python
si = StockInsider("sh603019")
si.plot_vma(verbose=True)
```

![Example 7](https://github.com/charlesdong1991/StockInsider/blob/master/examples/example7.png)


- Example8

```python
si = StockInsider("sh603019")
si.plot_vmacd(head=60)
```

![Example 8](https://github.com/charlesdong1991/StockInsider/blob/master/examples/example8.png)


- Example9

```python
si = StockInsider("sh603019")
si.plot_env(verbose=True, head=60)
```

![Example 9](https://github.com/charlesdong1991/StockInsider/blob/master/examples/example9.png)

- Example10

```python
si = StockInsider("sh603019")
si.plot_mike(head=60, ns=["ws", "wr"], verbose=True)
```

![Example 10](https://github.com/charlesdong1991/StockInsider/blob/master/examples/example10.png)


- Example11

```python
si = StockInsider("sh603019")
si.plot_adtm(head=120)
```

![Example 11](https://github.com/charlesdong1991/StockInsider/blob/master/examples/example11.png)


- Example12

```python
si = StockInsider("sh603019")
si.plot_bbiboll(head=80, n=11, m=9, verbose=True)
```

![Example 12](https://github.com/charlesdong1991/StockInsider/blob/master/examples/example12.png)


- Example13

```python
si = StockInsider("sh603019")
si.plot_cdp(verbose=False)
```

![Example 13](https://github.com/charlesdong1991/StockInsider/blob/master/examples/example13.png)


- Example14

```python
si = StockInsider("sh603019")
si.plot_sar(head=90, verbose=True)
```

![Example 14](https://github.com/charlesdong1991/StockInsider/blob/master/examples/example14.png)

- Example15

```python
si = StockInsider("sh603019")
si.plot_dmi()
```

![Example 15](https://github.com/charlesdong1991/StockInsider/blob/master/examples/example15.png)


## Donation (打赏)
It takes time and efforts to make the tool, and if you like it, you could
also support the author by donation via Wechat Pay :)

<img src="https://github.com/charlesdong1991/StockInsider/blob/master/examples/donation.png" height="240" weight="240">
