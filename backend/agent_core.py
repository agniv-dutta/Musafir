from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

from backend.tools.destination_tool import get_destination_info
from backend.tools.weather_tool import get_weather_forecast
from backend.tools.flight_tool import search_flights
from backend.tools.transport_tool import get_transport_options
from backend.tools.food_price_tool import estimate_food_prices
from backend.tools.currency_tool import convert_currency
from backend.tools.itinerary_tool import generate_itinerary
from backend.tools.calendar_tool import generate_trip_ics
from backend.tools.budget_tool import calculate_trip_budget

load_dotenv()

SYSTEM_PROMPT = """You are an expert travel planning assistant. Your goal is to help users plan complete, well-researched trips.

Tools:
- get_destination_info: Always call first to identify country, currency, and location context.
- get_weather_forecast: Use second for weather and seasonal packing guidance.
- search_flights: Use when user mentions origin city or asks about flights/transport costs.
- get_transport_options: Use for any route when user asks for train/bus options (global web search).
- convert_currency: Use when budget or currency conversion is requested.
- estimate_food_prices: Use to estimate food costs for the destination and duration.
- calculate_trip_budget: Use to produce a structured budget summary.
- generate_itinerary: Always call last after collecting all context.

CRITICAL RULES TO PREVENT HALLUCINATION:
- NEVER invent specific flight prices. If search_flights returns no data, explicitly say: Live pricing unavailable.
- NEVER invent specific train ticket prices for unknown routes. Use get_transport_options output only.
- For budget breakdowns, ALWAYS clearly state which numbers are live vs estimated.
- If a tool returns an error, acknowledge it honestly rather than substituting made-up values.
- The word approximately or estimated MUST appear before any number not directly returned by a tool.

Required tool calling order:
1. get_destination_info (always first)
2. get_weather_forecast
3. search_flights (if origin city provided)
4. get_transport_options (if train/bus or multi-mode request)
5. convert_currency (if budget mentioned)
6. estimate_food_prices (when food costs are needed)
7. calculate_trip_budget (when budget breakdown is requested)
8. generate_itinerary (always last)

Be thorough, transparent about uncertainty, and provide a clear final travel plan."""


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
    search_flights,
    get_transport_options,
    estimate_food_prices,
    convert_currency,
    calculate_trip_budget,
    generate_itinerary,
]

agent_executor = build_agent(tools)


if __name__ == "__main__":
    print("Agent core loaded successfully.")
