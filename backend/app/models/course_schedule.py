# Importamos las clases y funciones necesarias
from sqlalchemy import Column, Integer, String, ForeignKey, Time
from sqlalchemy.orm import relationship
from app.database import Base  # Clase base para los modelos

# Definimos el modelo CourseSchedule que representa la tabla "course_schedules"
class CourseSchedule(Base):
    __tablename__ = "course_schedules"  # Nombre de la tabla en la base de datos

    # Columna 'id': clave primaria, tipo entero, con índice para búsquedas rápidas
    id = Column(Integer, primary_key=True, index=True)

    # Columna 'day': día de la semana, tipo cadena, máximo 20 caracteres, no puede ser nulo
    day = Column(String(20), nullable=False)

    # Columna 'start_time': hora de inicio del curso, tipo Time, no puede ser nulo
    start_time = Column(Time, nullable=False)  # Hora de inicio

    # Columna 'end_time': hora de fin del curso, tipo Time, no puede ser nulo
    end_time = Column(Time, nullable=False)    # Hora de fin

    # Columna 'location': salón o ubicación del curso, opcional
    location = Column(String(200), nullable=True)

    # Columna 'course_id': clave foránea que referencia a la tabla 'courses'
    course_id = Column(Integer, ForeignKey("courses.id"))

    # Relación ORM con el modelo Course
    # back_populates indica que en Course existe un atributo 'schedules' que completa la relación bidireccional
    course = relationship("Course", back_populates="schedules")
