from typing import List, Optional, Dict
from pydantic import BaseModel, Field

# Modelos Pydantic para request/response
class SubjectPreference(BaseModel):
    """
    Preferencias para filtrar cursos de una materia.
    
    - Si ambos filtros están presentes: UNION (OR) - cursos que cumplan CUALQUIERA
    - Si solo uno está presente: filtra solo por ese criterio
    - Si ambos están vacíos: todos los cursos de la materia
    
    Ejemplos:
    - profesores=["Dr. Juan"], codes=[] -> Solo cursos del Dr. Juan
    - profesores=[], codes=[1001, 1002] -> Solo cursos 1001 o 1002
    - profesores=["Dr. Juan"], codes=[1001] -> Cursos del Dr. Juan O código 1001
    """
    profesores: Optional[List[str]] = Field(default_factory=list)
    codes: Optional[List[int]] = Field(default_factory=list)

class FilteredCourses(BaseModel):
    preferencias: Dict[str, SubjectPreference]
    freetime: Optional[Dict[str, List[int]]] = Field(default_factory=dict)
    
    class ConfigDict:
        json_schema_extra = {
            "example": {
                "preferencias": {
                    "Cálculo I": {
                        "profesores": [],
                        "codes": []
                    },
                    "Física I": {
                        "profesores": ["Dr. Juan Pérez"],
                        "codes": []
                    }
                },
                "freetime": {
                    "monday": [10, 11, 12],
                    "tuesday": [13, 14, 15]
                }
            }
        }

class CourseScheduleInfo(BaseModel):
    day: str
    start_time: str
    end_time: str
    location: Optional[str] = None

class CourseInfo(BaseModel):
    subject: str
    code: int
    teacher_name: str
    schedules: List[CourseScheduleInfo]

class ScheduleResponse(BaseModel):
    schedule_number: int
    courses: List[CourseInfo]
    schedule_matrix: List[List[str]]  # Representación visual del horario
    hour_labels: List[str]  # Etiquetas de horas (7am-6pm)
    day_labels: List[str]  # Etiquetas de días
