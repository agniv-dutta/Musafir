import axios, { AxiosInstance } from 'axios';
import { TripFormData, TripResult, WeatherForecast, CurrencyConversion, DestinationInfo, TransportPricesResponse, FoodEstimate, BudgetBreakdown } from '../types';

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for error handling
api.interceptors.request.use(
  config => {
    return config;
  },
  error => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      console.error('Response error:', error.response.data);
      throw new Error(error.response.data.detail || 'API Error');
    } else if (error.request) {
      console.error('Request error:', error.request);
      throw new Error('No response from server');
    } else {
      console.error('Error:', error.message);
      throw error;
    }
  }
);

export const travelApi = {
  /**
   * Plan a trip using the AI agent
   */
  planTrip: async (formData: TripFormData): Promise<TripResult> => {
    const response = await api.post<{
      final_answer: string;
      intermediate_steps: Array<{
        tool: string;
        input: string;
        output: string;
      }>;
    }>('/api/plan', {
      destination: formData.destination,
      origin: formData.origin,
      startDate: formData.startDate,
      duration: formData.duration,
      budgetAmount: formData.budgetAmount,
      budgetCurrency: formData.budgetCurrency,
      budgetLevel: formData.budgetLevel,
      travelStyle: formData.travelStyle,
      constraints: formData.constraints,
    });

    return {
      finalAnswer: response.data.final_answer,
      intermediateSteps: response.data.intermediate_steps,
      destination: formData.destination,
      duration: formData.duration,
      budgetLevel: formData.budgetLevel,
      origin: formData.origin,
      startDate: formData.startDate,
      budgetCurrency: formData.budgetCurrency,
    };
  },

  /**
   * Get weather forecast for a destination
   */
  getWeather: async (destination: string): Promise<WeatherForecast> => {
    const response = await api.get<WeatherForecast>('/api/weather', {
      params: { destination },
    });
    return response.data;
  },

  /**
   * Convert currency
   */
  convertCurrency: async (
    from: string,
    to: string,
    amount: number
  ): Promise<CurrencyConversion> => {
    const response = await api.get<{
      converted: number;
      rate: number;
      updated: string;
    }>('/api/currency', {
      params: { from, to, amount },
    });

    return {
      ...response.data,
      from,
      to,
      amount,
    };
  },

  /**
   * Get destination information
   */
  getDestination: async (name: string): Promise<DestinationInfo> => {
    const response = await api.get<DestinationInfo>('/api/destination', {
      params: { name },
    });
    return response.data;
  },

  getTransportPrices: async (payload: { origin: string; destination: string; date: string; modes: string[] }): Promise<TransportPricesResponse> => {
    const response = await api.post<TransportPricesResponse>('/api/transport', payload);
    return response.data;
  },

  getFoodEstimate: async (payload: { city: string; country?: string; days: number; budget_level: string }): Promise<FoodEstimate> => {
    const response = await api.post<FoodEstimate>('/api/food', payload);
    return response.data;
  },

  getBudgetEstimate: async (payload: { destination: string; origin: string; start_date: string; end_date: string; travelers: number; budget_level: string }): Promise<BudgetBreakdown> => {
    const response = await api.post<BudgetBreakdown>('/api/budget', payload);
    return response.data;
  },

  exportCalendar: async (payload: { destination: string; start_date: string; end_date: string; events: Array<{ day: number; title: string; time: string; description?: string }> }): Promise<{ download_url: string; event_count: number }> => {
    const response = await api.post<{ download_url: string; event_count: number }>('/calendar/export', payload);
    return response.data;
  },
};

export default api;
