from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.profile import Profile
from app.schemas.token_data import TokenData
import os

# -------------------------
# Configuración JWT
# -------------------------
# IMPORTANTE: En producción, usa variables de entorno
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM', "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30)

# OAuth2 scheme para obtener el token del header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# -------------------------
# Funciones para crear y verificar tokens
# -------------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crea un token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception):
    """Verifica y decodifica un token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        
        if email is None or user_id is None:
            raise credentials_exception
        
        token_data = TokenData(email=email, user_id=user_id)
        return token_data
    except JWTError:
        raise credentials_exception

# -------------------------
# Dependencias para proteger rutas
# -------------------------
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Profile:
    """
    Obtiene el usuario actual desde el token JWT.
    Esta dependencia se usa para proteger rutas.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verify_token(token, credentials_exception)
    
    user = db.query(Profile).filter(Profile.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_creator(
    current_user: Profile = Depends(get_current_user)
) -> Profile:
    """
    Verifica que el usuario actual tenga rol de creator.
    Usa esta dependencia para rutas que requieren permisos de creator.
    """
    if current_user.role.value != "creator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos suficientes"
        )
    return current_user