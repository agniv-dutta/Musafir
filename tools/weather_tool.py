import requests
from langchain.tools import tool

@tool
def get_weather_forecast(destination: str) -> str:
    """
    Fetches a 7-day weather forecast for a travel destination.
    Use this to advise the user on best travel dates and packing.
    Input: destination name (e.g., 'Bali', 'London', 'New York')
    """
    try:
        # First geocode the city using Nominatim
        geo_url = "https://nominatim.openstreetmap.org/search"
        geo_params = {"q": destination, "format": "json", "limit": 1}
        headers = {"User-Agent": "TravelPlannerAgent/1.0"}
        geo_data = requests.get(geo_url, params=geo_params, headers=headers).json()

        if not geo_data:
            return f"Could not geocode {destination} for weather lookup."

        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]

        # Open-Meteo: completely free, no key required
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {
            "latitude": lat,
            "longitude": lon,
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "windspeed_10m_max",
                "weathercode"
            ],
            "timezone": "auto",
            "forecast_days": 7
        }
        weather_data = requests.get(weather_url, params=weather_params).json()
        daily = weather_data.get("daily", {})

        # WMO weather code to human-readable description
        WMO_CODES = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Fog", 48: "Depositing rime fog",
            51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
            80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
            95: "Thunderstorm", 99: "Thunderstorm with hail"
        }

        forecast_lines = []
        dates = daily.get("time", [])
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])
        precip = daily.get("precipitation_sum", [])
        wind = daily.get("windspeed_10m_max", [])
        codes = daily.get("weathercode", [])

        for i in range(len(dates)):
            condition = WMO_CODES.get(codes[i], f"Code {codes[i]}")
            forecast_lines.append(
                f"{dates[i]}: {condition}, "
                f"Max {max_temps[i]}°C / Min {min_temps[i]}°C, "
                f"Rain {precip[i]}mm, Wind {wind[i]}km/h"
            )

        return f"7-Day Weather Forecast for {destination}:\n" + "\n".join(forecast_lines)

    except Exception as e:
        return f"Error fetching weather: {str(e)}"


if __name__ == "__main__":
    print(get_weather_forecast.run("Paris"))
