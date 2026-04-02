from langchain.agents import AgentExecutor, create_react_agent
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

GROQ_API_KEY = "your_key_here"  # Replace with your Groq API key

# System prompt for the Travel Planning Agent with specific instructions
TRAVEL_AGENT_SYSTEM_PROMPT = """
You are an expert travel planning assistant. Your goal is to help users plan complete, well-researched trips.

You must gather information before generating a final itinerary. Follow this EXACT logical order when using tools:
1. get_destination_info (always use this first to get basic country facts and coordinates)
2. get_weather_forecast (always use this second, before recommending any dates or packing tips)
3. convert_currency (use this third if a budget or currency is mentioned)
4. generate_itinerary (always use this last, passing all gathered details into it)

You have access to the following tools:
{tools}

Use this EXACT format for reasoning:
Thought: What do I need to figure out to answer this?
Action: [tool name from: {tool_names}]
Action Input: [input to the tool]
Observation: [result from tool]
... (repeat Thought/Action/Observation as needed)
Thought: I now have enough information to answer.
Final Answer: [a structured summary of the travel plan, presenting the final itinerary to the user]

Begin!
Question: {input}
{agent_scratchpad}
"""

def build_agent(tools: list) -> AgentExecutor:
    # Initialize the LLM
    llm = ChatGroq(
        model="llama3-8b-8192",
        temperature=0.3,
        api_key=GROQ_API_KEY
    )
    
    # Create the ReAct prompt
    prompt = PromptTemplate.from_template(TRAVEL_AGENT_SYSTEM_PROMPT)
    
    # Create the ReAct agent
    agent = create_react_agent(llm, tools, prompt)
    
    # Create and return the AgentExecutor
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True, # Prints Thought/Action/Observation strictly to terminal
        return_intermediate_steps=True, # Captures steps for log files if needed
        max_iterations=8, # Prevents infinite loops
        handle_parsing_errors=True # Robustness
    )