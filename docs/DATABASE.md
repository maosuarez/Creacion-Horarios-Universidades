# Base de Datos — Esquema y Modelos

## Diagrama de Relaciones

```
Teacher  1──< * Course
                   │
                   ├──< * CourseSchedule
                   │
                   └──< * Comment (opcional)

Profile  1──< * Comment
```

## Entidades

### Profile

Tabla `profiles`. Representa un usuario del sistema.

| Columna | Tipo | Restricción | Nulo | Default | Descripción |
|---------|------|-------------|------|---------|-------------|
| id | Integer | PRIMARY KEY | No | Auto | ID único del usuario |
| name | String(100) | — | No | — | Nombre del usuario |
| email | String(120) | UNIQUE | No | — | Email único |
| password_hash | String(255) | — | No | — | Hash seguro (bcrypt/scrypt) |
| bio | String(255) | — | Sí | NULL | Biografía opcional |
| role | Enum (UserRole) | — | No | viewer | `creator` (escribir) \| `viewer` (leer) |
| created_at | DateTime | — | No | NOW() | Timestamp de creación (zona UTC) |
| updated_at | DateTime | — | Sí | NOW() | Timestamp de última actualización |

**Restricciones**:
- Email único (dos usuarios no pueden tener el mismo email)
- Role solamente `creator` o `viewer`

---

### Teacher

Tabla `teachers`. Representa un profesor.

| Columna | Tipo | Restricción | Nulo | Default | Descripción |
|---------|------|-------------|------|---------|-------------|
| id | Integer | PRIMARY KEY | No | Auto | ID único del profesor |
| full_name | String(200) | — | No | — | Nombre completo |

**Restricciones**:
- `full_name` efectivamente único (no hay profesor duplicado en el código)

**Nota**: Los profesores se crean on-demand cuando se crea un curso (mediante `get_or_create_teacher`).

---

### Course

Tabla `courses`. Representa una materia/sección.

| Columna | Tipo | Restricción | Nulo | Default | Descripción |
|---------|------|-------------|------|---------|-------------|
| id | Integer | PRIMARY KEY | No | Auto | ID único del curso |
| subject | String(100) | — | No | — | Nombre de la materia (ej: "Cálculo I") |
| code | Integer | UNIQUE | No | — | Código de sección (4 dígitos, único) |
| teacher_id | Integer | FOREIGN KEY | Sí | NULL | Referencia al profesor que lo dicta |

**Restricciones**:
- `code` único en toda la BD (cada sección tiene código único)
- `teacher_id` puede ser NULL (posibilidad teórica; en práctica siempre presente)
- `code` debe ser exactamente 4 dígitos

**Relación con Teacher**: 
- Un profesor puede dictar muchos cursos (diferentes materias)
- Un curso tiene exactamente un profesor

---

### CourseSchedule

Tabla `course_schedules`. Representa bloques de horario de un curso.

| Columna | Tipo | Restricción | Nulo | Default | Descripción |
|---------|------|-------------|------|---------|-------------|
| id | Integer | PRIMARY KEY | No | Auto | ID único del bloque |
| course_id | Integer | FOREIGN KEY | Sí | NULL | Referencia al curso |
| day | String(20) | — | No | — | Día de la semana (español sin acentos: Lunes, Martes, Miercoles, Jueves, Viernes, Sabado) |
| start_time | Time | — | No | — | Hora inicio (HH:MM, rango 07:00–19:00) |
| end_time | Time | — | No | — | Hora fin (HH:MM, rango 08:00–19:00) |

**Restricciones**:
- `course_id` puede ser NULL (posibilidad teórica; en práctica referencia válida)
- `end_time` > `start_time`
- `start_time` en rango [07:00, 18:00]
- `end_time` en rango [08:00, 19:00]
- `day` en lista válida (Lunes, Martes, Miercoles, Jueves, Viernes, Sabado)

**Validación especial**: Cuando se crea o actualiza un curso, se valida que el profesor no tenga horarios solapados en sus otros cursos (ejemplo: Dr. García no puede tener dos clases a las 8am).

---

### Comment

Tabla `comments`. Feedback de usuarios sobre cursos/profesores.

| Columna | Tipo | Restricción | Nulo | Default | Descripción |
|---------|------|-------------|------|---------|-------------|
| id | Integer | PRIMARY KEY | No | Auto | ID único del comentario |
| profile_id | Integer | FOREIGN KEY | No | — | Referencia al usuario que comenta |
| course_id | Integer | FOREIGN KEY | Sí | NULL | Referencia al curso (opcional) |
| content | String(500) | — | No | — | Texto del comentario (máx. 500 caracteres) |
| created_at | DateTime | — | No | NOW() | Timestamp de creación (UTC) |

**Restricciones**:
- `profile_id` siempre referencia válida (validado al crear)
- `course_id` puede ser NULL (comentario general sin asociación)
- `content` no vacío, máx. 500 caracteres

---

## Convenciones

### Idioma en Horarios

**Días en Base de Datos**: Español sin acentos
- Válidos: `Lunes`, `Martes`, `Miercoles`, `Jueves`, `Viernes`, `Sabado`
- NO válidos: `lunes`, `miércoles`, `Lun`, etc.

**Días en API (generación de horarios)**: Acepta ambos inglés y español
- Inglés: `monday`, `tuesday`, `wednesday`, `thursday`, `friday`, `saturday`, `sunday`
- Español: `lunes`, `martes`, `miercoles`, `jueves`, `viernes`, `sabado`, `domingo`
- Internamente se normalizan a español para BD

### Matriz de Horarios

Representación interna (NumPy) durante generación:
- **Forma**: 12 filas × 6 columnas
- **Filas**: Horas 07:00–18:00 (índices 0–11)
- **Columnas**: Lunes–Sábado (índices 0–5)
- **Valores**: Código de curso (integer) o 0 (libre)
- **Conflicto**: Si alguna celda (hora × día) tiene valor no-cero en dos matrices simultáneamente

Representación en respuesta API:
- **Formato**: Array de strings (los códigos se convierten a string)
- **Etiquetas**: `hour_labels` (ej: "7-8", "8-9") y `day_labels` (ej: "Lunes", "Martes")

### Timestamps

Todas las tablas con `created_at` usan:
- **Tipo**: DateTime con timezone (UTC)
- **Función Default**: `func.now()` (SQLAlchemy) — obtiene timestamp actual del servidor
- **Formato JSON**: ISO 8601 (ej: `"2024-01-15T10:30:00Z"`)

---

## Selección de Base de Datos

El backend soporta múltiples engines configurables en `app/database.py` (evaluado en import-time):

### SQLite (Desarrollo y Testing)

**Activación**:
- `ENV=test` → Siempre SQLite in-memory (ignora `DB_ENGINE`)
- `DB_ENGINE=sqlite` → SQLite file en `SQLITE_PATH` (default: `./data/dev.db`)

**Ventajas**:
- Sin dependencias externas
- Transacciones inline (ideal para development)
- Hot-reload sin desconexiones

**Limitaciones**:
- Concurrencia limitada (lock a nivel de fichero)
- No soporta todas las features de PostgreSQL/MySQL (ej: ILIKE se simula)

---

### MySQL (Producción)

**Activación**:
- `DB_ENGINE=mysql` + `DB_USER`, `DB_PASS`, `DB_HOST`, `DB_PORT`, `DB_NAME`

**Configuración**:
```python
# URL de conexión (ejemplo)
mysql+pymysql://user:pass@host:3306/db_name
```

**SSL (Producción en Azure)**:
- Conectar con certificado: `/app/certs/BaltimoreCyberTrustRoot.crt.pem`
- URL fuerza `ssl_ca=/app/certs/...`
- El backend en Docker tiene el certificado incluido

**Ventajas**:
- Escalabilidad
- Concurrencia optimizada
- Features avanzadas (FULL TEXT SEARCH, etc.)

**Nota**: Para desarrollo local sin MySQL en Docker, usar SQLite (override dev).

---

## Creación de Tablas

Las tablas se crean automáticamente solo si:
- `ENV` es `local` o `test`
- En el `lifespan` de FastAPI, al iniciar la aplicación

**En producción** (`ENV=production`):
- Las tablas deben existir (migración manual previa)
- No se crea nada automáticamente (seguridad)

---

## Índices

**Actualmente no definidos en modelos** (SQLAlchemy permite agregarlos vía `Index`). Recomendaciones si hay problemas de rendimiento:

- `Course.code` (búsqueda por código)
- `Course.subject` (búsqueda de materias)
- `Comment.profile_id`, `Comment.course_id` (filtros)
- `CourseSchedule.course_id` (eager loading)
- `Profile.email` (login)

---

## Ejemplo: Crear un Curso

Flujo desde el API:

```json
POST /courses/
{
  "subject": "Cálculo I",
  "code": 1001,
  "teacher_name": "Dr. Juan Pérez",
  "schedules": [
    {"day": "Lunes", "start_time": "08:00", "end_time": "10:00"},
    {"day": "Miercoles", "start_time": "08:00", "end_time": "10:00"}
  ]
}
```

Backend:
1. Valida `code` es entero de 4 dígitos, único
2. Crea o busca `Teacher` con `full_name = "Dr. Juan Pérez"`
3. Crea `Course` con `subject`, `code`, `teacher_id`
4. Para cada schedule, valida horario y crea `CourseSchedule`
5. Valida que el profesor no tenga overlaps
6. Retorna Course con schedules inclusos (eager-loaded)

---

## Migraciones

Actualmente **sin Alembic**. Si se necesita cambiar esquema en producción:

1. Modificar modelos en `app/models/`
2. Crear script de migración manual (backup BD → alter table → verificar datos)
3. Ejecutar en producción
4. Actualizar `requirements.txt` si hay nuevas dependencias

**Próximo paso**: Implementar Alembic para versionado de schema.
