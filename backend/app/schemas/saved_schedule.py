from datetime import datetime
from pydantic import BaseModel, ConfigDict


class SaveScheduleRequest(BaseModel):
    name: str
    schedule_data: dict  # El objeto ScheduleResponse serializado


class SavedScheduleResponse(BaseModel):
    id: int
    name: str
    schedule_data: dict
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
