export interface TripFormData {
  destination: string;
  origin: string;
  startDate: string;
  duration: number;
  budgetAmount: number;
  budgetCurrency: string;
  budgetLevel: 'Budget' | 'Moderate' | 'Luxury';
  travelStyle: string;
  constraints: string;
}

export interface WeatherDay {
  date: string;
  condition: string;
  maxTemp: number;
  minTemp: number;
  precipitation: number;
  windSpeed: number;
  weatherCode: number;
}

export interface AgentStep {
  tool: string;
  input: string;
  output: string;
}

export interface TripResult {
  finalAnswer: string;
  intermediateSteps: AgentStep[];
  destination: string;
  duration: number;
  budgetLevel: 'Budget' | 'Moderate' | 'Luxury';
  origin: string;
  startDate: string;
  budgetCurrency: string;
  budgetAmount: number;
}

export interface TransportPrice {
  min_price: number;
  max_price: number;
  currency: string;
  source: string;
  booking_url: string;
  mode: string;
}

export interface TransportPricesResponse {
  flight?: TransportPrice;
  train?: TransportPrice;
  bus?: TransportPrice;
}

export interface FoodEstimate {
  breakfast_avg: number;
  lunch_avg: number;
  dinner_avg: number;
  daily_food_budget: number;
  total_food_cost: number;
  currency: string;
  notes: string;
  sources: string[];
}

export interface FoodDayMeal {
  amount: number;
  suggestion: string;
}

export interface FoodDayPlanItem {
  day: number;
  theme: string;
  context: string;
  breakfast: FoodDayMeal;
  lunch: FoodDayMeal;
  dinner: FoodDayMeal;
  daily_total: number;
  lunch_source?: string;
  dinner_source?: string;
  nearby_source?: string;
}

export interface FoodDayPlan {
  city: string;
  currency: string;
  days: FoodDayPlanItem[];
  daily_average: number;
  total_food_cost: number;
  notes: string;
  sources: string[];
}

export interface BudgetBreakdown {
  transport: { amount: number; mode: string; currency: string };
  accommodation: { amount: number; per_night: number; nights: number; currency: string };
  food: { amount: number; per_day: number; currency: string };
  activities: { amount: number; per_day: number; currency: string };
  miscellaneous: { amount: number; note: string };
  total_per_person: number;
  grand_total: number;
  currency: string;
  confidence: 'low' | 'medium' | 'high';
}

export interface DestinationInfo {
  country: string;
  capital: string;
  population: string;
  timezone: string;
  currency: string;
  languages: string[];
  coordinates: {
    latitude: number;
    longitude: number;
  };
  tips: string[];
}

export interface CurrencyConversion {
  converted: number;
  rate: number;
  updated: string;
  from: string;
  to: string;
  amount: number;
}

export interface PlaceSuggestion {
  name: string;
  display_name: string;
  city: string;
  country: string;
  type: string;
}

export interface FlightOffer {
  airline: string;
  airlineCode: string;
  departureTime: string;
  arrivalTime: string;
  arrivalDayOffset: number;
  duration: string;
  durationMinutes: number;
  stops: number;
  price: number;
  currency: string;
  route: string;
  sourceTitle?: string;
  sourceUrl?: string;
  sourceSnippet?: string;
}

export interface GroundTransportOption {
  mode: 'train' | 'bus';
  journeyTime: string;
  priceRange: string;
  frequency: string;
  source: 'live' | 'estimated' | string;
  minPrice?: number;
  durationHours?: number;
}

export interface TransportModeResponse {
  applicable: boolean;
  options: GroundTransportOption[];
  message?: string;
}

export interface TransportOverviewResponse {
  flights: FlightOffer[];
  flightSource?: string;
  flightMessage?: string;
  routeResolved?: {
    originCity?: string;
    destinationCity?: string;
    originIata?: string;
    destinationIata?: string;
  };
  trains: TransportModeResponse;
  buses: TransportModeResponse;
  bestValue: 'flight' | 'train' | 'bus' | null;
  bestValueReason: string;
}

export interface BudgetBreakdownCategory {
  amount: number;
  currency: string;
  source: 'travelpayouts_live' | 'estimated' | 'calculated' | 'not_applicable' | string;
  confidence: 'high' | 'medium' | 'low';
  detail: string;
}

export interface BudgetBreakdownResponse {
  breakdown: {
    transport: BudgetBreakdownCategory;
    accommodation: BudgetBreakdownCategory;
    food: BudgetBreakdownCategory;
    activities: BudgetBreakdownCategory;
    misc: BudgetBreakdownCategory;
  };
  total: number;
  currency: string;
  withinBudget: boolean;
  overage: number;
  adults: number;
  perPerson: number;
}

export interface WeatherForecast {
  forecast: WeatherDay[];
  recommendation: string;
}
