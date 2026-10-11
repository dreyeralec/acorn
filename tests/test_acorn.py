import pytest
import pandas as pd
import sys

from ibapi.contract import Contract
from ibapi.order import Order
from acorn.engine import (
    make_contract,
    make_order,
    get_mkt_price,
    validate_lmt_MoE
)
from acorn.util import eval_user_res
from acorn.adapter import get_account_data, get_portfolio_data

def test_make_valid_contract():
    c = Contract()
    c.symbol = "AAPL"
    c.secType = "STK"
    c.exchange = "SMART"
    c.currency = "USD"
    t = make_contract("AAPL")
    assert c.symbol == t.symbol
    assert c.secType == t.secType
    assert c.exchange == t.exchange
    assert c.currency == t.currency


def test_make_invalid_contract_ticker():
    t = "NVIDIA"
    with pytest.raises(ValueError, match=f"Invalid ticker {t}"):
        _ = make_contract(t)


def test_make_invalid_contract_sec_type():
    t = "NVDA"
    st = "LOAN"
    with pytest.raises(ValueError, match=f"Invalid or unsupported security type {st}"):
        _ = make_contract(symbol=t, sec_type=st)


def test_make_invalid_contract_exchange():
    t = "PLTR"
    et = "GARAGE SALE"
    with pytest.raises(ValueError, match=f"Invalid or unsupported exchange type {et}"):
        _ = make_contract(symbol=t, exchange=et)


def test_make_invalid_contract_currency():
    t = "MSFT"
    c = "EURO"
    with pytest.raises(ValueError, match=f"Invalid or unsupported currency type {c}"):
        _ = make_contract(symbol=t, currency=c)


def test_make_valid_order():
    o = Order()
    o.action = "BUY"
    o.orderType = "MKT"
    o.totalQuantity = 2
    t = make_order("BUY", "MKT", None, 2)
    assert o.action == t.action
    assert o.orderType == t.orderType
    assert o.lmtPrice == t.lmtPrice
    assert o.totalQuantity == t.totalQuantity


def test_make_invalid_order_action():
    a = "STEAL"
    ot = "MKT"
    l = None
    q = 2
    with pytest.raises(ValueError, match=f"Invalid or unsupported action {a}"):
        _ = make_order(a, ot, l, q)


def test_make_invalid_order_type():
    a = "BUY"
    ot = ""
    l = None
    q = 2
    with pytest.raises(ValueError, match=f"Invalid or unsupported order type {ot}"):
        _ = make_order(a, ot, l, q)


def test_make_invalid_order_quantity():
    a = "SELL"
    ot = "MKT"
    l = None
    q = -2
    with pytest.raises(ValueError, match=f"Invalid quantity {q}"):
        _ = make_order(a, ot, l, q)

# test limit price code paths
def test_make_invalid_order_no_limit_price():
    a = "BUY"
    ot = "LMT"
    l = None
    q = 2
    with pytest.raises(ValueError, match=f"Order type {ot} requires a limit price"):
        _ = make_order(a, ot, l, q)


def test_market_order_with_limit_price():
    o = Order()
    o.action = "BUY"
    o.orderType = "MKT"
    o.lmtPrice = 6
    o.totalQuantity = 2
    t = make_order("BUY", "MKT", 6, 2)
    assert o.action == t.action
    assert o.orderType == t.orderType
    assert o.lmtPrice != t.lmtPrice # IB defaults lmtPrice to float max value
    assert t.lmtPrice == sys.float_info.max
    assert o.totalQuantity == t.totalQuantity
    

def test_handle_response_yes():
    assert eval_user_res("Yes") is True
    assert eval_user_res("yes please") is True


def test_handle_response_no():
    assert eval_user_res("no") is False
    assert eval_user_res("") is False


def test_fetch_portfolio_data():
    data = get_portfolio_data()
    assert type(data) == pd.DataFrame
    assert data.columns.to_list() == ['Account', 'Symbol', 'Quantity', 'Average Cost']


def test_fetch_account_data():
    data = get_account_data()
    assert type(data) == dict
    assert list(data.keys()) == ['AvailableFunds', 'BuyingPower', 'NetLiquidation', 'TotalCashValue']


def test_get_market_price():
    c = Contract()
    c.symbol = "AAPL"
    c.secType = "STK"
    c.exchange = "SMART"
    c.currency = "USD"
    curr = get_mkt_price(c)
    assert curr is not None
    assert curr > 0


def test_validate_lmt_MoE():
    c = Contract()
    c.symbol = "AAPL"
    c.secType = "STK"
    c.exchange = "SMART"
    c.currency = "USD"
    assert validate_lmt_MoE(c, 1.2) is False
    assert validate_lmt_MoE(c, get_mkt_price(c)) is True