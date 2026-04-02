import requests
import json
from langchain.tools import tool

GROQ_API_KEY = "your_key_here"  # Replace with your Groq API key

@tool
def generate_itinerary(trip_details: str) -> str:
    """Generates a structured day-by-day itinerary with tips and budget summary.
    Input format should vaguely be: "destination: X, duration: Y days, budget: Z, style: W, constraints: V"
    """
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    system_prompt = """You are an expert travel itinerary planner.
Given the details of a trip, create a structured day-by-day plan.
Include some local tips and a brief budget summary at the end.
Be concise but highly actionable."""

    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Please plan this trip:\n{trip_details}"}
        ],
        "temperature": 0.3,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        
        if response.status_code != 200:
            error_data = response.json() if response.text else {}
            # Handle specific API errors
            error_msg = error_data.get('error', {}).get('message', 'Unknown Error')
            
            if response.status_code == 401:
                return "Config Error: Invalid Groq API Key. Please check your key."
            elif response.status_code == 429:
                return "Rate Limit Error: The Groq API rate limit was exceeded. Try again later."
            else:
                return f"Groq API Error {response.status_code}: {error_msg}"
                
        data = response.json()
        
        # Check if the response was cut off because of max_tokens
        finish_reason = data['choices'][0].get('finish_reason', '')
        content = data['choices'][0]['message']['content']
        
        if finish_reason == 'length':
            content += "\n\n[Warning: The itinerary was cut off mid-sentence due to exceeding the max_tokens limit of 1000.]"
            
        return content
        
    except requests.exceptions.Timeout:
        return "Timeout Error: The Groq API took too long to respond."
    except requests.exceptions.RequestException as e:
        return f"Network Error: Could not connect to Groq API. Details: {str(e)}"
    except Exception as e:
        return f"Unexpected Error generating itinerary: {str(e)}"

if __name__ == "__main__":
    test_details = "destination: London, duration: 3 days, budget: $500, style: historical, constraints: no early mornings"
    print("Testing generate_itinerary with sample details...")
    print(generate_itinerary.invoke(test_details))
