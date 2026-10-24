import pytest
import pandas as pd
import sys

from unittest.mock import patch
from ibapi.contract import Contract
from ibapi.order import Order
from acorn.engine import (
    make_contract,
    make_order,
    get_mkt_price,
    validate_lmt_MoE,
    place_trade
)
from acorn.util import eval_user_res, is_valid_ticker
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


def test_place_trade():
    limit_price = 10
    c = Contract()
    c.symbol = "AAPL"
    c.secType = "STK"
    c.exchange = "SMART"
    c.currency = "USD"
    with patch("telegram.telegram.telegram_client.tel_notify") as mock_tel_notify:
        place_trade("NVDA", "BUY", 5, "LMT", limit_price)
        mock_tel_notify.assert_called_once()
    with (
        patch("acorn.engine.submit_order") as mock_submit_order,
        patch("telegram.telegram.telegram_client.tel_notify") as mock_tel_notify,
    ):
        place_trade("AAPL", "BUY", 5, "LMT", get_mkt_price(c))
        mock_submit_order.assert_called_once()
        mock_tel_notify.assert_called_once()


def test_valid_ticker():
    assert is_valid_ticker("aapl") is True
    assert is_valid_ticker("NVDA") is True
    assert is_valid_ticker("NVIDIA") is False


def test_config_loads():
    from acorn.config import config

    assert config is not None
    assert config.ibg_port in [4001, 4002]
    assert config.data_relevancy in range(0, 6)
    assert config.limit_MoE < 1 and config.limit_MoE > 0
    assert config.model != ""
    assert config.timeout > 0
    assert config.openai_key is not None
    assert config.openai_key != ""
    assert config.telegram_bot_key is not None
    assert config.telegram_bot_key != ""