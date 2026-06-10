from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class SavedSchedule(Base):
    __tablename__ = "saved_schedules"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    name = Column(String(150), nullable=False)
    # Guarda el objeto ScheduleResponse completo serializado como JSON
    schedule_data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    profile = relationship("Profile", back_populates="saved_schedules")
