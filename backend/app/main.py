from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import date

from app import store
from app.models import TimeEntryCreate, TimeEntryOut, TimeEntryUpdate

app = FastAPI(title="Internal Time & Activity Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/time-entries", response_model=TimeEntryOut, status_code=201)
def create_time_entry(entry: TimeEntryCreate):
    created = store.create_entry(entry.model_dump())
    return created


@app.get("/api/time-entries", response_model=List[TimeEntryOut])
def list_time_entries(
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    person_name: Optional[str] = Query(default=None),
    team: Optional[str] = Query(default=None),
):
    filters = {
        "date_from": date_from,
        "date_to": date_to,
        "person_name": person_name,
        "team": team,
    }
    entries = store.list_entries(filters)
    return entries


@app.get("/api/time-entries/{entry_id}", response_model=TimeEntryOut)
def get_time_entry(entry_id: str):
    entry = store.get_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": f"Time entry with id {entry_id} not found", "detail": None})
    return entry


@app.put("/api/time-entries/{entry_id}", response_model=TimeEntryOut)
def update_time_entry(entry_id: str, update: TimeEntryCreate):
    updated = store.update_entry(entry_id, update.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": f"Time entry with id {entry_id} not found", "detail": None})
    return updated


@app.patch("/api/time-entries/{entry_id}", response_model=TimeEntryOut)
def patch_time_entry(entry_id: str, update: TimeEntryUpdate):
    updated = store.update_entry(entry_id, update.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": f"Time entry with id {entry_id} not found", "detail": None})
    return updated


@app.delete("/api/time-entries/{entry_id}", status_code=204)
def delete_time_entry(entry_id: str):
    deleted = store.delete_entry(entry_id)
    if not deleted:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": f"Time entry with id {entry_id} not found", "detail": None})
    return None
