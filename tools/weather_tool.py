import requests
from langchain.tools import tool

def get_forecast(lat: str, lon: str) -> str:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max,weathercode",
        "timezone": "auto",
        "forecast_days": 7
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        daily = data.get("daily", {})
        if not daily:
            return "Unexpected data format: daily section missing."
            
        time = daily.get("time", [])
        temp_max = daily.get("temperature_2m_max", [])
        temp_min = daily.get("temperature_2m_min", [])
        precip = daily.get("precipitation_sum", [])
        wind = daily.get("windspeed_10m_max", [])
        wmo_codes = daily.get("weathercode", [])
        
        wmo_decoder = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 
            3: "Overcast", 45: "Fog", 51: "Light drizzle", 
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            71: "Slight snow", 80: "Slight showers", 95: "Thunderstorm"
        }
        
        forecast_lines = []
        total_precip = 0
        sum_max_temp = 0
        
        for i in range(len(time)):
             code = wmo_codes[i]
             desc = wmo_decoder.get(code, f"Code {code}")
             
             day_precip = precip[i]
             day_max_temp = temp_max[i]
             
             total_precip += day_precip
             sum_max_temp += day_max_temp
             
             line = f"{time[i]}: {desc} | Max {day_max_temp}°C / Min {temp_min[i]}°C | Rain {day_precip}mm | Wind {wind[i]} km/h"
             forecast_lines.append(line)
        
        avg_max_temp = sum_max_temp / len(time) if len(time) > 0 else 0
        
        recommendation = ""
        if avg_max_temp > 35:
            recommendation = "Warning: Extreme heat expected. Stay hydrated and avoid midday sun."
        elif total_precip > 50:
            recommendation = "Warning: Significant rain expected. Pack a good rain jacket and waterproof gear."
        elif avg_max_temp < 10:
            recommendation = "Warning: Cold weather expected. Bring warm layers and a coat."
        else:
            recommendation = "Conditions look comfortable for travel!"
            
        result = "\n".join(forecast_lines)
        result += f"\n\nRecommendation: {recommendation}"
        
        return result
        
    except requests.exceptions.RequestException as e:
        return f"Error fetching weather forecast: {str(e)}"
    except Exception as e:
         return f"Unexpected error processing weather forecast: {str(e)}"

@tool
def get_weather_forecast(destination: str) -> str:
    """Gets a 7-day weather forecast and travel recommendation for a given destination."""
    geo_url = "https://nominatim.openstreetmap.org/search"
    geo_params = {"q": destination, "format": "json", "limit": 1}
    headers = {"User-Agent": "TravelPlannerAgent/1.0"}
    
    try:
        geo_res = requests.get(geo_url, params=geo_params, headers=headers, timeout=10)
        geo_res.raise_for_status()
        geo_data = geo_res.json()
        
        if not geo_data:
             return f"Error: Could not find location '{destination}' to check weather."
             
        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]
        
        return get_forecast(lat, lon)
        
    except Exception as e:
         return f"Failed to get weather for {destination} due to error: {str(e)}"

if __name__ == "__main__":
    print(get_weather_forecast.invoke("London"))
