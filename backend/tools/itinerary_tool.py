import requests
import os
from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv()


def _fetch_named_places(destination: str, limit: int = 12) -> list[str]:
    """Fetch nearby named attractions for grounding itinerary output."""
    headers = {"User-Agent": "MusafirPlanner/1.0"}
    fallback_catalog = {
        "paris": ["Louvre Museum", "Eiffel Tower", "Musee d'Orsay", "Notre-Dame Cathedral", "Montmartre", "Sainte-Chapelle"],
        "london": ["British Museum", "Tower of London", "Westminster Abbey", "St Paul's Cathedral", "Borough Market", "Hyde Park"],
        "tokyo": ["Senso-ji", "Meiji Jingu", "Tokyo Skytree", "Shibuya Crossing", "Ueno Park", "Tsukiji Outer Market"],
        "kyoto": ["Fushimi Inari Taisha", "Kinkaku-ji", "Arashiyama Bamboo Grove", "Kiyomizu-dera", "Nijo Castle", "Gion"],
        "osaka": ["Osaka Castle", "Dotonbori", "Shitenno-ji", "Kuromon Ichiba Market", "Umeda Sky Building", "Sumiyoshi Taisha"],
        "new york": ["Central Park", "Metropolitan Museum of Art", "Times Square", "Brooklyn Bridge", "High Line", "9/11 Memorial & Museum"],
        "rome": ["Colosseum", "Roman Forum", "Trevi Fountain", "Pantheon", "Vatican Museums", "Piazza Navona"],
        "barcelona": ["Sagrada Familia", "Park Guell", "Gothic Quarter", "Casa Batllo", "La Boqueria", "Montjuic"],
        "amsterdam": ["Rijksmuseum", "Anne Frank House", "Van Gogh Museum", "Jordaan", "Vondelpark", "Dam Square"],
        "bangkok": ["Grand Palace", "Wat Arun", "Wat Pho", "Chatuchak Market", "Jim Thompson House", "Asiatique The Riverfront"],
        "singapore": ["Gardens by the Bay", "Marina Bay Sands", "Sentosa", "Merlion Park", "Singapore Botanic Gardens", "Chinatown Singapore"],
        "dubai": ["Burj Khalifa", "Dubai Mall", "Al Fahidi Historical District", "Dubai Marina", "Museum of the Future", "Jumeirah Mosque"],
        "sydney": ["Sydney Opera House", "Harbour Bridge", "Bondi Beach", "The Rocks", "Taronga Zoo", "Royal Botanic Garden Sydney"],
        "mumbai": ["Gateway of India", "Chhatrapati Shivaji Maharaj Terminus", "Marine Drive", "Elephanta Caves", "Colaba Causeway", "Haji Ali Dargah"],
        "delhi": ["Red Fort", "Qutub Minar", "Humayun's Tomb", "India Gate", "Jama Masjid", "Lodhi Garden"],
        "goa": ["Basilica of Bom Jesus", "Fort Aguada", "Calangute Beach", "Dudhsagar Falls", "Anjuna Flea Market", "Chapora Fort"],
        "shanghai": ["The Bund", "Yu Garden", "Shanghai Tower", "Nanjing Road", "Jing'an Temple", "Shanghai Museum"],
    }

    normalized_destination = (destination or "").strip().lower()

    def _fallback_places() -> list[str]:
        for key, places in fallback_catalog.items():
            if key in normalized_destination or normalized_destination in key:
                return places[:limit]
        return []
    try:
        geo_response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": destination, "format": "json", "limit": 1},
            headers=headers,
            timeout=8,
        )
        geo_response.raise_for_status()
        geo_data = geo_response.json()
        if not geo_data:
            return _fallback_places()

        lat = geo_data[0].get("lat")
        lon = geo_data[0].get("lon")
        if not lat or not lon:
            return _fallback_places()

        wiki_response = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "geosearch",
                "gscoord": f"{lat}|{lon}",
                "gsradius": 12000,
                "gslimit": max(6, min(limit * 2, 50)),
                "format": "json",
            },
            headers=headers,
            timeout=8,
        )
        wiki_response.raise_for_status()
        payload = wiki_response.json()
        items = payload.get("query", {}).get("geosearch", [])

        results: list[str] = []
        seen = set()
        for item in items:
            title = (item.get("title") or "").strip()
            if not title:
                continue
            normalized = title.lower()
            if normalized.startswith("list of") or "disambiguation" in normalized:
                continue
            if normalized in seen:
                continue
            seen.add(normalized)
            results.append(title)
            if len(results) >= limit:
                break

        return results or _fallback_places()
    except Exception:
        return _fallback_places()

@tool
def generate_itinerary(trip_details: str) -> str:
    """
    Generates a structured day-by-day travel itinerary based on trip details.
    Use this AFTER gathering destination info and weather data.
    Input: a summary of trip details such as destination, duration, budget, 
           travel style (adventure/relaxed/cultural), and any constraints.
    Example input: 'destination: Paris, duration: 5 days, budget: moderate, 
                    style: cultural, constraints: vegetarian food needed'
    """
    try:
        # Parse the structured input
        lines = [line.strip() for line in trip_details.split(",")]
        details = {}
        for line in lines:
            if ":" in line:
                k, v = line.split(":", 1)
                details[k.strip().lower()] = v.strip()

        destination = details.get("destination", "the destination")
        duration = details.get("duration", "3 days")
        budget = details.get("budget", "moderate")
        style = details.get("style", "balanced")
        constraints = details.get("constraints", "none")
        named_places = _fetch_named_places(destination, limit=14)
        places_block = "\n".join(f"- {p}" for p in named_places) if named_places else "- (No live place list available)"

        # Call Groq (free LLM) to generate the itinerary
        groq_url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
            "Content-Type": "application/json"
        }
        prompt = f"""
Create a detailed {duration} travel itinerary for {destination}.
Budget level: {budget}
Travel style: {style}
Special constraints: {constraints}

Format your response as:
Day 1:
    Morning: [activity with at least one exact place name]
    Afternoon: [activity with at least one exact place name]
    Evening: [activity + dinner recommendation, include exact place name]
  Estimated cost: [cost in local currency]

(Repeat for each day)

Named places to prioritize (from live geosearch):
{places_block}

Strict rules:
- Use exact venue/attraction names, not generic text like "visit a museum" or "go to a park".
- Include at least 2 named places per day.
- If live place list is available, prefer those names.
- If uncertain, explicitly write "(verify opening hours)" instead of inventing details.

Travel Tips:
- [3-4 practical tips specific to this destination]

Best areas to stay:
- [2-3 accommodation area recommendations with reasoning]
"""
        payload = {
            "model": os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            "messages": [
                {"role": "system", "content": "You are an expert travel planner with deep knowledge of global destinations."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5,
            "max_tokens": 1000
        }

        response = requests.post(groq_url, headers=headers, json=payload)
        result = response.json()
        if "choices" not in result or not result["choices"]:
            error_msg = result.get("error", {}).get("message", "Unknown Groq response error")
            return f"Error generating itinerary: {error_msg}"

        itinerary = result["choices"][0]["message"]["content"]
        return f"Generated Itinerary for {destination}:\n\n{itinerary}"

    except Exception as e:
        return f"Error generating itinerary: {str(e)}"


if __name__ == "__main__":
    test_input = "destination: Goa, duration: 4 days, budget: budget, style: beach/relaxed, constraints: none"
    print(generate_itinerary.run(test_input))
