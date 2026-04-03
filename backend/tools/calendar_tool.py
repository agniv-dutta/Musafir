import json
import os
import tempfile
from datetime import datetime, date, time, timedelta
from uuid import uuid4
from typing import List, Dict, Any

from icalendar import Calendar, Event
from langchain.tools import tool


def _parse_date(value: str) -> date:
    return datetime.fromisoformat(value).date()


def _parse_time(value: str) -> time:
    if not value:
        return time(9, 0)
    parts = value.split(":")
    hour = int(parts[0])
    minute = int(parts[1]) if len(parts) > 1 else 0
    return time(hour, minute)


def _event_uid() -> str:
    return f"{uuid4()}@travelplanner"


def _normalize_events(events: Any) -> List[Dict]:
    if events is None:
        return []
    if isinstance(events, str):
        try:
            events = json.loads(events)
        except Exception:
            return []
    if not isinstance(events, list):
        return []
    return [event for event in events if isinstance(event, dict)]


@tool
def generate_trip_ics(destination: str, start_date: str, end_date: str, events: List[Dict[str, str]]) -> str:
    """
    Generates an .ics file for a trip.
    Input schema: { destination, start_date, end_date, events: [{day, title, time, description}] }
    day may be a day number ("1") or ISO date ("2026-04-03").
    Returns: { ics_path, event_count }
    """
    try:
        start = _parse_date(start_date)
        end = _parse_date(end_date)

        calendar = Calendar()
        calendar.add("prodid", "-//Wandr Travel Planner//")
        calendar.add("version", "2.0")

        # Trip block
        trip_event = Event()
        trip_event.add("uid", _event_uid())
        trip_event.add("summary", f"Trip to {destination}")
        trip_event.add("location", destination)
        trip_event.add("dtstart", start)
        trip_event.add("dtend", end + timedelta(days=1))
        trip_event.add("transp", "TRANSPARENT")
        calendar.add_component(trip_event)

        event_count = 1

        for item in _normalize_events(events):
            day_value = item.get("day", 1)
            if isinstance(day_value, str) and "-" in day_value:
                event_date = datetime.fromisoformat(day_value).date()
            else:
                day_offset = int(day_value) - 1
                event_date = start + timedelta(days=day_offset)

            event_time = _parse_time(item.get("time", ""))
            event_dt = datetime.combine(event_date, event_time)

            event = Event()
            event.add("uid", _event_uid())
            event.add("summary", item.get("title", "Activity"))
            event.add("description", item.get("description", ""))
            event.add("location", destination)
            event.add("dtstart", event_dt)
            event.add("dtend", event_dt + timedelta(hours=1))
            calendar.add_component(event)
            event_count += 1

        safe_destination = "".join(c for c in destination if c.isalnum() or c in ("-", "_")).strip()
        filename = f"trip_{safe_destination or 'destination'}_{start.isoformat()}.ics"
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)

        with open(file_path, "wb") as file_handle:
            file_handle.write(calendar.to_ical())

        return json.dumps({"ics_path": file_path, "event_count": event_count})

    except Exception as exc:
        return json.dumps({"error": str(exc)})
