import json
from typing import Dict

from langchain.tools import tool

from .search_utils import search_web, extract_price_range, extract_first_url


def _search_for_budget(city: str, country: str, budget_level: str) -> Dict:
    query = f"average meal cost {city} {country} {budget_level} traveler 2024"
    text = search_web(query)
    min_price, max_price, currency = extract_price_range(text)

    if min_price is None and max_price is None:
        return {
            "breakfast_avg": 8.0,
            "lunch_avg": 12.0,
            "dinner_avg": 18.0,
            "currency": "USD",
            "source": "estimate",
            "url": "",
        }

    avg = min_price if max_price is None else (min_price + max_price) / 2
    return {
        "breakfast_avg": round(avg * 0.25, 2),
        "lunch_avg": round(avg * 0.35, 2),
        "dinner_avg": round(avg * 0.4, 2),
        "currency": currency or "USD",
        "source": "DuckDuckGo",
        "url": extract_first_url(text) or "",
    }


@tool
def estimate_food_prices(city: str, country: str, days: int, budget_level: str) -> str:
    """
    Estimate per-day food costs for a city.
    Input schema: { city, country, days, budget_level }
    """
    try:
        budget_level = (budget_level or "mid").lower()
        base = _search_for_budget(city, country, budget_level)
        daily = base["breakfast_avg"] + base["lunch_avg"] + base["dinner_avg"]
        total = daily * max(int(days), 1)

        result = {
            "breakfast_avg": base["breakfast_avg"],
            "lunch_avg": base["lunch_avg"],
            "dinner_avg": base["dinner_avg"],
            "daily_food_budget": round(daily, 2),
            "total_food_cost": round(total, 2),
            "currency": base["currency"],
            "notes": "Prices vary by neighborhood and season.",
            "sources": [base["url"]] if base["url"] else [],
        }

        return json.dumps(result)

    except Exception as exc:
        return json.dumps({"error": str(exc)})
