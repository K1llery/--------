from pydantic import BaseModel, Field


class TimeSlotEntry(BaseModel):
    destination_id: str
    destination_name: str
    notes: str = ""


class TimeSlots(BaseModel):
    morning: TimeSlotEntry | None = None
    afternoon: TimeSlotEntry | None = None
    evening: TimeSlotEntry | None = None


class DayPlan(BaseModel):
    date: str
    city: str = ""
    time_slots: TimeSlots


class PlanCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    days: list[DayPlan] = Field(..., min_length=1)


class PlanUpdateRequest(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=100)
    days: list[DayPlan] | None = None


class PlanOut(BaseModel):
    id: int
    user_id: int
    title: str
    days: list[DayPlan]
    created_at: str
    updated_at: str


class PlanListResponse(BaseModel):
    items: list[PlanOut]
