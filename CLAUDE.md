# CLAUDE.md — creacion-horarios (monorepo)

Generador de horarios universitarios. Monorepo con dos servicios:
- `frontend/` → Next.js (App Router, TS, shadcn/ui, Tailwind, Radix). Puerto 3000.
- `backend/`  → FastAPI (Python 3.11, SQLAlchemy, Pydantic, numpy). Puerto 8000.

## MCP Tools: code-review-graph

**IMPORTANT: This project has a knowledge graph. ALWAYS use the
code-review-graph MCP tools BEFORE using Grep/Glob/Read to explore
the codebase.** The graph is faster, cheaper (fewer tokens), and gives
you structural context (callers, dependents, test coverage) that file
scanning cannot.

### When to use graph tools FIRST

- **Exploring code**: `semantic_search_nodes` or `query_graph` instead of Grep
- **Understanding impact**: `get_impact_radius` instead of manually tracing imports
- **Code review**: `detect_changes` + `get_review_context` instead of reading entire files
- **Finding relationships**: `query_graph` with callers_of/callees_of/imports_of/tests_for
- **Architecture questions**: `get_architecture_overview` + `list_communities`

Fall back to Grep/Glob/Read **only** when the graph doesn't cover what you need.

| Tool | Use when |
|------|----------|
| `detect_changes` | Reviewing code changes — gives risk-scored analysis |
| `get_review_context` | Need source snippets for review — token-efficient |
| `get_impact_radius` | Understanding blast radius of a change |
| `get_affected_flows` | Finding which execution paths are impacted |
| `query_graph` | Tracing callers, callees, imports, tests, dependencies |
| `semantic_search_nodes` | Finding functions/classes by name or keyword |
| `get_architecture_overview` | Understanding high-level codebase structure |
| `refactor_tool` | Planning renames, finding dead code |

## Arrancar el proyecto (Docker)

```bash
# Desarrollo — hot-reload + SQLite (recomendado para empezar)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Producción / stack completo con MySQL
docker compose up --build
```

Frontend: http://localhost:3000 · Backend: http://localhost:8000 · API docs: http://localhost:8000/docs

## frontend/ — Next.js

```bash
cd frontend
npm install
npm run dev    # dev server :3000
npm run build  # production build
npm run lint   # ESLint
```

### Arquitectura frontend

- App Router bajo `src/app/`, componentes en `src/components/`, utilidades en `src/lib/`.
- **Providers** (`src/app/providers.tsx`): `AuthProvider` envuelve `SettingsProvider`.
  Ambos usan React Context y guardan estado en `localStorage`.
- **API**: todo fetch pasa por `src/lib/api-client.ts::getApiUrl` que antepone
  `NEXT_PUBLIC_API_URL`. El token JWT se adjunta manualmente como header `Bearer`.
- **CLAVE**: `NEXT_PUBLIC_API_URL` se inlinea en build-time y corre en el NAVEGADOR
  del cliente. NUNCA usar un nombre de servicio Docker (`backend:8000`) — el
  navegador no puede resolverlo. Usar `http://localhost:8000` en local.
- **Auth** (`src/app/auth-context.tsx`): JWT en localStorage, roles `creator`|`viewer`.
  `ProtectedRoute` redirige a usuarios no autenticados.
- **Flujo principal**: `ScheduleGenerator` → `POST /courses/generate` → `ScheduleDisplay`
  (matriz de horarios, paginación, export Excel).
- **Settings** (`src/app/settings-context.tsx`): tema, colores, fuente, densidad,
  accesibilidad — aplicados via CSS custom properties en `<html>`.
- **UI** (`src/components/ui/`): primitivos shadcn/ui. No editar directamente; componer.

## backend/ — FastAPI

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload     # dev :8000
pytest -vv --cov=app              # tests con cobertura
pytest tests/test_schedule.py -vv # un solo archivo
```

### Arquitectura backend

| Capa | Ubicación | Rol |
|---|---|---|
| Models | `app/models/` | SQLAlchemy ORM — definición de tablas |
| Schemas | `app/schemas/` | Pydantic — formas de request/response |
| Routers | `app/routers/` | Handlers FastAPI (lógica de negocio aquí también) |
| Auth | `app/auth.py` | Creación/verificación JWT + dependencias FastAPI |
| Database | `app/database.py` | Selección de engine + provider `get_db` |

### Selección de engine (`app/database.py`, en import-time)

- `ENV=test` → SQLite in-memory (siempre, sin importar `DB_ENGINE`)
- `DB_ENGINE=sqlite` → SQLite file en `SQLITE_PATH` (default `./data/dev.db`)
- resto → MySQL vía PyMySQL usando `DB_USER/DB_PASS/DB_HOST/DB_PORT/DB_NAME`

**Nota SSL**: SSL es opt-in vía `DB_SSL_CA`. Si la variable está vacía o el archivo
no existe, MySQL conecta sin SSL (funciona en Docker local sin cert). Para
proveedores que requieren cert, definir `DB_SSL_CA=/ruta/al/cert.pem`.

### Auth

Roles en `Profile.role`: `creator` (escritura) y `viewer` (solo lectura).
- Rutas protegidas: dependen de `get_current_user`
- Rutas solo creator: dependen de `get_current_creator`
(Ambas en `app/auth.py`)

### Algoritmo de generación (`app/routers/schedule.py`)

Clase `ScheduleGenerator`. Representa horarios como matrices numpy 12×6
(filas = horas 7–18, cols = Lun–Sáb). Código de curso = valor de celda; 0 = libre.
Conflicto = cualquier celda no-cero en ambas matrices. Freetime fuerza celdas a 0.

### Tests

`tests/test_database.py` **debe importarse antes** de `app.main` en cualquier test —
fija `ENV=test` y hace override de `get_db` con StaticPool SQLite.
Todos los fixtures deben usar `TestingSessionLocal` de ese módulo.

### Variables de entorno clave

| Var | Default | Notas |
|---|---|---|
| `ENV` | `local` | Controla engine DB + CORS + auto-create de tablas |
| `DB_ENGINE` | `mysql` | `sqlite` para dev local |
| `SECRET_KEY` | — | Requerido en producción para firmar JWT |
| `ALGORITHM` | `HS256` | Algoritmo JWT |
| `FRONTEND_URL` | `http://localhost:3000` | Origen CORS en entornos no-local |
| `DB_SSL_CA` | `` (vacío) | Ruta al cert SSL MySQL; vacío = sin SSL |

## Principios de trabajo

- Cambios pequeños, verificables y reversibles.
- Simplicidad sobre inteligencia. Trade-offs explícitos.
- Documentar decisiones de arquitectura en `docs/`.
