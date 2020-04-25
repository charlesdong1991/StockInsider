import pytest

from insider.stock import Stock


def test_wrong_stock_code():
    msg = "Stock code needs to be either sz or sh"
    with pytest.raises(ValueError, match=msg):
        Stock("aa123445")

    msg = "Invalid code length: requires 8"
    with pytest.raises(ValueError, match=msg):
        Stock("sh11111")

    msg = "Code must be all digits after sh or sz"
    with pytest.raises(ValueError, match=msg):
        Stock("sha12344")


@pytest.mark.parametrize("ktype", ["a", "A", "WM"])
def test_wrong_ktype(ktype):
    msg = "Invalid ktype is given"
    with pytest.raises(ValueError, match=msg):
        Stock("sh123456", ktype=ktype)
