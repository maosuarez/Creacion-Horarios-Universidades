from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, NamedTuple, Annotated

from app.schemas.course_schedule import CourseScheduleCreate

# Objeto unico para las actualizaciones
SUBJECT_MAX = 100
TEACHER_MAX = 100
SCHEDULES_MAX = 10


# Objeto base de los cursos
class CourseBase(BaseModel):
    subject: Annotated[str, Field(min_length=1, max_length=SUBJECT_MAX)]
    code: Annotated[int, Field(strict=True, gt=0)]
    # Si quieres limitar el máximo del código (por ejemplo 6 dígitos), añade:
    # code: Annotated[int, Field(strict=True, gt=0, le=999999)]

# Este es el objeto que recibe la solicitud de crear cursos
class CourseCreate(CourseBase):
    teacher_name: Annotated[str, Field(min_length=1, max_length=TEACHER_MAX)]
    schedules: Annotated[
        List[CourseScheduleCreate],
        Field(min_length=1, max_length=SCHEDULES_MAX)
    ]

class CourseUpdate(BaseModel):
    subject: Optional[Annotated[str, Field(min_length=1, max_length=SUBJECT_MAX)]] = None
    code: Optional[Annotated[int, Field(strict=True, gt=0)]] = None
    teacher_name: Optional[Annotated[str, Field(min_length=1, max_length=TEACHER_MAX)]] = None
    schedules: Optional[
        Annotated[
            List[CourseScheduleCreate],
            Field(min_length=1, max_length=SCHEDULES_MAX)
        ]
    ] = None

    @model_validator(mode="after")
    def validate_any_field_present(self):
        if (
            self.subject is None and
            self.code is None and
            self.teacher_name is None and
            self.schedules is None
        ):
            raise ValueError("Debe enviar al menos un campo para actualizar.")

        return self


class CourseRowSubject(NamedTuple):
    code: int
    teacher_id: int
    teacher_name: str

class FreeTime(BaseModel):
    day: str
    hour: int

class FilteredCourses(BaseModel):
    subject: List[str]
    teacher_name: Optional[List[str]]
    code: Optional[List[int]]
    free_time: Optional[List[FreeTime]]

class ConfigDict(CourseBase):
    id: int
    teacher_id: int
    
    class ConfigDict:
        orm_mode = True

class SubjectOption(BaseModel):
    """Opción de materia para el selector"""
    subject: str
    count: int  # Cantidad de cursos disponibles

class CodeOption(BaseModel):
    """Opción de código filtrada por materia"""
    code: int
    course_id: int

class TeacherOption(BaseModel):
    """Opción de profesor filtrado por materia"""
    id: int
    full_name: str

