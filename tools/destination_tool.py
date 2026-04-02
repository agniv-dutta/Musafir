import requests
from langchain.tools import tool

def get_coordinates(destination: str) -> dict:
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": destination,
        "format": "json",
        "limit": 1,
        "addressdetails": 1
    }
    headers = {
        "User-Agent": "TravelPlannerAgent/1.0"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            return None
            
        result = data[0]
        address = result.get("address", {})
        country_code = address.get("country_code", "")
        
        return {
            "lat": result.get("lat"),
            "lon": result.get("lon"),
            "display_name": result.get("display_name"),
            "country_code": country_code
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"Error fetching coordinates: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error in geocoding: {str(e)}"}

def get_country_info(country_code: str) -> str:
    if not country_code:
        return "Country code is missing..."
        
    url = f"https://restcountries.com/v3.1/alpha/{country_code}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 404:
            return f"Country info not found for code: {country_code}"
        
        response.raise_for_status()
        data = response.json()
        
        if not data or not isinstance(data, list):
            return "Unexpected data format from RestCountries API."
            
        country = data[0]
        
        # Extract fields
        name = country.get("name", {}).get("common", "Unknown")
        capitals = country.get("capital", ["Unknown"])
        capital = capitals[0] if capitals else "Unknown"
        
        currencies_dict = country.get("currencies", {})
        currency_list = []
        for code, details in currencies_dict.items():
            curr_name = details.get("name", "")
            currency_list.append(f"{curr_name} ({code})")
        currencies_str = ", ".join(currency_list) if currency_list else "Unknown"
        
        languages_dict = country.get("languages", {})
        languages_str = ", ".join(languages_dict.values()) if languages_dict else "Unknown"
        
        region = country.get("region", "Unknown")
        population = country.get("population", 0)
        timezones_list = country.get("timezones", [])
        timezones_str = ", ".join(timezones_list) if timezones_list else "Unknown"
        
        info_str = (
            f"Country: {name}\n"
            f"Capital: {capital}\n"
            f"Region: {region}\n"
            f"Population: {population:,}\n"
            f"Currencies: {currencies_str}\n"
            f"Languages: {languages_str}\n"
            f"Timezones: {timezones_str}"
        )
        return info_str

    except requests.exceptions.RequestException as e:
        return f"Error fetching country info: {str(e)}"
    except Exception as e:
        return f"Unexpected error processing country info: {str(e)}"

@tool
def get_destination_info(destination: str) -> str:
    """Uses Nominatim and RestCountries to get coordinates, country name, capital, currency, languages and timezone for a destination.
    Always use this first when starting to gather information about a destination.
    """
    coord_data = get_coordinates(destination)
    if coord_data is None:
        return f"Error: Could not find coordinates for '{destination}'. Please try a more specific city or country name."
    if "error" in coord_data:
        return coord_data["error"]
        
    lat = coord_data.get("lat")
    lon = coord_data.get("lon")
    display_name = coord_data.get("display_name")
    country_code = coord_data.get("country_code")
    
    country_info = get_country_info(country_code)
    
    result = f"Destination: {display_name}\n"
    result += f"Coordinates: Lat {lat}, Lon {lon}\n\n"
    result += "-- Country Details --\n"
    result += country_info
    
    return result

if __name__ == "__main__":
    print(get_destination_info.invoke("Tokyo"))