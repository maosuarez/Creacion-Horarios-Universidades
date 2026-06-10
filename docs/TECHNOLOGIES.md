# Stack Tecnológico

Este documento detalla todas las tecnologías, librerías y herramientas utilizadas en el proyecto.

## Frontend (Next.js)

### Core Frameworks

| Librería | Versión | Uso |
|----------|---------|-----|
| **Next.js** | 15 | Framework fullstack (App Router, SSR, SSG, assets optimization) |
| **React** | 19 | Librería de componentes declarativos para UI |
| **TypeScript** | 5 | Tipado estático (dev-time checking) |
| **Node.js** | 18+ | Runtime para dev server y build |

### UI y Estilos

| Librería | Uso |
|----------|-----|
| **Tailwind CSS** | Framework CSS utility-first (responsive, composable) |
| **shadcn/ui** | Componentes accesibles reutilizables (Radix UI + Tailwind) |
| **Radix UI** | Primitivos de UI sin estilo (accesibilidad WCAG) |
| **Lucide React** | Iconografía SVG ligera (descargar como componentes) |
| **next-themes** | Gestión de temas (light/dark mode compatible con SSR) |
| **tailwindcss-animate** | Plugin de Tailwind para animaciones CSS |

### Formularios y Validación

| Librería | Uso |
|----------|-----|
| **React Hook Form** | Gestión de formularios performante (minimiza re-renders) |
| **Zod** | Validación de esquemas TypeScript-first |
| **@hookform/resolvers** | Integración de Zod con React Hook Form |

### Utilidades

| Librería | Uso |
|----------|-----|
| **clsx** | Construcción condicional de strings de clases CSS |
| **tailwind-merge** | Resolución de conflictos en clases Tailwind |
| **date-fns** | Manipulación y formateo de fechas |
| **Recharts** | Visualización de datos (gráficos interactivos) |

### Herramientas de Desarrollo

| Herramienta | Uso |
|-------------|-----|
| **ESLint** | Linting de código (detecta problemas y estilos) |
| **npm** | Gestor de dependencias y scripts |

---

## Backend (FastAPI)

### Core Frameworks

| Librería | Uso |
|----------|-----|
| **FastAPI** | Framework web asincrónico para APIs REST (auto-docs OpenAPI) |
| **Python** | 3.11+ (lenguaje, async/await, type hints) |
| **Uvicorn** | ASGI server (servidor de desarrollo y producción) |

### Base de Datos

| Librería | Uso |
|----------|-----|
| **SQLAlchemy** | ORM SQL (mapeo de modelos a tablas, queries type-safe) |
| **PyMySQL** | Driver MySQL puro en Python (alternativa a mysqlclient) |
| **sqlite3** | Driver SQLite (incluido en Python stdlib) |

### Validación

| Librería | Uso |
|----------|-----|
| **Pydantic** | Validación y serialización de datos (type-safe) |
| **python-multipart** | Parseo de formularios (OAuth2 password flow) |

### Seguridad y Autenticación

| Librería | Uso |
|----------|-----|
| **python-jose** | Creación y verificación de JWT |
| **passlib[bcrypt]** | Hash de contraseñas (bcrypt algorithm) |
| **PyJWT** | Alternativa a python-jose (validación JWT) |

### Computación

| Librería | Uso |
|----------|-----|
| **numpy** | Arrays multidimensionales (matrices 12×6 para horarios) |

### Testing

| Librería | Uso |
|----------|-----|
| **pytest** | Framework de testing (fixtures, assertions, plugins) |
| **pytest-cov** | Coverage reports (% de líneas testeadas) |
| **httpx** | Cliente HTTP asincrónico (testing de endpoints) |

### Utilidades

| Librería | Uso |
|----------|-----|
| **python-dotenv** | Carga de variables de entorno desde `.env` |
| **slugify** | Normalización de strings (slugs, URLs) |

---

## Infraestructura

### Desarrollo Local

| Herramienta | Versión | Uso |
|-------------|---------|-----|
| **Docker** | 20+ | Contenedorización (aislamiento de servicios) |
| **Docker Compose** | 2+ | Orquestación de servicios (frontend + backend + BD) |

### Producción

| Servicio | Uso |
|----------|-----|
| **Azure App Service** | Hosting de aplicaciones (frontend + backend) |
| **Azure Database for MySQL** | BD MySQL completamente manejada |
| **SSL/TLS** | Certificado Baltimore Cyber Trust (Azure CA) |

### Versionado

| Herramienta | Uso |
|-------------|-----|
| **Git** | Control de versión distribuido |
| **GitHub** | Repositorio remoto y CI/CD (si se configura) |

---

## Configuración y Estructura

### Frontend

```
frontend/
├── next.config.ts          # Configuración Next.js (rewrites, redirects)
├── tsconfig.json           # Configuración TypeScript
├── tailwind.config.ts      # Configuración Tailwind CSS
├── postcss.config.js       # Procesamiento PostCSS
├── package.json            # Dependencias npm
└── .env.local              # Variables de entorno locales
```

### Backend

```
backend/
├── app/
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas
│   ├── routers/            # Endpoints FastAPI
│   ├── auth.py             # JWT, dependencias auth
│   ├── database.py         # Configuración BD (SQLite/MySQL)
│   ├── config.py           # Settings, variables de entorno
│   ├── main.py             # Aplicación FastAPI
│   └── exceptions.py       # Excepciones custom
├── tests/                  # Test suite
├── requirements.txt        # Dependencias pip
├── pytest.ini              # Configuración pytest
└── .env.example            # Plantilla variables de entorno
```

---

## Variables de Entorno Críticas

### Frontend (build-time)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000  # URL del backend (inlineada en JS)
```

**Nota**: `NEXT_PUBLIC_*` se compila en el bundle JavaScript. El navegador del cliente lo usa directamente. No usar nombres de servicio Docker.

### Backend (runtime)

```bash
ENV=local                              # local | test | production
DB_ENGINE=sqlite                       # sqlite | mysql
SQLITE_PATH=./data/dev.db              # Path a fichero SQLite
DB_USER=root                           # Credencial MySQL
DB_PASS=password                       # Credencial MySQL
DB_HOST=localhost                      # Host MySQL
DB_PORT=3306                           # Puerto MySQL
DB_NAME=schedule_db                    # BD MySQL
SECRET_KEY=your-secret-key-here        # JWT signing (requerido en prod)
ALGORITHM=HS256                        # JWT algorithm
FRONTEND_URL=http://localhost:3000     # CORS origin
```

---

## Decisiones Tecnológicas

### Por qué Next.js (Frontend)

- **App Router**: Rutas basadas en directorios, composición clara
- **TypeScript integrado**: Type safety sin configuración extra
- **Tailwind + shadcn**: Componentes accesibles, mantenibles
- **Build optimizado**: Code splitting, tree-shaking automático

### Por qué FastAPI (Backend)

- **Performance**: Async first, comparado con Flask/Django
- **OpenAPI auto-generado**: Documentación interactiva en `/docs`
- **Validación Pydantic**: Type hints = esquemas automáticos
- **Moderno**: Python 3.11+, async/await nativo

### Por qué SQLAlchemy

- **Type-safe ORM**: Queries validadas en tiempo de compilación (con mypy)
- **Multi-BD**: Mismo código soporta SQLite, MySQL, PostgreSQL
- **Relationships automáticas**: Eager loading, lazy loading controlado

### Por qué NumPy para Horarios

- **Rapidez**: Cálculo vectorizado (sin loops Python)
- **Claridad**: Matriz 12×6 es representación intuitiva
- **Interoperabilidad**: Fácil de serializar a JSON

### Por qué JWT en localStorage

- **Simplicidad**: Sin servidor de sesiones
- **Stateless**: Escala horizontalmente
- **Cuidado XSS**: No usar httpOnly en SPA (trade-off conocido)

---

## Alternativas Consideradas

### Frontend

| Alternativa | Por qué no |
|-------------|-----------|
| **Gatsby** | Overkill para SPA; Next.js App Router más flexible |
| **Nuxt (Vue)** | Next.js tiene mejor ecosistema y TypeScript support |
| **Svelte** | Menor comunidad; TypeScript menos integrado |
| **Material-UI** | Menos customizable; shadcn/ui mejor para Tailwind |

### Backend

| Alternativa | Por qué no |
|-------------|-----------|
| **Django** | Más pesado; FastAPI suficiente para este caso |
| **Flask** | Sin validación nativa; Pydantic en FastAPI es superior |
| **Starlette** | Es lo que corre FastAPI, pero sin helpers de alto nivel |

### BD

| Alternativa | Por qué no |
|-------------|-----------|
| **PostgreSQL** | Overkill; MySQL o SQLite son suficientes |
| **MongoDB** | Relaciones complejas; SQL es mejor opción |
| **Prisma ORM** | TypeScript/Node; backend es Python |

---

## Roadmap Técnico

### Mejoras Futuras

1. **Testing Frontend**: Agregar Jest + React Testing Library
2. **Migraciones BD**: Implementar Alembic para schema versioning
3. **Rate Limiting**: Agregar middleware en FastAPI
4. **Caching**: Redis para búsquedas frecuentes
5. **CI/CD**: GitHub Actions para tests automáticos
6. **Monitoring**: Sentry para errores en producción
7. **Logs centralizados**: ELK stack o Azure Monitor

### Decisiones Pendientes

- Web sockets para colaboración en tiempo real
- Algoritmo de horarios: optimización (nearest neighbor, genetic algorithm)
- Exportación a PDF además de Excel
