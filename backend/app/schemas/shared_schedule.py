from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ShareScheduleRequest(BaseModel):
    recipient_email: str
    schedule_data: dict  # El objeto ScheduleResponse serializado
    message: Optional[str] = None


class SharedScheduleResponse(BaseModel):
    id: int
    sender_name: str
    sender_email: str
    schedule_data: dict
    message: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
