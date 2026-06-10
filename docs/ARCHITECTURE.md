# Arquitectura — Generador de Horarios Universitarios

## Visión General

El proyecto es un monorepo con dos servicios desacoplados comunicándose vía HTTP/REST:
- **Frontend**: Next.js en puerto 3000 (navegador del cliente)
- **Backend**: FastAPI en puerto 8000 (API REST)

Ambos pueden desarrollarse, testearse y desplegarse independientemente.

## Estructura de Directorios

```
creacion-horarios/
│
├── frontend/                       # Next.js 15 App Router
│   ├── src/
│   │   ├── app/                    # Rutas (App Router) y layouts globales
│   │   │   ├── layout.tsx          # Layout raíz (html, body, Providers)
│   │   │   ├── page.tsx            # Home: landing + generador de horarios
│   │   │   ├── (auth)/             # Rutas de autenticación (sin layout especial)
│   │   │   │   ├── login/page.tsx
│   │   │   │   └── signup/page.tsx
│   │   │   ├── courses/            # CRUD de cursos (creator-only)
│   │   │   │   └── page.tsx
│   │   │   ├── profile/            # Perfil de usuario (protegido)
│   │   │   │   └── page.tsx
│   │   │   ├── settings/           # Configuración de apariencia
│   │   │   │   └── page.tsx
│   │   │   ├── auth-context.tsx    # Context: autenticación
│   │   │   ├── settings-context.tsx # Context: tema, colores, accesibilidad
│   │   │   ├── globals.css         # Estilos globales + CSS custom props
│   │   │   └── providers.tsx       # Envuelve app con Providers
│   │   │
│   │   ├── components/
│   │   │   ├── ui/                 # Primitivos shadcn/ui (Button, Card, Input, etc.)
│   │   │   ├── schedule-generator.tsx   # Orquesta búsqueda + selección + generación
│   │   │   ├── schedule-display.tsx     # Renderiza matriz de horarios + paginación
│   │   │   ├── course-form.tsx          # Formulario CRUD de cursos
│   │   │   ├── subject-search.tsx       # Búsqueda typeahead de materias
│   │   │   ├── navbar.tsx               # Barra de navegación
│   │   │   ├── protected-route.tsx      # HOC para rutas autenticadas
│   │   │   └── ...                      # Otros componentes reutilizables
│   │   │
│   │   ├── lib/
│   │   │   ├── api-client.ts       # Cliente HTTP centralizado, getApiUrl()
│   │   │   ├── utils.ts            # Utilidades (cn, formateo, etc.)
│   │   │   └── ...
│   │   │
│   │   ├── types/
│   │   │   ├── settings.ts         # Tipos para theme/colors/accesibilidad
│   │   │   └── ...
│   │   │
│   │   └── config/
│   │       └── color-schemes.ts    # Paletas de colores disponibles
│   │
│   ├── public/                      # Assets estáticos
│   ├── package.json                # Dependencies, scripts (dev, build, lint)
│   ├── tsconfig.json               # Configuración TypeScript
│   ├── next.config.ts              # Configuración Next.js
│   └── tailwind.config.ts          # Configuración Tailwind CSS
│
├── backend/                         # FastAPI Python
│   ├── app/
│   │   ├── models/                 # SQLAlchemy ORM
│   │   │   ├── __init__.py
│   │   │   ├── profile.py          # Profile, UserRole enum
│   │   │   ├── course.py           # Course, Teacher, CourseSchedule
│   │   │   ├── comment.py          # Comment
│   │   │   └── base.py             # Base declarative, mixins de auditoría
│   │   │
│   │   ├── schemas/                # Pydantic request/response
│   │   │   ├── __init__.py
│   │   │   ├── auth.py             # SignupRequest, LoginRequest, ProfileResponse
│   │   │   ├── course.py           # CourseCreate, CourseUpdate, CourseResponse
│   │   │   ├── schedule.py         # ScheduleRequest, ScheduleResponse
│   │   │   ├── comment.py          # CommentCreate, CommentResponse
│   │   │   └── ...
│   │   │
│   │   ├── routers/                # Endpoints (lógica de negocio aquí)
│   │   │   ├── __init__.py
│   │   │   ├── auth.py             # /auth (signup, login, profile CRUD)
│   │   │   ├── courses.py          # /courses (CRUD, search, filters)
│   │   │   ├── schedule.py         # /generate-schedules (algoritmo)
│   │   │   ├── comment.py          # /comments (CRUD)
│   │   │   └── health.py           # /health, /health-db
│   │   │
│   │   ├── auth.py                 # JWT (crear, verificar), dependencias
│   │   ├── database.py             # Engine selection (SQLite/MySQL), SessionLocal, get_db
│   │   ├── config.py               # Variables de entorno + Settings
│   │   ├── main.py                 # FastAPI app, CORS, lifespan (create tables)
│   │   └── exceptions.py           # Excepciones personalizadas
│   │
│   ├── tests/
│   │   ├── conftest.py             # Fixtures comunes (TestingSessionLocal)
│   │   ├── test_database.py        # Configura ENV=test, override get_db
│   │   ├── test_auth.py
│   │   ├── test_courses.py
│   │   ├── test_schedule.py
│   │   └── ...
│   │
│   ├── requirements.txt            # Dependencies (fastapi, sqlalchemy, pydantic, numpy)
│   ├── pytest.ini                  # Configuración pytest
│   └── .env.example                # Variables de entorno (plantilla)
│
├── docker-compose.yml              # Producción: frontend + backend + MySQL
├── docker-compose.dev.yml          # Override dev: SQLite, hot-reload
├── Dockerfile (frontend)           # Build Next.js
├── Dockerfile (backend)            # Build FastAPI
├── CLAUDE.md                       # Instrucciones del proyecto (este repo)
└── docs/                           # Documentación (este directorio)
    ├── README.md                   # Índice de documentación
    ├── CONTEXT.md                  # Contexto del proyecto
    ├── ARCHITECTURE.md             # Este archivo
    ├── API.md                      # Endpoints REST
    ├── DATABASE.md                 # Modelos y esquema
    ├── TECHNOLOGIES.md             # Stack tecnológico detallado
    └── DEPLOYMENT.md               # Despliegue local y producción
```

## Flujo de Datos

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  SubjectSearch (GET /courses/search/subjects?query=)             │
│        ↓                                                          │
│  ScheduleGenerator (selecciona materias, profesores, freetime)   │
│        ↓                                                          │
│  POST /generate-schedules {preferencias, freetime}              │
│        ↓                ↑                                         │
│  ScheduleDisplay        └─ JSON: [ScheduleResponse...]          │
│        └→ exportToExcel()  (12×6 matrix, courses, labels)       │
│                                                                   │
│  [Protected Routes via ProtectedRoute HOC]                      │
│  ├─ LoginPage (POST /auth/login)                               │
│  ├─ SignupPage (POST /auth/signup)                             │
│  ├─ ProfilePage (GET/PUT/DELETE /auth/profile)                 │
│  ├─ CoursesPage (GET/POST/PUT/DELETE /courses)                 │
│  └─ SettingsPage (local storage + CSS custom props)            │
│                                                                   │
└──────────────── NEXT_PUBLIC_API_URL (build-time) ──────────────┘
                            ↓ HTTP REST
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  /auth          ← signup, login, profile CRUD                   │
│  /courses       ← CRUD, search/subjects, search/codes, search/  │
│  /comments      ← CRUD                                          │
│  /generate-schedules ← Algoritmo numpy (conflict-free combos)  │
│  /health        ← Health check                                  │
│                                                                   │
│  Routers (Business Logic)                                       │
│        ↓                                                          │
│  SQLAlchemy ORM ← Models (Profile, Course, Teacher, etc.)      │
│        ↓                                                          │
│  Database (SQLite dev / MySQL prod)                            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Responsabilidades por Capa

### Frontend (Next.js)

| Capa | Archivo(s) | Responsabilidad |
|------|-----------|-----------------|
| **Routing** | `src/app/layout.tsx`, `page.tsx`, `[slug]/` | Definir rutas, layouts, páginas |
| **Pages** | `src/app/{courses,profile,settings}/page.tsx` | Componentes de página (entry points) |
| **Features** | `src/components/schedule-*.tsx`, `course-form.tsx` | Lógica de negocio UI (generación, CRUD) |
| **UI Primitives** | `src/components/ui/` | Componentes base reutilizables (shadcn) |
| **Navigation** | `src/components/navbar.tsx` | Navegación, links de rutas |
| **Auth** | `src/app/auth-context.tsx`, `protected-route.tsx` | Autenticación, protección de rutas |
| **Settings** | `src/app/settings-context.tsx`, `src/app/globals.css` | Tema, colores, accesibilidad (CSS vars) |
| **HTTP Client** | `src/lib/api-client.ts` | Centralización de URLs y peticiones API |
| **Utils** | `src/lib/utils.ts`, `src/types/` | Helpers, tipos |

### Backend (FastAPI)

| Capa | Archivo(s) | Responsabilidad |
|------|-----------|-----------------|
| **Routes** | `app/routers/{auth,courses,comments,schedule}.py` | Endpoints HTTP, validación request |
| **Business Logic** | `routers/*.py` | Implementación de flujos (CRUD, algoritmo) |
| **Data Models** | `app/models/*.py` | SQLAlchemy ORM, definición de tablas |
| **Schemas** | `app/schemas/*.py` | Pydantic validación y serialización |
| **Auth** | `app/auth.py` | JWT (crear, verificar), dependencias FastAPI |
| **Database** | `app/database.py` | Engine selection, SessionLocal, `get_db()` |
| **Config** | `app/config.py` | Variables de entorno, Settings |
| **Main** | `app/main.py` | FastAPI app initialization, CORS, lifespan |

## Patrones Clave

### Frontend

1. **Client Components Only** — Todo es `"use client"`. No hay Server Components con data fetching.
2. **Context API** — `AuthContext` y `SettingsContext` persisten en localStorage.
3. **Centralized API Client** — `getApiUrl(endpoint)` construye URLs con `NEXT_PUBLIC_API_URL` inyectada en build.
4. **Protected Routes** — `<ProtectedRoute>` HOC redirige a `/login` si no hay token.
5. **Manual JWT Headers** — Cada fetch adjunta `Authorization: Bearer <token>` manualmente (no hay interceptor).

### Backend

1. **Dependency Injection** — FastAPI `Depends()` para auth (`get_current_user`, `get_current_creator`), BD (`get_db`).
2. **ORM + Schemas** — Separación entre SQLAlchemy models (BD) y Pydantic schemas (API contracts).
3. **Router-Based Organization** — Cada recurso en su router, importados en `main.py`.
4. **Eager Loading** — Relaciones se cargan con `selectinload()` en queries para evitar N+1.
5. **Validation in Schemas** — Pydantic `Field()` y validadores personalizados, no en modelos.

## Decisiones Arquitectónicas Clave

### 1. Separación Frontend-Backend
**Por qué**: Permite desarrollo independiente, escalado horizontal, cambios de UI sin tocar lógica de negocio.

### 2. Monorepo vs. Multi-Repo
**Por qué monorepo**: Facilita compartir tipos (aunque actualmente no sucede), coordinar cambios API, testing integrado. Se simplifica con Docker Compose.

### 3. JWT en localStorage (Frontend)
**Por qué**: Simplicidad, sin backend de sesiones. Requiere cuidado con XSS (httpOnly no aplica en SPA puro).

### 4. SQLite para Desarrollo
**Por qué**: Cero dependencias externas, fast iteration, transacciones inline. MySQL para producción garantiza escala.

### 5. Matriz NumPy para Horarios
**Por qué**: Cálculo rápido de conflictos, representación lineal clara (12 horas × 6 días).

### 6. Roles en Profile (creator|viewer)
**Por qué**: Control simple de permisos; creators escriben catálogo, viewers consumen.

## Integración Frontend-Backend

### Flujo Típico: Generar Horarios

```
1. Usuario en Home busca materias
   Frontend: GET /courses/search/subjects?query=Cál
   Backend: SELECT DISTINCT subject FROM courses WHERE subject ILIKE '%Cál%' → Retorna {subject, count}

2. Usuario selecciona: Cálculo I + freetime (lunch 12-14)
   Frontend: POST /generate-schedules con JSON {preferencias: {...}, freetime: {...}}
   
3. Backend recibe:
   a) Parsea preferencias → Filtra cursos por profesor/código (UNION logic)
   b) Genera todas las combinaciones de cursos
   c) Para cada combo, crea matrices NumPy y chequea conflictos
   d) Retorna lista de ScheduleResponse (válidas solo)

4. Frontend renderiza ScheduleDisplay con matrices visuales, permite paginar y exportar Excel
```

### Autenticación: Flujo JWT

```
1. POST /auth/signup {name, email, password, role}
   Backend valida → Crea Profile → Retorna perfil (NO token)
   
2. POST /auth/login {username (email), password}  [OAuth2 password flow]
   Backend valida → Retorna {access_token, token_type: "bearer"}
   Frontend guarda en localStorage["authToken"]
   
3. Petición protegida: GET /auth/profile
   Frontend adjunta: Authorization: Bearer <token>
   Backend verifica JWT (HS256, SECRET_KEY) → Retorna perfil con auditoría
   
4. Si token inválido/expirado:
   Backend retorna 401
   Frontend limpia localStorage, redirige a /login
```

## Cómo los Cambios Impactan Ambos Lados

| Cambio | Impacto Frontend | Impacto Backend |
|--------|------------------|-----------------|
| Nuevo endpoint `/courses/{id}/reviews` | `api-client.ts`: agregar petición | Nuevo router + schema |
| Nuevo campo en Course (difficulty) | Actualizar tipos/schemas | Migración BD, validación Pydantic |
| Cambio de algoritmo de conflictos | Potencialmente cambio en `schedule_matrix` format | Actualizar generador NumPy |
| Nuevo rol (moderator) | UI condicional basada en rol | Nueva dependencia en routers |

## Testing

### Frontend
- No hay tests configurados actualmente.
- Componentes son funcionales (sin lógica compleja), focus en manuales.

### Backend
- `tests/` con fixtures en `conftest.py`
- `test_database.py` debe importarse primero → setea `ENV=test` e inyecta SQLite in-memory
- Todos los fixtures usan `TestingSessionLocal` de ese módulo
- Correr: `pytest -vv --cov=app`
