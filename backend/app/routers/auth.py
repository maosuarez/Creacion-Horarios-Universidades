from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models.profile import Profile, UserRole

# Importar schemas desde tu profile_schema.py
from app.schemas.profile import (
    ProfileCreate,
    ProfileUpdate,
    PasswordUpdate,
    ProfileResponse,
    RoleAssignment,
)

# Importar schemas adicionales de auth
from app.schemas.token_data import Token, ProfileResponseWithDates

from app.auth import (
    create_access_token,
    get_current_user,
    get_current_creator,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# -------------------------
# Registro (Signup) 
# -------------------------
@router.post("/signup", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: ProfileCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario.

    - **name**: Nombre del usuario (cada palabra máximo 20 caracteres)
    - **email**: Email único
    - **password**: Contraseña (mínimo 6 caracteres, debe contener mayúscula y número)
    - **bio**: Biografía opcional (máximo 300 caracteres)

    El rol **no** se acepta en el registro:
    - El **primer** usuario en registrarse recibe automáticamente el rol `creator`.
    - Los siguientes reciben `viewer`.
    - Un `creator` puede cambiar el rol de otros usuarios vía `PATCH /auth/users/{id}/role`.
    """
    try:
        # Verificar si el email ya existe
        existing_user = db.query(Profile).filter(Profile.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )

        # El primer usuario registrado se convierte en creator (bootstrap de admin).
        # Todos los demás inician como viewer.
        is_first_user = db.query(Profile).count() == 0
        assigned_role = UserRole.creator if is_first_user else UserRole.viewer

        new_user = Profile(
            name=user_data.name,
            email=user_data.email,
            bio=user_data.bio,
            role=assigned_role,
        )
        new_user.set_password(user_data.password)

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


# -------------------------
# Login
# -------------------------
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Inicia sesión y retorna un token JWT.
    
    - **email**: Email del usuario
    - **password**: Contraseña
    """
    try:
        # Buscar usuario por email
        user = db.query(Profile).filter(Profile.email == form_data.username).first()
        
        if not user or not user.check_password(form_data.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Crear token JWT
        access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


# -------------------------
# Obtener perfil actual (requiere autenticación)
# -------------------------
@router.get("/profile", response_model=ProfileResponseWithDates)
def get_profile(current_user: Profile = Depends(get_current_user)):
    """
    Obtiene el perfil del usuario autenticado con fechas de auditoría.
    
    **Requiere autenticación**: Sí (Bearer token)
    """
    try:
        return current_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


# -------------------------
# Actualizar perfil (requiere autenticación)
# -------------------------
@router.put("/profile", response_model=ProfileResponse)
def update_profile(
    profile_data: ProfileUpdate,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza el perfil del usuario autenticado.
    
    **Requiere autenticación**: Sí (Bearer token)
    
    - **name**: Nuevo nombre (opcional)
    - **email**: Nuevo email (opcional)
    - **bio**: Nueva biografía (opcional)
    """
    try:
        # Actualizar campos si se proporcionan
        if profile_data.name is not None:
            current_user.name = profile_data.name
        
        if profile_data.email is not None:
            # Verificar que el nuevo email no esté en uso
            existing_user = db.query(Profile).filter(
                Profile.email == profile_data.email,
                Profile.id != current_user.id
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El email ya está en uso por otro usuario"
                )
            current_user.email = profile_data.email
        
        if profile_data.bio is not None:
            current_user.bio = profile_data.bio
        
        db.commit()
        db.refresh(current_user)
        
        return current_user

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


# -------------------------
# Cambiar contraseña (requiere autenticación)
# -------------------------
@router.put("/profile/password", status_code=status.HTTP_200_OK)
def change_password(
    password_data: PasswordUpdate,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cambia la contraseña del usuario autenticado.
    
    **Requiere autenticación**: Sí (Bearer token)
    
    - **old_password**: Contraseña actual
    - **new_password**: Nueva contraseña (mínimo 6 caracteres, debe contener mayúscula y número)
    """
    try:
        # Verificar contraseña actual
        if not current_user.check_password(password_data.old_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña actual es incorrecta"
            )
        
        # Establecer nueva contraseña
        current_user.set_password(password_data.new_password)
        db.commit()
        
        return {"message": "Contraseña actualizada exitosamente"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


# -------------------------
# Eliminar perfil (requiere autenticación)
# -------------------------
@router.delete("/profile", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Elimina el perfil del usuario autenticado.

    **Requiere autenticación**: Sí (Bearer token)

    Esta acción es irreversible y eliminará todos los comentarios asociados.
    """
    try:
        # Verificar que no sea el administrador principal (menor id)
        primary_admin = db.query(Profile).order_by(Profile.id).first()
        if primary_admin and primary_admin.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El administrador principal no puede eliminar su cuenta"
            )

        db.delete(current_user)
        db.commit()
        return None

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


# -------------------------
# Asignación de roles (solo creators)
# -------------------------
@router.patch("/users/{user_id}/role", response_model=ProfileResponse)
def assign_role(
    user_id: int,
    role_data: RoleAssignment,
    current_user: Profile = Depends(get_current_creator),
    db: Session = Depends(get_db),
):
    """
    Cambia el rol de otro usuario.

    **Requiere autenticación**: Sí (Bearer token)
    **Requiere rol**: `creator`

    - **user_id**: ID del usuario al que se le asigna el rol
    - **role**: `"creator"` o `"viewer"`

    Un creator no puede cambiar su propio rol (evita auto-bloqueo accidental).
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes cambiar tu propio rol",
        )

    target_user = db.query(Profile).filter(Profile.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    # Verificar que no sea el administrador principal
    primary_admin = db.query(Profile).order_by(Profile.id).first()
    if primary_admin and primary_admin.id == target_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No se puede cambiar el rol del administrador principal"
        )

    try:
        target_user.role = UserRole(role_data.role)
        db.commit()
        db.refresh(target_user)
        return target_user

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


# -------------------------
# Listar usuarios (solo creators)
# -------------------------
@router.get("/users", response_model=List[ProfileResponse])
def list_users(
    current_user: Profile = Depends(get_current_creator),
    db: Session = Depends(get_db),
):
    """
    Lista todos los usuarios registrados.
    Requiere rol creator.
    """
    users = db.query(Profile).order_by(Profile.id).all()
    return users
