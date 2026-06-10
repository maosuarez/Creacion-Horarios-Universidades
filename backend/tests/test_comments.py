import pytest
from tests.test_database import client

@pytest.fixture
def test_user_auth():
    """Datos de usuario para tests (cumple con tus validaciones)"""
    return {
        "name": "Test User",
        "email": "test-auth@example.com",
        "password": "Password123!",  # Cumple: mayúscula + número
        "bio": "Test bio",
        "role": "viewer"
    }

@pytest.fixture
def second_user_data():
    """Datos de segundo usuario para tests de autorización"""
    return {
        "name": "Second User",
        "email": "second@example.com",
        "password": "Password123",
        "bio": "Second bio",
        "role": "viewer"
    }

@pytest.fixture
def authenticated_client(test_user_auth):
    """Cliente autenticado con token"""
    # Registrar usuario
    client.post("/auth/signup", json=test_user_auth)
    
    # Login para obtener token
    response = client.post("/auth/login", data={
        "grant_type": "password",
        "username": test_user_auth["email"],
        "password": test_user_auth["password"]
    })
    token = response.json()["access_token"]
    
    return {
        "client": client,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
        "user_data": test_user_auth
    }

@pytest.fixture
def second_authenticated_client(second_user_data):
    """Segundo cliente autenticado para tests de autorización"""
    # Registrar segundo usuario
    client.post("/auth/signup", json=second_user_data)
    
    # Login para obtener token
    response = client.post("/auth/login", data={
        "grant_type": "password",
        "username": second_user_data["email"],
        "password": second_user_data["password"]
    })
    token = response.json()["access_token"]
    
    return {
        "client": client,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
        "user_data": second_user_data
    }

# -------------------------
# Tests de creación de comentarios
# -------------------------

def test_create_comment_success(authenticated_client):
    """Test de creación exitosa de comentario"""
    response = client.post(
        "/comments/",
        headers=authenticated_client["headers"],
        json={
            "content": "Este es un comentario de prueba",
            "course_id": None
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "Este es un comentario de prueba"
    assert "id" in data
    assert "profile_id" in data
    assert "created_at" in data
    assert data["author_name"] == authenticated_client["user_data"]["name"]

    client.delete("/comments/me/all", headers=authenticated_client["headers"])

def test_create_comment_with_course_id(authenticated_client):
    """Test de creación de comentario asociado a un curso"""
    response = client.post(
        "/comments/",
        headers=authenticated_client["headers"],
        json={
            "content": "Comentario sobre el curso",
            "course_id": 1
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["course_id"] == 1

    client.delete("/comments/me/all", headers=authenticated_client["headers"])

def test_create_comment_without_auth():
    """Test de creación sin autenticación debe fallar"""
    response = client.post(
        "/comments/",
        json={"content": "Comentario sin auth"}
    )
    
    assert response.status_code == 401

def test_create_comment_empty_content(authenticated_client):
    """Test de creación con contenido vacío debe fallar"""
    response = client.post(
        "/comments/",
        headers=authenticated_client["headers"],
        json={"content": ""}
    )
    
    assert response.status_code == 422

def test_create_comment_too_long(authenticated_client):
    """Test de creación con contenido > 500 caracteres debe fallar"""
    response = client.post(
        "/comments/",
        headers=authenticated_client["headers"],
        json={"content": "x" * 501}
    )
    
    assert response.status_code == 422

# -------------------------
# Tests de listado de comentarios
# -------------------------

def test_list_comments_empty():
    """Test de listado sin comentarios"""
    response = client.get("/comments/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["comments"]) == 0

def test_list_comments_with_data(authenticated_client):
    """Test de listado con comentarios"""
    # Crear algunos comentarios
    for i in range(3):
        client.post(
            "/comments/",
            headers=authenticated_client["headers"],
            json={"content": f"Comentario {i+1}"}
        )
    
    response = client.get("/comments/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["comments"]) == 3

    client.delete("/comments/me/all", headers=authenticated_client["headers"])

def test_list_comments_pagination(authenticated_client):
    """Test de paginación"""
    # Crear 15 comentarios
    for i in range(15):
        client.post(
            "/comments/",
            headers=authenticated_client["headers"],
            json={"content": f"Comentario {i+1}"}
        )
    
    # Primera página (10 por defecto)
    response = client.get("/comments/?page=1&page_size=10")
    data = response.json()
    assert len(data["comments"]) == 10
    assert data["total"] == 15
    
    # Segunda página
    response = client.get("/comments/?page=2&page_size=10")
    data = response.json()
    assert len(data["comments"]) == 5

    client.delete("/comments/me/all", headers=authenticated_client["headers"])

def test_list_comments_filter_by_profile(authenticated_client, second_authenticated_client):
    """Test de filtrado por usuario"""
    # Usuario 1 crea 2 comentarios
    for i in range(2):
        client.post(
            "/comments/",
            headers=authenticated_client["headers"],
            json={"content": f"Usuario 1 comentario {i+1}"}
        )
    
    # Usuario 2 crea 3 comentarios
    for i in range(3):
        client.post(
            "/comments/",
            headers=second_authenticated_client["headers"],
            json={"content": f"Usuario 2 comentario {i+1}"}
        )
    
    # Obtener profile_id del primer usuario
    profile_response = client.get("/auth/profile", headers=authenticated_client["headers"])
    profile_id = profile_response.json()["id"]
    
    # Filtrar por profile_id
    response = client.get(f"/comments/?profile_id={profile_id}")
    data = response.json()
    assert data["total"] == 2

    client.delete("/comments/me/all", headers=authenticated_client["headers"])
    client.delete("/comments/me/all", headers=second_authenticated_client["headers"])

def test_list_comments_filter_by_course(authenticated_client):
    """Test de filtrado por curso"""
    # Crear comentarios en diferentes cursos
    client.post("/comments/", headers=authenticated_client["headers"], json={"content": "Curso 1", "course_id": 1})
    client.post("/comments/", headers=authenticated_client["headers"], json={"content": "Curso 1", "course_id": 1})
    client.post("/comments/", headers=authenticated_client["headers"], json={"content": "Curso 2", "course_id": 2})
    
    response = client.get("/comments/?course_id=1")
    data = response.json()
    assert data["total"] == 2

    client.delete("/comments/me/all", headers=authenticated_client["headers"])

# -------------------------
# Tests de obtener comentario específico
# -------------------------

def test_get_comment_success(authenticated_client):
    """Test de obtener comentario específico"""
    # Crear comentario
    create_response = client.post(
        "/comments/",
        headers=authenticated_client["headers"],
        json={"content": "Comentario específico"}
    )
    comment_id = create_response.json()["id"]
    
    # Obtener comentario
    response = client.get(f"/comments/{comment_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == comment_id
    assert data["content"] == "Comentario específico"
    assert "author_name" in data
    assert "author_email" in data

    client.delete("/comments/me/all", headers=authenticated_client["headers"])

def test_get_comment_not_found():
    """Test de obtener comentario inexistente"""
    response = client.get("/comments/999")
    
    assert response.status_code == 404

# -------------------------
# Tests de mis comentarios
# -------------------------

def test_get_my_comments(authenticated_client):
    """Test de obtener mis comentarios"""
    # Crear algunos comentarios
    for i in range(3):
        client.post(
            "/comments/",
            headers=authenticated_client["headers"],
            json={"content": f"Mi comentario {i+1}"}
        )
    
    response = client.get("/comments/me/all", headers=authenticated_client["headers"])
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3

    client.delete("/comments/me/all", headers=authenticated_client["headers"])

def test_get_my_comments_without_auth():
    """Test de obtener mis comentarios sin autenticación"""
    response = client.get("/comments/me/all")
    
    assert response.status_code == 401

# -------------------------
# Tests de actualización de comentarios
# -------------------------

def test_update_comment_success(authenticated_client):
    """Test de actualización exitosa"""
    # Crear comentario
    create_response = client.post(
        "/comments/",
        headers=authenticated_client["headers"],
        json={"content": "Contenido original"}
    )
    comment_id = create_response.json()["id"]
    
    # Actualizar comentario
    response = client.put(
        f"/comments/{comment_id}",
        headers=authenticated_client["headers"],
        json={"content": "Contenido actualizado"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Contenido actualizado"

    client.delete("/comments/me/all", headers=authenticated_client["headers"])

def test_update_comment_not_owner(authenticated_client, second_authenticated_client):
    """Test de actualización por usuario que no es propietario"""
    # Usuario 1 crea comentario
    create_response = client.post(
        "/comments/",
        headers=authenticated_client["headers"],
        json={"content": "Comentario del usuario 1"}
    )
    comment_id = create_response.json()["id"]
    
    # Usuario 2 intenta actualizar
    response = client.put(
        f"/comments/{comment_id}",
        headers=second_authenticated_client["headers"],
        json={"content": "Intento de actualización"}
    )
    
    assert response.status_code == 403
    assert "permiso" in response.json()["detail"].lower()

    client.delete("/comments/me/all", headers=authenticated_client["headers"])
    client.delete("/comments/me/all", headers=second_authenticated_client["headers"])

def test_update_comment_without_auth(authenticated_client):
    """Test de actualización sin autenticación"""
    # Crear comentario
    create_response = client.post(
        "/comments/",
        headers=authenticated_client["headers"],
        json={"content": "Comentario"}
    )
    comment_id = create_response.json()["id"]
    
    # Intentar actualizar sin auth
    response = client.put(
        f"/comments/{comment_id}",
        json={"content": "Intento"}
    )
    
    assert response.status_code == 401

    client.delete("/comments/me/all", headers=authenticated_client["headers"])

def test_update_comment_not_found(authenticated_client):
    """Test de actualización de comentario inexistente"""
    response = client.put(
        "/comments/999",
        headers=authenticated_client["headers"],
        json={"content": "Contenido"}
    )
    
    assert response.status_code == 404

# -------------------------
# Tests de eliminación de comentarios
# -------------------------

def test_delete_comment_success(authenticated_client):
    """Test de eliminación exitosa"""
    # Crear comentario
    create_response = client.post(
        "/comments/",
        headers=authenticated_client["headers"],
        json={"content": "Comentario a eliminar"}
    )
    comment_id = create_response.json()["id"]
    
    # Eliminar comentario
    response = client.delete(
        f"/comments/{comment_id}",
        headers=authenticated_client["headers"]
    )
    
    assert response.status_code == 204
    
    # Verificar que ya no existe
    get_response = client.get(f"/comments/{comment_id}")
    assert get_response.status_code == 404

def test_delete_comment_not_owner(authenticated_client, second_authenticated_client):
    """Test de eliminación por usuario que no es propietario"""
    # Usuario 1 crea comentario
    create_response = client.post(
        "/comments/",
        headers=authenticated_client["headers"],
        json={"content": "Comentario del usuario 1"}
    )
    comment_id = create_response.json()["id"]
    
    # Usuario 2 intenta eliminar
    response = client.delete(
        f"/comments/{comment_id}",
        headers=second_authenticated_client["headers"]
    )
    
    assert response.status_code == 403

    client.delete("/comments/me/all", headers=authenticated_client["headers"])

def test_delete_comment_without_auth(authenticated_client):
    """Test de eliminación sin autenticación"""
    # Crear comentario
    create_response = client.post(
        "/comments/",
        headers=authenticated_client["headers"],
        json={"content": "Comentario"}
    )
    comment_id = create_response.json()["id"]
    
    # Intentar eliminar sin auth
    response = client.delete(f"/comments/{comment_id}")
    
    assert response.status_code == 401

    client.delete("/comments/me/all", headers=authenticated_client["headers"])

def test_delete_all_my_comments(authenticated_client):
    """Test de eliminación de todos mis comentarios"""
    # Crear varios comentarios
    for i in range(5):
        client.post(
            "/comments/",
            headers=authenticated_client["headers"],
            json={"content": f"Comentario {i+1}"}
        )
    
    # Eliminar todos
    response = client.delete("/comments/me/all", headers=authenticated_client["headers"])
    
    assert response.status_code == 200
    data = response.json()
    assert data["deleted_count"] == 5
    
    # Verificar que no quedan comentarios
    list_response = client.get("/comments/me/all", headers=authenticated_client["headers"])
    assert list_response.json()["total"] == 0
