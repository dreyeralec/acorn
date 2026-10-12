import logging
import json
from queue import Empty, ShutDown

from ib.ib import IBApp
from pandas import DataFrame
from ib.gateway import connect_ib_gateway

logger = logging.getLogger(__name__)


def get_portfolio_data() -> DataFrame:
    """Fetch portfolio data and return as a DataFrame.
    
        Returns:
            Dataframe of portfolio positions.
    """
    gateway: IBApp = connect_ib_gateway()
    gateway.request_positions_event.clear()
    gateway.reqPositions()
    if not gateway.request_positions_event.wait(10):
        raise TimeoutError("Timed out waiting for request positions")
    gateway.cancelPositions()
    return gateway.positions.copy()


def get_portfolio_data_json() -> str | None:
    """Fetch current portfolio positions as a JSON string.
    
        Returns:
            String of portfolio positions.
    """
    return get_portfolio_data().to_json("records")


def get_account_data() -> dict[str, str | float | int]:
    """Fetch current account info as a dictionary.
    
        Returns:
            Account data as a dictionary.
    """
    gateway: IBApp = connect_ib_gateway()
    tags = "NetLiquidation,TotalCashValue,BuyingPower,AvailableFunds,UnrealizedPnL,RealizedPnL"
    gateway.account_summary_event.clear()
    gateway.reqAccountSummary(9001, "All", tags)
    if not gateway.account_summary_event.wait(10):
        raise TimeoutError("Timed out waiting for account summary")
    gateway.cancelAccountSummary(9001)
    return gateway.account_values.copy()


def get_account_data_json() -> str:
    """Fetch current account info as a JSON string.

        Returns:
            String of account data.
    """
    return json.dumps(get_account_data())


def get_account_portfolio_json() -> str:
    """Fetch account and portfolio information as JSON string.
    
        Returns:
            Combined account and portfolio data as a string.
    """
    portfolio = get_portfolio_data_json()
    account = get_account_data_json()
    if portfolio is None:
        raise AttributeError(f"Portfolio data was empty portfolio: {portfolio}")
    return json.dumps(account + portfolio)


def consume_queue(gateway: IBApp, timeout: int = 10) -> dict[str, str | float] | None:
    try:
        return gateway.data_queue.get(timeout=timeout)
    except (Empty, ShutDown):
        return None