import json
from typing import List, Dict

from langchain.tools import tool

from .search_utils import search_web, extract_price_range, extract_first_url


def _build_query(origin: str, destination: str, date: str, mode: str) -> str:
    if mode == "flight":
        return f"cheapest flights {origin} to {destination} {date} price"
    if mode == "train":
        return f"{origin} to {destination} train ticket price {date}"
    return f"{origin} to {destination} bus fare {date}"


def _price_block(mode: str, query: str) -> Dict:
    text = search_web(query)
    min_price, max_price, currency = extract_price_range(text)
    source_url = extract_first_url(text) or ""

    return {
        "min_price": float(min_price) if min_price is not None else 0.0,
        "max_price": float(max_price) if max_price is not None else 0.0,
        "currency": currency or "USD",
        "source": "DuckDuckGo" if min_price is not None else "Estimate unavailable",
        "booking_url": source_url,
        "mode": mode,
    }


@tool
def get_transport_prices(origin: str, destination: str, date: str, modes: List[str]) -> str:
    """
    Fetch transport price ranges for flight/train/bus.
    Input schema: { origin, destination, date, modes }
    """
    try:
        modes = modes or ["flight", "train", "bus"]
        results = {}

        for mode in modes:
            query = _build_query(origin, destination, date, mode)
            results[mode] = _price_block(mode, query)

        return json.dumps(results)

    except Exception as exc:
        return json.dumps({"error": str(exc)})
