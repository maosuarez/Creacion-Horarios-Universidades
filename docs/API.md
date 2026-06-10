# API REST — Documentación de Endpoints

Backend FastAPI en puerto 8000. Todos los endpoints retornan JSON. 

**Base URL en desarrollo**: `http://localhost:8000`  
**Versión API**: 1.0.0 (sin versionado en URL)

## Autenticación

Usa **JWT Bearer tokens**. Los endpoints protegidos requieren el header:
```
Authorization: Bearer <token>
```

**Obtención del token**: Ver sección [Autenticación](#autenticación) más abajo.

---

## Autenticación

### POST `/auth/signup`
Registra un nuevo usuario.

**Autenticación**: ❌ No requerida

**Body** (application/json):
```json
{
  "name": "Juan Pérez",
  "email": "juan@ejemplo.com",
  "password": "Pass123",
  "bio": "Estudiante de ingeniería",
  "role": "creator"
}
```

**Validaciones**:
- `name`: Cada palabra máximo 20 caracteres
- `email`: Único, formato válido
- `password`: Mínimo 6 caracteres, debe contener mayúscula y número
- `bio`: Opcional, máximo 300 caracteres
- `role`: `"creator"` o `"viewer"` (default: `"viewer"`)

**Respuesta** `201`:
```json
{
  "id": 1,
  "name": "Juan Pérez",
  "email": "juan@ejemplo.com",
  "bio": "Estudiante de ingeniería",
  "role": "creator"
}
```

---

### POST `/auth/login`
Inicia sesión y retorna JWT.

**Autenticación**: ❌ No requerida

**Body** (application/x-www-form-urlencoded):
```
username=juan@ejemplo.com
password=Pass123
```

**Respuesta** `200`:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### GET `/auth/profile`
Obtiene el perfil del usuario autenticado.

**Autenticación**: ✅ Requerida

**Respuesta** `200`:
```json
{
  "id": 1,
  "name": "Juan Pérez",
  "email": "juan@ejemplo.com",
  "bio": "Estudiante de ingeniería",
  "role": "creator",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T14:45:00Z"
}
```

---

### PUT `/auth/profile`
Actualiza el perfil del usuario autenticado.

**Autenticación**: ✅ Requerida

**Body** (todos los campos opcionales):
```json
{
  "name": "Juan Carlos Pérez",
  "email": "juancarlos@ejemplo.com",
  "bio": "Estudiante de ingeniería de sistemas"
}
```

**Respuesta** `200`: Mismo formato que `/auth/profile`

---

### PUT `/auth/profile/password`
Cambia la contraseña del usuario autenticado.

**Autenticación**: ✅ Requerida

**Body**:
```json
{
  "old_password": "Pass123",
  "new_password": "NewPass456"
}
```

**Validaciones**: Nueva contraseña mínimo 6 caracteres, mayúscula y número.

**Respuesta** `200`: Confirmación

---

### DELETE `/auth/profile`
Elimina el perfil del usuario autenticado.

**Autenticación**: ✅ Requerida

⚠️ **IRREVERSIBLE**: Elimina todos los comentarios asociados.

**Respuesta** `204`: Sin contenido

---

## Cursos

### GET `/courses/`
Lista cursos.

**Autenticación**: ❌ No requerida

**Query Params** (opcionales):
- `skip`: Offset (default: 0)
- `limit`: Límite de resultados (default: 100)

**Respuesta** `200`:
```json
[
  {
    "id": 1,
    "subject": "Cálculo I",
    "code": 1001,
    "teacher_id": 5,
    "schedules": [
      {
        "id": 1,
        "day": "Lunes",
        "start_time": "08:00",
        "end_time": "10:00",
        "course_id": 1
      }
    ]
  }
]
```

---

### POST `/courses/`
Crea un nuevo curso.

**Autenticación**: ✅ Requerida (creator-only)

**Body**:
```json
{
  "subject": "Cálculo I",
  "code": 1001,
  "teacher_name": "Dr. Juan Pérez",
  "schedules": [
    {
      "day": "Lunes",
      "start_time": "08:00",
      "end_time": "10:00"
    },
    {
      "day": "Miercoles",
      "start_time": "08:00",
      "end_time": "10:00"
    }
  ]
}
```

**Validaciones**:
- `subject`: 1–100 caracteres
- `code`: Entero positivo, 4 dígitos, único
- `teacher_name`: 1–100 caracteres
- `schedules`: Mínimo 1, máximo 10 horarios
- `day`: Lunes/Martes/Miercoles/Jueves/Viernes/Sabado (español, sin acentos)
- Horas: 07:00–19:00, end > start

**Validación especial**: No puede haber solapamientos de horarios para el mismo profesor.

**Respuesta** `201`: Curso creado (mismo formato que GET)

---

### GET `/courses/{course_id}`
Obtiene un curso específico.

**Autenticación**: ❌ No requerida

**Parámetros**:
- `course_id` (path): ID del curso

**Respuesta** `200`: Detalles del curso

---

### PUT `/courses/{course_id}`
Actualiza un curso existente.

**Autenticación**: ✅ Requerida (creator-only)

**Parámetros**:
- `course_id` (path): ID del curso

**Body** (todos opcionales):
```json
{
  "subject": "Cálculo Diferencial",
  "code": 1002,
  "teacher_name": "Dra. María García",
  "schedules": [...]
}
```

**Respuesta** `200`: Curso actualizado

---

### DELETE `/courses/{course_id}`
Elimina un curso.

**Autenticación**: ✅ Requerida (creator-only)

**Parámetros**:
- `course_id` (path): ID del curso

**Respuesta** `200`: Confirmación

---

## Búsqueda de Cursos

### GET `/courses/search/subjects`
Búsqueda typeahead de materias.

**Autenticación**: ❌ No requerida

**Query Params**:
- `query`: Texto parcial (mínimo 1 caracter)

**Ejemplo**: `/courses/search/subjects?query=Cál`

**Respuesta** `200`:
```json
[
  {
    "subject": "Cálculo I",
    "count": 5
  },
  {
    "subject": "Cálculo II",
    "count": 3
  }
]
```

---

### GET `/courses/search/codes`
Obtiene códigos de sección para una materia.

**Autenticación**: ❌ No requerida

**Query Params**:
- `subject` (requerido): Nombre exacto

**Ejemplo**: `/courses/search/codes?subject=Cálculo I`

**Respuesta** `200`:
```json
[
  {
    "code": 1001,
    "course_id": 123
  },
  {
    "code": 1002,
    "course_id": 124
  }
]
```

---

### GET `/courses/search/teachers`
Obtiene profesores para una materia.

**Autenticación**: ❌ No requerida

**Query Params**:
- `subject` (requerido): Nombre exacto

**Ejemplo**: `/courses/search/teachers?subject=Física I`

**Respuesta** `200`:
```json
[
  {
    "id": 1,
    "full_name": "Dr. Juan Pérez"
  },
  {
    "id": 2,
    "full_name": "Dra. María García"
  }
]
```

---

## Generación de Horarios

### POST `/generate-schedules`
Genera todas las combinaciones posibles de horarios sin conflictos.

**Autenticación**: ❌ No requerida

**Body**:
```json
{
  "preferencias": {
    "Cálculo I": {
      "profesores": ["Dr. Juan Pérez"],
      "codes": [1001]
    },
    "Física I": {
      "profesores": [],
      "codes": [2001, 2002]
    },
    "Programación": {
      "profesores": [],
      "codes": []
    }
  },
  "freetime": {
    "Lunes": [12, 13, 14],
    "Viernes": [16, 17, 18]
  }
}
```

**Lógica de Filtros por Materia**:
- **Ambos con valores**: UNION (OR) — cursos del profesor **O** código especificado
- **Solo uno con valores**: Filtra solo por ese criterio
- **Ambos vacíos**: Incluye TODOS los cursos de esa materia

**Parámetros de Freetime**:
- Claves: Días en español (Lunes, Martes, Miercoles, Jueves, Viernes, Sabado)
- Valores: Array de horas (7–18, representan 7am–6pm)

**Respuesta** `200`:
```json
[
  {
    "schedule_number": 1,
    "courses": [
      {
        "subject": "Cálculo I",
        "code": 1001,
        "teacher_name": "Dr. Juan Pérez",
        "schedules": [
          {
            "day": "Lunes",
            "start_time": "08:00",
            "end_time": "10:00"
          }
        ]
      }
    ],
    "schedule_matrix": [
      ["1001", "", "", "", "", ""],
      ["1001", "", "2001", "", "", ""],
      ["", "", "2001", "", "", ""],
      ...
    ],
    "hour_labels": ["7-8", "8-9", "9-10", "10-11", "11-12", "12-1", "1-2", ...],
    "day_labels": ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado"]
  }
]
```

**Convenciones de Matriz**:
- 12 filas (horas 7–18)
- 6 columnas (Lunes–Sábado)
- Valores: Código de curso (string) o "" (vacío)
- Orden: Lunes es columna 0; Sábado es columna 5

---

## Comentarios

### POST `/comments/`
Crea un nuevo comentario.

**Autenticación**: ✅ Requerida

El `profile_id` se asigna automáticamente.

**Body**:
```json
{
  "content": "Excelente profesor, muy claro",
  "course_id": 123
}
```

**Validaciones**:
- `content`: 1–500 caracteres
- `course_id`: Opcional (puede ser null)

**Respuesta** `201`:
```json
{
  "id": 1,
  "content": "Excelente profesor, muy claro",
  "profile_id": 5,
  "course_id": 123,
  "created_at": "2024-01-15T10:30:00Z",
  "author_name": "Juan Pérez",
  "author_email": "juan@ejemplo.com"
}
```

---

### GET `/comments/`
Lista comentarios con paginación.

**Autenticación**: ❌ No requerida

**Query Params** (todos opcionales):
- `course_id`: Filtrar por curso
- `profile_id`: Filtrar por usuario
- `page`: Número de página (default: 1)
- `page_size`: Tamaño de página (default: 10, max: 100)

**Ejemplo**: `/comments/?course_id=123&page=1&page_size=20`

**Respuesta** `200`:
```json
{
  "total": 45,
  "page": 1,
  "page_size": 20,
  "comments": [
    {
      "id": 1,
      "content": "Excelente curso...",
      "profile_id": 5,
      "course_id": 123,
      "created_at": "2024-01-15T10:30:00Z",
      "author_name": "Juan Pérez",
      "author_email": "juan@ejemplo.com"
    }
  ]
}
```

---

### GET `/comments/{comment_id}`
Obtiene un comentario específico.

**Autenticación**: ❌ No requerida

**Respuesta** `200`: Detalles del comentario

---

### PUT `/comments/{comment_id}`
Actualiza un comentario.

**Autenticación**: ✅ Requerida

⚠️ Solo el propietario puede actualizarlo.

**Body**:
```json
{
  "content": "Contenido actualizado"
}
```

**Respuesta** `200`: Comentario actualizado

---

### DELETE `/comments/{comment_id}`
Elimina un comentario.

**Autenticación**: ✅ Requerida

⚠️ Solo el propietario puede eliminarlo.

**Respuesta** `204`: Sin contenido

---

### GET `/comments/me/all`
Obtiene todos los comentarios del usuario autenticado.

**Autenticación**: ✅ Requerida

**Query Params**:
- `page`: Número de página (default: 1)
- `page_size`: Tamaño de página (default: 10, max: 100)

**Respuesta** `200`: Mismo formato que `GET /comments/`

---

### DELETE `/comments/me/all`
Elimina todos los comentarios del usuario autenticado.

**Autenticación**: ✅ Requerida

⚠️ **ADVERTENCIA**: Irreversible.

**Respuesta** `200`: Confirmación

---

## Health Check

### GET `/health`
Verifica que la API esté operativa.

**Autenticación**: ❌ No requerida

**Respuesta** `200`:
```json
{
  "status": "ok"
}
```

---

### GET `/health-db`
Verifica la conexión con la base de datos.

**Autenticación**: ❌ No requerida

**Respuesta** `200`:
```json
{
  "database": "connected"
}
```

---

## Debug (Solo Desarrollo)

### GET `/debug/routes-markdown`
Lista todas las rutas en formato Markdown.

**Autenticación**: ❌ No requerida

Disponible solo si `ENV != "production"`.

---

## Códigos de Error

| Código | Significado |
|--------|-------------|
| `400` | Bad Request — datos inválidos |
| `401` | Unauthorized — token inválido o ausente |
| `403` | Forbidden — sin permisos (no creator, no propietario) |
| `404` | Not Found — recurso no existe |
| `422` | Unprocessable Entity — error de validación |
| `500` | Internal Server Error — error del servidor |

**Formato de error**:
```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "Password must contain at least one uppercase letter and one number",
      "type": "value_error"
    }
  ]
}
```

---

## Notas de Implementación

### CORS
- Origen permitido: `FRONTEND_URL` (env var, default `http://localhost:3000`)
- Métodos: GET, POST, PUT, DELETE, OPTIONS
- Credenciales: NO (JWT en header, no cookies)

### Rate Limiting
- No implementado actualmente

### Paginación
- Base de datos usa `skip` y `limit` (SQL OFFSET/LIMIT)
- Frontend convierte a `page` y `page_size`

### Búsqueda de Materias
- Usa ILIKE (case-insensitive, POSIX regex) en PostgreSQL
- En SQLite: Equivalente con `LIKE` (less powerful pero funcional)

### Algoritmo de Generación
- Crea todas las combinaciones posibles de cursos
- Para cada combo, valida con matrices NumPy 12×6
- Retorna solo las sin conflictos
- Orden: determinístico (por course.id)
