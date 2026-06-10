from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.course import Course
from app.models.teacher import Teacher
from app.schemas.course import CourseRowSubject
from app.database import get_db


# Prefijo de la ruta
router = APIRouter(prefix="/subjects", tags=["Subjects"])

# ------------------------------
# Rutas
# ------------------------------

# Obtener todos los nombres de cursos
@router.get("/")
def get_all_subjects(db: Session = Depends(get_db)):
    subjects = db.query(Course.subject).distinct().all()
    return [s[0] for s in subjects]

# Dado el nombre de una materia obtener los codigos y profesores asociados
@router.get("/{subject}/details")
def get_subject_details(subject: str, db: Session = Depends(get_db)):
    try:    
        rows: List[CourseRowSubject]  = (
            db.query(
                Course.code,
                Teacher.id.label("teacher_id"),
                Teacher.full_name.label("teacher_name"),
            )
            .join(Teacher, Course.teacher_id == Teacher.id)
            .filter(Course.subject == subject)
            .distinct()
            .all()
        )

        if not rows:
            raise HTTPException(404, "Materia no encontrada")

        codes = sorted({row.code for row in rows})

        teachers: List[dict[str, str | int]] = [
            {"id": row[0], "name": row[1]}
            for row in { (r.teacher_id, r.teacher_name) for r in rows }
        ]

        return {
            "subject": subject,
            "codes": codes,
            "teachers": teachers
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error interno: {str(e)}")

