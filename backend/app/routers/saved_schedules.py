from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.profile import Profile
from app.models.saved_schedule import SavedSchedule
from app.schemas.saved_schedule import SaveScheduleRequest, SavedScheduleResponse

router = APIRouter(
    prefix="/saved-schedules",
    tags=["saved-schedules"],
)


@router.post("/", response_model=SavedScheduleResponse, status_code=status.HTTP_201_CREATED)
def save_schedule(
    body: SaveScheduleRequest,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Guarda un horario generado en el perfil del usuario autenticado."""
    saved = SavedSchedule(
        profile_id=current_user.id,
        name=body.name,
        schedule_data=body.schedule_data,
    )
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return saved


@router.get("/", response_model=List[SavedScheduleResponse])
def list_saved_schedules(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista todos los horarios guardados del usuario autenticado."""
    return (
        db.query(SavedSchedule)
        .filter(SavedSchedule.profile_id == current_user.id)
        .order_by(SavedSchedule.created_at.desc())
        .all()
    )


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_schedule(
    schedule_id: int,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Elimina un horario guardado. Solo el propietario puede eliminarlo."""
    saved = (
        db.query(SavedSchedule)
        .filter(SavedSchedule.id == schedule_id, SavedSchedule.profile_id == current_user.id)
        .first()
    )
    if not saved:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Horario no encontrado")
    db.delete(saved)
    db.commit()
