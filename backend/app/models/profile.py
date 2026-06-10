
# Importamos las clases y funciones necesarias de SQLAlchemy
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Enum,
    func,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.database import Base  # Clase base para los modelos
import enum  # Para definir enumeraciones
from passlib.context import CryptContext  # Para manejo seguro de contraseñas

# -------------------------
# Configuración para hashing de contraseñas
# -------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Función para generar el hash de una contraseña
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Función para verificar si una contraseña coincide con su hash
def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

# -------------------------
# Enum para Roles de usuario
# -------------------------
class UserRole(enum.Enum):
    creator = "creator"  # Usuario con permisos de creación
    viewer = "viewer"    # Usuario con permisos de solo lectura

# -------------------------
# Modelo Profile
# -------------------------
class Profile(Base):
    __tablename__ = "profiles"  # Nombre de la tabla en la base de datos

    # Clave primaria
    id = Column(Integer, primary_key=True, index=True)

    # Datos básicos
    name = Column(String(100), nullable=False)  # Nombre del usuario
    bio = Column(String(255), nullable=True)    # Biografía opcional

    # Correo único y obligatorio
    email = Column(String(120), nullable=False, unique=True, index=True)

    # Hash de la contraseña (no se guarda la contraseña en texto plano)
    password_hash = Column(String(255), nullable=False)

    # Rol del usuario (Enum)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.viewer)

    # Auditoría: fecha de creación y actualización
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación con comentarios (un perfil puede tener muchos comentarios)
    comments = relationship(
        "Comment",
        back_populates="profile",
        cascade="all, delete-orphan"
    )

    # Relación con horarios guardados
    saved_schedules = relationship(
        "SavedSchedule",
        back_populates="profile",
        cascade="all, delete-orphan"
    )

    # Métodos útiles para manejar contraseñas
    def set_password(self, password: str):
        self.password_hash = hash_password(password)

    def check_password(self, password: str) -> bool:
        return verify_password(password, self.password_hash)

    # -------------------------
    # Constraints y Indexes
    # -------------------------
    __table_args__ = (
        UniqueConstraint('email', name='uq_profile_email'),  # Garantiza que el email sea único
    )
