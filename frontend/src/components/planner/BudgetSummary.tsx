import React, { useEffect, useMemo, useState } from 'react';
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip, Cell } from 'recharts';
import { travelApi } from '../../api/travel';
import { BudgetBreakdown } from '../../types';

interface BudgetSummaryProps {
  destination: string;
  origin: string;
  duration: number;
  budgetLevel: 'Budget' | 'Moderate' | 'Luxury';
  startDate: string;
  budgetCurrency: string;
}

export const BudgetSummary: React.FC<BudgetSummaryProps> = ({ destination, origin, duration, budgetLevel, startDate, budgetCurrency }) => {
  const [budget, setBudget] = useState<BudgetBreakdown | null>(null);
  const [rate, setRate] = useState(1);

  const dates = useMemo(() => {
    const start = new Date(startDate);
    const end = new Date(startDate);
    end.setDate(end.getDate() + Math.max(duration - 1, 0));
    return {
      start_date: start.toISOString().slice(0, 10),
      end_date: end.toISOString().slice(0, 10),
    };
  }, [startDate, duration]);

  useEffect(() => {
    const fetchBudget = async () => {
      if (!destination) return;
      const response = await travelApi.getBudgetEstimate({
        destination,
        origin: origin || 'your city',
        start_date: dates.start_date,
        end_date: dates.end_date,
        travelers: 1,
        budget_level: budgetLevel.toLowerCase(),
      });
      setBudget(response);
    };

    fetchBudget();
  }, [destination, origin, dates, budgetLevel]);

  useEffect(() => {
    const fetchRate = async () => {
      if (!budget || budget.currency === budgetCurrency) {
        setRate(1);
        return;
      }
      const response = await travelApi.convertCurrency(budget.currency, budgetCurrency, 1);
      setRate(response.rate || 1);
    };

    fetchRate();
  }, [budget, budgetCurrency]);

  if (!budget || !budget.transport || !budget.accommodation || !budget.food || !budget.activities) {
    return (
      <div className="fixed bottom-4 right-6 left-6 lg:left-[40%] bg-zinc-900/95 border border-zinc-800 rounded-2xl p-6 shadow-xl">
        <p className="text-sm text-zinc-400">Budget summary is loading…</p>
      </div>
    );
  }

  const data = [
    { name: 'Transport', value: (budget.transport.amount ?? 0) * rate, color: '#3B82F6' },
    { name: 'Hotel', value: (budget.accommodation.amount ?? 0) * rate, color: '#8B5CF6' },
    { name: 'Food', value: (budget.food.amount ?? 0) * rate, color: '#F59E0B' },
    { name: 'Activities', value: (budget.activities.amount ?? 0) * rate, color: '#14B8A6' },
    { name: 'Misc', value: (budget.miscellaneous?.amount ?? 0) * rate, color: '#94A3B8' },
  ];

  const confidenceColor = {
    high: 'bg-emerald-500/20 text-emerald-300',
    medium: 'bg-amber-500/20 text-amber-300',
    low: 'bg-red-500/20 text-red-300',
  }[budget.confidence];

  return (
    <div className="fixed bottom-4 right-6 left-6 lg:left-[40%] bg-zinc-900/95 border border-zinc-800 rounded-2xl p-6 shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-bold text-zinc-50">Budget Summary</h3>
          <p className="text-xs text-zinc-400">Estimated total for {destination}</p>
        </div>
        <span className={`text-xs px-3 py-1 rounded-full ${confidenceColor}`}>
          {budget.confidence.toUpperCase()} confidence
        </span>
      </div>

      <div className="grid lg:grid-cols-[1fr_220px] gap-6 items-center">
        <div className="h-40">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} layout="vertical" margin={{ left: 0 }}>
              <XAxis type="number" hide />
              <YAxis type="category" dataKey="name" width={90} tick={{ fill: '#9CA3AF', fontSize: 12 }} />
              <Tooltip cursor={{ fill: 'rgba(255,255,255,0.06)' }} />
              <Bar dataKey="value" radius={[0, 8, 8, 0]}>
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="text-right">
          <p className="text-xs text-zinc-400">Estimated total</p>
          <p className="text-3xl font-bold text-zinc-50">
            {budgetCurrency} {(budget.grand_total * rate).toFixed(0)}
          </p>
          <p className="text-sm text-zinc-400">
            Per person: {budgetCurrency} {(budget.total_per_person * rate).toFixed(0)}
          </p>
          <button className="mt-4 px-3 py-2 bg-zinc-800 text-zinc-200 rounded-lg text-xs">
            Refine Estimate
          </button>
        </div>
      </div>
    </div>
  );
};
