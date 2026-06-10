from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Tuple
from datetime import time
import random
import numpy as np

from app.schemas.schedule import SubjectPreference, FilteredCourses, CourseInfo, CourseScheduleInfo, ScheduleResponse

# Utilidades
def time_to_index(t: time) -> int:
    """Convierte hora a índice (0-11 representa 7am-6pm)"""
    return t.hour - 7

def index_to_hour(idx: int) -> str:
    """Convierte índice a etiqueta de hora"""
    hour = idx + 7
    return f"{hour}:00"

def day_to_index(day: str) -> int:
    """Convierte día a índice (0-5 para lunes-sabado)"""
    days = {
        "monday": 0, "lunes": 0,
        "tuesday": 1, "martes": 1,
        "wednesday": 2, "miércoles": 2, "miercoles": 2,
        "thursday": 3, "jueves": 3,
        "friday": 4, "viernes": 4,
        'saturday': 5, 'sabado': 5
    }
    return days.get(day.lower(), -1)

def index_to_day(idx: int) -> str:
    """Convierte índice a nombre de día"""
    days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
    return days[idx] if 0 <= idx < 6 else ""

# Lógica de generación de horarios
class ScheduleGenerator:
    def __init__(self, db: Session):
        self.db = db
    
    def get_filtered_courses_by_subject(
        self, 
        subject: str, 
        preference: SubjectPreference
    ) -> List[Tuple[int, Dict, str]]:
        """
        Obtiene cursos filtrados para una materia específica.
        Si se especifican profesores Y códigos, hace UNION (OR) de ambos filtros.
        Si solo se especifica uno, filtra por ese criterio.
        Retorna: [(code, schedules_dict, teacher_name), ...]
        """
        from app.models.course import Course
        from app.models.course_schedule import CourseSchedule
        from app.models.teacher import Teacher
        from sqlalchemy import or_
        
        base_query = self.db.query(Course).join(Teacher).filter(Course.subject == subject)
        
        # Si ambos filtros están presentes, hacer UNION (OR)
        if preference.profesores and preference.codes:
            query = base_query.filter(
                or_(
                    Teacher.full_name.in_(preference.profesores),
                    Course.code.in_(preference.codes)
                )
            )
        # Si solo hay filtro de profesores
        elif preference.profesores:
            query = base_query.filter(Teacher.full_name.in_(preference.profesores))
        # Si solo hay filtro de códigos
        elif preference.codes:
            query = base_query.filter(Course.code.in_(preference.codes))
        # Sin filtros, todos los cursos de la materia
        else:
            query = base_query
        
        courses = query.all()
        
        result = []
        for course in courses:
            # Crear diccionario de horarios
            schedules_dict = {}
            for schedule in course.schedules:
                day = schedule.day.lower()
                if day not in schedules_dict:
                    schedules_dict[day] = []
                schedules_dict[day].append((schedule.start_time, schedule.end_time))
            
            result.append((course.code, schedules_dict, course.teacher.full_name))
        
        return result
    
    def course_to_matrix(self, code: int, schedules_dict: Dict) -> np.ndarray:
        """Convierte un curso a matriz de horario (12x6)"""
        matrix = np.zeros((12, 6), dtype=int)
        
        for day, time_slots in schedules_dict.items():
            day_idx = day_to_index(day)
            if day_idx == -1:
                continue
            
            for start_time, end_time in time_slots:
                start_idx = time_to_index(start_time)
                end_idx = time_to_index(end_time)
                
                for hour_idx in range(start_idx, end_idx):
                    if 0 <= hour_idx < 12:
                        matrix[hour_idx][day_idx] = code
        
        return matrix
    
    def create_freetime_matrix(self, freetime: Dict[str, List[int]]) -> np.ndarray:
        """
        Crea una matriz que representa los tiempos libres requeridos.
        Los valores 1 indican que esa hora debe estar libre.
        """
        matrix = np.zeros((12, 6), dtype=int)
        
        for day, hours in freetime.items():
            day_idx = day_to_index(day)
            if day_idx == -1:
                continue
            
            for hour in hours:
                hour_idx = hour - 7  # Convertir hora absoluta a índice
                if 0 <= hour_idx < 12:
                    matrix[hour_idx][day_idx] = 1
        
        return matrix
    
    def check_freetime_constraint(
        self, 
        schedule_matrix: np.ndarray, 
        freetime_matrix: np.ndarray
    ) -> bool:
        """
        Verifica que el horario respete los tiempos libres.
        Retorna True si no hay conflictos.
        """
        # Donde freetime_matrix es 1 (debe estar libre), 
        # schedule_matrix debe ser 0 (no ocupado)
        conflicts = (freetime_matrix == 1) & (schedule_matrix != 0)
        return not np.any(conflicts)
    
    def has_conflict(self, matrix1: np.ndarray, matrix2: np.ndarray) -> bool:
        """Verifica si dos matrices de horario tienen conflicto"""
        return np.any((matrix1 != 0) & (matrix2 != 0))
    
    def generate_schedules(
        self,
        filters: FilteredCourses,
        max_results: int = 10,
    ) -> List[Tuple[np.ndarray, List]]:
        """
        Genera hasta `max_results` combinaciones válidas de horarios de forma aleatoria.

        Estrategia:
        - Mezcla los cursos de cada materia antes de combinar → variedad entre llamadas.
        - Limita las combinaciones intermedias a `max_results * 20` para evitar explosión
          combinatoria con muchas materias y cursos sin conflictos.
        - Al final devuelve exactamente `max_results` resultados (o menos si no hay suficientes).

        Retorna: [(matriz_horario, [(subject, code, teacher), ...]), ...]
        """
        # Obtener cursos para cada materia con sus preferencias específicas
        matrices_by_subject: List[List[np.ndarray]] = []
        codes_by_subject: List[List[Tuple]] = []

        for subject, preference in filters.preferencias.items():
            courses = self.get_filtered_courses_by_subject(subject, preference)

            if not courses:
                raise ValueError(
                    f"No se encontraron cursos para '{subject}' "
                    f"con las preferencias especificadas"
                )

            subject_matrices = []
            subject_codes = []

            for code, schedules_dict, teacher_name in courses:
                matrix = self.course_to_matrix(code, schedules_dict)
                subject_matrices.append(matrix)
                subject_codes.append((subject, code, teacher_name))

            # Mezclar para obtener resultados distintos en cada llamada
            combined = list(zip(subject_matrices, subject_codes))
            random.shuffle(combined)
            subject_matrices, subject_codes = zip(*combined) if combined else ([], [])

            matrices_by_subject.append(list(subject_matrices))
            codes_by_subject.append(list(subject_codes))

        # Crear matriz de tiempos libres
        freetime_matrix = self.create_freetime_matrix(filters.freetime)

        # Cota para intermedios: evita explosión con muchos cursos sin conflictos
        intermediate_cap = max_results * 20

        # Generar combinaciones usando enfoque iterativo con corte temprano
        possible_schedules = [np.zeros((12, 6), dtype=int)]
        schedule_codes: List[List] = [[]]

        for subject_idx in range(len(matrices_by_subject)):
            new_schedules: List[np.ndarray] = []
            new_codes: List[List] = []

            for schedule_idx in range(len(possible_schedules)):
                current_matrix = possible_schedules[schedule_idx]
                current_codes = schedule_codes[schedule_idx]

                for course_idx in range(len(matrices_by_subject[subject_idx])):
                    course_matrix = matrices_by_subject[subject_idx][course_idx]

                    if not self.has_conflict(current_matrix, course_matrix):
                        combined_matrix = current_matrix + course_matrix

                        if self.check_freetime_constraint(combined_matrix, freetime_matrix):
                            new_schedules.append(combined_matrix)
                            new_codes.append(
                                current_codes + [codes_by_subject[subject_idx][course_idx]]
                            )

                # Corte temprano: si ya tenemos suficientes intermedios, paramos.
                # Los intermedios ya están mezclados gracias al shuffle inicial.
                if len(new_schedules) >= intermediate_cap:
                    break

            possible_schedules = new_schedules[:intermediate_cap]
            schedule_codes = new_codes[:intermediate_cap]

            if not possible_schedules:
                break

        results = list(zip(possible_schedules, schedule_codes))

        # Devolver exactamente max_results (muestra aleatoria si hay más)
        if len(results) > max_results:
            results = random.sample(results, max_results)

        return results
    
    def format_schedule_matrix(
        self, 
        matrix: np.ndarray, 
        codes: List[Tuple[str, int, str]]
    ) -> List[List[str]]:
        """Convierte matriz numérica a matriz de texto con nombres de materias"""
        schedule_matrix = []
        
        # Crear diccionario código -> materia para búsqueda rápida
        code_to_subject = {code: subject for subject, code, _ in codes}
        
        for hour_idx in range(12):
            row = []
            for day_idx in range(6):
                code = matrix[hour_idx][day_idx]
                if code == 0:
                    row.append("")
                else:
                    subject = code_to_subject.get(code, str(code))
                    row.append(subject)
            schedule_matrix.append(row)
        
        return schedule_matrix

from fastapi import APIRouter, Query
from app.database import get_db

# Endpoint FastAPI
router = APIRouter(prefix="/generate-schedules", tags=["Generate Schedules"])

@router.post("/", response_model=List[ScheduleResponse])
async def generate_schedules(
    filters: FilteredCourses,
    count: int = Query(
        default=10,
        ge=1,
        le=50,
        description="Número de horarios aleatorios a retornar. Rango: 1–50.",
    ),
    db: Session = Depends(get_db),
):
    """
    Genera hasta `count` combinaciones **aleatorias** de horarios válidos.

    Cada llamada puede devolver resultados distintos gracias a la mezcla interna
    de cursos. Útil para explorar diferentes opciones sin generar todas las
    combinaciones posibles (lo que sería muy lento con muchas materias).

    **Query params:**
    - **count** *(int, 1–50, default 10)*: cuántos horarios retornar.

    **Body Parameters:**
    - **preferencias**: materias con filtros opcionales de profesor y código.
      - Lógica de filtros: si ambos tienen valores → OR; si uno → solo ese; si ninguno → todos.
    - **freetime**: horas que deben quedar libres por día (7–18).

    **Ejemplo:**
    ```json
    {
      "preferencias": {
        "Cálculo I": { "profesores": ["Dr. Juan Pérez"], "codes": [1001] },
        "Física I":  { "profesores": [], "codes": [2001, 2002] }
      },
      "freetime": { "monday": [12, 13, 14], "friday": [16, 17, 18] }
    }
    ```
    """
    try:
        if not filters.preferencias:
            raise HTTPException(
                status_code=400,
                detail="No se proporcionaron preferencias validas",
            )

        generator = ScheduleGenerator(db)
        schedules = generator.generate_schedules(filters, max_results=count)

        if not schedules:
            raise HTTPException(
                status_code=404,
                detail="No se encontraron combinaciones de horarios válidas con las preferencias dadas",
            )

        # Formatear respuesta
        response = []
        hour_labels = [index_to_hour(i) for i in range(12)]
        day_labels = [index_to_day(i) for i in range(6)]

        for idx, (matrix, codes) in enumerate(schedules, 1):
            schedule_matrix = generator.format_schedule_matrix(matrix, codes)

            courses_info = []
            for subject, code, teacher_name in codes:
                from app.models.course import Course
                course = db.query(Course).filter(Course.code == code).first()

                schedules_list = []
                for schedule in course.schedules:
                    schedules_list.append(CourseScheduleInfo(
                        day=schedule.day,
                        start_time=schedule.start_time.strftime("%H:%M"),
                        end_time=schedule.end_time.strftime("%H:%M"),
                        location=schedule.location,
                    ))

                courses_info.append(CourseInfo(
                    subject=subject,
                    code=code,
                    teacher_name=teacher_name,
                    schedules=schedules_list,
                ))

            response.append(ScheduleResponse(
                schedule_number=idx,
                courses=courses_info,
                schedule_matrix=schedule_matrix,
                hour_labels=hour_labels,
                day_labels=day_labels,
            ))

        return response

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
