
# Importamos las clases y funciones necesarias de SQLAlchemy
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base  # Clase base para los modelos

# Modelo que representa a los profesores en la base de datos
class Teacher(Base):
    __tablename__ = "teachers"  # Nombre de la tabla en la base de datos

    # Columna 'id': clave primaria, tipo entero, con índice para búsquedas rápidas
    id = Column(Integer, primary_key=True, index=True)

    # Columna 'full_name': nombre completo del profesor, tipo cadena, máximo 200 caracteres, no puede ser nulo
    full_name = Column(String(200), nullable=False)

    # Relación ORM con el modelo Course
    # back_populates indica que en Course existe un atributo 'teacher' que completa la relación bidireccional
    courses = relationship("Course", back_populates="teacher")
