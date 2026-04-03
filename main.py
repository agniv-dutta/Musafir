import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load .env before any module that needs API keys
load_dotenv()

from backend.agent_core import build_agent
from backend.tools.destination_tool import get_destination_info
from backend.tools.weather_tool import get_weather_forecast
from backend.tools.currency_tool import convert_currency
from backend.tools.itinerary_tool import generate_itinerary


def setup_logging():
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    # Create a timestamped log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/agent_run_{timestamp}.log"

    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return log_filename


def main():
    log_file = setup_logging()
    print(f"Logging session to: {log_file}")

    # Bind the tools
    tools = [
        get_destination_info,
        get_weather_forecast,
        convert_currency,
        generate_itinerary
    ]

    # Build the LangGraph ReAct agent
    agent = build_agent(tools)

    # Define 3 demo test queries
    queries = [
        "Plan a 4-day trip to Tokyo, Japan. My budget is 150,000 INR. I like historic sites.",
        "I want to go to Bali for 5 days. Budget is 2000 USD. I want a relaxing beach trip.",
        "Plan a 3-day weekend in Paris, France. Budget is 500 EUR. I want to see art and eat good food."
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n{'='*50}\nExecuting Demo Query {i}/{len(queries)}\n{'='*50}")
        print(f"User Query: {query}\n")

        # Log the user goal
        logging.info("--- STARTING NEW QUERY ---")
        logging.info(f"User Goal: {query}")

        try:
            # LangGraph returns a dict with a 'messages' list.
            # The last message contains the agent's final answer.
            response = agent.invoke({"messages": [("user", query)]})
            messages = response.get("messages", [])
            final_answer = messages[-1].content if messages else "No output generated."

            print("\n>> FINAL ANSWER <<")
            print(final_answer)

            # Log the final answer
            logging.info(f"Final Answer: {final_answer}")

        except Exception as e:
            error_msg = f"Agent crashed with error: {str(e)}"
            print(error_msg)
            logging.error(error_msg)


if __name__ == "__main__":
    main()
