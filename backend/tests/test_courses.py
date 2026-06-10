from tests.test_database import client

# ============================================================
# 1. Validaciones del campo "code"
# ============================================================

# 1.1 No puede recibir un código nulo
def test_failed_code_none():
    payload = {
        "subject": "IOT",
        "code": None,
        "teacher_name": "Alexander Jimenez",
        "schedules": [{"day": "Jueves", "start_time": "07:00", "end_time": "10:00"}]
    }
    resp = client.post("/courses/", json=payload)
    assert resp.status_code == 422


# 1.2 No puede ser igual a cero
def test_failed_code_zero():
    payload = {
        "subject": "IOT",
        "code": 0,
        "teacher_name": "Alexander Jimenez",
        "schedules": [{"day": "Jueves", "start_time": "07:00", "end_time": "10:00"}]
    }
    resp = client.post("/courses/", json=payload)
    assert resp.status_code == 422


# 1.3 No puede ser un número negativo
def test_failed_code_negative():
    payload = {
        "subject": "IOT",
        "code": -345,
        "teacher_name": "Alexander Jimenez",
        "schedules": [{"day": "Jueves", "start_time": "07:00", "end_time": "10:00"}]
    }
    resp = client.post("/courses/", json=payload)
    assert resp.status_code == 422


# 1.4 Debe tener 4 o 5 dígitos — 3 dígitos sigue siendo inválido
def test_invalid_code_length():
    payload = {
        "subject": "IOT",
        "code": 123,
        "teacher_name": "Alexander Jimenez",
        "schedules": [{"day": "Jueves", "start_time": "07:00", "end_time": "10:00"}]
    }
    resp = client.post("/courses/", json=payload)
    assert resp.status_code == 400
    assert resp.json()["detail"] == "El código debe ser un número de 4 o 5 dígitos."


# 1.5 No puede ser un valor no numérico
def test_invalid_code_not_numeric():
    payload = {
        "subject": "IOT",
        "code": "ABCD",
        "teacher_name": "Alexander Jimenez",
        "schedules": [{"day": "Lunes", "start_time": "09:00", "end_time": "11:00"}]
    }
    resp = client.post("/courses/", json=payload)
    assert resp.status_code == 422


# 1.6 No se puede duplicar el código
def test_duplicate_code():
    test_code = 7777

    check = client.get(f"/courses/{test_code}")
    if check.status_code == 200:
        client.delete(f"/courses/{check.json()['id']}")

    payload = {
        "subject": "IOT",
        "code": test_code,
        "teacher_name": "Camilo",
        "schedules": [{"day": "Lunes", "start_time": "07:00", "end_time": "09:00"}]
    }

    resp1 = client.post("/courses/", json=payload)
    assert resp1.status_code == 200

    resp2 = client.post("/courses/", json=payload)
    assert resp2.status_code == 400
    assert resp2.json()["detail"] == "El código del curso ya existe"


# ============================================================
# 2. Validaciones de "subject" y "teacher_name"
# ============================================================

# 2.1 Nombre del profesor vacío
def test_empty_teacher_name():
    payload = {
        "subject": "IOT",
        "code": 1234,
        "teacher_name": "",
        "schedules": [{"day": "Martes", "start_time": "08:00", "end_time": "10:00"}]
    }
    resp = client.post("/courses/", json=payload)
    assert resp.status_code == 422


# 2.2 Subject vacío
def test_empty_subject():
    payload = {
        "subject": "",
        "code": 1234,
        "teacher_name": "Juan Perez",
        "schedules": [{"day": "Lunes", "start_time": "07:00", "end_time": "09:00"}]
    }
    resp = client.post("/courses/", json=payload)
    assert resp.status_code == 422


# ============================================================
# 3. Validaciones de horarios
# ============================================================

# 3.1 Lista vacía de horarios
def test_no_schedules():
    payload = {
        "subject": "IOT",
        "code": 1234,
        "teacher_name": "Laura Martinez",
        "schedules": []
    }
    resp = client.post("/courses/", json=payload)
    assert resp.status_code == 422


# 3.2 Día inválido
def test_invalid_day():
    payload = {
        "subject": "IOT",
        "code": 1234,
        "teacher_name": "Pedro",
        "schedules": [{"day": "Domingo", "start_time": "10:00", "end_time": "12:00"}]
    }
    resp = client.post("/courses/", json=payload)
    assert resp.status_code == 400
    assert "no es válido" in resp.json()["detail"]


# 3.3 Orden inválido de horas
def test_invalid_time_order():
    payload = {
        "subject": "IOT",
        "code": "4444",
        "teacher_name": "Rosa",
        "schedules": [{"day": "Lunes", "start_time": "12:00", "end_time": "10:00"}]
    }
    resp = client.post("/courses/", json=payload)
    assert resp.status_code != 200


# ============================================================
# 4. Pruebas de CRUD existentes (OK)
# ============================================================

# 4.1 Creación exitosa
def test_successful_creation():
    payload = {
        "subject": "Matemáticas",
        "code": 2222,
        "teacher_name": "Mario Lopez",
        "schedules": [{"day": "Miercoles", "start_time": "08:00", "end_time": "10:00"}]
    }
    resp = client.post("/courses/", json=payload)
    data = resp.json()

    assert resp.status_code == 200
    assert data["course"]["subject"] == "Matemáticas"
    assert data["course"]["code"] == 2222
    assert len(data["course"]["schedules"]) == 1


# 4.2 Crear curso (duplicado con más validación)
def test_create_course():
    payload = {
        "subject": "IOT",
        "code": 3278,
        "teacher_name": "Alexander Jimenez",
        "schedules": [{"day": "Jueves", "start_time": "07:00", "end_time": "10:00"}]
    }
    response = client.post("/courses/", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["course"]["subject"] == "IOT"
    assert data["course"]["code"] == 3278
    assert len(data["course"]["schedules"]) == 1


# 4.3 Obtener curso
def test_get_course():
    response = client.get("/courses/1")
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == 1
    assert data["subject"] == "IOT"


# 4.4 Actualizar curso
def test_update_course():
    payload = {
        "subject": "IOT Avanzado",
        "code": 3279,
        "teacher_name": "Nuevo Profesor",
        "schedules": [{"day": "Lunes", "start_time": "10:00", "end_time": "13:00"}]
    }

    response = client.put("/courses/1", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["course"]["subject"] == "IOT Avanzado"
    assert data["course"]["code"] == 3279
    assert data["course"]["teacher_full_name"] == "Nuevo Profesor"
    assert len(data["course"]["schedules"]) == 1


# 4.5 Eliminar curso
def test_delete_course():
    response = client.delete("/courses/3")
    assert response.status_code == 200

    response = client.get("/courses/3")
    assert response.status_code == 404


# ============================================================
# 5. NUEVAS PRUEBAS (14)
# ============================================================

# 5.1 Subject con espacios y limpieza automática
def test_subject_trimmed():
    payload = {
        "subject": "   Fisica  ",
        "code": 5555,
        "teacher_name": "Luis Torres",
        "schedules": [{"day": "Martes", "start_time": "09:00", "end_time": "11:00"}]
    }
    resp = client.post("/courses/", json=payload)
    assert resp.status_code == 200
    assert resp.json()["course"]["subject"] == "Fisica"


# 5.2 Nombre de profesor con espacios
def test_teacher_name_trimmed():
    payload = {
        "subject": "Etica",
        "code": 6666,
        "teacher_name": "   Lucia   Ramos  ",
        "schedules": [{"day": "Viernes", "start_time": "11:00", "end_time": "12:00"}]
    }
    resp = client.post("/courses/", json=payload)
    assert resp.status_code == 200
    assert "Lucia Ramos" in resp.json()["course"]["teacher_full_name"]


# 5.3 Validar que no se permita duplicar nombre + horario en la misma semana
def test_schedule_conflict_same_teacher():
    payload1 = {
        "subject": "Robotica",
        "code": 8881,
        "teacher_name": "Carlos Ruiz",
        "schedules": [{"day": "Lunes", "start_time": "09:00", "end_time": "11:00"}]
    }
    payload2 = {
        "subject": "Robotica II",
        "code": 8882,
        "teacher_name": "Carlos Ruiz",
        "schedules": [{"day": "Lunes", "start_time": "10:00", "end_time": "12:00"}]
    }

    resp1 = client.post("/courses/", json=payload1)
    assert resp1.status_code == 200

    resp2 = client.post("/courses/", json=payload2)
    assert resp2.status_code in (400, 422)


# 5.4 Horarios con formato inválido
def test_invalid_time_format():
    payload = {
        "subject": "Termodinámica",
        "code": 9001,
        "teacher_name": "Miguel",
        "schedules": [{"day": "Martes", "start_time": "9am", "end_time": "10:00"}]
    }
    resp = client.post("/courses/", json=payload)
    assert resp.status_code in (400, 422)


# 5.5 Intentar obtener curso inexistente
def test_get_nonexistent_course():
    resp = client.get("/courses/999999")
    assert resp.status_code == 404


# 5.6 Intentar borrar curso inexistente
def test_delete_nonexistent_course():
    resp = client.delete("/courses/999999")
    assert resp.status_code == 404


# 5.7 Intentar actualizar curso inexistente
def test_update_nonexistent_course():
    payload = {
        "subject": "ABC",
        "code": 4444,
        "teacher_name": "Profesor X",
        "schedules": [{"day": "Lunes", "start_time": "09:00", "end_time": "10:00"}]
    }
    resp = client.put("/courses/999999", json=payload)
    assert resp.status_code == 404


# 5.8 Validar que un curso pueda tener múltiples horarios válidos
def test_multiple_schedules_creation():
    payload = {
        "subject": "Química",
        "code": 5556,
        "teacher_name": "Ana",
        "schedules": [
            {"day": "Lunes", "start_time": "07:00", "end_time": "09:00"},
            {"day": "Miercoles", "start_time": "10:00", "end_time": "12:00"}
        ]
    }
    resp = client.post("/courses/", json=payload)
    assert resp.status_code == 200
    assert len(resp.json()["course"]["schedules"]) == 2


# 5.9 Validar que los días aceptados sean estrictos
def test_day_case_sensitive():
    payload = {
        "subject": "Biología",
        "code": 1235,
        "teacher_name": "Marina",
        "schedules": [{"day": "lunes", "start_time": "08:00", "end_time": "09:00"}]
    }
    resp = client.post("/courses/", json=payload)
    assert resp.status_code == 400


# 5.10 Validar que start_time != end_time
def test_equal_start_end_time():
    payload = {
        "subject": "Historia",
        "code": 4321,
        "teacher_name": "Sergio",
        "schedules": [{"day": "Martes", "start_time": "08:00", "end_time": "08:00"}]
    }
    resp = client.post("/courses/", json=payload)
    assert resp.status_code == 400


# 5.11 Validar materia muy larga
def test_subject_too_long():
    payload = {
        "subject": "A" * 300,
        "code": 9991,
        "teacher_name": "Juan",
        "schedules": [{"day": "Viernes", "start_time": "08:00", "end_time": "09:00"}]
    }
    resp = client.post("/courses/", json=payload)
    assert resp.status_code in (400, 422)


# 5.12 Validar profesor muy largo
def test_teacher_name_too_long():
    payload = {
        "subject": "Arte",
        "code": 9992,
        "teacher_name": "A" * 300,
        "schedules": [{"day": "Martes", "start_time": "07:00", "end_time": "08:00"}]
    }
    resp = client.post("/courses/", json=payload)
    assert resp.status_code in (400, 422)


# 5.13 Código de 5 dígitos ahora es válido
def test_code_more_than_4_digits():
    payload = {
        "subject": "Geografía",
        "code": 12345,
        "teacher_name": "Luis",
        "schedules": [{"day": "Viernes", "start_time": "07:00", "end_time": "09:00"}]
    }
    resp = client.post("/courses/", json=payload)
    assert resp.status_code == 200


# 5.14 Validar que se rechacen horarios cruzados dentro del mismo curso
def test_internal_schedule_overlap():
    payload = {
        "subject": "Programación",
        "code": 3456,
        "teacher_name": "Carlos",
        "schedules": [
            {"day": "Jueves", "start_time": "07:00", "end_time": "09:00"},
            {"day": "Jueves", "start_time": "08:00", "end_time": "10:00"}
        ]
    }
    resp = client.post("/courses/", json=payload)
    assert resp.status_code in (400, 422)

# ============================
# A. UPDATE (20 tests)
# ============================

def test_update_only_subject():
    payload = {"subject": "Nuevo Subject", "code": 1234, "teacher_name": "Mario",
               "schedules": [{"day": "Lunes", "start_time": "07:00", "end_time": "09:00"}]}
    resp = client.put("/courses/1", json=payload)
    assert resp.status_code == 200
    assert resp.json()["course"]["subject"] == "Nuevo Subject"


def test_update_only_teacher():
    payload = {"subject": "IOT", "code": 1234, "teacher_name": "Nuevo Docente",
               "schedules": [{"day": "Lunes", "start_time": "09:00", "end_time": "11:00"}]}
    resp = client.put("/courses/1", json=payload)
    assert resp.status_code == 200
    assert resp.json()["course"]["teacher_full_name"] == "Nuevo Docente"


def test_update_same_code():
    get = client.get("/courses/1")
    assert get.status_code == 200

    course = get.json()
    payload = {
        "subject": "IOT X",
        "code": course["code"],
        "teacher_name": course["teacher_full_name"],
        "schedules": course["schedules"]
    }

    resp = client.put(f"/courses/{course['id']}", json=payload)
    assert resp.status_code == 200


def test_update_with_duplicate_code():
    payload1 = {
        "subject": "Curso1",
        "code": 5511,
        "teacher_name": "Ana",
        "schedules": [{"day": "Martes", "start_time": "08:00", "end_time": "10:00"}]
    }
    payload2 = {
        "subject": "Curso2",
        "code": 5522,
        "teacher_name": "Luis",
        "schedules": [{"day": "Jueves", "start_time": "09:00", "end_time": "11:00"}]
    }

    c1 = client.post("/courses/", json=payload1).json()["course"]
    c2 = client.post("/courses/", json=payload2).json()["course"]

    payload2["code"] = 5511
    resp = client.put(f"/courses/{c2['id']}", json=payload2)
    assert resp.status_code == 400


def test_update_teacher_empty():
    resp = client.put("/courses/1", json={
        "subject": "Nuevo",
        "code": 1200,
        "teacher_name": "",
        "schedules": [{"day": "Viernes", "start_time": "07:00", "end_time": "09:00"}]
    })
    assert resp.status_code == 422


def test_update_subject_empty():
    resp = client.put("/courses/1", json={
        "subject": "",
        "code": 1200,
        "teacher_name": "Jose",
        "schedules": [{"day": "Viernes", "start_time": "07:00", "end_time": "09:00"}]
    })
    assert resp.status_code == 422


def test_update_empty_schedules():
    resp = client.put("/courses/1", json={
        "subject": "Test",
        "code": 1200,
        "teacher_name": "Carlos",
        "schedules": []
    })
    assert resp.status_code == 422


def test_update_invalid_day():
    resp = client.put("/courses/1", json={
        "subject": "Test",
        "code": 1200,
        "teacher_name": "Carlos",
        "schedules": [{"day": "Domingo", "start_time": "08:00", "end_time": "10:00"}]
    })
    assert resp.status_code == 400


def test_update_invalid_time_order():
    resp = client.put("/courses/1", json={
        "subject": "Test",
        "code": 1200,
        "teacher_name": "Carlos",
        "schedules": [{"day": "Lunes", "start_time": "10:00", "end_time": "09:00"}]
    })
    assert resp.status_code != 200


def test_update_schedule_conflict_other_course():
    p1 = client.post("/courses/", json={
        "subject": "C1", "code": 9911, "teacher_name": "AAA",
        "schedules": [{"day": "Martes", "start_time": "09:00", "end_time": "11:00"}]
    }).json()["course"]

    p2 = client.post("/courses/", json={
        "subject": "C2", "code": 9912, "teacher_name": "AAA",
        "schedules": [{"day": "Martes", "start_time": "11:00", "end_time": "13:00"}]
    }).json()["course"]

    resp = client.put(f"/courses/{p2['id']}", json={
        "subject": "C2", "code": 9912, "teacher_name": "AAA",
        "schedules": [{"day": "Martes", "start_time": "10:00", "end_time": "12:00"}]
    })
    assert resp.status_code in (400, 422)


def test_update_multiple_schedules():
    resp = client.put("/courses/1", json={
        "subject": "Multi",
        "code": 1300,
        "teacher_name": "Pedro",
        "schedules": [
            {"day": "Lunes", "start_time": "07:00", "end_time": "09:00"},
            {"day": "Miercoles", "start_time": "10:00", "end_time": "12:00"}
        ]
    })
    assert resp.status_code == 200


def test_update_invalid_time_format():
    resp = client.put("/courses/1", json={
        "subject": "Formato",
        "code": 1301,
        "teacher_name": "Luis",
        "schedules": [{"day": "Martes", "start_time": "9am", "end_time": "10:00"}]
    })
    assert resp.status_code in (400, 422)


def test_update_day_case_sensitive():
    resp = client.put("/courses/1", json={
        "subject": "Dia",
        "code": 1302,
        "teacher_name": "Maria",
        "schedules": [{"day": "lunes", "start_time": "08:00", "end_time": "09:00"}]
    })
    assert resp.status_code == 400


def test_update_invalid_id_string():
    resp = client.put("/courses/abc", json={
        "subject": "X",
        "code": 1234,
        "teacher_name": "Y",
        "schedules": [{"day": "Lunes", "start_time": "08:00", "end_time": "10:00"}]
    })
    assert resp.status_code == 422


def test_update_invalid_id_negative():
    resp = client.put("/courses/-1", json={
        "subject": "X",
        "code": 1234,
        "teacher_name": "Y",
        "schedules": [{"day": "Lunes", "start_time": "08:00", "end_time": "10:00"}]
    })
    assert resp.status_code == 422


def test_update_internal_overlap():
    resp = client.put("/courses/1", json={
        "subject": "Test",
        "code": 4444,
        "teacher_name": "Z",
        "schedules": [
            {"day": "Lunes", "start_time": "08:00", "end_time": "10:00"},
            {"day": "Lunes", "start_time": "09:00", "end_time": "11:00"}
        ]
    })
    assert resp.status_code in (400, 422)


def test_update_teacher_too_long():
    resp = client.put("/courses/1", json={
        "subject": "Test",
        "code": 4445,
        "teacher_name": "A" * 300,
        "schedules": [{"day": "Lunes", "start_time": "07:00", "end_time": "08:00"}]
    })
    assert resp.status_code in (400, 422)


def test_update_subject_too_long():
    resp = client.put("/courses/1", json={
        "subject": "A" * 300,
        "code": 4446,
        "teacher_name": "Pedro",
        "schedules": [{"day": "Viernes", "start_time": "07:00", "end_time": "09:00"}]
    })
    assert resp.status_code in (400, 422)


def test_update_code_more_than_5_digits():
    resp = client.put("/courses/1", json={
        "subject": "Geo",
        "code": 123456,
        "teacher_name": "Sofia",
        "schedules": [{"day": "Viernes", "start_time": "07:00", "end_time": "09:00"}]
    })
    assert resp.status_code == 400


def test_update_empty_body():
    resp = client.put("/courses/1", json={})
    assert resp.status_code in (400, 422)


# ============================
# B. DELETE (5 tests)
# ============================

def test_delete_and_check_list():
    c = client.post("/courses/", json={
        "subject": "ToDelete",
        "code": 7771,
        "teacher_name": "X",
        "schedules": [{"day": "Lunes", "start_time": "07:00", "end_time": "09:00"}]
    }).json()["course"]

    del_resp = client.delete(f"/courses/{c['id']}")
    assert del_resp.status_code == 200

    list_resp = client.get("/courses/")
    assert all(item["id"] != c["id"] for item in list_resp.json())


def test_delete_twice():
    c = client.post("/courses/", json={
        "subject": "Twice",
        "code": 7772,
        "teacher_name": "Y",
        "schedules": [{"day": "Martes", "start_time": "07:00", "end_time": "09:00"}]
    }).json()["course"]

    first = client.delete(f"/courses/{c['id']}")
    second = client.delete(f"/courses/{c['id']}")

    assert first.status_code == 200
    assert second.status_code == 404


def test_delete_invalid_id_string():
    resp = client.delete("/courses/abc")
    assert resp.status_code == 422


def test_delete_invalid_id_negative():
    resp = client.delete("/courses/-10")
    assert resp.status_code == 422


def test_delete_invalid_id_large():
    resp = client.delete("/courses/99999999999")
    assert resp.status_code in (404, 422)


# ============================
# C. GET (5 tests)
# ============================

def test_get_all_courses():
    resp = client.get("/courses/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_invalid_id_string():
    resp = client.get("/courses/abc")
    assert resp.status_code == 422


def test_get_invalid_id_negative():
    resp = client.get("/courses/-1")
    assert resp.status_code == 422


def test_get_after_delete():
    c = client.post("/courses/", json={
        "subject": "Temp",
        "code": 7773,
        "teacher_name": "X",
        "schedules": [{"day": "Viernes", "start_time": "07:00", "end_time": "09:00"}]
    }).json()["course"]

    client.delete(f"/courses/{c['id']}")
    resp = client.get(f"/courses/{c['id']}")
    assert resp.status_code == 404


def test_get_large_id():
    resp = client.get("/courses/99999999999")
    assert resp.status_code in (404, 422)


# ============================
# D. Validación de 5 dígitos
# ============================

def test_valid_5_digit_code():
    payload = {
        "subject": "Redes Avanzadas",
        "code": 10001,
        "teacher_name": "Juan Prueba",
        "schedules": [{"day": "Lunes", "start_time": "07:00", "end_time": "09:00"}]
    }
    resp = client.post("/courses/", json=payload)
    assert resp.status_code == 200
    assert resp.json()["course"]["code"] == 10001
