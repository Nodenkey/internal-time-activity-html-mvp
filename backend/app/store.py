from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional
import uuid


TimeEntryDict = Dict[str, Any]


_store: Dict[str, TimeEntryDict] = {}


def _seed_data() -> None:
    global _store
    if _store:
        return

    examples = [
        {
            "id": str(uuid.uuid4()),
            "date": date(2026, 4, 15).isoformat(),
            "person_name": "Alice Johnson",
            "team": "Engineering",
            "activity": "Implementing new feature X",
            "start_time": "09:00",
            "end_time": "11:00",
            "duration_minutes": 120,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": None,
        },
        {
            "id": str(uuid.uuid4()),
            "date": date(2026, 4, 15).isoformat(),
            "person_name": "Bob Smith",
            "team": "HR",
            "activity": "Conducting interviews",
            "start_time": "10:00",
            "end_time": "12:30",
            "duration_minutes": 150,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": None,
        },
        {
            "id": str(uuid.uuid4()),
            "date": date(2026, 4, 16).isoformat(),
            "person_name": "Carol Lee",
            "team": "Finance",
            "activity": "Monthly budget review",
            "start_time": "13:00",
            "end_time": "15:00",
            "duration_minutes": 120,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": None,
        },
    ]

    _store = {entry["id"]: entry for entry in examples}


_seed_data()


def list_entries(filters: Optional[Dict[str, Any]] = None) -> List[TimeEntryDict]:
    if filters is None:
        filters = {}

    date_from: Optional[date] = filters.get("date_from")
    date_to: Optional[date] = filters.get("date_to")
    person_name: Optional[str] = filters.get("person_name")
    team: Optional[str] = filters.get("team")

    results = list(_store.values())

    if date_from is not None:
        results = [e for e in results if date.fromisoformat(e["date"]) >= date_from]

    if date_to is not None:
        results = [e for e in results if date.fromisoformat(e["date"]) <= date_to]

    if person_name:
        needle = person_name.lower()
        results = [e for e in results if needle in e["person_name"].lower()]

    if team:
        team_lower = team.lower()
        results = [e for e in results if e["team"].lower() == team_lower]

    return results


def get_entry(entry_id: str) -> Optional[TimeEntryDict]:
    return _store.get(entry_id)


def create_entry(data: Dict[str, Any]) -> TimeEntryDict:
    entry_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    entry: TimeEntryDict = {
        "id": entry_id,
        "created_at": now,
        "updated_at": None,
        **data,
    }

    _store[entry_id] = entry
    return entry


def update_entry(entry_id: str, data: Dict[str, Any]) -> Optional[TimeEntryDict]:
    existing = _store.get(entry_id)
    if not existing:
        return None

    updated = {**existing, **data, "id": entry_id, "updated_at": datetime.utcnow().isoformat()}
    _store[entry_id] = updated
    return updated


def delete_entry(entry_id: str) -> bool:
    if entry_id not in _store:
        return False
    del _store[entry_id]
    return True
