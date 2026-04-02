import requests
from langchain.tools import tool

API_KEY = "your_key_here"  # Replace with your ExchangeRate-API key

CURRENCY_NAMES = {
    "INR": "Indian Rupee",
    "USD": "US Dollar",
    "EUR": "Euro",
    "GBP": "British Pound",
    "JPY": "Japanese Yen",
    "AUD": "Australian Dollar",
    "THB": "Thai Baht",
    "SGD": "Singapore Dollar",
    "AED": "United Arab Emirates Dirham",
    "IDR": "Indonesian Rupiah"
}

@tool
def convert_currency(query: str) -> str:
    """Converts money between currencies. Input format: AMOUNT FROM_CURRENCY TO_CURRENCY (e.g. '1000 INR USD')."""
    # Defensive parsing
    parts = query.strip().split()
    if len(parts) < 3:
        return "Format Error: Please provide the amount, from currency, and to currency (e.g., '1000 INR USD')."
        
    try:
        amount_str = parts[0]
        amount = float(amount_str)
    except ValueError:
        return f"Format Error: '{parts[0]}' is not a valid number. Please use format like '1000 INR USD'."
        
    from_currency = parts[1].strip().upper()
    to_currency = parts[2].strip().upper()
    
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{from_currency}/{to_currency}/{amount}"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # Handle specific API errors
        if data.get("result") == "error":
            error_type = data.get("error-type")
            if error_type == "invalid-key":
                return "Config Error: Invalid ExchangeRate API key. Please check your key."
            elif error_type == "unsupported-code":
                return f"Unsupported Currency: One or both currency codes ({from_currency}, {to_currency}) are not supported."
            elif error_type == "quota-reached":
                return "Quota Error: The free tier limit for the ExchangeRate API has been reached."
            else:
                return f"API Error: {error_type}"
                
        response.raise_for_status()
        
        conversion_result = data.get("conversion_result")
        conversion_rate = data.get("conversion_rate")
        time_last_update_utc = data.get("time_last_update_utc")
        
        from_name = CURRENCY_NAMES.get(from_currency, from_currency)
        to_name = CURRENCY_NAMES.get(to_currency, to_currency)
        
        return (f"{amount:,.2f} {from_currency} ({from_name}) = {conversion_result:,.2f} {to_currency} ({to_name})\n"
                f"Rate: 1 {from_currency} = {conversion_rate} {to_currency} | Updated: {time_last_update_utc}")
                
    except requests.exceptions.Timeout:
        return "Timeout Error: The currency API took too long to respond. Please try again later."
    except requests.exceptions.RequestException as e:
        return f"Network Error: Could not connect to the currency API. Details: {str(e)}"
    except Exception as e:
        return f"Unexpected Error processing currency conversion: {str(e)}"

if __name__ == "__main__":
    print("Testing string '1000 INR USD'...")
    print(convert_currency.invoke("1000 INR USD"))
    print("\nTesting invalid format '1000 INR'...")
    print(convert_currency.invoke("1000 INR"))
