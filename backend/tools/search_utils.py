import re
import requests
from typing import Optional, Tuple


def search_web(query: str) -> str:
    """Lightweight web search via DuckDuckGo HTML (best-effort)."""
    url = "https://duckduckgo.com/html/"
    params = {"q": query}
    headers = {"User-Agent": "WandrAgent/1.0"}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception:
        return ""


def extract_first_url(text: str) -> Optional[str]:
    match = re.search(r"https?://[^\s\"'<>]+", text)
    return match.group(0) if match else None


def extract_price_range(text: str) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    """Extract a basic price range and currency symbol/code from text."""
    if not text:
        return None, None, None

    currency_pattern = r"USD|EUR|GBP|INR|JPY|AUD|CAD"
    symbol_pattern = r"[$€£₹¥]"

    range_pattern = re.compile(
        rf"(?P<cur>{currency_pattern}|{symbol_pattern})?\s*(?P<min>\d+(?:,\d{{3}})*(?:\.\d+)?)\s*(?:-|–|to)\s*(?P<max>\d+(?:,\d{{3}})*(?:\.\d+)?)(?:\s*(?P<cur2>{currency_pattern}|{symbol_pattern}))?",
        flags=re.IGNORECASE,
    )

    matches = list(range_pattern.finditer(text))
    values = []
    currency = None

    for match in matches:
        cur = match.group("cur") or match.group("cur2")
        if cur:
            currency = _normalize_currency(cur)
        min_val = float(match.group("min").replace(",", ""))
        max_val = float(match.group("max").replace(",", ""))
        values.extend([min_val, max_val])

    # Match individual prices
    price_matches = re.findall(
        rf"(?:{currency_pattern})\s?\d+(?:,\d{{3}})*(?:\.\d+)?|{symbol_pattern}\s?\d+(?:,\d{{3}})*(?:\.\d+)?|\d+(?:,\d{{3}})*(?:\.\d+)?\s?(?:{currency_pattern})",
        text,
        flags=re.IGNORECASE,
    )

    if not price_matches:
        if not values:
            return None, None, None
    else:
        for match in price_matches:
            cleaned = match.strip()
            symbol_match = re.search(symbol_pattern, cleaned)
            code_match = re.search(currency_pattern, cleaned, flags=re.IGNORECASE)
            if symbol_match:
                currency = _normalize_currency(symbol_match.group(0))
            if code_match:
                currency = _normalize_currency(code_match.group(0))

            number_match = re.search(r"\d+(?:,\d{3})*(?:\.\d+)?", cleaned)
            if number_match:
                values.append(float(number_match.group(0).replace(",", "")))

    if not values:
        return None, None, None

    min_val, max_val = min(values), max(values)
    if not _is_reasonable_price(min_val, max_val, currency):
        return None, None, currency

    return min_val, max_val, currency


def _is_reasonable_price(min_val: float, max_val: float, currency: Optional[str]) -> bool:
    if min_val <= 0 or max_val <= 0:
        return False

    if max_val / max(min_val, 1) > 100:
        return False

    currency = (currency or "USD").upper()
    if currency in {"USD", "EUR", "GBP", "AUD", "CAD"}:
        return max_val <= 5000
    if currency in {"INR"}:
        return max_val <= 500000
    if currency in {"JPY"}:
        return max_val <= 500000

    return max_val <= 100000


def _normalize_currency(value: str) -> Optional[str]:
    value = value.upper()
    symbols = {
        "$": "USD",
        "€": "EUR",
        "£": "GBP",
        "₹": "INR",
        "¥": "JPY",
    }
    return symbols.get(value, value if value.isalpha() else None)
