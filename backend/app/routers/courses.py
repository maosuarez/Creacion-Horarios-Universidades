from typing import Dict, List, Tuple
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from typing import Annotated
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from datetime import time, datetime
from sqlalchemy import func

from app.models.course import Course
from app.models.course_schedule import CourseSchedule
from app.models.teacher import Teacher
from app.schemas.course import CourseCreate, CourseUpdate, CodeOption, TeacherOption, SubjectOption, TeacherNameSuggestion, LocationSuggestion
from app.schemas.course_schedule import CourseSchedule as SchemaSchedule
from app.database import get_db

# Prefijo de la ruta
router = APIRouter(prefix="/courses", tags=["Courses"])

# ------------------------------
# Funciones para las Rutas
# ------------------------------

# Funcion para buscar o crear el profesor
def get_or_create_teacher(db: Session, full_name: str):
    '''
    Funcion para encontrar o crear un profesor
    dado su nombre
    '''
    ## Inicio de la transaccion
    try:
        # Query para filtrar por el nombre
        teacher = (
            db.query(Teacher)
            .filter(Teacher.full_name == full_name)
            .first()
        )

        # Verificacion de existencia
        if teacher:
            return teacher
        
        # Crear nuevo profesor
        full_name =  ' '.join(full_name.strip().split())
        teacher = Teacher(full_name=full_name)
        db.add(teacher)
        db.flush()  # evita commit prematuro; asegura ID

        # Devuelve el Profesor recien creado
        return teacher
    
    # Error que le indica que debe retroceder
    except SQLAlchemyError as e:

        # Retroceder
        db.rollback()
        raise e

# ------------------------------
# Rutas
# ------------------------------
# Crear un nuevo curso
@router.post("/")
def create_course(data: CourseCreate, db: Session = Depends(get_db)):
    try:
        # -----------------------------
        # Validaciones de campos básicos
        # -----------------------------
        if not data.code or len(str(data.code)) not in (4, 5):
            raise HTTPException(status_code=400, detail="El código debe ser un número de 4 o 5 dígitos.")

        if not data.teacher_name or data.teacher_name.strip() == "":
            raise HTTPException(status_code=400, detail="Debe proporcionar un nombre de profesor.")

        if not data.subject or data.subject.strip() == "":
            raise HTTPException(status_code=400, detail="Debe proporcionar una materia (subject).")

        if not data.schedules or len(data.schedules) == 0:
            raise HTTPException(status_code=400, detail="Debe proporcionar al menos un horario.")

        # Validación de días
        valid_days = {"Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado"}
        for s in data.schedules:
            if s.day not in valid_days:
                raise HTTPException(
                    status_code=400,
                    detail=f"El día '{s.day}' no es válido. Use: {', '.join(valid_days)}."
                )

        # Normalizar nombre del profesor
        teacher_name = data.teacher_name.strip()

        # -----------------------------
        # Obtener o crear profesor
        # -----------------------------
        teacher = get_or_create_teacher(db, teacher_name)

        if not teacher:
            raise HTTPException(
                status_code=501,
                detail="No se creo el teacher adecuadamente"
            )
        
        schedule_teacher = (
            db.query(Course)
            .options(joinedload(Course.schedules))  # eager load
            .filter(Course.teacher_id == teacher.id)
            .all()
        )

        por_sche: Dict[str, List[Tuple[time, time]]] = {}
        for c in schedule_teacher:
            for s in c.schedules:
                por_sche.setdefault(s.day, []).append((
                    s.start_time,
                    s.end_time
                ))
        for day in por_sche:
            por_sche[day].sort(key=lambda x: x[0])

        # -----------------------------
        # Validar Codigo Unico
        # -----------------------------
        existing = (
            db.query(Course)
            .filter(Course.code == data.code)
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="El código del curso ya existe"
            )

        # -----------------------------
        # Crear curso
        # -----------------------------
        course = Course(
            subject=data.subject.strip(),
            code=data.code,
            teacher_id=teacher.id,
        )

        db.add(course)
        db.flush()  # obtener course.id antes de crear schedules

        # -----------------------------
        # Crear horarios
        # -----------------------------
        # Rango permitido
        START_MIN = time(7, 0)   # 7:00 AM
        START_MAX = time(18, 0)  # 6:00 PM

        END_MIN = time(8, 0)     # 8:00 AM
        END_MAX = time(19, 0)    # 7:00 PM

        # Validacion de solapamiento interno
        por_dia: Dict[str, List[Tuple[time, time, SchemaSchedule]]] = {}

        for s in data.schedules:

            # Validar día
            if s.day not in valid_days:
                raise HTTPException(
                    400,
                    f"El día '{s.day}' no es válido. Debe ser: {', '.join(valid_days)}"
                )

            # -------------------------
            # Validar formato horario
            # -------------------------
            try:
                start_t = datetime.strptime(s.start_time, "%H:%M").time()
                end_t   = datetime.strptime(s.end_time, "%H:%M").time()
            except Exception:
                raise HTTPException(
                    400,
                    f"El formato de hora es inválido: '{s.start_time}' → '{s.end_time}'. Debe ser 'HH:MM'."
                )
            
            # -------------------------
            # Validar que no haya solapamiento con el mismo profesor
            # -------------------------
            for (s_exist, e_exist) in por_sche.get(s.day, []):
                # Solapan si max(start) < min(end) — semántica [inicio, fin)
                if max(start_t, s_exist) < min(end_t, e_exist):
                    raise HTTPException(
                        400,
                        f"Solape con horario existente del profesor."
                    )

            # -------------------------
            # Validar rango permitido
            # -------------------------
            if not (START_MIN <= start_t <= START_MAX):
                raise HTTPException(
                    400,
                    f"La hora de inicio '{s.start_time}' está fuera del rango permitido (07:00 - 18:00)."
                )

            if not (END_MIN <= end_t <= END_MAX):
                raise HTTPException(
                    400,
                    f"La hora de fin '{s.end_time}' está fuera del rango permitido (08:00 - 19:00)."
                )

            # -------------------------
            # Validar coherencia (end > start)
            # -------------------------
            if end_t <= start_t:
                raise HTTPException(
                    400,
                    f"La hora de fin '{s.end_time}' debe ser mayor que la de inicio '{s.start_time}'."
                )
            
            # -------------------------
            # Validar que no se solapen si hay multiples
            # -------------------------
            por_dia.setdefault(s.day, []).append((start_t, end_t, s))
            
            # -------------------------
            # Guardar convertidos a datetime.time
            # -------------------------
            course.schedules.append(
                CourseSchedule(
                    day=s.day,
                    start_time=start_t,
                    end_time=end_t,
                    location=s.location,
                )
            )

        # Revisar cada día
        for _, slots in por_dia.items():
            # Ordenar por hora de inicio
            slots.sort(key=lambda x: x[0])

            # Verificar solapes adyacentes
            for i in range(1, len(slots)):
                _ , prev_end, _ = slots[i - 1]
                curr_start, _ , _ = slots[i]

                # Condición de solape para intervalos [a,b) y [c,d):
                # se solapan si curr_start < prev_end y prev_start < curr_end
                # Dado que están ordenados por curr_start >= prev_start, basta con:
                if curr_start < prev_end:
                    raise HTTPException(
                        400,
                        f"Solape entre los horarios del curso."
                    )
        # -----------------------------
        # Guardar todo
        # -----------------------------
        db.commit()
        db.refresh(course)

        # Respuesta final HTTP 200 con objeto actualizado
        return JSONResponse(
            status_code=200,
            content={
                "message": "Horarios actualizados correctamente",
                "course": {
                    "id": course.id,
                    "subject": course.subject,
                    "code": course.code,
                    "teacher_full_name": teacher.full_name,
                    "schedules": [
                        {
                            "id": s.id,
                            "day": s.day,
                            "start_time": str(s.start_time),
                            "end_time": str(s.end_time),
                            "location": s.location,
                        }
                        for s in course.schedules
                    ]
                }
            }
        )

    except HTTPException as e:
        db.rollback()
        raise e

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.put("/{course_id}")
def update_course(course_id: Annotated[int, Path(title="ID del curso", description="Debe ser un entero positivo", ge=1)], data: CourseUpdate, db: Session = Depends(get_db)):
    try:
        course = (
            db.query(Course)
            .options(joinedload(Course.teacher), joinedload(Course.schedules))
            .filter(Course.id == course_id)
            .first()
        )
        if not course:
            raise HTTPException(404, "Curso no encontrado")

        # -----------------------------
        # Validaciones simples
        # -----------------------------
        if data.subject is not None and data.subject != course.subject:
            if data.subject.strip() == "":
                raise HTTPException(400, "La materia no puede estar vacía.")
            course.subject = data.subject.strip()

        if data.code is not None and data.code != course.code:
            code_str = str(data.code)
            if not code_str.isdigit() or len(code_str) not in (4, 5):
                raise HTTPException(400, "El código debe ser un número de 4 o 5 dígitos.")

            # Validar código único (evitar choque con otros cursos)
            existing = (
                db.query(Course)
                .filter(Course.code == data.code, Course.id != course_id)
                .first()
            )
            if existing:
                raise HTTPException(400, "El código del curso ya está en uso por otro curso")

            course.code = data.code

        # -----------------------------
        # Actualizar profesor
        # -----------------------------
        if data.teacher_name is not None:
            name = data.teacher_name.strip()
            if name == "":
                raise HTTPException(400, "El nombre del profesor no puede estar vacío.")

            teacher = get_or_create_teacher(db, name)
            course.teacher_id = teacher.id

        try:
            # Obtener horarios actuales desde la BD
            old_schedules = (
                db.query(CourseSchedule)
                .filter(CourseSchedule.course_id == course_id)
                .all()
            )

            def normalize_time_any(t):
                # Acepta datetime.time o string
                if isinstance(t, str):
                    h, m = t.split(":")[:2]
                    return f"{h.zfill(2)}:{m.zfill(2)}"

                # Es datetime.time
                return f"{str(t.hour).zfill(2)}:{str(t.minute).zfill(2)}"

            # Normalizar horarios antiguos
            old_list = [
                (s.day,
                normalize_time_any(s.start_time),
                normalize_time_any(s.end_time))
                for s in old_schedules
            ]

            # Normalizar horarios nuevos (los que llegan desde data)
            new_list = [
                (s.day,
                normalize_time_any(s.start_time),
                normalize_time_any(s.end_time))
                for s in data.schedules
            ]

            # Comparación ordenada para evitar falsos positivos
            old_list_sorted = sorted(old_list)
            new_list_sorted = sorted(new_list)

            schedules_changed = old_list_sorted != new_list_sorted

        except:
            schedules_changed = True

        # -----------------------------
        # Actualizar horarios
        # -----------------------------
        if data.schedules is not None and schedules_changed:

            # horarios del profesor ya establecidos
            schedule_teacher = (
                db.query(Course)
                .options(joinedload(Course.schedules))  # eager load
                .filter(Course.teacher_id == course.teacher_id)
                .filter(Course.id != course.id)
                .all()
            )

            por_sche: Dict[str, List[Tuple[time, time]]] = {}
            for c in schedule_teacher:
                for s in c.schedules:
                    por_sche.setdefault(s.day, []).append((
                        s.start_time,
                        s.end_time
                    ))
            for day in por_sche:
                por_sche[day].sort(key=lambda x: x[0])

            valid_days = {"Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado"}

            START_MIN = time(7, 0)
            START_MAX = time(18, 0)
            END_MIN   = time(8, 0)
            END_MAX   = time(19, 0)

            # Borrar horarios antiguos correctamente
            db.query(CourseSchedule).filter(CourseSchedule.course_id == course_id).delete()
            db.flush()

            # Validacion de solapamiento interno
            por_dia: Dict[str, List[Tuple[time, time, SchemaSchedule]]] = {}

            for s in data.schedules:

                # Validar día
                if s.day not in valid_days:
                    raise HTTPException(
                        400,
                        f"El día '{s.day}' no es válido. Debe ser: {', '.join(valid_days)}"
                    )

                # Validar formato HH:MM
                try:
                    start_t = datetime.strptime(s.start_time, "%H:%M").time()
                    end_t   = datetime.strptime(s.end_time, "%H:%M").time()
                except:
                    raise HTTPException(
                        400,
                        f"El formato de hora es inválido: '{s.start_time}' → '{s.end_time}'. Debe ser 'HH:MM'."
                    )
                
                # -------------------------
                # Validar que no haya solapamiento con el mismo profesor
                # -------------------------
                for (s_exist, e_exist) in por_sche.get(s.day, []):
                    # Solapan si max(start) < min(end) — semántica [inicio, fin)
                    if max(start_t, s_exist) < min(end_t, e_exist):
                        raise HTTPException(
                            400,
                            f"Solape con horario existente del profesor."
                        )

                # Validar rango
                if not (START_MIN <= start_t <= START_MAX):
                    raise HTTPException(
                        400,
                        f"La hora de inicio '{s.start_time}' está fuera del rango permitido (07:00 - 18:00)."
                    )

                if not (END_MIN <= end_t <= END_MAX):
                    raise HTTPException(
                        400,
                        f"La hora de fin '{s.end_time}' está fuera del rango permitido (08:00 - 19:00)."
                    )

                # Validar coherencia
                if end_t <= start_t:
                    raise HTTPException(
                        400,
                        f"La hora de fin '{s.end_time}' debe ser mayor que la de inicio '{s.start_time}'."
                    )
                
                # -------------------------
                # Validar que no se solapen si hay multiples
                # -------------------------
                por_dia.setdefault(s.day, []).append((start_t, end_t, s))

                # Guardar
                course.schedules.append(
                    CourseSchedule(
                        day=s.day,
                        start_time=start_t,
                        end_time=end_t,
                        location=s.location,
                    )
                )
            # Revisar cada día
            for _, slots in por_dia.items():
                # Ordenar por hora de inicio
                slots.sort(key=lambda x: x[0])

                # Verificar solapes adyacentes
                for i in range(1, len(slots)):
                    _ , prev_end, _ = slots[i - 1]
                    curr_start, _ , _ = slots[i]

                    # Condición de solape para intervalos [a,b) y [c,d):
                    # se solapan si curr_start < prev_end y prev_start < curr_end
                    # Dado que están ordenados por curr_start >= prev_start, basta con:
                    if curr_start < prev_end:
                        raise HTTPException(
                            400,
                            f"Solape entre los horarios del curso."
                        )

        # Guardar cambios y recargar relaciones
        db.commit()
        db.refresh(course)
        teacher_full_name = course.teacher.full_name if course.teacher else None

        return {
            "message": "Curso actualizado correctamente",
            "course": {
                "id": course.id,
                "subject": course.subject,
                "code": course.code,
                "teacher_full_name": teacher_full_name,
                "schedules": [
                    {
                        "id": s.id,
                        "day": s.day,
                        "start_time": str(s.start_time),
                        "end_time": str(s.end_time),
                        "location": s.location,
                    }
                    for s in course.schedules
                ]
            }
        }

    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Error interno: {str(e)}")

@router.get("/all")
def get_all_courses(db: Session = Depends(get_db)):
    try:
        # Consulta con cargas anticipadas
        courses = (
            db.query(Course)
            .options(
                joinedload(Course.teacher),
                joinedload(Course.schedules)
            )
            .all()
        )

        payload = []
        for course in courses:
            # Nombre seguro del profesor
            teacher_full_name = course.teacher.full_name if course.teacher else None

            # Horarios seguros
            schedules = []
            for s in (course.schedules or []):
                schedules.append({
                    "day": s.day,
                    "start_time": s.start_time,
                    "end_time": s.end_time,
                    "location": s.location,
                })

            payload.append({
                "id": course.id,
                "subject": course.subject,
                "code": course.code,
                "teacher_full_name": teacher_full_name,
                "schedules": schedules
            })

        return JSONResponse(content=jsonable_encoder(payload), status_code=200)

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Error en la base de datos al consultar los cursos"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al procesar los cursos: {type(e).__name__}"
        )

@router.get("/{course_id}")
def get_course(course_id: Annotated[int, Path(title="ID del curso", description="Debe ser un entero positivo", ge=1)], db: Session = Depends(get_db)):
    try:
        # Consulta con cargas anticipadas
        course = (
            db.query(Course)
            .options(
                joinedload(Course.teacher),
                joinedload(Course.schedules)
            )
            .filter(Course.id == course_id)
            .first()
        )

        if not course:
            raise HTTPException(status_code=404, detail="Curso no encontrado")

        # Manejo seguro de campos del profesor
        teacher_full_name = None
        if course.teacher:
            teacher_full_name = course.teacher.full_name

        # Manejo seguro de horarios
        schedules = []
        for s in (course.schedules or []):
            schedules.append({
                "day": s.day,
                "start_time": s.start_time,
                "end_time": s.end_time,
                "location": s.location,
            })

        payload = {
            "id": course.id,
            "subject": course.subject,
            "code": course.code,
            "teacher_full_name": teacher_full_name,
            "schedules": schedules
        }

        return JSONResponse(content=jsonable_encoder(payload), status_code=200)

    except HTTPException:
        # Re-lanzamos errores esperados manualmente (404 por ejemplo)
        raise

    except SQLAlchemyError:
        # Errores de base de datos
        raise HTTPException(
            status_code=500,
            detail="Error en la base de datos al consultar el curso"
        )

    except Exception as e:
        # Cualquier error inesperado: serialización, atributos nulos, etc.
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al procesar el curso: {type(e).__name__}"
        )

# Eliminar un curso por ID
@router.delete("/{course_id}")
def delete_course(course_id: Annotated[int, Path(title="ID del curso", description="Debe ser un entero positivo", ge=1)], db: Session = Depends(get_db)):
    try:
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(404, "Curso no encontrado")

        db.delete(course)
        db.commit()

        return {"detail": "Curso eliminado correctamente"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Error interno: {str(e)}")


@router.get("/search/subjects", response_model=List[SubjectOption])
def search_subjects(
    query: str = Query(..., min_length=1, description="Texto parcial para buscar materias"),
    db: Session = Depends(get_db)
):
    """
    Búsqueda typeahead de materias. Solo este endpoint usa búsqueda por prefijo.
    Retorna materias que comiencen con el texto ingresado.
    """
    try:
        results = (
            db.query(
                Course.subject,
                func.count(Course.id).label("count")
            )
            .filter(Course.subject.ilike(f"{query}%"))
            .group_by(Course.subject)
            .order_by(Course.subject)
            .limit(20)
            .all()
        )
        return [SubjectOption(subject=r[0], count=r[1]) for r in results]

    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error interno al buscar materias")


@router.get("/search/codes", response_model=List[CodeOption])
def get_codes_by_subject(
    subject: str = Query(..., description="Materia seleccionada"),
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los códigos de curso disponibles para una materia específica.
    No usa búsqueda typeahead, retorna todas las opciones.
    """
    try:
        courses = db.query(Course).filter(
            Course.subject == subject
        ).order_by(Course.code).all()

        if not courses:
            raise HTTPException(status_code=404, detail="No se encontraron cursos para esta materia")

        return [CodeOption(code=int(c.code), course_id=int(c.id)) for c in courses]

    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error interno al consultar códigos de curso")
    except HTTPException:
        raise


@router.get("/search/teachers", response_model=List[TeacherOption])
def get_teachers_by_subject(
    subject: str = Query(..., description="Materia seleccionada"),
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los profesores que enseñan una materia específica.
    No usa búsqueda typeahead, retorna todas las opciones.
    """
    try:
        teachers = db.query(Teacher).join(Course).filter(
            Course.subject == subject
        ).distinct().order_by(Teacher.full_name).all()

        if not teachers:
            raise HTTPException(status_code=404, detail="No se encontraron profesores para esta materia")

        return [TeacherOption(id=t.id, full_name=t.full_name) for t in teachers]

    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error interno al consultar profesores")
    except HTTPException:
        raise


@router.get("/search/teacher-names", response_model=List[TeacherNameSuggestion])
def search_teacher_names(
    query: str = Query(..., min_length=1, description="Texto parcial para buscar profesores"),
    db: Session = Depends(get_db)
):
    """
    Búsqueda typeahead de nombres de profesores (para autocompletado en formulario).
    Retorna profesores cuyo nombre contenga el texto ingresado (insensible a mayúsculas).
    """
    try:
        results = (
            db.query(Teacher.full_name)
            .filter(Teacher.full_name.ilike(f"%{query}%"))
            .order_by(Teacher.full_name)
            .limit(20)
            .all()
        )
        return [TeacherNameSuggestion(full_name=r[0]) for r in results]

    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error interno al buscar profesores")


@router.get("/search/locations", response_model=List[LocationSuggestion])
def search_locations(
    query: str = Query(..., min_length=1, description="Texto parcial para buscar ubicaciones"),
    db: Session = Depends(get_db)
):
    """
    Búsqueda typeahead de ubicaciones/salones (para autocompletado en formulario).
    Retorna ubicaciones distintas que contengan el texto ingresado.
    """
    try:
        results = (
            db.query(CourseSchedule.location)
            .filter(
                CourseSchedule.location.isnot(None),
                CourseSchedule.location != "",
                CourseSchedule.location.ilike(f"%{query}%")
            )
            .distinct()
            .order_by(CourseSchedule.location)
            .limit(20)
            .all()
        )
        return [LocationSuggestion(location=r[0]) for r in results]

    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error interno al buscar ubicaciones")
