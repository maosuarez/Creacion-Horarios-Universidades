from pydantic import BaseModel
from typing import Optional

# Modelo Base de los Horarios
class CourseScheduleBase(BaseModel):
    day: str # Lunes, Martes, Miercoles, Jueves, Viernes o Sabado
    start_time: str
    end_time: str
    location: Optional[str] = None

class CourseScheduleCreate(CourseScheduleBase):
    pass

class CourseSchedule(CourseScheduleBase):
    id: int
    course_id: int
    
    class ConfigDict:
        orm_mode = True