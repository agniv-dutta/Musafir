import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Navbar } from '../components/layout/Navbar';
import { Footer } from '../components/layout/Footer';
import { TripForm } from '../components/planner/TripForm';
import { ResultPanel } from '../components/planner/ResultPanel';
import { TripCalendar } from '../components/planner/TripCalendar';
import { TransportPriceCard } from '../components/planner/TransportPriceCard';
import { BudgetSummary } from '../components/planner/BudgetSummary';
import { TripFormData } from '../types';
import { useTripPlanner } from '../hooks/useTripPlanner';
import { motion } from 'framer-motion';

export const PlannerPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const { result, isLoading, error, planTrip, reset, clearError } = useTripPlanner();
  const [initialData, setInitialData] = useState<Partial<TripFormData> | undefined>(undefined);

  useEffect(() => {
    // Check if there's a pre-filled destination from URL params
    const destination = searchParams.get('destination');
    if (destination) {
      setInitialData({
        destination,
         origin: '',
         startDate: new Date().toISOString().slice(0, 10),
        duration: 5,
        budgetAmount: 150000,
        budgetCurrency: 'INR',
        budgetLevel: 'Moderate',
        travelStyle: 'Balanced',
        constraints: '',
      });
    }
  }, [searchParams]);

  const handleReset = () => {
    reset();
    setInitialData(undefined);
  };

  return (
    <div className="min-h-screen bg-zinc-950">
      <Navbar />

      <main className="pt-24 pb-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="mb-12"
          >
            <h1 className="text-4xl sm:text-5xl font-black text-zinc-50 mb-4">
              Plan Your Perfect Trip
            </h1>
            <p className="text-zinc-400 text-lg max-w-2xl">
              Tell us your preferences and let our AI agent create a personalized itinerary, check the weather, convert your budget, and provide destination insights.
            </p>
          </motion.div>

          {/* Error message */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-8 p-4 bg-red-400/10 border border-red-500/30 rounded-xl text-red-300 flex items-start gap-3"
            >
              <span className="text-2xl mt-1">⚠️</span>
              <div>
                <p className="font-semibold">Error</p>
                <p className="text-sm mt-1">{error}</p>
                <button
                  onClick={clearError}
                  className="text-sm mt-2 underline hover:no-underline"
                >
                  Dismiss
                </button>
              </div>
            </motion.div>
          )}

          {/* Main content grid */}
          <div className="grid lg:grid-cols-[400px_1fr] gap-8">
            <div>
              <TripForm
                onSubmit={planTrip}
                isLoading={isLoading}
                initialData={initialData}
              />
            </div>

            <div className="space-y-6">
              {result && (
                <TripCalendar
                  destination={result.destination}
                  duration={result.duration}
                   startDate={result.startDate}
                  finalAnswer={result.finalAnswer}
                />
              )}

              {result && (
                <TransportPriceCard
                  origin={result.origin}
                  destination={result.destination}
                   date={result.startDate}
                  budgetCurrency={result.budgetCurrency}
                />
              )}

              <ResultPanel
                result={result}
                isLoading={isLoading}
                onReset={handleReset}
              />
            </div>
          </div>
        </div>
      </main>

      {result && (
        <BudgetSummary
          destination={result.destination}
          origin={result.origin}
          duration={result.duration}
          budgetLevel={result.budgetLevel}
           startDate={result.startDate}
          budgetCurrency={result.budgetCurrency}
        />
      )}

      <Footer />
    </div>
  );
};
