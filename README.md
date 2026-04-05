<div align="center">

# 🌍 MUSAFIR

**AI-Powered Travel Planning Made Simple**

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3%2B-61dafb?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5%2B-3178c6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-3.4%2B-06b6d4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.0%2B-1c3c3c?style=for-the-badge&logo=langchain&logoColor=white)](https://www.langchain.com/)
[![Vite](https://img.shields.io/badge/Vite-5.4%2B-646cff?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)

### ✨ Intelligent Travel Companion Powered by ReAct Agent Framework

Musafir uses an advanced AI agent orchestrated with **LangGraph ReAct** to intelligently plan your trips. It analyzes your preferences, destination context, and real-time data to generate personalized itineraries, dynamic budgets, weather insights, and transport recommendations.

---

### 👥 Contributors

| Developer |
|-----------|
| **Agniv Dutta** |
| **Aditya Choudhuri** |
| **Aaryan Dubey** |

</div>

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [Configuration](#-configuration)
- [Running the App](#-running-the-app)
- [Development](#-development)

---

## ✨ Features

### 🎯 Core Features

- **AI-Powered Itinerary Generation**: Uses LangGraph ReAct agent with LLaMA 3.1 to create detailed, context-aware travel plans
- **Dynamic Daily Food Planning**: Per-day meal suggestions with regional specialties, themed costs, and dietary constraint support
- **Real-Time Currency Conversion**: Convert trip budgets dynamically between any currency pair using live exchange rates
- **7-Day Weather Forecasts**: Accurate weather predictions with alerts and recommendations for your destination
- **Transport Price Comparison**: Flight, train, and bus pricing across multiple providers
- **Trip Budget Breakdown**: Detailed expense estimations including flights, accommodation, food, activities, and transport
- **Destination Intelligence**: Rich destination insights including cultural tips, local food, attractions, and geography
- **Calendar Integration**: Export itineraries as `.ics` files and integrate with your calendar app
- **Responsive Design**: Fully mobile-optimized UI with dark theme and glassmorphism styling

### 🚀 Advanced Features

- **Activity-Based Theme Detection**: Meal plans and recommendations adapt to your travel style (cultural, beach, nightlife, shopping, adventure)
- **Regional Cuisine Integration**: Curated meal suggestions from 7+ countries with authentic local dishes
- **Multi-Leg Trip Support**: Handle complex routes with multiple destinations and stopovers
- **Constraint-Aware Planning**: Dietary restrictions and travel preferences are incorporated throughout the itinerary
- **Agent Reasoning Trace**: Inspect the AI's decision-making process step-by-step through the ReAct trace panel
- **Error Recovery**: Intelligent fallback system synthesizes itineraries dynamically when APIs are rate-limited
- **Dynamic Itinerary Synthesis**: Context-aware fallback generation that incorporates actual trip details, never using templates

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework for building APIs
- **LangChain** - LLM orchestration and agent framework
- **LangGraph** - Multi-agent orchestration with ReAct pattern
- **Groq LLaMA 3.1** - Fast, efficient large language model
- **Python Requests** - HTTP client for external APIs
- **iCalendar** - Calendar file generation
- **Python-dotenv** - Environment variable management

### Frontend
- **React 18** - UI library
- **TypeScript 5.5** - Type-safe JavaScript
- **Tailwind CSS 3.4** - Utility-first CSS framework
- **Vite 5.4** - Lightning-fast build tool
- **React Router v6** - Client-side routing
- **Axios** - HTTP client
- **Framer Motion** - Animation library
- **React Big Calendar** - Calendar component
- **Lucide React** - Icon library
- **Recharts** - Charting library
- **Date-fns** - Date utility library

### External APIs
- **Groq API** - LLM inference (llama-3.1-8b-instant)
- **ExchangeRate-API** - Real-time currency conversion
- **Open-Meteo** - Free weather forecasting
- **Travelpayouts** - Flight and transport pricing
- **Nominatim (OpenStreetMap)** - Geocoding and location data
- **REST Countries API** - Country metadata
- **DuckDuckGo Search** - Web search integration

---

## 📁 Project Structure

```
Musafir/
├── backend/
│   ├── agent_core.py              # ReAct agent with LangGraph orchestration
│   ├── server.py                  # FastAPI application with all endpoints
│   ├── requirements.txt           # Python dependencies
│   ├── run_tools_demo.py         # Tool demonstration script
│   └── tools/
│       ├── __init__.py
│       ├── budget_tool.py         # Trip budget estimation
│       ├── calendar_tool.py       # Calendar event generation
│       ├── currency_tool.py       # Currency conversion
│       ├── destination_tool.py    # Destination information fetching
│       ├── food_price_tool.py     # Dynamic meal planning with regional dishes
│       ├── itinerary_tool.py      # Structured itinerary generation
│       ├── search_utils.py        # Web search utilities
│       ├── transport_tool.py      # Flight/train/bus pricing
│       └── weather_tool.py        # Weather forecasting
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── travel.ts          # API client with typed endpoints
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Navbar.tsx     # Navigation header
│   │   │   │   └── Footer.tsx     # Footer
│   │   │   ├── home/
│   │   │   │   ├── Hero.tsx       # Landing hero section
│   │   │   │   └── FeatureCards.tsx # Feature showcase
│   │   │   ├── planner/
│   │   │   │   ├── TripForm.tsx   # Main trip form
│   │   │   │   ├── ResultPanel.tsx # Results container
│   │   │   │   ├── ItineraryTab.tsx # Day-by-day itinerary
│   │   │   │   ├── WeatherTab.tsx # Weather forecast
│   │   │   │   ├── CurrencyTab.tsx # Currency conversion display
│   │   │   │   ├── DestinationTab.tsx # Destination info
│   │   │   │   ├── AgentTraceTab.tsx # ReAct reasoning trace
│   │   │   │   ├── BudgetSummary.tsx # Budget breakdown
│   │   │   │   ├── TripCalendar.tsx # Calendar view
│   │   │   │   ├── TransportPriceCard.tsx # Transport options
│   │   │   │   └── WeatherWarning.tsx # Weather alerts
│   │   │   └── ui/
│   │   │       ├── Badge.tsx      # Status badges
│   │   │       ├── Button.tsx     # Button component
│   │   │       ├── Card.tsx       # Card component
│   │   │       ├── Spinner.tsx    # Loading spinner
│   │   │       └── TabBar.tsx     # Tab navigation
│   │   ├── hooks/
│   │   │   └── useTripPlanner.ts  # Trip planning logic hook
│   │   ├── pages/
│   │   │   ├── HomePage.tsx       # Home page
│   │   │   └── PlannerPage.tsx    # Planner page
│   │   ├── types/
│   │   │   └── index.ts           # TypeScript type definitions
│   │   ├── App.tsx                # Main app component
│   │   ├── main.tsx               # Entry point
│   │   └── index.css              # Global styles + Tailwind
│   ├── index.html                 # HTML template
│   ├── package.json               # Frontend dependencies
│   ├── tsconfig.json              # TypeScript config
│   ├── tsconfig.node.json         # Build-time TypeScript config
│   ├── vite.config.ts             # Vite configuration
│   ├── tailwind.config.ts         # Tailwind configuration
│   ├── postcss.config.js          # PostCSS configuration
│   ├── .env                       # Frontend environment variables
│   └── README.md                  # Frontend documentation
│
├── .env                           # Backend environment variables
├── .env.example                   # Environment template
├── requirements.txt               # Root-level requirements (optional)
├── main.py                        # Optional root entry point
├── agent_core.py                  # Optional root agent file
├── PROJECT_SUMMARY.md             # Project completion summary
├── SETUP.md                       # Setup guide
└── README.md                      # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Node.js 18 or higher
- npm or yarn
- API keys for:
  - **Groq API** (free tier available)
  - **ExchangeRate-API** (free tier: 1500 calls/month)

### 1. Backend Setup

```bash
# Navigate to project root
cd Musafir

# Create Python virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.\.venv\Scripts\Activate.ps1

# Or on macOS/Linux
source .venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the project root with your API keys:

```bash
# .env
GROQ_API_KEY=your_groq_api_key_here
EXCHANGE_RATE_API_KEY=your_exchange_rate_api_key_here
```

Get your API keys:
- **Groq API**: Go to [console.groq.com](https://console.groq.com) and create a free API key
- **ExchangeRate-API**: Visit [exchangerate-api.com](https://www.exchangerate-api.com) for free tier access

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install frontend dependencies
npm install

# Create frontend .env (optional, defaults work)
# Copy from .env.example if needed
```

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000/api
```

### Endpoints

#### 🎯 Trip Planning

##### `POST /api/plan`
Generate complete trip plan with itinerary, budget, and recommendations.

**Request Body:**
```json
{
  "destination": "Paris, France",
  "origin": "New York, USA",
  "duration": 7,
  "budgetAmount": 3000,
  "budgetCurrency": "USD",
  "budgetLevel": "Moderate",
  "travelStyle": "Cultural",
  "constraints": "vegetarian"
}
```

**Response:**
```json
{
  "final_answer": "Day 1: Arrive in Paris...",
  "intermediate_steps": ["identify_destination", "generate_itinerary", "estimate_budget"],
  "trip_context": {
    "destination": "Paris",
    "country": "France",
    "duration": 7,
    "budget": 3000,
    "currency": "USD"
  }
}
```

---

#### 🌤️ Weather

##### `GET /api/weather`
Get 7-day weather forecast for destination.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `destination` | string | City and country (e.g., "Paris, France") |

**Response:**
```json
{
  "destination": "Paris, France",
  "forecast": [
    {
      "date": "2026-04-01",
      "condition": "Partly Cloudy",
      "maxTemp": 18,
      "minTemp": 12,
      "precipitation": 0.2,
      "windSpeed": 12,
      "weatherCode": 2
    }
  ]
}
```

---

#### 💱 Currency Conversion

##### `GET /api/currency`
Convert between any two currencies with live exchange rates.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `from` | string | Source currency code (e.g., "USD") |
| `to` | string | Target currency code (e.g., "EUR") |
| `amount` | float | Amount to convert (default: 100) |

**Example:**
```
GET /api/currency?from=USD&to=EUR&amount=500
```

**Response:**
```json
{
  "from": "USD",
  "to": "EUR",
  "amount": 500,
  "converted": 462.50,
  "rate": 0.925,
  "timestamp": "2026-04-04T10:30:00Z"
}
```

---

#### 🍽️ Food & Budget

##### `POST /api/food`
Get overall food budget estimate for a trip.

**Request Body:**
```json
{
  "city": "Bangkok",
  "country": "Thailand",
  "days": 5,
  "budget_level": "Budget"
}
```

**Response:**
```json
{
  "city": "Bangkok",
  "country": "Thailand",
  "currency": "THB",
  "daily_average": 1200,
  "total_food_cost": 6000,
  "budget_level": "Budget"
}
```

##### `POST /api/food/day-plan`
Get **context-aware per-day meal plans** with regional specialties and themed adjustments.

**Request Body:**
```json
{
  "city": "Zagreb",
  "country": "Croatia",
  "days": 5,
  "budget_level": "Moderate",
  "itinerary_days": [
    "Beach day at Adriatic, relax and swim",
    "Old town cultural exploration",
    "Nightlife in Grič, wine tasting",
    "Food market tour and cooking class",
    "Shopping and last-minute souvenirs"
  ]
}
```

**Response:**
```json
{
  "city": "Zagreb",
  "country": "Croatia",
  "currency": "HRK",
  "daily_average": 450,
  "total_food_cost": 2250,
  "days": [
    {
      "day": 1,
      "theme": "Beach",
      "context": "Beach day at Adriatic, relax and swim",
      "breakfast": { "amount": 120, "suggestion": "Fresh bakery pastries with Adriatic sea view" },
      "lunch": { "amount": 280, "suggestion": "Grilled fish with local olive oil" },
      "dinner": { "amount": 320, "suggestion": "Seafood risotto (Crni rižoto)" },
      "daily_total": 720,
      "nearby_source": "https://duckduckgo.com/?q=beach+food+croatia"
    }
  ]
}
```

##### `POST /api/budget`
Get comprehensive trip budget breakdown.

**Request Body:**
```json
{
  "destination": "Bangkok, Thailand",
  "origin": "Tokyo, Japan",
  "start_date": "2026-04-15",
  "end_date": "2026-04-22",
  "travelers": 2,
  "budget_level": "Moderate"
}
```

**Response:**
```json
{
  "destination": "Bangkok, Thailand",
  "total_budget": 6000,
  "currency": "USD",
  "breakdown": {
    "flights": 1200,
    "accommodation": 2400,
    "food": 1500,
    "activities": 600,
    "transport": 300
  },
  "daily_average": 857
}
```

---

#### 🚗 Transport

##### `POST /api/transport`
Get transport options comparison (flight, train, bus).

**Request Body:**
```json
{
  "origin": "New York, USA",
  "destination": "London, UK",
  "date": "2026-05-01",
  "modes": ["flight", "train"]
}
```

**Response:**
```json
{
  "flight": {
    "price": 450,
    "currency": "USD",
    "duration": "7h 30m",
    "provider": "Travelpayouts"
  },
  "train": null,
  "routeResolved": {
    "originCity": "New York",
    "destinationCity": "London",
    "originIata": "JFK",
    "destinationIata": "LHR"
  }
}
```

##### `GET /api/transport`
Query transport prices with query parameters.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `origin` | string | Origin city |
| `destination` | string | Destination city |
| `date` | string | Travel date (YYYY-MM-DD) |
| `travel_class` | string | Economy, Business, etc. |

---

#### 🗺️ Destination

##### `GET /api/destination`
Get rich destination information.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | City and country (e.g., "Paris, France") |

**Response:**
```json
{
  "name": "Paris",
  "country": "France",
  "currency": "Euro (EUR)",
  "timezone": "Europe/Paris",
  "language": "French",
  "best_time": "April to June, September to October",
  "description": "The City of Light...",
  "attractions": ["Eiffel Tower", "Louvre", "Arc de Triomphe"],
  "local_food": ["Croissants", "Coq au Vin", "Escargot"],
  "culture": "Rich history, art, cuisine, romance",
  "safety": "Safe city with excellent public transport",
  "budget_tips": "Street markets offer affordable meals"
}
```

---

#### 📅 Calendar

##### `POST /calendar/export`
Export trip itinerary as `.ics` calendar file.

**Request Body:**
```json
{
  "destination": "Tokyo, Japan",
  "start_date": "2026-05-01",
  "end_date": "2026-05-08",
  "events": [
    {
      "day": 1,
      "title": "Arrival at Narita Airport",
      "time": "14:00",
      "description": "Arrive and transfer to hotel"
    }
  ]
}
```

**Response:**
```json
{
  "download_url": "/calendar/download?filename=Tokyo-2026-05-01.ics",
  "filename": "Tokyo-2026-05-01.ics"
}
```

##### `GET /calendar/download`
Download the generated `.ics` file.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `filename` | string | The `.ics` filename to download |

---

#### 📍 Places

##### `GET /api/places/suggest`
Get place suggestions (cities, attractions).

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Search term |
| `max_results` | int | Maximum results (default: 5) |

**Response:**
```json
{
  "suggestions": [
    { "name": "Paris, France", "type": "city", "region": "Ile-de-France" },
    { "name": "Versailles, France", "type": "city", "region": "Ile-de-France" }
  ]
}
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Required API Keys
GROQ_API_KEY=gsk_...your_key_here...
EXCHANGE_RATE_API_KEY=your_exchange_rate_key_here

# Optional: Backend Settings
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DEBUG=false

# Optional: Frontend Settings (in frontend/.env)
VITE_API_BASE_URL=http://localhost:8000
```

### CORS Settings
The backend is configured to accept requests from:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (Alternative frontend port)
- `http://127.0.0.1:5173` (IPv4 localhost)

---

## 🏃 Running the App

### Development Mode

#### Terminal 1: Start Backend

```powershell
# Windows PowerShell
cd C:\Musafir
.\.venv\Scripts\Activate.ps1
uvicorn backend.server:app --host 0.0.0.0 --port 8000 --reload
```

Or directly with Python:

```bash
python backend/server.py
```

Backend runs at: `http://localhost:8000`
API docs available at: `http://localhost:8000/docs` (Swagger UI)

#### Terminal 2: Start Frontend

```bash
cd C:\Musafir\frontend
npm run dev
```

Frontend runs at: `http://localhost:5173`

---

### Production Build

#### Build Frontend

```bash
cd frontend
npm run build
npm run preview
```

#### Run Backend Production

```bash
pip install gunicorn
gunicorn backend.server:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 🛠️ Development

### Project Setup

```bash
# Clone and setup
git clone <repository-url>
cd Musafir

# Backend setup
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate     # macOS/Linux
pip install -r backend/requirements.txt

# Frontend setup
cd frontend
npm install
cd ..
```

### Running Tests

```bash
# Backend tools test
python backend/run_tools_demo.py
```

### Hot Reload

- **Backend**: Uvicorn watches for Python file changes automatically (with `--reload`)
- **Frontend**: Vite provides instant HMR (Hot Module Replacement)

### IDE Setup

**Recommended VS Code Extensions:**
- Python
- Pylance
- FastAPI
- TypeScript Vue Plugin
- Tailwind CSS IntelliSense
- Thunder Client or REST Client (for API testing)

### Code Style

- **Python**: Follow PEP 8 (use `black` for formatting)
- **TypeScript/React**: Use Prettier for code formatting
- **CSS**: Tailwind utility classes

---

## 🌟 Key Highlights

### ReAct Agent Architecture
The app uses LangGraph's ReAct (Reasoning + Acting) pattern to orchestrate the AI:
1. **Reasoning**: LLaMA 3.1 thinks through the trip requirements
2. **Acting**: Calls specialized tools (destination, weather, transport, food, budget)
3. **Iterating**: Refines results based on tool outputs
4. **Fallback**: If primary tools fail, dynamically generates contextual itineraries

### Dynamic Content Generation
- **Itineraries** are synthesized from real data, never using templates
- **Food plans** adapt to daily activities and regional cuisines
- **Budgets** incorporate real-time exchange rates and actual provider pricing
- **Constraints** (dietary, travel style) influence all recommendations

### Responsive UX
- Mobile-first design with Tailwind CSS
- Dark theme with glassmorphism UI
- Real-time API responses with loading states
- Calendar integration for easy travel planning

---

## 📝 License

This project is open source and available under the MIT License.

---

## 🤝 Support

For issues, questions, or suggestions, please open an issue on the repository.

Happy traveling with Musafir! ✈️🌎🗺️
