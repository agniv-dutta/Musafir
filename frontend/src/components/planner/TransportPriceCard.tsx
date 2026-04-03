import React, { useEffect, useMemo, useState } from 'react';
import { travelApi } from '../../api/travel';
import { TransportPricesResponse, TransportPrice } from '../../types';
import { motion } from 'framer-motion';

interface TransportPriceCardProps {
  origin: string;
  destination: string;
  date: string;
  budgetCurrency: string;
}

const tabs = ['flight', 'train', 'bus'] as const;

export const TransportPriceCard: React.FC<TransportPriceCardProps> = ({ origin, destination, date, budgetCurrency }) => {
  const [activeTab, setActiveTab] = useState<typeof tabs[number]>('flight');
  const [data, setData] = useState<TransportPricesResponse | null>(null);
  const [rate, setRate] = useState(1);

  useEffect(() => {
    const fetchPrices = async () => {
      const response = await travelApi.getTransportPrices({
        origin: origin || 'your city',
        destination,
        date,
        modes: ['flight', 'train', 'bus'],
      });
      setData(response);
    };

    if (destination) {
      fetchPrices();
    }
  }, [origin, destination, date]);

  useEffect(() => {
    const fetchRate = async () => {
      if (!data) return;
      const first = Object.values(data).find(Boolean);
      if (!first) return;
      if (first.currency === budgetCurrency) {
        setRate(1);
        return;
      }
      const response = await travelApi.convertCurrency(first.currency, budgetCurrency, 1);
      setRate(response.rate || 1);
    };

    fetchRate();
  }, [data, budgetCurrency]);

  const cheapest = useMemo<TransportPrice | null>(() => {
    if (!data) return null;
    const options = Object.values(data).filter(Boolean) as TransportPrice[];
    if (options.length === 0) return null;
    return options.reduce((prev, current) => (current.min_price < prev.min_price ? current : prev), options[0]);
  }, [data]);

  const active = data?.[activeTab];

  return (
    <div className="bg-zinc-900/60 border border-zinc-800 rounded-2xl p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-zinc-50">Transport Prices</h3>
          <p className="text-xs text-zinc-400">Best current ranges</p>
        </div>
        {cheapest && (
          <span className="text-xs bg-emerald-500/20 text-emerald-300 px-3 py-1 rounded-full">
            Best value: {cheapest.mode}
          </span>
        )}
      </div>

      <div className="flex gap-2">
        {tabs.map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-3 py-1 rounded-full text-xs font-semibold ${
              activeTab === tab ? 'bg-orange-500 text-white' : 'bg-zinc-800 text-zinc-400'
            }`}
          >
            {tab.toUpperCase()}
          </button>
        ))}
      </div>

      {active && active.max_price > 0 ? (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
          <div className="flex items-center justify-between text-zinc-300 text-sm">
            <span>Min: {budgetCurrency} {(active.min_price * rate).toFixed(0)}</span>
            <span>Max: {budgetCurrency} {(active.max_price * rate).toFixed(0)}</span>
          </div>
          <div className="w-full h-2 bg-zinc-800 rounded-full">
            <div className="h-2 bg-orange-500 rounded-full" style={{ width: '60%' }} />
          </div>
          <div className="text-xs text-zinc-400 flex items-center justify-between">
            <span>via {active.source}</span>
            {active.booking_url && (
              <a href={active.booking_url} target="_blank" rel="noreferrer" className="text-orange-400">
                View source
              </a>
            )}
          </div>
        </motion.div>
      ) : (
        <div className="text-sm text-zinc-500">Price estimate unavailable for this mode.</div>
      )}
    </div>
  );
};
