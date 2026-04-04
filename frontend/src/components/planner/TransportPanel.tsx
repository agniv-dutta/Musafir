import React, { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import { MapPin, Plane, Train, Bus, ArrowRight, Clock3 } from 'lucide-react';
import { travelApi } from '../../api/travel';
import { FlightOffer, TransportOverviewResponse } from '../../types';

interface TransportPanelProps {
  origin: string;
  destination: string;
  date: string;
  currency: string;
}

type TabId = 'flight' | 'train' | 'bus';

const tabs: Array<{ id: TabId; label: string; icon: React.ReactNode }> = [
  { id: 'flight', label: 'Flight', icon: <Plane size={14} /> },
  { id: 'train', label: 'Train', icon: <Train size={14} /> },
  { id: 'bus', label: 'Bus', icon: <Bus size={14} /> },
];

const initials = (airline: string) =>
  airline
    .split(' ')
    .map(part => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();

const stopBadgeClass = (stops: number) => {
  if (stops === 0) return 'bg-emerald-500/20 text-emerald-300';
  if (stops === 1) return 'bg-amber-500/20 text-amber-300';
  return 'bg-red-500/20 text-red-300';
};

const stopLabel = (stops: number) => {
  if (stops === 0) return 'Direct';
  if (stops === 1) return '1 stop';
  return `${stops} stops`;
};

export const TransportPanel: React.FC<TransportPanelProps> = ({ origin, destination, date, currency }) => {
  const [activeTab, setActiveTab] = useState<TabId>('flight');
  const [data, setData] = useState<TransportOverviewResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTransport = async () => {
      if (!destination) return;

      setLoading(true);
      setError(null);
      try {
        const response = await travelApi.getTransportOverview({
          from: origin || 'N/A',
          to: destination,
          date,
          currency,
        });
        setData(response);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch transport options');
      } finally {
        setLoading(false);
      }
    };

    fetchTransport();
  }, [origin, destination, date, currency]);

  const cheapestFlight = useMemo(() => {
    if (!data?.flights?.length) return null;
    return data.flights.reduce((best, offer) => (offer.price < best.price ? offer : best), data.flights[0]);
  }, [data]);

  const focusOriginField = () => {
    const element = document.getElementById('origin-city-input') as HTMLInputElement | null;
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      window.setTimeout(() => element.focus(), 300);
    }
  };

  const renderFlightTab = () => {
    if (!origin.trim()) {
      return (
        <div className="rounded-xl border border-zinc-700 bg-zinc-900/70 p-5 text-zinc-300">
          <div className="flex items-center gap-2 text-zinc-200 font-medium mb-2">
            <MapPin size={16} />
            Add an origin city to see flight prices.
          </div>
          <button
            type="button"
            onClick={focusOriginField}
            className="mt-2 rounded-lg bg-violet-600 px-3 py-2 text-sm font-medium text-white hover:bg-violet-500"
          >
            Jump to Origin Field
          </button>
        </div>
      );
    }

    if (loading) {
      return <div className="text-sm text-zinc-400">Loading transport options...</div>;
    }

    if (error) {
      return <div className="text-sm text-red-400">{error}</div>;
    }

    if (!data?.flights?.length) {
      const routeLabel = data?.routeResolved?.originIata && data?.routeResolved?.destinationIata
        ? `${data.routeResolved.originIata} -> ${data.routeResolved.destinationIata}`
        : `${origin} -> ${destination}`;
      return (
        <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-4 text-sm text-amber-100">
          <p className="font-medium">Live flight fares are unavailable for this route/date.</p>
          <p className="mt-1 text-amber-200/90">Resolved route: {routeLabel}</p>
          <p className="mt-1 text-amber-200/90">
            {data?.flightMessage || 'The free provider did not return priced results for the selected day.'}
          </p>
          <p className="mt-2 text-amber-200/80">Try adjusting the date by 1-3 days or selecting a nearby major city airport.</p>
        </div>
      );
    }

    return (
      <div className="space-y-3">
        {data.flights.map((offer: FlightOffer) => {
          const best = cheapestFlight && offer.price === cheapestFlight.price;
          const offsetLabel = offer.arrivalDayOffset > 0 ? ` (+${offer.arrivalDayOffset})` : '';

          return (
            <motion.div
              key={`${offer.airlineCode}-${offer.departureTime}-${offer.arrivalTime}-${offer.price}`}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className="rounded-xl border border-zinc-700 bg-zinc-900/70 p-4"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-violet-600/25 text-violet-200 text-xs font-bold">
                    {initials(offer.airline)}
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-zinc-100">{offer.airline}</p>
                    <p className="mt-1 flex items-center gap-2 text-sm text-zinc-300">
                      <span>{offer.departureTime}</span>
                      <ArrowRight size={13} className="text-zinc-500" />
                      <span>{offer.arrivalTime}{offsetLabel}</span>
                    </p>
                  </div>
                </div>

                <div className="text-right">
                  {best && (
                    <span className="mb-1 inline-block rounded-full bg-violet-500/20 px-2 py-0.5 text-[11px] font-medium text-violet-300">
                      Best value
                    </span>
                  )}
                  <p className="text-xl font-bold text-zinc-50">{offer.currency} {offer.price.toLocaleString()}</p>
                </div>
              </div>

              <div className="mt-3 flex items-center gap-2 text-xs">
                <span className="rounded-full bg-zinc-800 px-2 py-1 text-zinc-300 inline-flex items-center gap-1">
                  <Clock3 size={12} /> {offer.duration}
                </span>
                <span className={`rounded-full px-2 py-1 ${stopBadgeClass(offer.stops)}`}>
                  {stopLabel(offer.stops)}
                </span>
              </div>

              {(offer.sourceTitle || offer.sourceUrl) && (
                <div className="mt-3 rounded-lg border border-zinc-700/70 bg-zinc-950/40 px-3 py-2 text-xs text-zinc-400">
                  <div className="flex items-center justify-between gap-3">
                    <span className="truncate">
                      Web result: {offer.sourceTitle || 'Flight search source'}
                    </span>
                    {offer.sourceUrl && (
                      <a
                        href={offer.sourceUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="shrink-0 text-violet-300 hover:text-violet-200"
                      >
                        Open source
                      </a>
                    )}
                  </div>
                  {offer.sourceSnippet && (
                    <p className="mt-1 line-clamp-2 text-zinc-500">
                      {offer.sourceSnippet}
                    </p>
                  )}
                </div>
              )}
            </motion.div>
          );
        })}
      </div>
    );
  };

  const renderGroundTab = (mode: 'train' | 'bus') => {
    if (loading) return <div className="text-sm text-zinc-400">Loading transport options...</div>;
    if (error) return <div className="text-sm text-red-400">{error}</div>;

    const section = mode === 'train' ? data?.trains : data?.buses;
    if (!section) return <div className="text-sm text-zinc-400">No data available.</div>;

    if (!section.applicable) {
      return (
        <div className="text-sm text-zinc-400">
          {section.message || `${mode === 'train' ? 'Train' : 'Bus'} travel not applicable for international routes.`}
        </div>
      );
    }

    const option = section.options[0];
    if (!option) {
      return <div className="text-sm text-zinc-400">No {mode} options available.</div>;
    }

    return (
      <div className="rounded-xl border border-zinc-700 bg-zinc-900/70 p-4">
        <div className="flex items-center justify-between">
          <p className="font-semibold text-zinc-100">{mode === 'train' ? 'Train' : 'Bus'} option</p>
          <span className="rounded-full bg-amber-500/20 px-2 py-0.5 text-[11px] text-amber-300">Estimated</span>
        </div>
        <div className="mt-3 space-y-2 text-sm text-zinc-300">
          <p>Journey time: {option.journeyTime}</p>
          <p>Price range: {option.priceRange}</p>
          <p>Frequency: {option.frequency}</p>
        </div>
      </div>
    );
  };

  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-900/60 p-6 space-y-4">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h3 className="text-lg font-bold text-zinc-50">Transport Prices</h3>
          <p className="text-xs text-zinc-400">Pre-fetched across flight, train, and bus</p>
        </div>
        {data?.bestValue && (
          <span className="rounded-full bg-emerald-500/20 px-3 py-1 text-xs font-medium text-emerald-300">
            Best value: {data.bestValue} ({data.bestValueReason})
          </span>
        )}
      </div>

      <div className="flex gap-2">
        {tabs.map(tab => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            className={`inline-flex items-center gap-1 rounded-full px-3 py-1.5 text-xs font-semibold ${
              activeTab === tab.id ? 'bg-violet-600 text-white' : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
            }`}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'flight' && renderFlightTab()}
      {activeTab === 'train' && renderGroundTab('train')}
      {activeTab === 'bus' && renderGroundTab('bus')}
    </div>
  );
};
