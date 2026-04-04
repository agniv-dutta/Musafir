# Enhanced Transport System - Trains & Buses Support

## Overview
Extended the transport system to include trains and buses as transport options alongside flights. Now supports domestic and international routes across India, Europe, Asia, and beyond.

## What Changed

### Previous Behavior
- ❌ Only showed flights for most routes
- ❌ Trains/buses only for Indian domestic routes (hardcoded data)
- ❌ International routes had "not applicable" for ground transport

### New Behavior
- ✅ Shows flights, trains, AND buses for most routes
- ✅ Supports 3+ major regions (Indian, European, Asian)
- ✅ Smart region detection with dynamic pricing
- ✅ 30+ curated train routes across 3 continents
- ✅ Fallback to distance-based pricing for any unknown route

## Supported Regions

### 🇮🇳 Indian Domestic Routes
**16 major routes** with real pricing:
- Mumbai ↔ Pune (3h train | INR 150-800)
- Delhi ↔ Agra (2h train | INR 120-950)
- Bangalore ↔ Chennai (5h train | INR 180-950)
- And 13 more major Indian city pairs

**Coverage**: 15 major Indian cities

### 🇪🇺 European Routes
**10 major routes** with real operators:
- London ↔ Paris (3h 15m Eurostar | GBP 25-120)
- Budapest ↔ Vienna (2h 45m Austrian Railways | EUR 18-75)
- Florence ↔ Rome (2h 30m Trenitalia | EUR 20-80)
- Barcelona ↔ Madrid (2h 30m Renfe | EUR 25-150)
- Amsterdam ↔ Brussels (1h 50m NS/SNCB | EUR 15-65)
- Berlin ↔ Prague (2h 30m Czech Railways | EUR 15-80)
- Munich ↔ Vienna (2h 15m ÖBB | EUR 20-90)
- Edinburgh ↔ London (7h LNER | GBP 35-120)
- Vienna ↔ Zagreb (6h Croatian Railways | EUR 25-90)
- Geneva ↔ Zurich (3h SBB | CHF 40-120)

**Bonus**: FlixBus available for all European routes

**Coverage**: 17 major European cities

### 🌏 Asian Routes
**4 major routes** with regional operators:
- Bangkok ↔ Chiang Mai (13h Thai Railways | THB 500-1500)
- Tokyo ↔ Kyoto (2h 15m JR Shinkansen | JPY 13500-14320)
- Singapore ↔ Kuala Lumpur (7h KTM | SGD 45-95)
- Hong Kong ↔ Guangzhou (1h MTR | HKD 75-220)

**Coverage**: 10 Asian cities

### 🌐 Global Routes
**Any other city pair** gets synthetic but realistic pricing based on:
- Distance between cities
- Route region (if detectable)
- Travel time estimates
- Regional pricing conventions

## How It Works

### 1. Route Region Detection
```
User searches: "Mumbai to Pune"
↓
System detects: Indian domestic route
↓
Uses: INDIAN_ROUTE_DATA (hardcoded actual prices)
```

### 2. Fallback Chain
```
Search for route data:
1. Check exact route in region database
2. If found: Use actual pricing & operators
3. If not found: Generate synthetic by distance
4. Calculate time: distance / typical_speed
5. Calculate price: distance * regional_multiplier
```

### 3. City Normalization
All city lookups normalized:
- "New York" → "new-york"
- "San Francisco" → "san-francisco"
- Handles commas, spaces, hyphens
- Case-insensitive matching

## Transport Data Structure

### Train Option
```json
{
  "journeyTime": "2h 45m",
  "priceRange": "EUR 18-75",
  "frequency": "Multiple daily",
  "operator": "Austrian Railways",
  "source": "live|estimated",
  "minPrice": 18.0,
  "durationHours": 2.75
}
```

### Bus Option
```json
{
  "journeyTime": "3h 30m",
  "priceRange": "EUR 12-35",
  "frequency": "Multiple daily",
  "operator": "FlixBus",
  "source": "live|estimated",
  "minPrice": 12.0,
  "durationHours": 3.5
}
```

## Regional Pricing Multipliers

| Region | Distance Multiplier | Example |
|--------|------------------|---------|
| Indian | 1.0x (baseline) | 500 km = INR 350-1200 |
| European | 0.6-0.7x (cheaper) | 500 km = EUR 30-70 |
| Asian | 0.8-1.0x (moderate) | 500 km = ₹400-1800 |
| Global fallback | 1.0x | Estimated by distance |

## Speed Assumptions

| Mode | Speed | Use Case |
|------|-------|----------|
| Train | 100-120 km/h (short) | Local/regional |
| Train | 80 km/h (long-distance) | Cross-country |
| Bus | 60-80 km/h | All distances |
| Flight | 700 km/h + handling | International |

## Example Responses

### Mumbai to Pune
```
✈️  FLIGHT: IndiGo  | 1h | Direct | INR 5,135
🚂 TRAIN:  Indian Railways | 3h | Hourly | INR 150-800
🚌 BUS:    Regional Operators | 3.5h | Every 30 min | INR 200-600

💡 Best value: BUS (cheapest per travel hour)
```

### Paris to London
```
✈️  FLIGHT: British Airways | 1h 15m | 1 stop | GBP 89
🚂 TRAIN:  Eurostar | 3h 15m | Every 2 hours | GBP 25-120
🚌 BUS:    FlixBus | 8h | Multiple daily | GBP 15-50

💡 Best value: BUS (cheapest per travel hour)
```

### Unknown Route: San Francisco to Los Angeles
```
✈️  FLIGHT: United | 1h | Direct | USD 120
🚂 TRAIN:  Regional | 12.5h | Daily | USD 150-350 (estimated)
🚌 BUS:    Regional | 15h | Daily | USD 100-250 (estimated)

💡 Best value: FLIGHT (fastest for price)
```

## API Integration

### Python Example
```python
from backend.tools.transport_tool import get_transport_options_data

result = get_transport_options_data(
    'Vienna',
    'Budapest',
    currency='EUR'
)

# Output:
# {
#   'region': 'european',
#   'flights': [...],
#   'trains': {
#     'applicable': True,
#     'options': [{
#       'journeyTime': '2h 45m',
#       'priceRange': 'EUR 18-75',
#       'operator': 'Austrian Railways',
#       ...
#     }]
#   },
#   'buses': {...},
#   'bestValue': 'train',
#   'bestValueReason': 'Cheapest per travel hour'
# }
```

## Files Modified

| File | Changes |
|------|---------|
| `backend/tools/transport_tool.py` | Complete refactor with region detection, new route databases, synthetic generation |
| `backend/server.py` | No changes (backward compatible) |
| `frontend/` | No changes needed |

## New Databases

### `EUROPEAN_ROUTE_DATA`
10 routes with real Eurostar, Trenitalia, ÖBB, etc. pricing

### `ASIAN_ROUTE_DATA`
4 routes with Thai Railways, JR Shinkansen, KTM, MTR pricing

### `EUROPEAN_CITY_COORDS`
17 European city coordinates for distance calculation

### `ASIAN_CITY_COORDS`
10 Asian city coordinates for distance calculation

## Backward Compatibility

✅ Fully backward compatible:
- Same API interface
- Same response structure
- Added `operator` field (optional)
- Added `region` field in response (informational)
- Existing code continues to work

## Adding Custom Routes

To add a custom route, update the appropriate database:

```python
# For European routes:
EUROPEAN_ROUTE_DATA["berlin-amsterdam"] = {
    "train": {
        "time": "6h 30m",
        "price_range": "EUR 35-95",
        "frequency": "Multiple daily",
        "operator": "Deutsche Bahn"
    },
    "bus": {
        "time": "8h",
        "price_range": "EUR 15-40",
        "frequency": "Multiple daily",
        "operator": "FlixBus"
    }
}
```

## Future Enhancements

### Phase 2: Real-Time Integration
- Integrate Rome2Rio API for live pricing
- Fetch Trainline.eu data for European trains
- Connect to ITA Matrix for ground transport

### Phase 3: Regional Expansion
- Add Middle East routes (Cairo, Dubai, Istanbul)
- Add South American routes (São Paulo, Buenos Aires)
- Add African routes (Johannesburg, Nairobi)

### Phase 4: Smart Recommendations
- Carbon impact comparison (train vs flight)
- Comfort ratings by mode
- Combined multi-modal journeys
- Portal at time + cost optimization

## Testing

Tested routes verified:
- ✓ Mumbai → Pune (Indian, hardcoded data)
- ✓ Paris → London (European, real Eurostar)
- ✓ Tokyo → Kyoto (Asian, real JR Shinkansen)
- ✓ Vienna → Budapest (European, real Austrian Railways)
- ✓ Unknown routes (synthetic generation)
- ✓ Cross-region routes (fallback to flight + synthetic ground)

## Summary

The enhanced transport system now provides:
1. **Multi-modal options** - Always show flights, trains, AND buses
2. **Regional coverage** - Three continents with real pricing
3. **Smart fallback** - Distance-based pricing for unknown routes
4. **Better UX** - "Best value" recommendation helps travelers choose
5. **Future-proof** - Easy to add new routes and integrate APIs

Users can now find the most economical route between any two cities, whether flying, taking a train, or hopping on a bus! 🚀
