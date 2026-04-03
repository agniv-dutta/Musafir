import React, { useMemo, useState } from 'react';
import { Calendar, dateFnsLocalizer, Event as CalendarEvent } from 'react-big-calendar';
import { format, parse, startOfWeek, getDay } from 'date-fns';
import { enUS } from 'date-fns/locale';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import { travelApi, API_BASE_URL } from '../../api/travel';
import { motion } from 'framer-motion';

const locales = {
  'en-US': enUS,
};

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek,
  getDay,
  locales,
});

interface TripCalendarProps {
  destination: string;
  duration: number;
  startDate: string;
  finalAnswer: string;
}

interface ParsedEvent {
  day: number;
  title: string;
  time: string;
  description: string;
}

const parseEvents = (text: string): ParsedEvent[] => {
  const dayPattern = /Day\s+(\d+):([\s\S]*?)(?=Day\s+\d+:|$)/gi;
  const events: ParsedEvent[] = [];
  let match;

  while ((match = dayPattern.exec(text)) !== null) {
    const day = parseInt(match[1], 10);
    const content = match[2];
    const lines = content.split('\n').filter(line => line.trim());

    lines.forEach(line => {
      const clean = line.replace(/^[-•*]\s*/, '').trim();
      if (!clean) return;
      events.push({
        day,
        title: clean.split('.')[0] || clean,
        time: '09:00',
        description: clean,
      });
    });
  }

  return events.slice(0, 20);
};

export const TripCalendar: React.FC<TripCalendarProps> = ({ destination, duration, startDate, finalAnswer }) => {
  const [selectedDay, setSelectedDay] = useState<number | null>(null);
  const [downloading, setDownloading] = useState(false);

  const start = useMemo(() => new Date(startDate), [startDate]);
  const end = useMemo(() => {
    const date = new Date(startDate);
    date.setDate(date.getDate() + Math.max(duration - 1, 0));
    return date;
  }, [startDate, duration]);

  const parsedEvents = useMemo(() => parseEvents(finalAnswer), [finalAnswer]);

  const calendarEvents: CalendarEvent[] = useMemo(() => {
    const tripBlock = {
      title: `Trip to ${destination}`,
      start,
      end: new Date(end.getTime() + 24 * 60 * 60 * 1000),
      allDay: true,
    } as CalendarEvent;

    const dayEvents = parsedEvents.map(event => {
      const eventDate = new Date(start);
      eventDate.setDate(eventDate.getDate() + event.day - 1);
      return {
        title: event.title,
        start: eventDate,
        end: eventDate,
        allDay: true,
      } as CalendarEvent;
    });

    return [tripBlock, ...dayEvents];
  }, [destination, start, end, parsedEvents]);

  const eventsByDay = useMemo(() => {
    return parsedEvents.reduce<Record<number, ParsedEvent[]>>((acc, event) => {
      if (!acc[event.day]) acc[event.day] = [];
      acc[event.day].push(event);
      return acc;
    }, {});
  }, [parsedEvents]);

  const handleExport = async () => {
    try {
      setDownloading(true);
      const payload = {
        destination,
        start_date: start.toISOString().slice(0, 10),
        end_date: end.toISOString().slice(0, 10),
        events: parsedEvents.map(event => ({
          day: event.day,
          title: event.title,
          time: event.time,
          description: event.description,
        })),
      };
      const response = await travelApi.exportCalendar(payload);
      window.open(`${API_BASE_URL}${response.download_url}`, '_blank');
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="bg-zinc-900/60 border border-zinc-800 rounded-2xl p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-bold text-zinc-50">Trip Calendar</h3>
          <p className="text-sm text-zinc-400">Visualize your trip schedule</p>
        </div>
        <button
          onClick={handleExport}
          disabled={downloading}
          className="px-4 py-2 bg-orange-500 text-white rounded-xl text-sm font-semibold hover:bg-orange-400 transition"
        >
          {downloading ? 'Generating...' : '📅 Add to Calendar'}
        </button>
      </div>

      <Calendar
        localizer={localizer}
        events={calendarEvents}
        startAccessor="start"
        endAccessor="end"
        style={{ height: 360 }}
        views={['month']}
        onSelectEvent={(event: CalendarEvent) => {
          if (event.title.startsWith('Trip')) {
            setSelectedDay(null);
          } else {
            const dayIndex = parsedEvents.find(e => e.title === event.title)?.day || null;
            setSelectedDay(dayIndex);
          }
        }}
        eventPropGetter={(event: CalendarEvent) => {
          if (event.title.startsWith('Trip')) {
            return { className: 'bg-orange-500 text-white border-0' };
          }
          return { className: 'bg-violet-500 text-white border-0' };
        }}
      />

      {selectedDay && eventsByDay[selectedDay] && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-zinc-800/60 border border-zinc-700 rounded-xl p-4"
        >
          <h4 className="text-sm font-semibold text-zinc-200 mb-3">Day {selectedDay} Itinerary</h4>
          <div className="space-y-2">
            {eventsByDay[selectedDay].map((event, index) => (
              <div key={index} className="text-sm text-zinc-300">
                <span className="text-orange-400 font-semibold">• </span>
                {event.description}
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
};
