# Documentación — Generador de Horarios Universitarios

Este directorio contiene la documentación completa del proyecto monorepo de generación de horarios universitarios. El proyecto consta de dos servicios independientes: un frontend en Next.js y un backend en FastAPI.

## Documentos Principales

- **[ARCHITECTURE.md](./docs/ARCHITECTURE.md)** — Arquitectura global del monorepo, estructura de directorios, patrones de diseño y flujo de datos entre frontend y backend.

- **[API.md](./docs/API.md)** — Referencia completa de todos los endpoints REST del backend. Incluye autenticación, operaciones CRUD, búsqueda y generación de horarios.

- **[DATABASE.md](./docs/DATABASE.md)** — Esquema de la base de datos, modelos SQLAlchemy, relaciones y restricciones de integridad.

- **[TECHNOLOGIES.md](./docs/TECHNOLOGIES.md)** — Stack tecnológico completo del proyecto: frontend (Next.js, React, TypeScript, Tailwind, shadcn/ui) y backend (FastAPI, SQLAlchemy, Pydantic, numpy).

- **[DEPLOYMENT.md](./docs/DEPLOYMENT.md)** — Guías de despliegue: desarrollo local con Docker, despliegue a Azure en producción, variables de entorno y configuración de servicios.

- **[CONTEXT.md](./docs/CONTEXT.md)** — Contexto de negocio y producto: qué es el proyecto, quiénes son los usuarios, flujos centrales y convenciones clave.

## Estructura del Proyecto

```
creacion-horarios/              # Monorepo
├── frontend/                   # Next.js 15, React 19, TS, shadcn/ui
│   ├── src/
│   │   ├── app/               # App Router (rutas, layouts, páginas)
│   │   ├── components/        # Componentes React
│   │   └── lib/               # Utilidades y cliente API
│   ├── package.json
│   └── tsconfig.json
│
├── backend/                    # FastAPI, Python 3.11
│   ├── app/
│   │   ├── models/            # Modelos SQLAlchemy
│   │   ├── schemas/           # Esquemas Pydantic (request/response)
│   │   ├── routers/           # Endpoints FastAPI
│   │   ├── auth.py            # Autenticación JWT
│   │   ├── database.py        # Configuración de BD
│   │   └── main.py            # Aplicación FastAPI
│   ├── tests/
│   ├── requirements.txt
│   └── pytest.ini
│
├── docker-compose.yml          # Stack de producción (MySQL)
├── docker-compose.dev.yml      # Override para desarrollo (SQLite)
├── CLAUDE.md                   # Instrucciones del proyecto
└── docs/                       # Esta documentación
```

## Inicio Rápido

### Desarrollo Local

```bash
# Con Docker (recomendado — hot-reload + SQLite)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Sin Docker
cd frontend && npm install && npm run dev  # :3000
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload  # :8000
```

**URLs:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs interactivos: http://localhost:8000/docs

### Producción

```bash
# Con Docker (MySQL + certificados SSL)
docker compose up --build
```

## Convenciones Clave

- **Frontend**: Todo código UI es `"use client"` (no hay Server Components con lógica de datos)
- **Auth**: JWT en `localStorage`, roles `creator` (escribir) y `viewer` (leer)
- **API**: Cliente centralizado en `src/lib/api-client.ts::getApiUrl()`
- **Horarios**: Matriz 12×6 (horas 7–18, lunes–sábado), sin conflictos
- **Idioma**: Comentarios en español, documentación en español

## Para Comenzar a Trabajar

1. Lee [CONTEXT.md](./CONTEXT.md) para entender qué es el proyecto y por qué existe.
2. Lee [ARCHITECTURE.md](./ARCHITECTURE.md) para entender cómo está organizado.
3. Consulta [API.md](./API.md) y [DATABASE.md](./DATABASE.md) según necesites (backend).
4. Revisa [TECHNOLOGIES.md](./TECHNOLOGIES.md) para el stack técnico específico.
5. Consulta [DEPLOYMENT.md](./DEPLOYMENT.md) si necesitas hacer despliegue.

## Actualizando la Documentación

- Cada documento debe ser auto-contenido y explicar el "por qué" de las decisiones.
- No copies código; documenta patrones y convenciones.
- Usa ejemplos mínimos pero funcionales.
- Mantén la documentación en sincronía con los cambios del código.
