from langchain.agents import AgentExecutor, create_react_agent
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.tools import Tool

# System prompt for the Travel Planning Agent
TRAVEL_AGENT_SYSTEM_PROMPT = """
You are an expert travel planning assistant. Your goal is to help users plan 
complete, well-researched trips.

You have access to the following tools:
{tools}

Use this EXACT format for reasoning:
Thought: What do I need to figure out to answer this?
Action: [tool name from: {tool_names}]
Action Input: [input to the tool]
Observation: [result from tool]
... (repeat Thought/Action/Observation as needed)
Thought: I now have enough information to answer.
Final Answer: [a complete, structured travel plan]

Begin!
Question: {input}
{agent_scratchpad}
"""

def build_agent(tools: list) -> AgentExecutor:
    llm = ChatGroq(
        model="llama3-8b-8192",
        temperature=0.3,
        api_key="YOUR_GROQ_API_KEY"
    )
    prompt = PromptTemplate.from_template(TRAVEL_AGENT_SYSTEM_PROMPT)
    agent = create_react_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,          # This produces observable agent logs for the rubric
        handle_parsing_errors=True,
        max_iterations=8
    )

if __name__ == "__main__":
    # Placeholder test — tools wired in main.py
    print("Agent core loaded successfully.")