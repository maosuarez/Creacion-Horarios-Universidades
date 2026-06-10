from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class SharedSchedule(Base):
    __tablename__ = "shared_schedules"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    # Horario completo serializado como JSON
    schedule_data = Column(JSON, nullable=False)
    message = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sender = relationship("Profile", foreign_keys=[sender_id])
    recipient = relationship("Profile", foreign_keys=[recipient_id])
