import pytest

from ai.model import call_trading_model, call_analysis_model
from acorn.adapter import get_account_portfolio_json
from acorn.util import is_valid_ticker


def test_call_trading_model():
    port = get_account_portfolio_json() # build some fake data instead of this
    res = call_trading_model(port)
    print(res)
    assert res is not None
    assert res.confidence in ["low", "medium", "high"]
    assert len(res.overall_reasoning) > 0
    for action in res.actions:
        assert is_valid_ticker(action.symbol)


def test_call_analysis_model():
    port = get_account_portfolio_json() # build some fake data instead of this
    res = call_analysis_model(port)
    assert res is not None
    assert len(res) > 0