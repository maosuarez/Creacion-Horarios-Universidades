import pytest
from tests.test_database import client

@pytest.fixture
def test_user_data():
    """Datos de usuario para tests (cumple con tus validaciones)"""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "password": "Password123!",  # Cumple: mayúscula + número
        "bio": "Test bio",
        "role": "viewer"
    }

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
def authenticated_client(test_user_auth):
    """Cliente autenticado con token"""
    # Registrar usuario
    res_signup = client.post("/auth/signup", json=test_user_auth)
    
    # Login para obtener token
    response = client.post("/auth/login", data={
        "grant_type": "password",
        "username": test_user_auth["email"],
        "password": test_user_auth["password"]
    })
    token = response.json()["access_token"]
    
    # Retornar cliente con headers de autorización
    return {
        "client": client,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
        "user_data": test_user_auth
    }

# -------------------------
# Tests de Signup con validaciones de ProfileCreate
# -------------------------
def test_signup_success(test_user_data):
    """Test de registro exitoso"""
    response = client.post("/auth/signup", json=test_user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["name"] == test_user_data["name"]
    assert "password" not in data
    assert "id" in data

def test_signup_duplicate_email(test_user_data):
    """Test de registro con email duplicado"""
    # Primer registro
    client.post("/auth/signup", json=test_user_data)
    
    # Intento de segundo registro con mismo email
    response = client.post("/auth/signup", json=test_user_data)
    
    assert response.status_code == 400
    assert "email ya está registrado" in response.json()["detail"]

def test_signup_invalid_email():
    """Test de registro con email inválido"""
    response = client.post("/auth/signup", json={
        "name": "Test",
        "email": "invalid-email",
        "password": "Password123"
    })
    
    assert response.status_code == 422

def test_signup_short_password():
    """Test de registro con contraseña muy corta (< 6 caracteres)"""
    response = client.post("/auth/signup", json={
        "name": "Test",
        "email": "test@example.com",
        "password": "Pass1"  # Solo 5 caracteres
    })
    
    assert response.status_code == 422

def test_signup_password_without_uppercase():
    """Test validación: contraseña sin mayúscula"""
    response = client.post("/auth/signup", json={
        "name": "Test",
        "email": "test@example.com",
        "password": "password123"  # Sin mayúscula
    })
    
    assert response.status_code == 422
    assert "mayúscula" in str(response.json()["detail"]).lower()

def test_signup_password_without_number():
    """Test validación: contraseña sin número"""
    response = client.post("/auth/signup", json={
        "name": "Test",
        "email": "test@example.com",
        "password": "Password"  # Sin número
    })
    
    assert response.status_code == 422
    assert "número" in str(response.json()["detail"]).lower()

def test_signup_name_word_too_long():
    """Test validación: palabra del nombre > 20 caracteres"""
    response = client.post("/auth/signup", json={
        "name": "Test Nombredemasiadolargo",  # Segunda palabra > 20 chars
        "email": "test@example.com",
        "password": "Password123"
    })
    
    assert response.status_code == 422

def test_signup_bio_too_long():
    """Test validación: bio > 300 caracteres"""
    response = client.post("/auth/signup", json={
        "name": "Test",
        "email": "test@example.com",
        "password": "Password123",
        "bio": "x" * 301  # 301 caracteres
    })
    
    assert response.status_code == 422

def test_signup_role_field_ignored():
    """El campo 'role' enviado en el signup es ignorado — el backend asigna el rol."""
    response = client.post("/auth/signup", json={
        "name": "Test Role Ignored",
        "email": "roleignored@example.com",
        "password": "Password123",
        "role": "creator",  # ignorado; el backend decide
    })
    # El registro debe ser exitoso aunque se mande un role cualquiera
    assert response.status_code == 201
    # El rol asignado es válido (creator si es el primero, viewer si no)
    assert response.json()["role"] in ("creator", "viewer")

# -------------------------
# Tests de Login
# -------------------------
def test_login_success(test_user_data):
    """Test de login exitoso"""
    # Registrar usuario
    client.post("/auth/signup", json=test_user_data)
    
    # Login
    response = client.post("/auth/login", data={
        "grant_type": "password",
        "username": test_user_data["email"],
        "password": test_user_data["password"]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(test_user_data):
    """Test de login con contraseña incorrecta"""
    # Registrar usuario
    client.post("/auth/signup", json=test_user_data)
    
    # Login con contraseña incorrecta
    response = client.post("/auth/login", data={
        "grant_type": "password",
        "username": test_user_data["email"],
        "password": "WrongPassword123"
    })
    
    assert response.status_code == 401
    assert "Credenciales inválidas" in response.json()["detail"]

def test_login_nonexistent_user():
    """Test de login con usuario que no existe"""
    response = client.post("/auth/login", data={
        "grant_type": "password",
        "username": "noexiste@example.com",
        "password": "Password123"
    })
    
    assert response.status_code == 401

# -------------------------
# Tests de Profile (protegidos)
# -------------------------
def test_get_profile_success(authenticated_client):
    """Test de obtener perfil autenticado"""
    response = client.get(
        "/auth/profile",
        headers=authenticated_client["headers"]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "name" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_get_profile_without_token():
    """Test de obtener perfil sin token"""
    response = client.get("/auth/profile")
    
    assert response.status_code == 401

def test_get_profile_invalid_token():
    """Test de obtener perfil con token inválido"""
    response = client.get(
        "/auth/profile",
        headers={"Authorization": "Bearer token_invalido"}
    )
    
    assert response.status_code == 401

def test_update_profile_success(authenticated_client):
    """Test de actualización de perfil"""
    response = client.put(
        "/auth/profile",
        headers=authenticated_client["headers"],
        json={
            "name": "Updated Name",
            "bio": "Updated bio"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["bio"] == "Updated bio"

def test_update_profile_email(authenticated_client):
    """Test de actualización de email"""
    response = client.put(
        "/auth/profile",
        headers=authenticated_client["headers"],
        json={"email": "newemail@example.com"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newemail@example.com"

def test_update_profile_email_duplicate(authenticated_client):
    """Test de actualización con email ya existente"""
    # Crear segundo usuario
    client.post("/auth/signup", json={
        "name": "Other User",
        "email": "other@example.com",
        "password": "Password123"
    })
    
    # Intentar actualizar con email del otro usuario
    response = client.put(
        "/auth/profile",
        headers=authenticated_client["headers"],
        json={"email": "other@example.com"}
    )
    
    assert response.status_code == 400
    assert "email ya está en uso" in response.json()["detail"]

def test_update_profile_without_token():
    """Test de actualización sin token"""
    response = client.put(
        "/auth/profile",
        json={"name": "New Name"}
    )
    
    assert response.status_code == 401

# -------------------------
# Tests de cambio de contraseña
# -------------------------
def test_change_password_success(authenticated_client):
    """Test de cambio de contraseña exitoso"""
    response = client.put(
        "/auth/profile/password",
        headers=authenticated_client["headers"],
        json={
            "old_password": authenticated_client["user_data"]["password"],
            "new_password": "NewPassword456"
        }
    )
    
    assert response.status_code == 200
    
    # Verificar que puede loguearse con nueva contraseña
    login_response = client.post("/auth/login", data={
        "grant_type": "password",
        "username": authenticated_client["user_data"]["email"],
        "password": "NewPassword456"
    })
    assert login_response.status_code == 200

    response = client.put(
        "/auth/profile/password",
        headers={"Authorization": f"Bearer {login_response.json()['access_token']}"},
        json={
            "old_password": "NewPassword456",
            "new_password": "Password123!"
        }
    )

    assert response.status_code == 200


def test_change_password_wrong_old_password(authenticated_client):
    """Test de cambio con contraseña actual incorrecta"""
    response = client.put(
        "/auth/profile/password",
        headers=authenticated_client["headers"],
        json={
            "old_password": "WrongPassword123",
            "new_password": "NewPassword456"
        }
    )
    
    assert response.status_code == 400
    assert "incorrecta" in response.json()["detail"]

def test_change_password_invalid_new_password(authenticated_client):
    """Test de cambio con nueva contraseña inválida (sin mayúscula)"""
    response = client.put(
        "/auth/profile/password",
        headers=authenticated_client["headers"],
        json={
            "old_password": authenticated_client["user_data"]["password"],
            "new_password": "newpassword123"  # Sin mayúscula
        }
    )
    
    assert response.status_code == 422

# -------------------------
# Tests de eliminación de perfil
# -------------------------
def test_delete_profile_success(authenticated_client):
    """Test de eliminación de perfil"""
    # Eliminar perfil
    response = client.delete(
        "/auth/profile",
        headers=authenticated_client["headers"]
    )
    
    assert response.status_code == 204
    
    # Intentar login después de eliminar
    login_response = client.post("/auth/login", data={
        "grant_type": "password",
        "username":  authenticated_client["user_data"]["email"],
        "password": authenticated_client["user_data"]["password"]
    })
    
    assert login_response.status_code == 401

def test_delete_profile_without_token():
    """Test de eliminación sin token"""
    response = client.delete("/auth/profile")
    
    assert response.status_code == 401

# -------------------------
# Tests de roles
# -------------------------
def test_signup_default_role_viewer():
    """
    Usuarios registrados después del primero reciben rol viewer.
    (el primer usuario del test DB es test@example.com, creado por test_signup_success)
    """
    response = client.post("/auth/signup", json={
        "name": "Default User",
        "email": "default@example.com",
        "password": "Password123",
    })

    assert response.status_code == 201
    assert response.json()["role"] == "viewer"


def test_assign_role_as_creator():
    """Un creator puede asignar el rol creator a un viewer."""
    # test@example.com fue el primer usuario registrado en los tests → creator
    login = client.post("/auth/login", data={
        "grant_type": "password",
        "username": "test@example.com",
        "password": "Password123!",
    })
    assert login.status_code == 200, f"Login falló: {login.json()}"
    creator_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    # Crear un viewer nuevo
    res = client.post("/auth/signup", json={
        "name": "Promote Me",
        "email": "promoteme@example.com",
        "password": "Password123!",
    })
    assert res.status_code == 201
    assert res.json()["role"] == "viewer"
    new_user_id = res.json()["id"]

    # El creator asigna rol creator al nuevo usuario
    response = client.patch(
        f"/auth/users/{new_user_id}/role",
        json={"role": "creator"},
        headers=creator_headers,
    )
    assert response.status_code == 200
    assert response.json()["role"] == "creator"


def test_assign_role_viewer_cannot_assign():
    """Un viewer no puede asignar roles."""
    # Crear un viewer fresco para este test
    client.post("/auth/signup", json={
        "name": "Viewer Only",
        "email": "vieweronly@example.com",
        "password": "Password123!",
    })
    login = client.post("/auth/login", data={
        "grant_type": "password",
        "username": "vieweronly@example.com",
        "password": "Password123!",
    })
    viewer_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    # Intenta cambiar el rol del usuario 1 (cualquier usuario)
    response = client.patch(
        "/auth/users/1/role",
        json={"role": "creator"},
        headers=viewer_headers,
    )
    assert response.status_code == 403


def test_assign_role_self_change_forbidden():
    """Un creator no puede cambiar su propio rol."""
    login = client.post("/auth/login", data={
        "grant_type": "password",
        "username": "test@example.com",
        "password": "Password123!",
    })
    creator_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    creator_id = client.get("/auth/profile", headers=creator_headers).json()["id"]

    response = client.patch(
        f"/auth/users/{creator_id}/role",
        json={"role": "viewer"},
        headers=creator_headers,
    )
    assert response.status_code == 400


def test_assign_role_nonexistent_user():
    """Intentar asignar rol a usuario inexistente → 404."""
    login = client.post("/auth/login", data={
        "grant_type": "password",
        "username": "test@example.com",
        "password": "Password123!",
    })
    creator_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = client.patch(
        "/auth/users/999999/role",
        json={"role": "viewer"},
        headers=creator_headers,
    )
    assert response.status_code == 404
