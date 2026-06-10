from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# -------------------------
# Schemas adicionales para Auth (complementan profile_schema.py)
# -------------------------

class Token(BaseModel):
    """Schema para respuesta de token JWT"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema para datos decodificados del token"""
    email: Optional[str] = None
    user_id: Optional[int] = None

class ProfileResponseWithDates(BaseModel):
    """Schema extendido con fechas de auditoría"""
    id: int
    name: str
    email: str
    bio: Optional[str]
    role: str
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {
        "from_attributes": True,
        "use_enum_values": True,
    }