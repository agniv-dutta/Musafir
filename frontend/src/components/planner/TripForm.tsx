import React, { useState } from 'react';
import { TripFormData } from '../../types';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Spinner } from '../ui/Spinner';
import { MapPin } from 'lucide-react';
import { motion } from 'framer-motion';

interface TripFormProps {
  onSubmit: (data: TripFormData) => Promise<void>;
  isLoading: boolean;
  initialData?: Partial<TripFormData>;
}

const budgetLevels: Array<'Budget' | 'Moderate' | 'Luxury'> = ['Budget', 'Moderate', 'Luxury'];

const travelStyles = [
  { emoji: '🏛', label: 'Cultural' },
  { emoji: '🏖', label: 'Beach' },
  { emoji: '🧗', label: 'Adventure' },
  { emoji: '🍜', label: 'Food & Nightlife' },
  { emoji: '🛍', label: 'Shopping' },
  { emoji: '⚖', label: 'Balanced' },
];

const currencies = ['INR', 'USD', 'EUR', 'GBP', 'JPY', 'AUD', 'THB', 'SGD'];

export const TripForm: React.FC<TripFormProps> = ({ onSubmit, isLoading, initialData }) => {
  const [formData, setFormData] = useState<TripFormData>({
    destination: initialData?.destination || '',
    origin: initialData?.origin || '',
    startDate: initialData?.startDate || new Date().toISOString().slice(0, 10),
    duration: initialData?.duration || 7,
    budgetAmount: initialData?.budgetAmount || 150000,
    budgetCurrency: initialData?.budgetCurrency || 'INR',
    budgetLevel: initialData?.budgetLevel || 'Moderate',
    travelStyle: initialData?.travelStyle || 'Balanced',
    constraints: initialData?.constraints || '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.destination.trim()) {
      await onSubmit(formData);
    }
  };

  const setBudgetLevel = (level: 'Budget' | 'Moderate' | 'Luxury') => {
    setFormData(prev => ({ ...prev, budgetLevel: level }));
  };

  const setTravelStyle = (style: string) => {
    setFormData(prev => ({ ...prev, travelStyle: style }));
  };

  return (
    <Card className="sticky top-24 h-fit">
      <motion.form
        onSubmit={handleSubmit}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="space-y-6"
      >
        <div>
          <h3 className="text-2xl font-bold text-zinc-50 flex items-center gap-2 mb-6">
            <MapPin size={24} />
            Plan your trip
          </h3>
        </div>

        {/* Destination Input */}
        <div>
          <label className="block text-sm font-medium text-zinc-300 mb-2">
            Destination
          </label>
          <div className="relative">
            <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-400" size={20} />
            <input
              type="text"
              placeholder="Where do you want to go?"
              value={formData.destination}
              onChange={e => setFormData(prev => ({ ...prev, destination: e.target.value }))}
              className="w-full bg-zinc-800 border border-zinc-700 rounded-xl px-4 py-3 pl-12 text-zinc-50 placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-violet-500 transition-all duration-300"
            />
          </div>
        </div>

        {/* Origin Input */}
        <div>
          <label className="block text-sm font-medium text-zinc-300 mb-2">
            Origin City
          </label>
          <input
            type="text"
            placeholder="Where are you starting from?"
            value={formData.origin}
            onChange={e => setFormData(prev => ({ ...prev, origin: e.target.value }))}
            className="w-full bg-zinc-800 border border-zinc-700 rounded-xl px-4 py-3 text-zinc-50 placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-violet-500 transition-all duration-300"
          />
        </div>

        {/* Duration Slider */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <label className="text-sm font-medium text-zinc-300">Duration</label>
            <span className="text-sm bg-violet-600 text-white px-3 py-1 rounded-full font-medium">
              {formData.duration} days
            </span>
          </div>
          <input
            type="range"
            min="1"
            max="30"
            value={formData.duration}
            onChange={e => setFormData(prev => ({ ...prev, duration: parseInt(e.target.value) }))}
            className="w-full h-2 bg-zinc-700 rounded-lg appearance-none cursor-pointer accent-violet-600"
          />
          <div className="flex justify-between text-xs text-zinc-500 mt-2">
            <span>1 day</span>
            <span>7 days</span>
            <span>14 days</span>
            <span>30 days</span>
          </div>
        </div>

        {/* Start Date */}
        <div>
          <label className="block text-sm font-medium text-zinc-300 mb-2">
            Start Date
          </label>
          <input
            type="date"
            value={formData.startDate}
            onChange={e => setFormData(prev => ({ ...prev, startDate: e.target.value }))}
            className="w-full bg-zinc-800 border border-zinc-700 rounded-xl px-4 py-3 text-zinc-50 focus:outline-none focus:ring-2 focus:ring-violet-500 transition-all duration-300"
          />
        </div>

        {/* Budget Section */}
        <div>
          <label className="block text-sm font-medium text-zinc-300 mb-2">Budget</label>
          <div className="flex gap-2 mb-3">
            <input
              type="number"
              placeholder="Amount"
              value={formData.budgetAmount}
              onChange={e => setFormData(prev => ({ ...prev, budgetAmount: parseFloat(e.target.value) }))}
              className="flex-1 bg-zinc-800 border border-zinc-700 rounded-xl px-4 py-3 text-zinc-50 placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-violet-500"
            />
            <select
              value={formData.budgetCurrency}
              onChange={e => setFormData(prev => ({ ...prev, budgetCurrency: e.target.value }))}
              className="bg-zinc-800 border border-zinc-700 rounded-xl px-4 py-3 text-zinc-50 focus:outline-none focus:ring-2 focus:ring-violet-500 cursor-pointer appearance-none"
            >
              {currencies.map(curr => (
                <option key={curr} value={curr}>{curr}</option>
              ))}
            </select>
          </div>

          {/* Budget Level Toggle */}
          <div className="flex gap-2">
            {budgetLevels.map(level => (
              <button
                key={level}
                type="button"
                onClick={() => setBudgetLevel(level)}
                className={`flex-1 py-2 px-3 rounded-xl font-medium text-sm transition-all duration-300 ${
                  formData.budgetLevel === level
                    ? 'bg-violet-600 text-white'
                    : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
                }`}
              >
                {level}
              </button>
            ))}
          </div>
        </div>

        {/* Travel Style Grid */}
        <div>
          <label className="block text-sm font-medium text-zinc-300 mb-3">Travel Style</label>
          <div className="grid grid-cols-2 gap-2">
            {travelStyles.map(style => (
              <button
                key={style.label}
                type="button"
                onClick={() => setTravelStyle(style.label)}
                className={`border rounded-xl p-3 text-center transition-all duration-300 ${
                  formData.travelStyle === style.label
                    ? 'border-violet-500 bg-violet-500/10 text-violet-300'
                    : 'border-zinc-700 bg-zinc-800/50 text-zinc-400 hover:border-zinc-600'
                }`}
              >
                <div className="text-2xl mb-2">{style.emoji}</div>
                <div className="text-sm font-medium">{style.label}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Constraints Textarea */}
        <div>
          <label className="block text-sm font-medium text-zinc-300 mb-2">Special Requirements</label>
          <textarea
            placeholder="Any special needs? (vegetarian, kids, wheelchair, etc.)"
            value={formData.constraints}
            onChange={e => setFormData(prev => ({ ...prev, constraints: e.target.value }))}
            rows={3}
            className="w-full bg-zinc-800 border border-zinc-700 rounded-xl px-4 py-3 text-zinc-50 placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-violet-500 resize-none transition-all duration-300"
          />
        </div>

        {/* Submit Button */}
        <Button
          type="submit"
          disabled={isLoading || !formData.destination.trim()}
          size="lg"
          className="w-full"
        >
          {isLoading ? (
            <>
              <Spinner size="sm" /> Planning your trip...
            </>
          ) : (
            'Plan My Trip ✈'
          )}
        </Button>
      </motion.form>
    </Card>
  );
};
