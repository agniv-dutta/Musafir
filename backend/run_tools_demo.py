from backend.tools.destination_tool import get_destination_info
from backend.tools.weather_tool import get_weather_forecast
from backend.tools.currency_tool import convert_currency
from backend.tools.itinerary_tool import generate_itinerary

if __name__ == "__main__":
    print(get_destination_info.run("Tokyo"))
    print()
    print(get_weather_forecast.run("Paris"))
    print()
    print(convert_currency.run("1000 INR USD"))
    print()
    print(generate_itinerary.run("destination: Goa, duration: 4 days, budget: budget, style: beach/relaxed, constraints: none"))
