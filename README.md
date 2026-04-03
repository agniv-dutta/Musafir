# Wandr

Wandr is a travel-planning agent with a FastAPI backend and a Vite + React frontend.
It provides destination facts, weather forecasts, currency conversion, itinerary generation, transport pricing, food estimates, trip budget breakdowns, and calendar exports.

## Project Structure

```text
Wandr/
  .env
  .env.example
  backend/
    agent_core.py
    server.py
    requirements.txt
    tools/
      calendar_tool.py
      transport_tool.py
      food_price_tool.py
      budget_tool.py
      destination_tool.py
      weather_tool.py
      currency_tool.py
      itinerary_tool.py
  frontend/
    src/
    package.json
```

## Backend Setup

```powershell
cd c:\Projects\Wandr
python -m venv .\.venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

## Run The Backend API

```powershell
cd c:\Projects\Wandr
python backend\server.py
```

## Run The Frontend

```powershell
cd c:\Projects\Wandr\frontend
npm install
npm run dev
```

## Environment

Keep API keys in the root `.env` file. Copy `.env.example` for a template.
Required keys:
- `GROQ_API_KEY`
- `EXCHANGE_RATE_API_KEY`

## Calendar Export

The planner can generate an `.ics` file and download it directly.
Use the **Add to Calendar** button in the planner UI.
