# test_courses.py
import pytest
from tests.test_database import TestingSessionLocal, client

from app.models.teacher import Teacher
from app.models.course import Course

@pytest.fixture(scope="session")
def test_db():
    db = TestingSessionLocal()
    yield db
    db.close()

@pytest.fixture
def sample_data(test_db):
    """Fixture que limpia tablas y crea datos de prueba"""

    # Limpiar tablas (primero Course porque tiene FK a Teacher)
    test_db.query(Course).delete()
    test_db.query(Teacher).delete()
    test_db.commit()

    # Crear profesores
    teacher1 = Teacher(id=100, full_name="María González")
    teacher2 = Teacher(id=200, full_name="Juan Pérez")
    teacher3 = Teacher(id=300, full_name="Ana Martínez")

    test_db.add_all([teacher1, teacher2, teacher3])
    test_db.commit()

    # Crear cursos
    courses = [
        Course(id=101, subject="Matemáticas", code=2345, teacher_id=100),
        Course(id=102, subject="Matemáticas", code=1234, teacher_id=100),
        Course(id=103, subject="Matemáticas Avanzadas", code=1235, teacher_id=200),
        Course(id=104, subject="Física", code=1236, teacher_id=200),
        Course(id=105, subject="Física", code=1237, teacher_id=300),
        Course(id=106, subject="Programación", code=1238, teacher_id=300),
        Course(id=107, subject="Química", code=1239, teacher_id=100),
        Course(id=108, subject="Biología", code=1230, teacher_id=200),
    ]

    test_db.add_all(courses)
    test_db.commit()

    return {
        "teachers": [teacher1, teacher2, teacher3],
        "courses": courses
    }



# ==================== TESTS PARA /search/subjects ====================

def test_search_subjects_basic(sample_data):
    """Test 1: Búsqueda básica de materias con prefijo"""
    response = client.get("/courses/search/subjects?query=Mat")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # "Matemáticas" y "Matemáticas Avanzadas"
    assert any(s["subject"] == "Matemáticas" for s in data)
    assert any(s["subject"] == "Matemáticas Avanzadas" for s in data)

def test_search_subjects_case_insensitive(sample_data):
    """Test 2: Búsqueda case-insensitive"""
    response = client.get("/courses/search/subjects?query=mat")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    response2 = client.get("/courses/search/subjects?query=MAT")
    assert response2.status_code == 200
    data2 = response2.json()
    assert len(data2) == 2

def test_search_subjects_exact_match(sample_data):
    """Test 3: Búsqueda con coincidencia exacta"""
    response = client.get("/courses/search/subjects?query=Física")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["subject"] == "Física"

def test_search_subjects_count_correct(sample_data):
    """Test 4: Verificar que el conteo de cursos sea correcto"""
    response = client.get("/courses/search/subjects?query=Mat")
    assert response.status_code == 200
    data = response.json()
    
    matematicas = next(s for s in data if s["subject"] == "Matemáticas")
    assert matematicas["count"] == 2  # MAT101 y MAT102

def test_search_subjects_no_results(sample_data):
    """Test 5: Búsqueda sin resultados"""
    response = client.get("/courses/search/subjects?query=Xyz")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0

def test_search_subjects_single_character(sample_data):
    """Test 6: Búsqueda con un solo carácter"""
    response = client.get("/courses/search/subjects?query=P")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["subject"] == "Programación"

def test_search_subjects_missing_query_param(sample_data):
    """Test 7: Petición sin parámetro query (debe fallar)"""
    response = client.get("/courses/search/subjects")
    assert response.status_code == 422  # Unprocessable Entity

def test_search_subjects_empty_query(sample_data):
    """Test 8: Búsqueda con query vacío (debe fallar por min_length=1)"""
    response = client.get("/courses/search/subjects?query=")
    assert response.status_code == 422

def test_search_subjects_prefix_only(test_db):
    """Test 9: Verificar que solo busca por prefijo, no en medio"""
    # Agregar un curso con "Análisis Matemático" que contiene "Mat" pero no empieza con "Mat"
    course = Course(subject="Análisis Matemático", code="ANA101", teacher_id=1)
    test_db.add(course)
    test_db.commit()
    test_db.close()
    
    response = client.get("/courses/search/subjects?query=Mat")
    data = response.json()
    # No debe incluir "Análisis Matemático" porque no empieza con "Mat"
    assert not any(s["subject"] == "Análisis Matemático" for s in data)

def test_search_subjects_limit_20(test_db):
    """Test 10: Verificar límite de 20 resultados"""
    # Crear 25 materias diferentes
    for i in range(25):
        course = Course(subject=f"Test{i:02d}", code=f"TST{i:03d}", teacher_id=1)
        test_db.add(course)
    test_db.commit()
    test_db.close()
    
    response = client.get("/courses/search/subjects?query=Test")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 20  # Máximo 20 resultados


# ==================== TESTS PARA /codes ====================

def test_get_codes_by_subject_success(sample_data):
    """Test 11: Obtener códigos por materia exitosamente"""
    response = client.get("/courses/search/codes?subject=Matemáticas")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    codes = [c["code"] for c in data]
    assert 1234 in codes
    assert 2345 in codes

def test_get_codes_ordered(sample_data):
    """Test 12: Verificar que los códigos estén ordenados"""
    response = client.get("/courses/search/codes?subject=Matemáticas")
    assert response.status_code == 200
    data = response.json()
    codes = [c["code"] for c in data]
    assert codes == sorted(codes)

def test_get_codes_includes_course_id(sample_data):
    """Test 13: Verificar que se incluya el course_id"""
    response = client.get("/courses/search/codes?subject=Física")
    assert response.status_code == 200
    data = response.json()
    assert all("course_id" in c for c in data)
    assert all("code" in c for c in data)

def test_get_codes_subject_not_found(sample_data):
    """Test 14: Materia no existente debe retornar 404"""
    response = client.get("/courses/search/codes?subject=Inexistente")
    assert response.status_code == 404
    assert "No se encontraron cursos" in response.json()["detail"]

def test_get_codes_case_sensitive(sample_data):
    """Test 15: Búsqueda de códigos es case-sensitive para materia"""
    response = client.get("/courses/search/codes?subject=matemáticas")
    # Debe fallar porque "matemáticas" != "Matemáticas"
    assert response.status_code == 404

def test_get_codes_missing_subject_param(sample_data):
    """Test 16: Petición sin parámetro subject"""
    response = client.get("/courses/search/codes")
    assert response.status_code == 422


# ==================== TESTS PARA /teachers ====================

def test_get_teachers_by_subject_success(sample_data):
    """Test 17: Obtener profesores por materia exitosamente"""
    response = client.get("/courses/search/teachers?subject=Matemáticas")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["full_name"] == "María González"
    assert data[0]["id"] == 100

def test_get_teachers_multiple_teachers(sample_data):
    """Test 18: Materia con múltiples profesores"""
    # Agregar otro curso de Física con profesor diferente
    # Ya existe Física con teacher_id=2 y teacher_id=3
    response = client.get("/courses/search/teachers?subject=Física")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # Juan Pérez y Ana Martínez
    teacher_names = [t["full_name"] for t in data]
    assert "Juan Pérez" in teacher_names
    assert "Ana Martínez" in teacher_names

def test_get_teachers_ordered_by_name(sample_data):
    """Test 19: Verificar que los profesores estén ordenados alfabéticamente"""
    response = client.get("/courses/search/teachers?subject=Física")
    assert response.status_code == 200
    data = response.json()
    names = [t["full_name"] for t in data]
    assert names == sorted(names)

def test_get_teachers_subject_not_found(sample_data):
    """Test 20: Materia sin profesores debe retornar 404"""
    response = client.get("/courses/search/teachers?subject=Inexistente")
    assert response.status_code == 404
    assert "No se encontraron profesores" in response.json()["detail"]


# ==================== TESTS ADICIONALES ====================

def test_get_teachers_distinct_check(sample_data):
    """Test 21 (Bonus): Verificar que un profesor no se repita si tiene múltiples cursos de la misma materia"""
    # María González tiene 2 cursos de Matemáticas (MAT101 y MAT102)
    response = client.get("/courses/search/teachers?subject=Matemáticas")
    assert response.status_code == 200
    data = response.json()
    # Debe aparecer solo una vez
    assert len(data) == 1
    assert data[0]["full_name"] == "María González"

def test_search_subjects_special_characters(test_db):
    """Test 22 (Bonus): Búsqueda con caracteres especiales"""
    course = Course(subject="Matemáticas & Lógica", code=1784, teacher_id=1)
    test_db.add(course)
    test_db.commit()
    test_db.close()
    
    response = client.get("/courses/search/subjects?query=Matemáticas")
    assert response.status_code == 200
    data = response.json()
    subjects = [s["subject"] for s in data]
    assert "Matemáticas & Lógica" in subjects

def test_get_codes_single_course(sample_data):
    """Test 23 (Bonus): Materia con un solo curso"""
    response = client.get("/courses/search/codes?subject=Programación")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["code"] == 1238

def test_search_subjects_unicode(test_db):
    """Test 24 (Bonus): Búsqueda con caracteres unicode"""
    course = Course(subject="Ética", code="ETI101", teacher_id=1)
    test_db.add(course)
    test_db.commit()
    test_db.close()
    
    response = client.get("/courses/search/subjects?query=Éti")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1