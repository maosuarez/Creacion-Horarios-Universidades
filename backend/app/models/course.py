
# Importamos las clases y funciones necesarias de SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base  # Clase base para los modelos

# Modelo que representa los cursos en la base de datos
class Course(Base):
    __tablename__ = "courses"  # Nombre de la tabla en la base de datos

    # Columna 'id': clave primaria, tipo entero, con índice para búsquedas rápidas
    id = Column(Integer, primary_key=True, index=True)

    # Columna 'subject': nombre o materia del curso, tipo cadena, máximo 50 caracteres, no puede ser nulo
    subject = Column(String(50), nullable=False)

    # Columna 'code': código único del curso, tipo entero, no puede ser nulo
    code = Column(Integer, nullable=False)

    # Columna 'teacher_id': clave foránea que referencia a la tabla 'teachers'
    teacher_id = Column(Integer, ForeignKey("teachers.id"))

    # Restricción única para el campo 'code' (no puede repetirse en la tabla)
    __table_args__ = (
        UniqueConstraint('code', name='uq_course_code'),
    )

    # Relación ORM con el modelo Teacher
    # back_populates indica que en Teacher existe un atributo 'courses' que completa la relación bidireccional
    teacher = relationship("Teacher", back_populates="courses")

    # Relación ORM con el modelo CourseSchedule
    # cascade="all, delete-orphan" asegura que si se elimina un curso, también se eliminan sus horarios asociados
    schedules = relationship(
        "CourseSchedule",
        back_populates="course",
        cascade="all, delete-orphan"
    )

