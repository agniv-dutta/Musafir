from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

from backend.tools.destination_tool import get_destination_info
from backend.tools.weather_tool import get_weather_forecast
from backend.tools.transport_tool import get_transport_prices
from backend.tools.food_price_tool import estimate_food_prices
from backend.tools.currency_tool import convert_currency
from backend.tools.itinerary_tool import generate_itinerary
from backend.tools.calendar_tool import generate_trip_ics
from backend.tools.budget_tool import calculate_trip_budget

load_dotenv()

SYSTEM_PROMPT = """You are an expert travel planning assistant. Your goal is to help users plan complete, well-researched trips.

Follow this logical order when using tools:
1. get_destination_info (always use this first)
2. get_weather_forecast (always use this second)
3. get_transport_prices
4. estimate_food_prices
5. convert_currency (use if a budget or currency is mentioned)
6. generate_itinerary
7. generate_trip_ics
8. calculate_trip_budget (always use this last)

After planning any trip, you MUST:
1. Call get_transport_prices for the origin→destination route
2. Call estimate_food_prices for the destination city and trip duration
3. Call calculate_trip_budget to produce a full cost breakdown
4. Call generate_trip_ics with the final itinerary dates and day events (day can be a number or ISO date)
Always return prices in the user's local currency using convert_currency.

Be thorough, structured, and present a clear final travel plan."""


def build_agent(tools: list):
    """Build and return a LangGraph ReAct agent with the given tools."""
    llm = ChatGroq(
        model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        temperature=0.3,
        api_key=os.getenv("GROQ_API_KEY")  # Loaded from .env
    )

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=SYSTEM_PROMPT
    )

    return agent


tools = [
    get_destination_info,
    get_weather_forecast,
    get_transport_prices,
    estimate_food_prices,
    convert_currency,
    generate_itinerary,
    generate_trip_ics,
    calculate_trip_budget,
]

agent_executor = build_agent(tools)


if __name__ == "__main__":
    print("Agent core loaded successfully.")
