import threading
import queue
import logging
import pandas as pd

from ibapi.common import OrderId
from threading import Event
from queue import Queue
from pandas.core.frame import DataFrame
from _thread import lock
from typing import Any, override

from ibapi.client import EClient, OrderId
from ibapi.wrapper import EWrapper

logger = logging.getLogger(__name__)


# Wrapper for handling callback functions called by the gateway connection
# custom functionality can be added here
class IBApp(EWrapper, EClient):
    def __init__(self) -> None:
        EClient.__init__(self, wrapper=self)
        self.order_id: OrderId | None = None
        self.connected_event: Event = threading.Event()
        self.request_positions_event: Event = threading.Event()
        self.account_summary_event: Event = threading.Event()
        self.data_queue: Queue[dict[str, str | float | int]] = queue.Queue(maxsize=0)   # data accessible to main thread
        self.positions: DataFrame = pd.DataFrame(data=[], columns=['Account', 'Symbol', 'Quantity', 'Average Cost'])
        self.account_values: dict[str, str | float | int] = {}
        self.open_orders: dict[Any, Any] = {}
        self.lock: lock = threading.Lock()

    # called on init
    @override
    def nextValidId(self, orderId: OrderId) -> None:
        with self.lock:
            self.order_id = orderId
        self.connected_event.set()
        logger.info(f"Connected. Next order ID: {orderId}")


    def get_next_order_id(self) -> OrderId:
        with self.lock:
            if self.order_id is not None:
                oid = self.order_id
                self.order_id += 1
                return oid
            else:
                logger.error("next_order_id is null in get_next_order_id()")
                raise RuntimeError("next_order_id is null in get_next_order_id()")


    @override
    def connectionClosed(self) -> None:
        logger.warning("Connection closed — need reconnect logic here")
        self.connected_event.clear()


    @override
    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson="") -> None:
        # Codes 2104, 2106, 2158 etc. are informational, not errors
        if errorCode in (2104, 2106, 2158):
            logger.info(f"Info: {errorString}")
        else:
            logger.error(f"Error {errorCode} (reqId {reqId}): {errorString}")


    @override
    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice) -> None:
        logger.info(f"Order {orderId}: {status}, filled={filled}, avgPrice={avgFillPrice}")
        with self.lock:
            self.open_orders[orderId] = status


    @override
    def position(self, account, contract, position, avgCost) -> None:
        with self.lock:
            index: str = str(account) + str(contract.symbol)
            self.positions.loc[index] = account, contract.symbol, position, avgCost


    @override
    def positionEnd(self) -> None:
        return self.request_positions_event.set()


    @override
    def updateAccountValue(self, key: str, val: str, currency: str, accountName: str) -> None:
        self.account_values[key] = float(val)


    @override
    def accountSummary(self, reqId: int, account: str, tag: str, value: str, currency: str) -> None:
        self.account_values[tag] = value


    @override
    def accountSummaryEnd(self, reqId) -> None:
        return self.account_summary_event.set()


    @override
    def tickPrice(self, reqId, tickType, price, attrib) -> None:
        self.data_queue.put(item=({"event": "ticker", "req_id": reqId, "tick_type": tickType, "price": price}))


    @override
    def historicalData(self, reqId, bar) -> None:
        print(f"reqId={reqId} {bar.date} O:{bar.open} H:{bar.high} L:{bar.low} C:{bar.close} V:{bar.volume}")
        self.data_queue.put(item=("bar", reqId, bar))


    @override
    def historicalDataEnd(self, reqId, start, end) -> None:
        print(f"Historical data complete for reqId {reqId}: {start} to {end}")
        self.data_queue.put(item=("bars_done", reqId))