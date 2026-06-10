from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.profile import Profile
from app.models.shared_schedule import SharedSchedule
from app.schemas.shared_schedule import ShareScheduleRequest, SharedScheduleResponse

router = APIRouter(
    prefix="/shared-schedules",
    tags=["shared-schedules"],
)


@router.post("/", response_model=SharedScheduleResponse, status_code=status.HTTP_201_CREATED)
def share_schedule(
    body: ShareScheduleRequest,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Envía un horario a otro usuario identificado por email."""
    recipient = db.query(Profile).filter(Profile.email == body.recipient_email).first()
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró ningún usuario con ese correo electrónico",
        )
    if recipient.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes compartir un horario contigo mismo",
        )

    shared = SharedSchedule(
        sender_id=current_user.id,
        recipient_id=recipient.id,
        schedule_data=body.schedule_data,
        message=body.message,
    )
    db.add(shared)
    db.commit()
    db.refresh(shared)

    return SharedScheduleResponse(
        id=shared.id,
        sender_name=current_user.name,
        sender_email=current_user.email,
        schedule_data=shared.schedule_data,
        message=shared.message,
        created_at=shared.created_at,
    )


@router.get("/received", response_model=List[SharedScheduleResponse])
def list_received_schedules(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista los horarios que otros usuarios compartieron con el usuario autenticado."""
    rows = (
        db.query(SharedSchedule)
        .filter(SharedSchedule.recipient_id == current_user.id)
        .order_by(SharedSchedule.created_at.desc())
        .all()
    )
    return [
        SharedScheduleResponse(
            id=r.id,
            sender_name=r.sender.name,
            sender_email=r.sender.email,
            schedule_data=r.schedule_data,
            message=r.message,
            created_at=r.created_at,
        )
        for r in rows
    ]


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_received_schedule(
    schedule_id: int,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Elimina un horario compartido recibido. Solo el destinatario puede eliminarlo."""
    shared = (
        db.query(SharedSchedule)
        .filter(
            SharedSchedule.id == schedule_id,
            SharedSchedule.recipient_id == current_user.id,
        )
        .first()
    )
    if not shared:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Horario no encontrado")
    db.delete(shared)
    db.commit()
