from pydantic import BaseModel, Field, EmailStr, constr, model_validator, field_validator
from typing import List, Optional, Annotated
from app.schemas.comment import Comment

# -----------------------------
# MODELOS BASE
# -----------------------------
class ProfileBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    bio: Optional[str] = None
    email: Optional[EmailStr] = None

# -----------------------------
# MODELOS PARA CREAR
# -----------------------------
class ProfileCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    bio: Annotated[Optional[str], Field(max_length=300)] = None
    email: EmailStr
    # El rol NO se acepta en el signup; siempre lo asigna el backend.
    # El primer usuario registrado recibe "creator"; los demás, "viewer".
    # Un creator puede cambiar roles vía PATCH /auth/users/{id}/role.
    password: Annotated[str, Field(min_length=6, max_length=128)]

    model_config = {"extra": "ignore"}  # campo `role` enviado por el cliente se descarta

    @field_validator('name', mode="before")
    def validate_name_words(cls, v: str):
        # Regla: ninguna palabra del nombre puede exceder 20 caracteres
        # (ejemplo: "Test Nombredemasiadolargo" falla por la segunda palabra)
        words = v.strip().split()
        for w in words:
            if len(w) >= 20:
                raise ValueError("Cada palabra del nombre debe tener como máximo 20 caracteres")
        return v

    @model_validator(mode="before")
    def check_password_strength(cls, values):
        pwd = values.get("password")
        if pwd:
            if not any(c.isupper() for c in pwd):
                raise ValueError("La contraseña debe contener al menos una letra mayúscula")
            if not any(c.isdigit() for c in pwd):
                raise ValueError("La contraseña debe contener al menos un número")
        return values


# -----------------------------
# ASIGNACIÓN DE ROL (solo creators)
# -----------------------------
class RoleAssignment(BaseModel):
    role: Annotated[str, Field(pattern="^(creator|viewer)$")]

# -----------------------------
# MODELOS PARA ACTUALIZAR
# -----------------------------
class ProfileUpdate(BaseModel):
    name: Optional[Annotated[str, Field(min_length=1, max_length=100)]] = None
    email: Optional[EmailStr] = None
    bio: Optional[str] = None

class PasswordUpdate(BaseModel):
    old_password: str
    new_password: Annotated[str, Field(min_length=6, max_length=128)]

    @model_validator(mode="before")
    def check_password_strength(cls, values):
        pwd = values.get("new_password")
        if pwd:
            if not any(c.isupper() for c in pwd):
                raise ValueError("La contraseña debe contener al menos una letra mayúscula")
            if not any(c.isdigit() for c in pwd):
                raise ValueError("La contraseña debe contener al menos un número")
        return values

# -----------------------------
# MODELOS DE RESPUESTA
# -----------------------------
class ProfileResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    bio: Optional[str]
    role: str

    model_config = {
        "from_attributes": True,
        # Extrae .value de los enums SQLAlchemy (UserRole → "creator" / "viewer")
        "use_enum_values": True,
    }

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Profile(ProfileBase):
    id: int
    comments: List[Comment] = []

    model_config = {
        "from_attributes": True
    }

