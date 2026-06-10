import pytest
from datetime import time
import numpy as np

# Importar modelos y app
from app.models.course import Course
from app.models.teacher import Teacher
from app.models.course_schedule import CourseSchedule
from app.routers.schedule import ScheduleGenerator
from tests.test_database import TestingSessionLocal, client

@pytest.fixture(scope="session")
def test_db():
    db = TestingSessionLocal()
    yield db
    db.close()

@pytest.fixture
def sample_teachers(test_db):
    teachers = [
        Teacher(full_name="Dr. Juan Pérez"),
        Teacher(full_name="Dra. María García"),
        Teacher(full_name="Dr. Carlos López")
    ]

    test_db.add_all(teachers)
    test_db.commit()

    # refrescar para acceder a IDs generados
    for t in teachers:
        test_db.refresh(t)

    return teachers


@pytest.fixture
def sample_courses(test_db, sample_teachers):
    teachers = sample_teachers

    courses = [
        Course(subject="Cálculo I", code=1001, teacher_id=teachers[0].id),
        Course(subject="Cálculo I", code=1002, teacher_id=teachers[1].id),

        Course(subject="Física I", code=2001, teacher_id=teachers[0].id),
        Course(subject="Física I", code=2002, teacher_id=teachers[2].id),

        Course(subject="Programación I", code=3001, teacher_id=teachers[1].id),
    ]

    test_db.add_all(courses)
    test_db.commit()

    # refrescar IDs reales
    for c in courses:
        test_db.refresh(c)

    # Horarios ya usando IDs reales
    schedules = [
        # Cálculo I opción 1
        CourseSchedule(course_id=courses[0].id, day="monday", start_time=time(7, 0), end_time=time(9, 0)),
        CourseSchedule(course_id=courses[0].id, day="wednesday", start_time=time(7, 0), end_time=time(9, 0)),

        # Cálculo I opción 2
        CourseSchedule(course_id=courses[1].id, day="tuesday", start_time=time(10, 0), end_time=time(12, 0)),
        CourseSchedule(course_id=courses[1].id, day="thursday", start_time=time(10, 0), end_time=time(12, 0)),

        # Física opción 1
        CourseSchedule(course_id=courses[2].id, day="monday", start_time=time(14, 0), end_time=time(16, 0)),
        CourseSchedule(course_id=courses[2].id, day="wednesday", start_time=time(14, 0), end_time=time(16, 0)),

        # Física opción 2
        CourseSchedule(course_id=courses[3].id, day="tuesday", start_time=time(7, 0), end_time=time(9, 0)),
        CourseSchedule(course_id=courses[3].id, day="thursday", start_time=time(7, 0), end_time=time(9, 0)),

        # Programación
        CourseSchedule(course_id=courses[4].id, day="friday", start_time=time(9, 0), end_time=time(13, 0)),
    ]

    test_db.add_all(schedules)
    test_db.commit()

    return courses


# Tests de utilidades
def test_time_to_index():
    """Test conversión de hora a índice"""
    from app.routers.schedule import time_to_index
    assert time_to_index(time(7, 0)) == 0
    assert time_to_index(time(12, 0)) == 5
    assert time_to_index(time(18, 0)) == 11

def test_day_to_index():
    """Test conversión de día a índice"""
    from app.routers.schedule import day_to_index
    # Test inglés
    assert day_to_index("monday") == 0
    assert day_to_index("wednesday") == 2
    assert day_to_index("friday") == 4
    # Test español
    assert day_to_index("lunes") == 0
    assert day_to_index("miércoles") == 2
    assert day_to_index("viernes") == 4
    # Test inválido
    assert day_to_index("invalid") == -1

def test_index_to_hour():
    """Test conversión de índice a hora"""
    from app.routers.schedule import index_to_hour
    assert index_to_hour(0) == "7:00"
    assert index_to_hour(5) == "12:00"
    assert index_to_hour(11) == "18:00"

def test_index_to_day():
    """Test conversión de índice a día"""
    from app.routers.schedule import index_to_day
    assert index_to_day(0) == "Lunes"
    assert index_to_day(2) == "Miércoles"
    assert index_to_day(4) == "Viernes"

def test_algo(sample_teachers ,sample_courses):
    # sample_courses ya tiene cursos y horarios válidos
    assert True

# Tests de ScheduleGenerator
def test_get_filtered_courses_by_subject_no_filters(test_db):
    """Test obtener cursos de una materia sin filtros"""
    # Obtener una instancia real de la sesión desde get_db()

    generator = ScheduleGenerator(test_db)
    from app.routers.schedule import SubjectPreference
    
    preference = SubjectPreference(profesores=[], codes=[])
    courses = generator.get_filtered_courses_by_subject("Cálculo I", preference)
    
    assert len(courses) == 2
    assert all(isinstance(c, tuple) and len(c) == 3 for c in courses)

def test_get_filtered_courses_by_subject_with_teacher(test_db):
    """Test filtrar cursos por profesor específico"""
    generator = ScheduleGenerator(test_db)
    from app.routers.schedule import SubjectPreference
    
    preference = SubjectPreference(profesores=["Dr. Juan Pérez"], codes=[])
    courses = generator.get_filtered_courses_by_subject("Cálculo I", preference)
    
    assert len(courses) == 1
    assert courses[0][2] == "Dr. Juan Pérez"

def test_get_filtered_courses_by_subject_with_code(test_db):
    """Test filtrar cursos por código específico"""
    generator = ScheduleGenerator(test_db)
    from app.routers.schedule import SubjectPreference
    
    preference = SubjectPreference(profesores=[], codes=[1002])
    courses = generator.get_filtered_courses_by_subject("Cálculo I", preference)
    
    assert len(courses) == 1
    assert courses[0][0] == 1002

def test_get_filtered_courses_by_subject_with_both_filters(test_db):
    """Test filtrar cursos por profesor O código (UNION)"""
    generator = ScheduleGenerator(test_db)
    from app.routers.schedule import SubjectPreference
    
    # Cálculo I tiene:
    # - Código 1001 con Dr. Juan Pérez
    # - Código 1002 con Dra. María García
    # Pedimos: Dr. Juan Pérez O código 1002
    # Debería retornar AMBOS (UNION)
    preference = SubjectPreference(profesores=["Dr. Juan Pérez"], codes=[1002])
    courses = generator.get_filtered_courses_by_subject("Cálculo I", preference)
    
    assert len(courses) == 2  # Ambos cursos porque es UNION
    codes = [c[0] for c in courses]
    teachers = [c[2] for c in courses]
    
    assert 1001 in codes  # Curso del Dr. Juan Pérez
    assert 1002 in codes  # Código solicitado
    assert "Dr. Juan Pérez" in teachers
    assert "Dra. María García" in teachers

def test_get_filtered_courses_union_same_course(test_db):
    """Test UNION cuando profesor y código apuntan al mismo curso"""
    generator = ScheduleGenerator(test_db)
    from app.routers.schedule import SubjectPreference
    
    # Pedir Dr. Juan Pérez O código 1001 (mismo curso)
    preference = SubjectPreference(profesores=["Dr. Juan Pérez"], codes=[1001])
    courses = generator.get_filtered_courses_by_subject("Cálculo I", preference)
    
    # Debería retornar solo 1 curso (sin duplicados)
    assert len(courses) == 1
    assert courses[0][0] == 1001
    assert courses[0][2] == "Dr. Juan Pérez"

def test_get_filtered_courses_union_no_overlap(test_db):
    """Test UNION con profesor y código que no se solapan"""
    generator = ScheduleGenerator(test_db)
    from app.routers.schedule import SubjectPreference
    
    # Física I tiene:
    # - Código 2001 con Dr. Juan Pérez
    # - Código 2002 con Dr. Carlos López
    # Pedir Dr. Juan Pérez O código 2002
    preference = SubjectPreference(profesores=["Dr. Juan Pérez"], codes=[2002])
    courses = generator.get_filtered_courses_by_subject("Física I", preference)
    
    assert len(courses) == 2  # Ambos por UNION
    codes = [c[0] for c in courses]
    assert 2001 in codes
    assert 2002 in codes

def test_course_to_matrix(test_db):
    """Test conversión de curso a matriz"""
    generator = ScheduleGenerator(test_db)
    
    schedules_dict = {
        "monday": [(time(7, 0), time(9, 0))],
        "wednesday": [(time(7, 0), time(9, 0))]
    }
    
    matrix = generator.course_to_matrix(1001, schedules_dict)
    
    # Verificar dimensiones
    assert matrix.shape == (12, 6)
    
    # Verificar que las horas 7-9 en lunes (columna 0) estén marcadas
    assert matrix[0][0] == 1001  # 7am lunes
    assert matrix[1][0] == 1001  # 8am lunes
    assert matrix[0][2] == 1001  # 7am miércoles
    assert matrix[1][2] == 1001  # 8am miércoles
    assert matrix[2][0] == 0     # 9am lunes (libre)

def test_create_freetime_matrix(test_db):
    """Test creación de matriz de tiempos libres"""
    generator = ScheduleGenerator(test_db)
    
    freetime = {
        "monday": [12, 13, 14],  # 12pm-2pm lunes
        "friday": [16, 17, 18]   # 4pm-6pm viernes
    }
    
    matrix = generator.create_freetime_matrix(freetime)
    
    # Verificar dimensiones
    assert matrix.shape == (12, 6)
    
    # Verificar tiempos libres marcados (1)
    assert matrix[5][0] == 1   # 12pm lunes (índice 5)
    assert matrix[6][0] == 1   # 1pm lunes
    assert matrix[7][0] == 1   # 2pm lunes
    assert matrix[9][4] == 1   # 4pm viernes
    assert matrix[10][4] == 1  # 5pm viernes
    assert matrix[11][4] == 1  # 6pm viernes
    
    # Verificar otros espacios libres (0)
    assert matrix[0][0] == 0
    assert matrix[0][1] == 0

def test_check_freetime_constraint_pass(test_db):
    """Test verificación de restricción de tiempo libre (sin conflictos)"""
    generator = ScheduleGenerator(test_db)
    
    schedule_matrix = np.zeros((12, 6), dtype=int)
    schedule_matrix[0][0] = 1001  # Lunes 7am ocupado
    
    freetime_matrix = np.zeros((12, 6), dtype=int)
    freetime_matrix[5][0] = 1  # Lunes 12pm debe estar libre
    
    # No hay conflicto: lunes 7am está ocupado pero lunes 12pm está libre
    assert generator.check_freetime_constraint(schedule_matrix, freetime_matrix) == True

def test_check_freetime_constraint_fail(test_db):
    """Test verificación de restricción de tiempo libre (con conflictos)"""
    generator = ScheduleGenerator(test_db)
    
    schedule_matrix = np.zeros((12, 6), dtype=int)
    schedule_matrix[5][0] = 1001  # Lunes 12pm ocupado
    
    freetime_matrix = np.zeros((12, 6), dtype=int)
    freetime_matrix[5][0] = 1  # Lunes 12pm debe estar libre
    
    # Hay conflicto: lunes 12pm está ocupado pero debe estar libre
    assert generator.check_freetime_constraint(schedule_matrix, freetime_matrix) == False

def test_has_conflict(test_db):
    """Test detección de conflictos en horarios"""
    generator = ScheduleGenerator(test_db)
    
    matrix1 = np.zeros((12, 6), dtype=int)
    matrix1[0][0] = 1001  # Lunes 7am
    
    matrix2 = np.zeros((12, 6), dtype=int)
    matrix2[0][0] = 2001  # Lunes 7am - CONFLICTO
    
    matrix3 = np.zeros((12, 6), dtype=int)
    matrix3[1][0] = 2001  # Lunes 8am - Sin conflicto
    
    assert generator.has_conflict(matrix1, matrix2) == True
    assert generator.has_conflict(matrix1, matrix3) == False

def test_format_schedule_matrix(test_db):
    """Test formateo de matriz a texto"""
    generator = ScheduleGenerator(test_db)
    
    matrix = np.zeros((12, 6), dtype=int)
    matrix[0][0] = 1001
    matrix[1][0] = 1001
    matrix[5][2] = 2001
    
    codes = [
        ("Cálculo I", 1001, "Dr. Juan Pérez"),
        ("Física I", 2001, "Dra. María García")
    ]
    
    result = generator.format_schedule_matrix(matrix, codes)
    
    assert len(result) == 12
    assert len(result[0]) == 6
    assert result[0][0] == "Cálculo I"
    assert result[1][0] == "Cálculo I"
    assert result[5][2] == "Física I"
    assert result[0][1] == ""

# Tests de generación de horarios
def test_generate_schedules_single_subject(test_db):
    """Test generación con una sola materia"""
    generator = ScheduleGenerator(test_db)
    from app.routers.schedule import FilteredCourses, SubjectPreference
    
    filters = FilteredCourses(
        preferencias={
            "Programación I": SubjectPreference(profesores=[], codes=[])
        },
        freetime={}
    )
    
    schedules = generator.generate_schedules(filters)
    
    assert len(schedules) == 1
    assert len(schedules[0][1]) == 1  # Solo un curso

def test_generate_schedules_multiple_subjects(test_db):
    """Test generación con múltiples materias"""
    generator = ScheduleGenerator(test_db)
    from app.routers.schedule import FilteredCourses, SubjectPreference
    
    filters = FilteredCourses(
        preferencias={
            "Cálculo I": SubjectPreference(profesores=[], codes=[]),
            "Física I": SubjectPreference(profesores=[], codes=[])
        },
        freetime={}
    )
    
    schedules = generator.generate_schedules(filters)
    
    # Deberían existir múltiples combinaciones
    assert len(schedules) >= 2
    
    # Cada horario debe tener 2 materias
    for matrix, codes in schedules:
        assert len(codes) == 2

def test_generate_schedules_with_teacher_preference(test_db):
    """Test generación con preferencia de profesor"""
    generator = ScheduleGenerator(test_db)
    from app.routers.schedule import FilteredCourses, SubjectPreference
    
    filters = FilteredCourses(
        preferencias={
            "Cálculo I": SubjectPreference(profesores=["Dr. Juan Pérez"], codes=[])
        },
        freetime={}
    )
    
    schedules = generator.generate_schedules(filters)
    
    assert len(schedules) == 1
    assert schedules[0][1][0][2] == "Dr. Juan Pérez"

def test_generate_schedules_with_code_preference(test_db):
    """Test generación con preferencia de código"""
    generator = ScheduleGenerator(test_db)
    from app.routers.schedule import FilteredCourses, SubjectPreference
    
    filters = FilteredCourses(
        preferencias={
            "Física I": SubjectPreference(profesores=[], codes=[2002])
        },
        freetime={}
    )
    
    schedules = generator.generate_schedules(filters)
    
    assert len(schedules) == 1
    assert schedules[0][1][0][1] == 2002

def test_generate_schedules_with_freetime(test_db):
    """Test generación respetando tiempos libres"""
    generator = ScheduleGenerator(test_db)
    from app.routers.schedule import FilteredCourses, SubjectPreference
    
    # Programación I es viernes 9-13 (horas 9, 10, 11, 12)
    # Solicitar viernes 9-13 libre debería eliminar esta opción
    filters = FilteredCourses(
        preferencias={
            "Programación I": SubjectPreference(profesores=[], codes=[])
        },
        freetime={
            "friday": [9, 10, 11, 12]
        }
    )
    
    schedules = generator.generate_schedules(filters)
    
    # No debería haber horarios disponibles
    assert len(schedules) == 0

def test_generate_schedules_freetime_not_affecting(test_db):
    """Test que tiempo libre no afecte si no hay conflicto"""
    generator = ScheduleGenerator(test_db)
    from app.routers.schedule import FilteredCourses, SubjectPreference
    
    # Cálculo I código 1001 es lunes/miércoles 7-9
    # Pedir libre martes 10-12 no debería afectar
    filters = FilteredCourses(
        preferencias={
            "Cálculo I": SubjectPreference(profesores=[], codes=[1001])
        },
        freetime={
            "tuesday": [10, 11, 12]
        }
    )
    
    schedules = generator.generate_schedules(filters)
    
    assert len(schedules) == 1

def test_generate_schedules_different_preferences_per_subject(test_db):
    """Test con diferentes preferencias por materia"""
    generator = ScheduleGenerator(test_db)
    from app.routers.schedule import FilteredCourses, SubjectPreference
    
    filters = FilteredCourses(
        preferencias={
            "Cálculo I": SubjectPreference(profesores=["Dr. Juan Pérez"], codes=[]),
            "Física I": SubjectPreference(profesores=[], codes=[2002])
        },
        freetime={}
    )
    
    schedules = generator.generate_schedules(filters)
    
    assert len(schedules) >= 1
    
    # Verificar que se cumplan las preferencias
    for matrix, codes in schedules:
        calculo_course = next(c for c in codes if c[0] == "Cálculo I")
        fisica_course = next(c for c in codes if c[0] == "Física I")
        
        assert calculo_course[2] == "Dr. Juan Pérez"
        assert fisica_course[1] == 2002

def test_generate_schedules_missing_subject(test_db):
    """Test error cuando falta una materia solicitada"""
    generator = ScheduleGenerator(test_db)
    from app.routers.schedule import FilteredCourses, SubjectPreference
    
    filters = FilteredCourses(
        preferencias={
            "Materia Inexistente": SubjectPreference(profesores=[], codes=[])
        },
        freetime={}
    )
    
    with pytest.raises(ValueError, match="No se encontraron cursos"):
        generator.generate_schedules(filters)

def test_generate_schedules_no_valid_combinations(test_db):
    """Test cuando no hay combinaciones válidas"""
    generator = ScheduleGenerator(test_db)
    from app.routers.schedule import FilteredCourses, SubjectPreference
    
    # Pedir todo el día libre en todos los días
    filters = FilteredCourses(
        preferencias={
            "Cálculo I": SubjectPreference(profesores=[], codes=[])
        },
        freetime={
            "monday": list(range(7, 19)),
            "tuesday": list(range(7, 19)),
            "wednesday": list(range(7, 19)),
            "thursday": list(range(7, 19)),
            "friday": list(range(7, 19))
        }
    )
    
    schedules = generator.generate_schedules(filters)
    
    assert len(schedules) == 0

# Tests del endpoint
def test_endpoint_basic_request():
    """Test endpoint con solicitud básica"""
    payload = {
        "preferencias": {
            "Cálculo I": {
                "profesores": [],
                "codes": []
            }
        },
        "freetime": {}
    }
    
    response = client.post("/generate-schedules", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["schedule_number"] == 1
    assert len(data[0]["courses"]) >= 1

def test_endpoint_with_teacher_preference():
    """Test endpoint con preferencia de profesor"""
    payload = {
        "preferencias": {
            "Física I": {
                "profesores": ["Dr. Carlos López"],
                "codes": []
            }
        },
        "freetime": {}
    }
    
    response = client.post("/generate-schedules", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    for schedule in data:
        for course in schedule["courses"]:
            if course["subject"] == "Física I":
                assert course["teacher_name"] == "Dr. Carlos López"

def test_endpoint_with_code_preference():
    """Test endpoint con preferencia de código"""
    payload = {
        "preferencias": {
            "Cálculo I": {
                "profesores": [],
                "codes": [1002]
            }
        },
        "freetime": {}
    }
    
    response = client.post("/generate-schedules", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    for schedule in data:
        for course in schedule["courses"]:
            if course["subject"] == "Cálculo I":
                assert course["code"] == 1002

def test_endpoint_with_freetime():
    """Test endpoint con tiempo libre"""
    payload = {
        "preferencias": {
            "Programación I": {
                "profesores": [],
                "codes": []
            }
        },
        "freetime": {
            "friday": [9, 10, 11, 12]
        }
    }
    
    response = client.post("/generate-schedules", json=payload)
    
    # Debería retornar 404 porque Programación I es viernes 9-13
    assert response.status_code == 404

def test_endpoint_multiple_subjects_different_preferences():
    """Test endpoint con múltiples materias y diferentes preferencias"""
    payload = {
        "preferencias": {
            "Cálculo I": {
                "profesores": ["Dr. Juan Pérez"],
                "codes": [1002]  # UNION: Dr. Juan Pérez O código 1002
            },
            "Física I": {
                "profesores": [],
                "codes": [2002]
            },
            "Programación I": {
                "profesores": [],
                "codes": []
            }
        },
        "freetime": {
            "monday": [12, 13]
        }
    }
    
    response = client.post("/generate-schedules", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verificar que todos los horarios cumplan las preferencias
    for schedule in data:
        assert len(schedule["courses"]) == 3
        
        calculo_found = False
        for course in schedule["courses"]:
            if course["subject"] == "Cálculo I":
                calculo_found = True
                # Debe ser Dr. Juan Pérez O código 1002
                is_valid = (
                    course["teacher_name"] == "Dr. Juan Pérez" or 
                    course["code"] == 1002
                )
                assert is_valid, f"Cálculo I debe cumplir: Dr. Juan Pérez O código 1002"
            elif course["subject"] == "Física I":
                assert course["code"] == 2002
        
        assert calculo_found, "Debe incluir Cálculo I"

def test_endpoint_invalid_subject():
    """Test endpoint con materia inexistente"""
    payload = {
        "preferencias": {
            "Materia Falsa": {
                "profesores": [],
                "codes": []
            }
        },
        "freetime": {}
    }
    
    response = client.post("/generate-schedules", json=payload)
    
    assert response.status_code == 400
    assert "No se encontraron cursos" in response.json()["detail"]

def test_endpoint_empty_preferences():
    """Test endpoint sin preferencias"""
    payload = {
        "preferencias": {},
        "freetime": {}
    }
    
    response = client.post("/generate-schedules", json=payload)
    
    # Debería retornar 404 o 400
    assert response.status_code in [400, 404]

def test_endpoint_response_structure():
    """Test estructura completa de respuesta"""
    payload = {
        "preferencias": {
            "Cálculo I": {
                "profesores": [],
                "codes": []
            }
        },
        "freetime": {}
    }
    
    response = client.post("/generate-schedules", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verificar estructura de cada horario
    for schedule in data:
        assert "schedule_number" in schedule
        assert "courses" in schedule
        assert "schedule_matrix" in schedule
        assert "hour_labels" in schedule
        assert "day_labels" in schedule
        
        # Verificar dimensiones de matriz
        assert len(schedule["schedule_matrix"]) == 12  # 12 horas
        assert len(schedule["schedule_matrix"][0]) == 6  # 5 días
        
        # Verificar labels
        assert len(schedule["hour_labels"]) == 12
        assert len(schedule["day_labels"]) == 6
        
        # Verificar estructura de cursos
        for course in schedule["courses"]:
            assert "subject" in course
            assert "code" in course
            assert "teacher_name" in course
            assert "schedules" in course
            
            for sched in course["schedules"]:
                assert "day" in sched
                assert "start_time" in sched
                assert "end_time" in sched

def test_endpoint_union_filter():
    """Test endpoint con filtro UNION (profesor O código)"""
    payload = {
        "preferencias": {
            "Física I": {
                "profesores": ["Dr. Juan Pérez"],
                "codes": [2002]  # UNION: cursos del Dr. Juan Pérez O código 2002
            }
        },
        "freetime": {}
    }
    
    response = client.post("/generate-schedules", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Debería haber horarios con cualquiera de los dos cursos
    # Código 2001 (Dr. Juan Pérez) o código 2002 (Dr. Carlos López)
    codes_found = set()
    teachers_found = set()
    
    for schedule in data:
        for course in schedule["courses"]:
            if course["subject"] == "Física I":
                codes_found.add(course["code"])
                teachers_found.add(course["teacher_name"])
    
    # Debe incluir al menos uno de los dos
    assert 2001 in codes_found or 2002 in codes_found
    # Puede incluir ambos en diferentes horarios
    assert len(codes_found) >= 1

def test_health_check_endpoint():
    """Test endpoint de health check"""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"