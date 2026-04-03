import json
from datetime import datetime
from typing import Dict

from langchain.tools import tool

from .transport_tool import get_transport_prices
from .food_price_tool import estimate_food_prices
from .search_utils import search_web, extract_price_range, extract_first_url


def _safe_float(value: float) -> float:
    return float(value) if value is not None else 0.0


def _estimate_hotel(destination: str, budget_level: str) -> Dict:
    query = f"average hotel price per night {destination} {budget_level}"
    text = search_web(query)
    min_price, max_price, currency = extract_price_range(text)
    per_night = min_price if max_price is None else (min_price + max_price) / 2

    return {
        "per_night": _safe_float(per_night),
        "currency": currency or "USD",
        "source": extract_first_url(text) or "",
    }


def _estimate_activities(destination: str) -> Dict:
    query = f"average daily activities cost {destination} traveler"
    text = search_web(query)
    min_price, max_price, currency = extract_price_range(text)
    per_day = min_price if max_price is None else (min_price + max_price) / 2

    return {
        "per_day": _safe_float(per_day),
        "currency": currency or "USD",
        "source": extract_first_url(text) or "",
    }


@tool
def calculate_trip_budget(destination: str, origin: str, start_date: str, end_date: str, travelers: int, budget_level: str) -> str:
    """
    Calculate a trip budget by combining transport, food, hotel, and activities.
    Input schema: { destination, origin, start_date, end_date, travelers, budget_level }
    """
    try:
        start = datetime.fromisoformat(start_date).date()
        end = datetime.fromisoformat(end_date).date()
        nights = max((end - start).days, 1)
        days = nights + 1

        transport_raw = json.loads(
            get_transport_prices.run(
                {
                    "origin": origin,
                    "destination": destination,
                    "date": start_date,
                    "modes": ["flight", "train", "bus"],
                }
            )
        )
        cheapest_mode = min(
            (mode for mode in transport_raw.values()),
            key=lambda item: item.get("min_price", 0.0) or float("inf"),
        )

        transport_amount = cheapest_mode.get("min_price", 0.0)
        transport_currency = cheapest_mode.get("currency", "USD")

        food_raw = json.loads(
            estimate_food_prices.run(
                {
                    "city": destination,
                    "country": "",
                    "days": days,
                    "budget_level": budget_level,
                }
            )
        )

        hotel = _estimate_hotel(destination, budget_level)
        activities = _estimate_activities(destination)

        accommodation_total = hotel["per_night"] * nights
        activities_total = activities["per_day"] * days

        food_total = food_raw.get("total_food_cost", 0.0)
        per_day_food = food_raw.get("daily_food_budget", 0.0)

        subtotal = transport_amount + accommodation_total + food_total + activities_total
        misc = subtotal * 0.1
        total_per_person = subtotal + misc
        grand_total = total_per_person * max(int(travelers), 1)

        result = {
            "transport": {"amount": round(transport_amount, 2), "mode": cheapest_mode.get("mode", "flight"), "currency": transport_currency},
            "accommodation": {"amount": round(accommodation_total, 2), "per_night": round(hotel["per_night"], 2), "nights": nights, "currency": hotel["currency"]},
            "food": {"amount": round(food_total, 2), "per_day": round(per_day_food, 2), "currency": food_raw.get("currency", "USD")},
            "activities": {"amount": round(activities_total, 2), "per_day": round(activities["per_day"], 2), "currency": activities["currency"]},
            "miscellaneous": {"amount": round(misc, 2), "note": "~10% buffer"},
            "total_per_person": round(total_per_person, 2),
            "grand_total": round(grand_total, 2),
            "currency": transport_currency,
            "confidence": "low" if transport_amount == 0 else "medium",
        }

        return json.dumps(result)

    except Exception as exc:
        return json.dumps({"error": str(exc)})
