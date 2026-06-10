from pydantic import BaseModel, model_validator
from datetime import datetime

# El modelo de la base de datos es:
# id: int
# content: str
# profile_id: int
# course_id: int
# created_at: DateTime

# Modelo Base
class CommentBase(BaseModel):
    content: str
    course_id: int | None = None

from pydantic import BaseModel
from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# -------------------------
# Schemas para Comment
# -------------------------

class CommentBase(BaseModel):
    """Schema base para comentarios"""
    content: str = Field(..., min_length=1, max_length=500)
    course_id: Optional[int] = None

class CommentCreate(CommentBase):
    """
    Schema para crear un comentario.
    
    El profile_id se obtiene automáticamente del usuario autenticado.
    """
    pass

class CommentUpdate(BaseModel):
    """
    Schema para actualizar un comentario.
    
    Solo se puede actualizar el contenido.
    """
    content: str = Field(..., min_length=1, max_length=500)

class CommentResponse(BaseModel):
    """Schema para respuesta de comentario"""
    id: int
    content: str
    profile_id: int
    course_id: Optional[int]
    created_at: datetime
    
    # Información del autor (opcional, útil para mostrar)
    author_name: Optional[str] = None
    author_email: Optional[str] = None

    @model_validator(mode="after")
    def fill_author_fields(self):
        """
        Completa author_name y author_email automáticamente
        si el ORM trae la relación comment.profile.
        """
        profile = getattr(self, "profile", None)

        if profile is not None:
            self.author_name = getattr(profile, "name", None)
            self.author_email = getattr(profile, "email", None)

        return self

    model_config = {"from_attributes": True}

class CommentListResponse(BaseModel):
    """Schema para lista paginada de comentarios"""
    total: int
    page: int
    page_size: int
    comments: list[CommentResponse]

# Comentario - Interfaz igual a la base de datos
class Comment(CommentBase):
    id: int
    created_at: datetime

    class ConfigDict:
        orm_mode = True