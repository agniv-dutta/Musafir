import requests
import os
from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv()

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
  Morning: [activity]
  Afternoon: [activity]  
  Evening: [activity + dinner recommendation]
  Estimated cost: [cost in local currency]

(Repeat for each day)

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
