from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class TimeEntryBase(BaseModel):
    date: date = Field(..., description="Entry date (ISO date)")
    person_name: str = Field(..., min_length=1, description="Person's full name")
    team: str = Field(..., min_length=1, description="Team or department name")
    activity: str = Field(..., min_length=1, description="Description of activity")
    start_time: str = Field(..., description="Start time in HH:MM")
    end_time: str = Field(..., description="End time in HH:MM")
    duration_minutes: Optional[int] = Field(
        default=None,
        ge=1,
        description="Duration in minutes; if omitted, can be computed client-side",
    )

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        if len(v) != 5 or v[2] != ":":
            raise ValueError("time must be in HH:MM format")
        hh, mm = v.split(":", 1)
        if not (hh.isdigit() and mm.isdigit()):
            raise ValueError("time must be numeric HH:MM")
        h, m = int(hh), int(mm)
        if not (0 <= h <= 23 and 0 <= m <= 59):
            raise ValueError("time must be a valid 24h time")
        return v

    @model_validator(mode="after")
    def validate_time_order(self) -> "TimeEntryBase":
        # Only enforce if both provided and duration not explicitly set
        if self.start_time and self.end_time:
            sh, sm = map(int, self.start_time.split(":"))
            eh, em = map(int, self.end_time.split(":"))
            start_total = sh * 60 + sm
            end_total = eh * 60 + em
            if end_total <= start_total:
                raise ValueError("end_time must be after start_time")
        return self


class TimeEntryCreate(TimeEntryBase):
    pass


class TimeEntryUpdate(BaseModel):
    date: Optional[date] = None
    person_name: Optional[str] = Field(default=None, min_length=1)
    team: Optional[str] = Field(default=None, min_length=1)
    activity: Optional[str] = Field(default=None, min_length=1)
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_minutes: Optional[int] = Field(default=None, ge=1)

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if len(v) != 5 or v[2] != ":":
            raise ValueError("time must be in HH:MM format")
        hh, mm = v.split(":", 1)
        if not (hh.isdigit() and mm.isdigit()):
            raise ValueError("time must be numeric HH:MM")
        h, m = int(hh), int(mm)
        if not (0 <= h <= 23 and 0 <= m <= 59):
            raise ValueError("time must be a valid 24h time")
        return v


class TimeEntryOut(TimeEntryBase):
    id: str
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True
