# Constants used in Stock class
STOCK_URL = (
    "http://api.finance.ifeng.com/{ktype}/?code={code}&type=last"
)  # URL to fetch stock information
MA_COLS = ["ma5", "ma10", "ma20"]  # columns from dataset to use to plot MA lines
MA_COLORS = ["black", "orange", "red"]  # colors to choose to plot different MA lines
KTYPE_CONVERSION = {
    "D": "akdaily",
    "W": "akweekly",
    "M": "akmonthly",
}  # Conversion for the type of K-lines for URL
KTYPES = ["D", "W", "M"]  # Allowed types of K-lines
DAY_COL = ["day"]  # date column from fetched dataset
NUMERIC_COLUMNS = [
    "open",
    "high",
    "close",
    "low",
    "volumn",
    "price_change",
    "percent_change",
    "ma5",
    "ma10",
    "ma20",
    "v_ma5",
    "v_ma10",
    "v_ma20",
]  # all numeric columns from fetched dataset

# Constants used in Mixins
MOVING_COLS = ["day", "close"]  # cols used for Moving indicator mixin for `close`
MOVING_VOLUMN_COLS = ["day", "volumn"]  # cols used for Moving indicator mixin for `volumn`
HIGH_LOW_COLS = ["day", "close", "high", "low"]  # cols used for KDJ indicator mixin
VOLUMN_VOLS = ["day", "close", "volumn"]  # cols used for RSI & VRSI & OBV indicator mixin
ADTM_COLS = ["day", "open", "close", "high", "low"]  # cols used for ADTM indicator mixin

# Constants used in StockInsider class
MA_N = [5, 10, 20, 60]  # Number of days counted for MA indicator
MD_N = [5, 10, 20]  # Number of days counted for MD indicator
EXPMA_N = [5, 10, 20, 60]  # Number of days counted for EMA indicator
RSI_N = [6, 12, 24]  # Number of days counted for RSI/VRSI indicator
MIKE_COLS = ["wr", "mr", "sr", "ws", "ms", "ss"]  # Columns defined in MIKE indicator
CDP_COLS = ["ah", "nh", "cdp", "al", "nl"]  # Columns defined in CDP indicator

# Constants used in SARIndicator Mixin
INITIAL_TREND = True
INITIAL_AF = 0.02
