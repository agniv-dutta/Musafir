# Wandr

A travel-planning agent backend with a placeholder frontend. The backend exposes tools for destination facts and 7-day weather forecasts.

## Project Structure

```
Wandr/
  backend/
    __init__.py
    agent_core.py
    run_tools_demo.py
    requirements.txt
    tools/
      __init__.py
      destination_tool.py
      weather_tool.py
  frontend/
    index.html
```

## Backend Setup

Create and activate a virtual environment, then install dependencies:

```powershell
cd c:\Projects\Wandr
python -m venv .\backend\.venv
.\backend\.venv\Scripts\Activate.ps1
pip install -r .\backend\requirements.txt
```

## Run the Backend Demo

Runs the destination, weather, currency conversion, and itinerary generation tools (uses public APIs):

```powershell
cd c:\Projects\Wandr
python -m backend.run_tools_demo
```

## Agent Core

`backend/agent_core.py` builds the LangChain agent. To run an agent session, configure a Groq API key and wire tools in your own entry point.

## Frontend

`frontend/index.html` is a static placeholder. Replace it with your UI and connect it to the backend when ready.
