from pydantic import BaseModel
from typing import List
from app.schemas.course import Course

class TeacherBase(BaseModel):
    full_name: str

class TeacherCreate(TeacherBase):
    pass

class Teacher(TeacherBase):
    id: int
    courses: List[Course]

    class ConfigDict:
        orm_mode = True