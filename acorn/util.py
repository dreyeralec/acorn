import pandas as pd

from .config import WakeUpEvent, config
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


NASDAQ_TICKERS_URL = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
OTHER_TICKERS_URL = "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"


def load_us_tickers() -> set[str]:
    """Load all major US market tickers from nasdaqtrader.com.
    
        Returns:
            Set of all valid tickers.
    """
    nasdaq = pd.read_csv(NASDAQ_TICKERS_URL, sep="|")
    other = pd.read_csv(OTHER_TICKERS_URL, sep="|")
    nasTickers = nasdaq.iloc[:,[0]]
    otherTickers = other.iloc[:,[0]]
    nasTickers.columns = otherTickers.columns

    allTickers = pd.concat([nasTickers, otherTickers], ignore_index=True)

    return set(allTickers["ACT Symbol"])


US_MARKET_TICKERS = load_us_tickers()


def is_valid_ticker(symbol: str) -> bool:
    """Check if a ticker is valid on major US Markets.

        Args:
            symbol: Ticker to be validated.

        Returns:
            If ticker was validated.
    """
    return symbol.upper() in US_MARKET_TICKERS


def time_to_next_position_update() -> tuple[float, str]:
    """Gets amount of time for ACORN to sleep until the next position update window.

        Returns:
            Tuple containing seconds till the next event and the name of the event
    """
    now: datetime = datetime.now(ZoneInfo("America/New_York"))
    events: list[WakeUpEvent] = sorted(config.wake_up_events, key=lambda e: (e.hour, e.minute, e.second))
    if not events:
        raise ValueError("No wake up events were configured")
    for days_ahead in range(4):
        target_date = now.date() + timedelta(days=days_ahead)
        if target_date.weekday() > 4:
            continue
        for event in events:
            target = now.replace(
                year=target_date.year,
                month=target_date.month,
                day=target_date.day,
                hour=event.hour,
                minute=event.minute,
                second=event.second,
                microsecond=0
            )
            if target > now:
                return (target - now).total_seconds(), event.type

    raise RuntimeError("Couldn't find the next wake up event")


def eval_user_res(res: str | None) -> bool:
    """Process the user's telegram message in response to a trading recommendation.
    
        Args:
            response: String of the user's response.

        Returns:
            If the user confirmed or denied the recommendation.
    """
    if res is None or "yes" not in res.lower():
        return False
    return True