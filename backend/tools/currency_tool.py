import requests
import os
from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv()

@tool
def convert_currency(query: str) -> str:
    """
    Converts an amount from one currency to another for travel budgeting.
    Input format: 'AMOUNT FROM_CURRENCY TO_CURRENCY'
    Examples: '1000 INR USD', '500 EUR JPY', '200 USD GBP'
    """
    try:
        parts = query.strip().upper().split()
        if len(parts) != 3:
            return (
                "Invalid format. Use: 'AMOUNT FROM_CURRENCY TO_CURRENCY'\n"
                "Example: '1000 INR USD'"
            )

        amount_str, from_currency, to_currency = parts
        amount = float(amount_str)

        # ExchangeRate-API: 1500 free calls/month, no card needed
        # Sign up at https://www.exchangerate-api.com/ for a free key
        API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")
        url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{from_currency}/{to_currency}/{amount}"

        response = requests.get(url)
        data = response.json()

        if data.get("result") == "success":
            converted = data["conversion_result"]
            rate = data["conversion_rate"]
            return (
                f"Currency Conversion:\n"
                f"{amount:,.2f} {from_currency} = {converted:,.2f} {to_currency}\n"
                f"Exchange rate: 1 {from_currency} = {rate} {to_currency}\n"
                f"(Rates updated: {data.get('time_last_update_utc', 'N/A')})"
            )
        else:
            return f"Conversion failed: {data.get('error-type', 'Unknown error')}"

    except ValueError:
        return "Invalid amount. Please enter a valid number."
    except Exception as e:
        return f"Error during currency conversion: {str(e)}"


def convert_amount(from_currency: str, to_currency: str, amount: float) -> dict:
    """Return a structured conversion for internal API usage."""
    API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{from_currency}/{to_currency}/{amount}"

    response = requests.get(url)
    data = response.json()

    if data.get("result") != "success":
        return {
            "converted": 0.0,
            "rate": 0.0,
            "updated": data.get("time_last_update_utc", "N/A"),
        }

    return {
        "converted": data["conversion_result"],
        "rate": data["conversion_rate"],
        "updated": data.get("time_last_update_utc", "N/A"),
    }


if __name__ == "__main__":
    print(convert_currency.run("1000 INR USD"))
