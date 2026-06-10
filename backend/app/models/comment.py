
# Importamos las clases y funciones necesarias de SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base  # Base es la clase declarativa para los modelos

# Definimos el modelo Comment que representa la tabla "comments"
class Comment(Base):
    __tablename__ = "comments"  # Nombre de la tabla en la base de datos

    # Columna 'id': clave primaria, tipo entero, con índice para búsquedas rápidas
    id = Column(Integer, primary_key=True, index=True)

    # Columna 'content': texto del comentario, máximo 500 caracteres, no puede ser nulo
    content = Column(String(500), nullable=False)

    # Columna 'profile_id': clave foránea que referencia a la tabla 'profiles'
    # Es obligatoria, cada comentario debe estar asociado a un perfil
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)

    # Columna 'course_id': clave foránea que referencia a la tabla 'courses'
    # Es opcional, el comentario puede no estar asociado a un curso
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)

    # Columna 'created_at': fecha y hora de creación del comentario
    # Incluye zona horaria y se asigna automáticamente con la función NOW() del servidor
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relación ORM con el modelo Profile
    # back_populates indica que en Profile existe un atributo 'comments' que completa la relación bidireccional
    profile = relationship("Profile", back_populates="comments")
