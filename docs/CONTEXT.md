# Contexto del Proyecto: Generador de Horarios Universitarios

## Qué es

Plataforma web que permite a estudiantes universitarios generar y visualizar todas las combinaciones posibles de horarios sin conflictos en base a sus materias deseadas y disponibilidad de tiempo.

## Por qué existe

Los estudiantes universitarios enfrentan un problema de optimización combinatoria: dadas sus materias obligatorias y electivas, con múltiples secciones y profesores disponibles, calcular manualmente todas las combinaciones de horarios válidos es tedioso y propenso a errores. Esta plataforma automatiza ese cálculo y presenta las opciones de forma visual.

## Usuarios principales

- **Estudiantes (viewers)**: Buscan materias, exploran combinaciones de horarios, descargan en Excel.
- **Administradores de cursos (creators)**: Cargan y mantienen el catálogo de materias, profesores, secciones y horarios disponibles.

## Stack Técnico

### Frontend
- **Framework**: Next.js 15 (App Router)
- **UI**: React 19 + TypeScript 5
- **Estilos**: Tailwind CSS 4 + shadcn/ui (Radix UI primitives)
- **Forms**: React Hook Form + Zod
- **Auth**: JWT en localStorage (manual, sin librerías de sesión)
- **Puerto**: 3000

### Backend
- **Framework**: FastAPI (Python 3.11)
- **ORM**: SQLAlchemy
- **Validación**: Pydantic
- **Algoritmo**: NumPy (matrices de horarios 12×6)
- **Auth**: JWT (HS256)
- **DB**: SQLite (dev/test) o MySQL (producción)
- **Puerto**: 8000

### Infraestructura
- **Desarrollo**: Docker + Docker Compose (hot-reload)
- **Producción**: Azure App Service (MySQL + SSL)

## Estructura de Datos

```
Teacher  ──< Course >──< CourseSchedule
                ↑
         (teacher_id)

Profile  ──< Comment >──< Course (opcional)
```

### Entidades Principales

| Entidad | Rol | Detalles |
|---------|-----|----------|
| **Profile** | Usuario | email único, role (creator\|viewer), password_hash, auditoría (created_at, updated_at) |
| **Teacher** | Docente | full_name único, creado on-demand |
| **Course** | Materia/Sección | subject, code (4 dígitos, único), teacher_id, puede estar asociado a múltiples horarios |
| **CourseSchedule** | Bloque de clase | day (Lun–Sáb), start_time, end_time, course_id |
| **Comment** | Feedback | content, profile_id, course_id (opcional), timestamps |

### Reglas de Negocio

- **Código de curso**: Exactamente 4 dígitos, único en la BD.
- **Horarios**: Las horas están en rango [07:00, 19:00], end > start.
- **Overlap**: No hay solapamientos de horarios para un mismo profesor (validado en create/update).
- **Matriz de horarios**: Representada internamente como array NumPy de 12×6 (12 horas × 6 días).
  - Filas: horas 07:00–18:00
  - Columnas: lunes–sábado
  - Valores: código del curso (0 = libre)
  - Conflicto: cualquier celda (hora × día) con valor no-cero en dos matrices simultáneamente

## Flujos Centrales

### Flujo Principal: Generar Horarios

1. Usuario accede a `/` (home)
2. Busca materias vía `SubjectSearch` → `GET /courses/search/subjects?query=`
3. Para cada materia, selecciona:
   - Profesores específicos (opcional)
   - Códigos de sección (opcional)
   - Si ambos vacíos → todos los de esa materia
4. Define bloques de tiempo libre (freetime) por día
5. Envía `POST /generate-schedules` con preferencias
6. Backend retorna lista de `ScheduleResponse` (todas las combinaciones válidas)
7. Frontend muestra matriz visual, permite paginar y exportar a Excel

### Flujo de Autenticación

1. Usuario se registra: `POST /auth/signup` (nombre, email, contraseña, rol)
2. Backend retorna perfil (sin token)
3. Usuario inicia sesión: `POST /auth/login` (email, contraseña)
4. Backend retorna JWT
5. Frontend guarda JWT en `localStorage["authToken"]`
6. Toda petición autenticada adjunta header `Authorization: Bearer <token>`
7. Al cerrar sesión, se limpia `localStorage`

### Flujo de CRUD de Cursos (Creator-only)

1. Creator accede a `/courses` (ruta protegida)
2. Ve listado de sus cursos: `GET /courses`
3. Crea/edita/elimina via `POST/PUT/DELETE /courses/{id}`
4. Al crear/editar, especifica:
   - Materia (subject)
   - Código de sección (code)
   - Profesor (nombre o nuevo)
   - Horarios (día, hora inicio, hora fin)

## Convenciones y Patrones

### Frontend

- **Rutas protegidas**: Usan componente `<ProtectedRoute>` que chequea `useAuth()` y redirige a `/login`
- **Client Components**: Todo es `"use client"` — no hay Server Components con lógica de datos
- **API Client**: Centralizado en `src/lib/api-client.ts::getApiUrl()` — construye URLs con `NEXT_PUBLIC_API_URL` (inyectado en build-time)
- **Contextos globales**:
  - `AuthContext` (`src/app/auth-context.tsx`) — JWT, perfil, funciones de login/signup
  - `SettingsContext` (`src/app/settings-context.tsx`) — tema, colores, fuente, accesibilidad
- **Headers de peticiones**: Token JWT adjuntado manualmente en cada fetch (no hay interceptor global)

### Backend

- **Routers**: Cada recurso (auth, courses, comments, schedule) en su propio router
- **Auth**: Dependencias FastAPI (`get_current_user`, `get_current_creator`) validan JWT
- **BD**: `get_db()` inyecta sesión SQLAlchemy; en tests es overrideado con SQLite in-memory
- **Selección de BD**: En import-time (`app/database.py`):
  - `ENV=test` → SQLite in-memory
  - `DB_ENGINE=sqlite` → SQLite file
  - resto → MySQL vía `DB_USER`, `DB_PASS`, `DB_HOST`, `DB_PORT`, `DB_NAME`

### Horarios

- Representados como matriz NumPy 12×6 internamente
- Códigos de curso como valores de celda; 0 = libre
- Conflict-free: ningún código repetido en la misma fila (hora) del mismo usuario
- Idiomas: Generación acepta días en inglés y español; BD usa español sin acentos (Lunes, Miercoles)
- Horas: 07:00–18:00 en bloques de 1 hora

## Variables de Entorno Clave

| Variable | Default | Notas |
|----------|---------|-------|
| `ENV` | `local` | Controla engine BD, CORS, auto-create de tablas |
| `DB_ENGINE` | `mysql` | `sqlite` para dev local |
| `DB_USER`, `DB_PASS`, `DB_HOST`, `DB_PORT`, `DB_NAME` | — | Credenciales MySQL |
| `SECRET_KEY` | — | Requerido en producción (JWT signing) |
| `ALGORITHM` | `HS256` | Algoritmo JWT |
| `FRONTEND_URL` | URL Azure | Origen CORS en prod |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | URL base de API (inlinizada en build frontend) |

## Principios de Desarrollo

1. **Cambios pequeños, verificables y reversibles** — Commits atómicos, PRs enfocados
2. **Simplicidad sobre inteligencia** — Trade-offs explícitos, documentados
3. **Documentar decisiones** — Especialmente arquitectura y cambios significativos en `docs/`
4. **Lenguaje**: Comentarios de código en español; documentación en español; API responses bilingües si aplica

## Notas sobre Despliegue

- **Desarrollo local**: Docker Compose con SQLite y hot-reload
- **Producción**: Azure App Service, MySQL con certificado SSL (Baltimore Cyber Trust), variables de entorno seguras
- **CORS**: Controlado por `FRONTEND_URL` en backend; frontend valida con `NEXT_PUBLIC_API_URL`
- **SSL**: MySQL en producción fuerza `ssl_ca=/app/certs/BaltimoreCyberTrustRoot.crt.pem`
