import json
import math
import re
import random
import xml.etree.ElementTree as ET
from html import unescape
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote_plus, urlparse

from langchain.tools import tool
import requests

from .flight_tool import search_flights_structured

INDIAN_ROUTE_DATA: Dict[str, Dict] = {
    "mumbai-pune": {
        "train": {"time": "3h", "price_range": "INR 150-800", "frequency": "Hourly"},
        "bus": {"time": "3.5h", "price_range": "INR 200-600", "frequency": "Every 30 min"},
        "flight": {"time": "1h", "price_range": "INR 2500-6000", "frequency": "4 flights/day"},
    },
    "delhi-agra": {
        "train": {"time": "2h", "price_range": "INR 120-950", "frequency": "Every 1-2 hours"},
        "bus": {"time": "4h", "price_range": "INR 250-700", "frequency": "Hourly"},
        "flight": {"time": "N/A", "price_range": "INR 0-0", "frequency": "Limited"},
    },
    "bangalore-chennai": {
        "train": {"time": "5h", "price_range": "INR 180-950", "frequency": "Every 2 hours"},
        "bus": {"time": "6h", "price_range": "INR 350-1200", "frequency": "Every 45 min"},
        "flight": {"time": "1h", "price_range": "INR 2200-6500", "frequency": "8 flights/day"},
    },
    "delhi-mumbai": {
        "train": {"time": "15h", "price_range": "INR 600-3500", "frequency": "Daily"},
        "bus": {"time": "24h", "price_range": "INR 1800-3500", "frequency": "Daily"},
        "flight": {"time": "2h 10m", "price_range": "INR 4200-12000", "frequency": "20+ flights/day"},
    },
    "mumbai-goa": {
        "train": {"time": "8h", "price_range": "INR 350-1800", "frequency": "Daily"},
        "bus": {"time": "11h", "price_range": "INR 900-2200", "frequency": "Every 2 hours"},
        "flight": {"time": "1h 15m", "price_range": "INR 2800-9000", "frequency": "10 flights/day"},
    },
    "kolkata-delhi": {
        "train": {"time": "17h", "price_range": "INR 700-3800", "frequency": "Daily"},
        "bus": {"time": "30h", "price_range": "INR 2200-4800", "frequency": "Daily"},
        "flight": {"time": "2h 20m", "price_range": "INR 4500-13000", "frequency": "12 flights/day"},
    },
    "hyderabad-bangalore": {
        "train": {"time": "10h", "price_range": "INR 300-1600", "frequency": "Daily"},
        "bus": {"time": "9h", "price_range": "INR 700-1900", "frequency": "Hourly"},
        "flight": {"time": "1h 10m", "price_range": "INR 2600-8500", "frequency": "9 flights/day"},
    },
    "chennai-hyderabad": {
        "train": {"time": "12h", "price_range": "INR 350-1750", "frequency": "Daily"},
        "bus": {"time": "11h", "price_range": "INR 850-2200", "frequency": "Every 90 min"},
        "flight": {"time": "1h 20m", "price_range": "INR 3000-9000", "frequency": "8 flights/day"},
    },
    "delhi-jaipur": {
        "train": {"time": "4.5h", "price_range": "INR 200-1200", "frequency": "Every 2 hours"},
        "bus": {"time": "6h", "price_range": "INR 300-1100", "frequency": "Every 30 min"},
        "flight": {"time": "1h", "price_range": "INR 2800-8000", "frequency": "3 flights/day"},
    },
    "delhi-varanasi": {
        "train": {"time": "11h", "price_range": "INR 350-2200", "frequency": "Daily"},
        "bus": {"time": "14h", "price_range": "INR 900-2300", "frequency": "Daily"},
        "flight": {"time": "1h 30m", "price_range": "INR 3200-9500", "frequency": "7 flights/day"},
    },
    "mumbai-ahmedabad": {
        "train": {"time": "6h", "price_range": "INR 250-1400", "frequency": "Every 2 hours"},
        "bus": {"time": "8h", "price_range": "INR 500-1700", "frequency": "Hourly"},
        "flight": {"time": "1h 15m", "price_range": "INR 2500-7800", "frequency": "11 flights/day"},
    },
    "bangalore-goa": {
        "train": {"time": "13h", "price_range": "INR 300-1600", "frequency": "Daily"},
        "bus": {"time": "11h", "price_range": "INR 850-2200", "frequency": "Daily"},
        "flight": {"time": "1h 20m", "price_range": "INR 3200-9800", "frequency": "5 flights/day"},
    },
    "delhi-amritsar": {
        "train": {"time": "6h", "price_range": "INR 220-1300", "frequency": "Every 2 hours"},
        "bus": {"time": "8h", "price_range": "INR 500-1600", "frequency": "Hourly"},
        "flight": {"time": "1h 15m", "price_range": "INR 2600-8400", "frequency": "6 flights/day"},
    },
    "pune-hyderabad": {
        "train": {"time": "10h", "price_range": "INR 300-1700", "frequency": "Daily"},
        "bus": {"time": "11h", "price_range": "INR 700-2200", "frequency": "Daily"},
        "flight": {"time": "1h 20m", "price_range": "INR 3000-9000", "frequency": "6 flights/day"},
    },
    "kolkata-bhubaneswar": {
        "train": {"time": "6h", "price_range": "INR 250-1200", "frequency": "Every 2 hours"},
        "bus": {"time": "7h", "price_range": "INR 450-1200", "frequency": "Hourly"},
        "flight": {"time": "1h", "price_range": "INR 2300-7000", "frequency": "4 flights/day"},
    },
    "chennai-kochi": {
        "train": {"time": "12h", "price_range": "INR 320-1700", "frequency": "Daily"},
        "bus": {"time": "12h", "price_range": "INR 800-2000", "frequency": "Every 2 hours"},
        "flight": {"time": "1h 20m", "price_range": "INR 2800-8600", "frequency": "5 flights/day"},
    },
}

# European & International Train Routes
EUROPEAN_ROUTE_DATA: Dict[str, Dict] = {
    "london-paris": {
        "train": {"time": "3h 15m", "price_range": "GBP 25-120", "frequency": "Every 2 hours", "operator": "Eurostar"},
        "bus": {"time": "8h", "price_range": "GBP 15-50", "frequency": "Multiple daily", "operator": "FlixBus"},
    },
    "berlin-prague": {
        "train": {"time": "2h 30m", "price_range": "EUR 15-80", "frequency": "Multiple daily", "operator": "Czech Railways"},
        "bus": {"time": "4h", "price_range": "EUR 10-30", "frequency": "Multiple daily", "operator": "FlixBus"},
    },
    "budapest-vienna": {
        "train": {"time": "2h 45m", "price_range": "EUR 18-75", "frequency": "Multiple daily", "operator": "Austrian Railways"},
        "bus": {"time": "3h 30m", "price_range": "EUR 12-35", "frequency": "Multiple daily", "operator": "FlixBus"},
    },
    "vienna-zagreb": {
        "train": {"time": "6h", "price_range": "EUR 25-90", "frequency": "Daily", "operator": "Croatian Railways"},
        "bus": {"time": "7h", "price_range": "EUR 20-50", "frequency": "Multiple daily", "operator": "FlixBus"},
    },
    "amsterdam-brussels": {
        "train": {"time": "1h 50m", "price_range": "EUR 15-65", "frequency": "Hourly", "operator": "NS/SNCB"},
        "bus": {"time": "2h 30m", "price_range": "EUR 10-25", "frequency": "Multiple daily", "operator": "FlixBus"},
    },
    "munich-vienna": {
        "train": {"time": "2h 15m", "price_range": "EUR 20-90", "frequency": "Multiple daily", "operator": "ÖBB"},
        "bus": {"time": "3h", "price_range": "EUR 15-40", "frequency": "Multiple daily", "operator": "FlixBus"},
    },
    "barcelona-madrid": {
        "train": {"time": "2h 30m", "price_range": "EUR 25-150", "frequency": "Multiple daily", "operator": "Renfe"},
        "bus": {"time": "7h", "price_range": "EUR 15-40", "frequency": "Multiple daily", "operator": "FlixBus"},
    },
    "florence-rome": {
        "train": {"time": "2h 30m", "price_range": "EUR 20-80", "frequency": "Every 30 min", "operator": "Trenitalia"},
        "bus": {"time": "4h", "price_range": "EUR 12-30", "frequency": "Multiple daily", "operator": "FlixBus"},
    },
    "edinburgh-london": {
        "train": {"time": "7h", "price_range": "GBP 35-120", "frequency": "Multiple daily", "operator": "LNER"},
        "bus": {"time": "10h", "price_range": "GBP 20-60", "frequency": "Multiple daily", "operator": "FlixBus"},
    },
    "geneva-zurich": {
        "train": {"time": "3h", "price_range": "CHF 40-120", "frequency": "Hourly", "operator": "SBB"},
        "bus": {"time": "4h", "price_range": "CHF 25-60", "frequency": "Multiple daily", "operator": "FlixBus"},
    },
}

# Asian train routes
ASIAN_ROUTE_DATA: Dict[str, Dict] = {
    "bangkok-chiangmai": {
        "train": {"time": "13h", "price_range": "THB 500-1500", "frequency": "Daily", "operator": "Thai Railways"},
        "bus": {"time": "10h", "price_range": "THB 400-800", "frequency": "Multiple daily", "operator": "Local operators"},
    },
    "tokyo-kyoto": {
        "train": {"time": "2h 15m", "price_range": "JPY 13500-14320", "frequency": "Multiple daily", "operator": "JR"},
        "bus": {"time": "7h", "price_range": "JPY 2500-5000", "frequency": "Multiple daily", "operator": "Willer Express"},
    },
    "singapore-kuala-lumpur": {
        "train": {"time": "7h", "price_range": "SGD 45-95", "frequency": "Daily", "operator": "KTM"},
        "bus": {"time": "5h", "price_range": "SGD 20-35", "frequency": "Multiple daily", "operator": "Local operators"},
    },
    "hong-kong-guangzhou": {
        "train": {"time": "1h", "price_range": "HKD 75-220", "frequency": "Multiple daily", "operator": "MTR"},
        "bus": {"time": "2h 30m", "price_range": "HKD 50-120", "frequency": "Multiple daily", "operator": "Local operators"},
    },
}

INDIAN_CITY_COORDS = {
    "mumbai": (19.0760, 72.8777),
    "pune": (18.5204, 73.8567),
    "delhi": (28.6139, 77.2090),
    "agra": (27.1767, 78.0081),
    "bangalore": (12.9716, 77.5946),
    "chennai": (13.0827, 80.2707),
    "kolkata": (22.5726, 88.3639),
    "hyderabad": (17.3850, 78.4867),
    "jaipur": (26.9124, 75.7873),
    "varanasi": (25.3176, 82.9739),
    "ahmedabad": (23.0225, 72.5714),
    "goa": (15.2993, 74.1240),
    "amritsar": (31.6340, 74.8723),
    "bhubaneswar": (20.2961, 85.8245),
    "kochi": (9.9312, 76.2673),
}

# European city coordinates
EUROPEAN_CITY_COORDS = {
    "paris": (48.8566, 2.3522),
    "london": (51.5074, -0.1278),
    "berlin": (52.5200, 13.4050),
    "prague": (50.0755, 14.4378),
    "vienna": (48.2082, 16.3738),
    "budapest": (47.4979, 19.0402),
    "zagreb": (45.8150, 15.9819),
    "amsterdam": (52.3676, 4.9041),
    "brussels": (50.8503, 4.3517),
    "munich": (48.1351, 11.5820),
    "barcelona": (41.3851, 2.1734),
    "madrid": (40.4168, -3.7038),
    "rome": (41.9028, 12.4964),
    "florence": (43.7695, 11.2558),
    "edinburgh": (55.9533, -3.1883),
    "geneva": (46.2044, 6.1431),
    "zurich": (47.3769, 8.5469),
    "istanbul": (41.0082, 28.9784),
    "athens": (37.9838, 23.7275),
}

# Asian city coordinates
ASIAN_CITY_COORDS = {
    "bangkok": (13.7563, 100.5018),
    "chiangmai": (18.7883, 98.9853),
    "tokyo": (35.6762, 139.6503),
    "kyoto": (35.0116, 135.7681),
    "singapore": (1.3521, 103.8198),
    "kuala-lumpur": (3.1390, 101.6869),
    "hong-kong": (22.3193, 114.1694),
    "guangzhou": (23.1291, 113.2644),
    "shanghai": (31.2304, 121.4737),
    "beijing": (39.9042, 116.4074),
}


GENERIC_REGION_OPERATORS = {
    "indian": {
        "train": ["Indian Railways", "Vande Bharat", "Tejas Express"],
        "bus": ["MSRTC", "RedBus operators", "Intercity Volvo"],
    },
    "european": {
        "train": ["Regional Railways", "EuroCity", "Intercity Express"],
        "bus": ["FlixBus", "RegioJet", "Intercity coach"],
    },
    "asian": {
        "train": ["Regional Railways", "Express Rail", "Intercity Rail"],
        "bus": ["Express coach", "Intercity bus", "Night coach"],
    },
    "global": {
        "train": ["Regional Railways", "Intercity Rail", "Express Rail"],
        "bus": ["Intercity bus", "Express coach", "Budget coach"],
    },
}

COUNTRY_HINTS = {
    "india": "indian",
    "germany": "european",
    "france": "european",
    "italy": "european",
    "spain": "european",
    "netherlands": "european",
    "austria": "european",
    "hungary": "european",
    "croatia": "european",
    "switzerland": "european",
    "japan": "asian",
    "thailand": "asian",
    "singapore": "asian",
    "malaysia": "asian",
    "china": "asian",
    "hong kong": "asian",
}



def _route_key(from_city: str, to_city: str) -> str:
    """Generate route key - cities are normalized and sorted alphabetically."""
    a = _normalize_city_name(from_city)
    b = _normalize_city_name(to_city)
    return "-".join(sorted([a, b]))


def _bing_rss_search(query: str) -> List[Dict[str, str]]:
    try:
        response = requests.get(
            "https://www.bing.com/search",
            params={"format": "rss", "q": query},
            timeout=8,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()
        root = ET.fromstring(response.text)
    except Exception:
        return []

    items: List[Dict[str, str]] = []
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        description = (item.findtext("description") or "").strip()
        if title or description:
            items.append({"title": title, "link": link, "description": description})
    return items


def _duckduckgo_html_search(query: str) -> List[Dict[str, str]]:
    try:
        response = requests.get(
            "https://duckduckgo.com/html/",
            params={"q": query},
            timeout=8,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()
        html = response.text
    except Exception:
        return []

    items: List[Dict[str, str]] = []
    anchor_pattern = re.compile(
        r'<a[^>]*class="[^"]*result__a[^"]*"[^>]*href="(?P<href>[^"]+)"[^>]*>(?P<title>.*?)</a>',
        flags=re.IGNORECASE | re.DOTALL,
    )
    snippet_pattern = re.compile(
        r'<a[^>]*class="[^"]*result__snippet[^"]*"[^>]*>(?P<snippet>.*?)</a>',
        flags=re.IGNORECASE | re.DOTALL,
    )

    snippets = [re.sub(r"<[^>]+>", "", s).strip() for s in snippet_pattern.findall(html)]
    for idx, match in enumerate(anchor_pattern.finditer(html)):
        href = unescape(match.group("href") or "").strip()
        title_html = match.group("title") or ""
        title = re.sub(r"<[^>]+>", "", title_html).strip()
        snippet = snippets[idx] if idx < len(snippets) else ""
        if title or snippet:
            items.append({"title": title, "link": href, "description": snippet})
        if len(items) >= 25:
            break

    return items


def _extract_city_parts(city: str) -> Tuple[str, str]:
    cleaned = re.sub(r"\s+", " ", (city or "").strip())
    if not cleaned:
        return "", ""

    parts = [part.strip() for part in cleaned.split(",") if part.strip()]
    city_part = parts[0] if parts else cleaned
    country_part = parts[-1].lower() if len(parts) >= 2 else ""
    return city_part, country_part


def _detect_route_region(from_city: str, to_city: str) -> Tuple[str, bool]:
    """
    Detect which region a route belongs to and return (region, has_good_trains).
    Regions: 'indian', 'european', 'asian', 'global'
    """
    from_lower = _normalize_city_name(from_city)
    to_lower = _normalize_city_name(to_city)
    _, from_country = _extract_city_parts(from_city)
    _, to_country = _extract_city_parts(to_city)
    
    # Check Indian
    if from_lower in INDIAN_CITY_COORDS and to_lower in INDIAN_CITY_COORDS:
        return "indian", True
    
    # Check European
    eu_cities = set(EUROPEAN_CITY_COORDS.keys())
    if from_lower in eu_cities and to_lower in eu_cities:
        return "european", True
    
    # Check Asian
    asian_cities = set(ASIAN_CITY_COORDS.keys())
    if from_lower in asian_cities and to_lower in asian_cities:
        return "asian", True
    
    # Check if either is in good-train regions
    good_train_regions = eu_cities | asian_cities | set(INDIAN_CITY_COORDS.keys())
    if from_lower in good_train_regions or to_lower in good_train_regions:
        return "global", True

    # Country-level hints when city is not known.
    from_hint = COUNTRY_HINTS.get(from_country)
    to_hint = COUNTRY_HINTS.get(to_country)
    if from_hint and to_hint and from_hint == to_hint:
        return from_hint, True
    if from_hint or to_hint:
        return (from_hint or to_hint), True
    
    return "global", False


def _normalize_city_name(city: str) -> str:
    """Normalize city name for lookup."""
    city_part, _ = _extract_city_parts(city)
    normalized = re.sub(r"[^a-z0-9\s-]", "", city_part.lower()).strip()
    aliases = {
        "bengaluru": "bangalore",
        "bombay": "mumbai",
        "new york city": "new-york",
    }
    normalized = aliases.get(normalized, normalized)
    return normalized.replace(" ", "-")


def _get_distance_km(from_city: str, to_city: str, region: str) -> float:
    """Calculate distance between cities."""
    coords_map = {}
    if region == "indian":
        coords_map = INDIAN_CITY_COORDS
    elif region == "european":
        coords_map = EUROPEAN_CITY_COORDS
    elif region == "asian":
        coords_map = ASIAN_CITY_COORDS
    else:
        # Combined for global
        coords_map = {**INDIAN_CITY_COORDS, **EUROPEAN_CITY_COORDS, **ASIAN_CITY_COORDS}
    
    from_normalized = _normalize_city_name(from_city)
    to_normalized = _normalize_city_name(to_city)
    
    a = coords_map.get(from_normalized)
    b = coords_map.get(to_normalized)
    
    if not a or not b:
        return 500.0  # fallback distance
    
    return _haversine_km(a[0], a[1], b[0], b[1])


def _generate_train_bus_options(from_city: str, to_city: str, distance_km: float, region: str) -> Dict[str, Dict]:
    """Generate realistic train and bus options for a route based on distance."""
    
    # Distance-based pricing and time estimation
    if distance_km < 200:  # Short distance
        train_hours = max(distance_km / 100, 1.5)
        train_low = int(distance_km * 0.3)
        train_high = int(distance_km * 0.8)
        bus_hours = max(distance_km / 80, 1.5)
        bus_low = int(distance_km * 0.25)
        bus_high = int(distance_km * 0.7)
        
    elif distance_km < 500:  # Medium distance
        train_hours = max(distance_km / 120, 3.0)
        train_low = int(distance_km * 0.2)
        train_high = int(distance_km * 0.6)
        bus_hours = max(distance_km / 80, 4.0)
        bus_low = int(distance_km * 0.15)
        bus_high = int(distance_km * 0.5)
        
    else:  # Long distance
        train_hours = max(distance_km / 80, 8.0)
        train_low = int(distance_km * 0.1)
        train_high = int(distance_km * 0.4)
        bus_hours = max(distance_km / 60, 10.0)
        bus_low = int(distance_km * 0.08)
        bus_high = int(distance_km * 0.35)
    
    # Adjust for region
    if region == "european":
        train_low = int(train_low * 0.6)  # European trains cheaper per km
        train_high = int(train_high * 0.7)
        currency = "EUR"
    elif region == "asian":
        train_low = int(train_low * 0.8)  # Asian trains moderate pricing
        train_high = int(train_high * 1.0)
        currency = "Local"
    else:  # Indian or unknown
        currency = "INR"
    
    return {
        "train": {
            "time": f"{train_hours:.1f}h",
            "price_range": f"{train_low:,}-{train_high:,}",
            "frequency": "Multiple daily" if distance_km < 500 else "Daily",
            "source": "estimated",
            "operator": "Regional operator",
        },
        "bus": {
            "time": f"{bus_hours:.1f}h",
            "price_range": f"{bus_low:,}-{bus_high:,}",
            "frequency": "Multiple daily",
            "source": "estimated",
            "operator": "Regional/Budget operators",
        },
    }


def _parse_price_range_to_min(price_range: str) -> Optional[float]:
    match = re.search(r"(\d+(?:,\d+)?)\s*[-–]\s*(\d+(?:,\d+)?)", price_range)
    if not match:
        return None
    low = float(match.group(1).replace(",", ""))
    return low


def _parse_time_to_hours(time_text: str) -> Optional[float]:
    if not time_text or time_text == "N/A":
        return None

    match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)h(?:\s*(\d+)m)?\s*", time_text)
    if match:
        hours = float(match.group(1))
        minutes = float(match.group(2) or 0)
        return hours + minutes / 60

    return None


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c


def _default_date() -> str:
    return (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d")


def _build_ground_mode(mode_name: str, raw: Dict) -> Dict:
    min_price = _parse_price_range_to_min(raw.get("price_range", ""))
    duration_hours = _parse_time_to_hours(raw.get("time", ""))

    return {
        "mode": mode_name,
        "journeyTime": raw.get("time", "N/A"),
        "priceRange": raw.get("price_range", "N/A"),
        "frequency": raw.get("frequency", "N/A"),
        "operator": raw.get("operator", "Operator"),
        "source": raw.get("source", "live"),
        "sourceTitle": raw.get("source_title", ""),
        "sourceUrl": raw.get("source_url", ""),
        "sourceSnippet": raw.get("source_snippet", ""),
        "minPrice": min_price,
        "durationHours": duration_hours,
    }


def _search_ground_source(from_city: str, to_city: str, mode: str, travel_date: str) -> Dict[str, str]:
    from_base, _ = _extract_city_parts(from_city)
    to_base, _ = _extract_city_parts(to_city)
    from_token = _normalize_city_name(from_base).replace("-", " ")
    to_token = _normalize_city_name(to_base).replace("-", " ")

    mode_domains = {
        "train": ["ixigo", "trainline", "raileurope", "irctc", "rome2rio", "railway"],
        "bus": ["redbus", "flixbus", "rome2rio", "bus", "intercity"],
    }
    mode_keywords = {
        "train": r"train|rail|railway|irctc|metro|station",
        "bus": r"bus|coach|intercity",
    }
    banned_terms = ["live updates", "highlights", "rain", "weather", "news", "dead", "election"]

    queries = [
        f"{from_city} to {to_city} {mode} tickets {travel_date}",
        f"best {mode} from {from_city} to {to_city}",
        f"{from_city} {to_city} {mode} timetable",
    ]

    for query in queries:
        items = _bing_rss_search(query)
        for item in items:
            title = item.get("title", "")
            description = item.get("description", "")
            link = item.get("link", "")
            text = f"{title} {description}".lower()
            link_lower = link.lower()
            if any(term in text for term in banned_terms):
                continue
            domain_match = any(domain in link.lower() for domain in mode_domains.get(mode, []))
            keyword_match = re.search(mode_keywords.get(mode, mode), text, re.IGNORECASE) is not None
            from_match = bool(from_token) and ((from_token in text) or (from_token in link_lower))
            to_match = bool(to_token) and ((to_token in text) or (to_token in link_lower))
            route_match = from_match and to_match
            if not route_match:
                continue
            if not (domain_match or keyword_match):
                continue

            return {
                "source_title": title or "Bing web search result",
                "source_url": link,
                "source_snippet": description[:180],
            }

    return {
        "source_title": "Bing web search result",
        "source_url": "",
        "source_snippet": f"Search query: {from_city} to {to_city} {mode} tickets {travel_date}",
    }


def _extract_duration_text(text: str) -> str:
    if not text:
        return "N/A"

    normalized = re.sub(r"\s+", " ", text)

    # Examples: 6h 30m, 6 h 30 m, 6 hours 30 min
    hm = re.search(r"(\d{1,2})\s*(?:h|hr|hrs|hour|hours)\s*(\d{1,2})?\s*(?:m|min|mins|minute|minutes)?", normalized, flags=re.IGNORECASE)
    if hm:
        hours = int(hm.group(1))
        mins = int(hm.group(2) or 0)
        return f"{hours}h {mins:02d}m" if mins else f"{hours}h"

    # Example: 06:45
    colon = re.search(r"\b(\d{1,2}):(\d{2})\b", normalized)
    if colon:
        hours = int(colon.group(1))
        mins = int(colon.group(2))
        if 0 <= hours <= 24 and 0 <= mins < 60:
            return f"{hours}h {mins:02d}m"

    return "N/A"


def _extract_price_range_text(text: str) -> str:
    if not text:
        return "N/A"

    symbol_to_code = {
        "$": "USD",
        "€": "EUR",
        "£": "GBP",
        "₹": "INR",
        "¥": "JPY",
    }
    currency_regex = r"USD|EUR|GBP|INR|JPY|CNY|RMB|SGD|HKD|AUD|CAD|THB|MYR|AED|CHF"
    price_pattern = re.compile(
        rf"(?:(?P<code>{currency_regex})\s*)?(?P<sym>[$€£₹¥])?\s*(?P<num>\d{{1,3}}(?:,\d{{3}})*(?:\.\d+)?)",
        flags=re.IGNORECASE,
    )

    values: List[int] = []
    currency = ""
    for match in price_pattern.finditer(text):
        raw = match.group("num")
        if not raw:
            continue
        amount = float(raw.replace(",", ""))
        if amount <= 0 or amount > 500000:
            continue
        code = (match.group("code") or "").upper()
        sym = match.group("sym")
        has_currency_marker = bool(code or sym)
        # Ignore tiny uncoded numbers (e.g., years in snippets) unless currency is explicit.
        if not has_currency_marker and amount < 20:
            continue

        values.append(int(round(amount)))

        if not currency:
            if code:
                currency = code
            elif sym:
                currency = symbol_to_code.get(sym, "")

    if not values:
        return "N/A"

    values = sorted(values)
    if len(values) == 1:
        low = max(int(values[0] * 0.85), 1)
        high = int(values[0] * 1.15)
    else:
        low = values[0]
        high = values[1]

    prefix = f"{currency} " if currency else ""
    return f"{prefix}{low:,}-{high:,}".strip()


def _operator_from_link_or_title(link: str, title: str, mode: str, region: str) -> str:
    parsed = urlparse(link or "")
    host = (parsed.netloc or "").lower()
    host = host.replace("www.", "")
    if host:
        base = host.split(".")[0].replace("-", " ").strip()
        if base and len(base) > 2:
            return base.title()

    operators = GENERIC_REGION_OPERATORS.get(region, GENERIC_REGION_OPERATORS["global"]).get(mode, [])
    return operators[0] if operators else ("Rail Operator" if mode == "train" else "Bus Operator")


def _build_ground_options_from_web(
    mode_name: str,
    from_city: str,
    to_city: str,
    travel_date: str,
    region: str,
    max_results: int = 3,
) -> List[Dict]:
    from_base, _ = _extract_city_parts(from_city)
    to_base, _ = _extract_city_parts(to_city)
    from_token = _normalize_city_name(from_base).replace("-", " ")
    to_token = _normalize_city_name(to_base).replace("-", " ")

    mode_keywords = {
        "train": r"train|rail|railway|station|intercity",
        "bus": r"bus|coach|intercity|terminal",
    }

    queries = [
        f"{from_city} to {to_city} {mode_name} tickets price schedule",
        f"{from_city} to {to_city} {mode_name} booking",
        f"{from_city} {to_city} {mode_name} timetable fare {travel_date}",
    ]

    raw_candidates: List[Dict[str, str]] = []
    seen = set()
    for query in queries:
        for item in _bing_rss_search(query):
            link = item.get("link", "")
            title = item.get("title", "")
            key = (link or title).strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)
            raw_candidates.append(item)
        for item in _duckduckgo_html_search(query):
            link = item.get("link", "")
            title = item.get("title", "")
            key = (link or title).strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)
            raw_candidates.append(item)

    options: List[Dict] = []
    for item in raw_candidates:
        title = item.get("title", "")
        description = item.get("description", "")
        link = item.get("link", "")
        text = f"{title} {description}".lower()

        if re.search(mode_keywords.get(mode_name, mode_name), text, re.IGNORECASE) is None:
            continue

        from_match = bool(from_token) and ((from_token in text) or (from_token in link.lower()))
        to_match = bool(to_token) and ((to_token in text) or (to_token in link.lower()))
        if not (from_match and to_match):
            continue

        combined_text = f"{title} {description}"
        option = {
            "time": _extract_duration_text(combined_text),
            "price_range": _extract_price_range_text(combined_text),
            "frequency": "Check latest schedule",
            "operator": _operator_from_link_or_title(link, title, mode_name, region),
            "source": "web_search",
            "source_title": title or "Bing web search result",
            "source_url": link,
            "source_snippet": description[:180],
        }
        options.append(_build_ground_mode(mode_name, option))

        if len(options) >= max_results:
            break

    if options:
        return options

    # Dynamic fallback: still return web-query-driven option so UI can provide actionable links.
    if raw_candidates:
        weak_match = None
        for candidate in raw_candidates:
            title = candidate.get("title", "")
            description = candidate.get("description", "")
            link = candidate.get("link", "")
            text = f"{title} {description}".lower()
            has_mode_signal = re.search(mode_keywords.get(mode_name, mode_name), text, re.IGNORECASE) is not None
            has_from_signal = (from_token in text) or (from_token in link.lower())
            has_to_signal = (to_token in text) or (to_token in link.lower())
            has_route_signal = has_from_signal and has_to_signal
            if has_mode_signal and has_route_signal:
                weak_match = candidate
                break

        if weak_match is None:
            query_url = f"https://www.google.com/search?q={quote_plus(queries[0])}"
            fallback_option = {
                "time": "N/A",
                "price_range": "N/A",
                "frequency": "Check latest schedule",
                "operator": GENERIC_REGION_OPERATORS.get(region, GENERIC_REGION_OPERATORS["global"]).get(mode_name, [mode_name.title()])[0],
                "source": "web_search",
                "source_title": f"Live {mode_name} search: {from_city} to {to_city}",
                "source_url": query_url,
                "source_snippet": f"No strongly route-matched listing found. Open live search results for query: {queries[0]}",
            }
            return [_build_ground_mode(mode_name, fallback_option)]

        top = weak_match
        top_title = top.get("title", "")
        top_link = top.get("link", "")
        top_desc = top.get("description", "")
        combined = f"{top_title} {top_desc}"
        parsed_time = _extract_duration_text(combined)
        parsed_price = _extract_price_range_text(combined)
        fallback_option = {
            "time": parsed_time,
            "price_range": parsed_price,
            "frequency": "Check latest schedule",
            "operator": _operator_from_link_or_title(top_link, top_title, mode_name, region),
            "source": "web_search",
            "source_title": top_title or f"{mode_name.title()} web search result",
            "source_url": top_link or f"https://www.google.com/search?q={quote_plus(queries[0])}",
            "source_snippet": (top_desc or f"Live search query: {queries[0]}")[:180],
        }
        return [_build_ground_mode(mode_name, fallback_option)]

    return []


def _expand_ground_options(mode_name: str, base_raw: Dict, from_city: str, to_city: str, travel_date: str, region: str) -> List[Dict]:
    operators = GENERIC_REGION_OPERATORS.get(region, GENERIC_REGION_OPERATORS["global"])[mode_name]
    base_low = _parse_price_range_to_min(base_raw.get("price_range", "")) or 0.0
    duration_hours = _parse_time_to_hours(base_raw.get("time", "")) or 0.0
    source_meta = _search_ground_source(from_city, to_city, mode_name, travel_date)

    options: List[Dict] = []
    for idx, operator in enumerate(operators[:3]):
        multiplier = 1.0 + (idx * 0.18)
        low = int(base_low * multiplier) if base_low > 0 else 0
        high = int(low * 1.9) if low > 0 else 0
        range_currency = "INR" if "INR" in base_raw.get("price_range", "") else ("EUR" if "EUR" in base_raw.get("price_range", "") else "")
        price_range = base_raw.get("price_range", "N/A")
        if low > 0 and high > 0:
            price_range = f"{range_currency} {low:,}-{high:,}".strip()

        journey_time = base_raw.get("time", "N/A")
        if duration_hours > 0:
            adjusted = max(duration_hours * (1.0 + (idx * 0.08)), 0.8)
            hours = int(adjusted)
            minutes = int(round((adjusted - hours) * 60))
            journey_time = f"{hours}h {minutes:02d}m" if hours > 0 else f"{minutes}m"

        option = {
            "time": journey_time,
            "price_range": price_range,
            "frequency": base_raw.get("frequency", "Multiple daily"),
            "operator": operator,
            "source": "web_search",
            **source_meta,
        }
        options.append(_build_ground_mode(mode_name, option))

    return options


def get_transport_options_data(from_city: str, to_city: str, date: Optional[str] = None, currency: str = "INR") -> Dict:
    travel_date = date or _default_date()

    flights_data = search_flights_structured(
        from_city=from_city,
        to_city=to_city,
        departure_date=travel_date,
        currency=currency,
        adults=1,
        max_results=5,
    )

    flight_offers = flights_data.get("offers", []) if flights_data.get("success") else []

    # Keep region detection for labels/operator fallback, but train/bus discovery is always dynamic web-first.
    region, _ = _detect_route_region(from_city, to_city)

    train_options = _build_ground_options_from_web(
        "train",
        from_city,
        to_city,
        travel_date,
        region,
    )
    bus_options = _build_ground_options_from_web(
        "bus",
        from_city,
        to_city,
        travel_date,
        region,
    )

    trains = {
        "applicable": bool(train_options),
        "options": train_options,
        "message": "No route-specific train web results found for this date/query." if not train_options else "",
    }
    buses = {
        "applicable": bool(bus_options),
        "options": bus_options,
        "message": "No route-specific bus web results found for this date/query." if not bus_options else "",
    }

    modes_for_value: List[Tuple[str, float]] = []

    if flight_offers:
        cheapest_flight = min(flight_offers, key=lambda item: item.get("price", float("inf")))
        duration_hours = max((cheapest_flight.get("durationMinutes", 0) or 1) / 60.0, 0.5)
        cost_per_hour = float(cheapest_flight.get("price", 0)) / duration_hours
        modes_for_value.append(("flight", cost_per_hour))

    if trains["applicable"] and trains["options"]:
        train = trains["options"][0]
        if train.get("minPrice") and train.get("durationHours"):
            modes_for_value.append(("train", float(train["minPrice"]) / float(train["durationHours"])))

    if buses["applicable"] and buses["options"]:
        bus = buses["options"][0]
        if bus.get("minPrice") and bus.get("durationHours"):
            modes_for_value.append(("bus", float(bus["minPrice"]) / float(bus["durationHours"])))

    best_value = None
    best_value_reason = "Insufficient comparable transport data"
    if modes_for_value:
        best_value = min(modes_for_value, key=lambda item: item[1])[0]
        best_value_reason = "Cheapest per travel hour"

        value_map = {name: value for name, value in modes_for_value}
        if "flight" in value_map and "bus" in value_map and value_map["flight"] * 3 < value_map["bus"]:
            best_value = "flight"
            best_value_reason = "Flight is >3x cheaper per travel hour than bus"

    return {
        "flights": flight_offers[:3],
        "flightSource": flights_data.get("provider") if flight_offers else (flights_data.get("error_type") or "unavailable"),
        "flightMessage": flights_data.get("message", "") if not flight_offers else "",
        "routeResolved": {
            "originCity": flights_data.get("origin_city", from_city),
            "destinationCity": flights_data.get("destination_city", to_city),
            "originIata": flights_data.get("origin_iata", ""),
            "destinationIata": flights_data.get("destination_iata", ""),
        },
        "trains": trains,
        "buses": buses,
        "bestValue": best_value,
        "bestValueReason": best_value_reason,
        "region": region,  # Include for frontend reference
    }


@tool
def get_transport_options(query: str) -> str:
    """
    Returns transport mode options (flight/train/bus) between cities with estimated prices and travel times.
    Works for domestic Indian routes, European routes, Asian routes, and any major transportation corridors.
    Use when user asks about transport, travel modes, or alternative transportation.
    Input: "FROM_CITY TO_CITY"
    """
    cleaned = " ".join((query or "").strip().split())
    if not cleaned:
        return "Invalid input. Use: 'FROM_CITY TO_CITY'."

    if " to " in cleaned.lower():
        parts = re.split(r"\s+to\s+", cleaned, flags=re.IGNORECASE)
        if len(parts) != 2:
            return "Invalid input. Use: 'FROM_CITY TO_CITY'."
        from_city, to_city = parts[0], parts[1]
    else:
        tokens = cleaned.split()
        if len(tokens) < 2:
            return "Invalid input. Use: 'FROM_CITY TO_CITY'."
        from_city = " ".join(tokens[:-1])
        to_city = tokens[-1]

    data = get_transport_options_data(from_city, to_city)

    lines = [
        f"Transport options from {from_city} to {to_city}:",
        f"Region: {data.get('region', 'Global')} | Distance-based pricing",
        "-" * 70,
    ]

    # Flights
    if data.get("flights"):
        cheapest = min(data["flights"], key=lambda item: item.get("price", float("inf")))
        stop_text = "Direct" if cheapest.get("stops", 0) == 0 else f"{cheapest.get('stops', 0)} stop(s)"
        lines.append(
            f"✈️  FLIGHT: {cheapest.get('airline', 'Airline'):20s} | {cheapest.get('duration', 'N/A'):10s} | "
            f"{stop_text:15s} | {cheapest.get('currency', 'INR')} {cheapest.get('price', 0):,.0f}"
        )
    else:
        message = data.get("flightMessage") or "Live flight pricing unavailable."
        lines.append(f"✈️  FLIGHT: {message}")

    # Trains
    if data.get("trains", {}).get("applicable"):
        train = data["trains"]["options"][0]
        operator = train.get("operator", "Rail operator")
        lines.append(
            f"🚂 TRAIN:  {operator:20s} | {train.get('journeyTime'):10s} | "
            f"{train.get('frequency'):15s} | {train.get('priceRange')}"
        )
    else:
        lines.append(f"🚂 TRAIN:  {data.get('trains', {}).get('message', 'Not available for this route.')}")

    # Buses
    if data.get("buses", {}).get("applicable"):
        bus = data["buses"]["options"][0]
        operator = bus.get("operator", "Bus operator")
        lines.append(
            f"🚌 BUS:    {operator:20s} | {bus.get('journeyTime'):10s} | "
            f"{bus.get('frequency'):15s} | {bus.get('priceRange')}"
        )
    else:
        lines.append(f"🚌 BUS:    {data.get('buses', {}).get('message', 'Not available for this route.')}")

    if data.get("bestValue"):
        lines.append("-" * 70)
        lines.append(f"💡 Best value: {data['bestValue'].upper()} ({data.get('bestValueReason', 'Cheapest per travel hour')})")

    return "\n".join(lines)


# Compatibility wrapper for older imports
@tool
def get_transport_prices(origin: str, destination: str, date: str, modes: List[str]) -> str:
    """
    Compatibility wrapper that returns transport price blocks for flight/train/bus.
    Input schema: { origin, destination, date, modes }
    """
    data = get_transport_options_data(origin, destination, date)
    mode_map = {
        "flight": data.get("flights", [None])[0],
        "train": (data.get("trains", {}).get("options") or [None])[0],
        "bus": (data.get("buses", {}).get("options") or [None])[0],
    }

    out: Dict[str, Dict] = {}
    for mode in modes or ["flight", "train", "bus"]:
        item = mode_map.get(mode)
        if not item:
            out[mode] = {
                "min_price": 0.0,
                "max_price": 0.0,
                "currency": "INR",
                "source": "Estimate unavailable",
                "booking_url": "",
                "mode": mode,
            }
            continue

        if mode == "flight":
            out[mode] = {
                "min_price": float(item.get("price", 0.0)),
                "max_price": float(item.get("price", 0.0)),
                "currency": item.get("currency", "INR"),
                "source": "Travelpayouts",
                "booking_url": "",
                "mode": mode,
            }
        else:
            min_price = float(item.get("minPrice") or 0.0)
            out[mode] = {
                "min_price": min_price,
                "max_price": min_price,
                "currency": "INR",
                "source": item.get("source", "estimated"),
                "booking_url": "",
                "mode": mode,
            }

    return json.dumps(out)
