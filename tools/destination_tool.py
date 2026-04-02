import requests
from langchain.tools import tool

@tool
def get_destination_info(destination: str) -> str:
    """
    Fetches key facts about a travel destination: country details,
    currency, languages spoken, and geographic coordinates.
    Use this first when the user names any destination.
    Input: destination name (city or country, e.g. 'Paris' or 'Japan')
    """
    try:
        # Step 1: Geocode the destination using Nominatim (free, no key)
        geo_url = "https://nominatim.openstreetmap.org/search"
        geo_params = {
            "q": destination,
            "format": "json",
            "limit": 1,
            "addressdetails": 1
        }
        headers = {"User-Agent": "TravelPlannerAgent/1.0"}
        geo_response = requests.get(geo_url, params=geo_params, headers=headers)
        geo_data = geo_response.json()

        if not geo_data:
            return f"Could not find location data for {destination}."

        location = geo_data[0]
        country_code = location.get("address", {}).get("country_code", "").upper()
        lat = location["lat"]
        lon = location["lon"]
        display_name = location["display_name"]

        # Step 2: Get country-level info via RestCountries (free, no key)
        country_url = f"https://restcountries.com/v3.1/alpha/{country_code}"
        country_response = requests.get(country_url)
        country_data = country_response.json()[0]

        country_name = country_data.get("name", {}).get("common", "Unknown")
        capital = country_data.get("capital", ["Unknown"])[0]
        currencies = ", ".join(
            [f"{v['name']} ({k})" for k, v in country_data.get("currencies", {}).items()]
        )
        languages = ", ".join(country_data.get("languages", {}).values())
        region = country_data.get("region", "Unknown")
        population = f"{country_data.get('population', 0):,}"
        timezones = ", ".join(country_data.get("timezones", []))

        result = f"""
Destination: {display_name}
Coordinates: Lat {lat}, Lon {lon}
Country: {country_name} ({region})
Capital: {capital}
Currency: {currencies}
Languages: {languages}
Population: {population}
Timezones: {timezones}
        """.strip()

        return result

    except Exception as e:
        return f"Error fetching destination info: {str(e)}"


if __name__ == "__main__":
    print(get_destination_info.run("Tokyo"))