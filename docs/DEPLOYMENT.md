# Despliegue y Configuración

## Desarrollo Local

### Prerequisitos

- **Docker 20+** y **Docker Compose 2+** instalados
- **Git** configurado
- (Opcional) **Node.js 18+** y **Python 3.11+** si quieres ejecutar servicios sin Docker

### Arranque con Docker (Recomendado)

```bash
# Desarrollo: hot-reload, SQLite in-memory, sin dependencias externas
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# URLs disponibles:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs interactivos: http://localhost:8000/docs
```

**Lo que hace**:
- Frontend Next.js en puerto 3000 (con hot-reload)
- Backend FastAPI en puerto 8000 (con reload automático)
- BD SQLite en memoria (se limpia al detener)
- Volúmenes montados (cambios en código se reflejan inmediatamente)

### Arranque sin Docker (Opcional)

#### Frontend

```bash
cd frontend
npm install
npm run dev
# Disponible en http://localhost:3000
```

#### Backend

```bash
cd backend
pip install -r requirements.txt
export DB_ENGINE=sqlite  # En Windows: set DB_ENGINE=sqlite
export ENV=local
uvicorn app.main:app --reload
# Disponible en http://localhost:8000
```

### Variables de Entorno (Desarrollo)

Crea `.env` en la raíz o en cada servicio:

**Frontend** (`.env.local`):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Backend** (`.env`):
```
ENV=local
DB_ENGINE=sqlite
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
FRONTEND_URL=http://localhost:3000
```

---

## Testing

### Backend

```bash
cd backend

# Todos los tests con cobertura
pytest -vv --cov=app

# Un archivo específico
pytest tests/test_schedule.py -vv

# Un test específico
pytest tests/test_schedule.py::test_generate_no_conflict -vv
```

**Nota importante**: `tests/test_database.py` debe importarse primero en cualquier test. Configura `ENV=test` e inyecta SQLite in-memory como `get_db()`.

```python
# En conftest.py o al inicio de test_*.py
from tests.test_database import TestingSessionLocal  # IMPORTAR PRIMERO
from app.database import get_db
from fastapi.testclient import TestClient

app.dependency_overrides[get_db] = lambda: TestingSessionLocal()
```

---

## Producción

### Stack Productivo

```bash
# Todas las dependencias externas (MySQL + frontend optimizado)
docker compose up --build
```

**Lo que incluye**:
- Frontend Next.js (build optimizado, sin hot-reload)
- Backend FastAPI (Uvicorn multiworker)
- MySQL 8.0 (BD persistente)

### Variables de Entorno Producción

**Backend** (Azure App Service env vars):
```
ENV=production
DB_ENGINE=mysql
DB_USER=<azure-user>
DB_PASS=<azure-password>
DB_HOST=<mysql-host>.mysql.database.azure.com
DB_PORT=3306
DB_NAME=schedule_db
SECRET_KEY=<generate-strong-random-key>
ALGORITHM=HS256
FRONTEND_URL=https://yourdomain.com
```

**Frontend** (build-time env vars):
```
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

**Nota SSL**: El backend en Docker ya incluye el certificado Baltimore Cyber Trust (`/app/certs/BaltimoreCyberTrustRoot.crt.pem`). La URL MySQL se construye automáticamente con `ssl_ca=...`.

### Despliegue en Azure App Service

#### 1. Preparar Imagen Docker

```bash
# Build local
docker build -t creacion-horarios-frontend frontend/
docker build -t creacion-horarios-backend backend/

# Empujar a Azure Container Registry (ACR)
az acr build --registry <registry-name> --image creacion-horarios-frontend:latest frontend/
az acr build --registry <registry-name> --image creacion-horarios-backend:latest backend/
```

#### 2. Crear App Service

```bash
# Frontend
az appservice plan create --name plan-frontend --sku B2 --is-linux
az webapp create --resource-group mygroup --plan plan-frontend --name myapp-frontend

# Backend
az appservice plan create --name plan-backend --sku B2 --is-linux
az webapp create --resource-group mygroup --plan plan-backend --name myapp-backend
```

#### 3. Configurar Variables de Entorno

```bash
# Backend
az webapp config appsettings set --resource-group mygroup --name myapp-backend \
  --settings ENV=production DB_ENGINE=mysql DB_USER=... SECRET_KEY=...
```

#### 4. Desplegar Contenedor

```bash
az webapp config container set --resource-group mygroup --name myapp-backend \
  --docker-custom-image-name creacion-horarios-backend:latest \
  --docker-registry-server-url https://<registry>.azurecr.io
```

---

## Alternativas de Despliegue

### Vercel (Frontend Only)

```bash
# Conectar repositorio GitHub
# Vercel detecta Next.js automáticamente
# Deploy automático en push a main
```

**Ventajas**: Free tier, HTTPS automático, CDN global.

### AWS ECS (Contenedores)

```bash
# Build y empujar a ECR
aws ecr create-repository --repository-name creacion-horarios
docker tag creacion-horarios-backend:latest <account>.dkr.ecr.<region>.amazonaws.com/creacion-horarios:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/creacion-horarios:latest

# Crear ECS cluster y task definition
# Configurar RDS (MySQL managed)
```

### Google Cloud Run

```bash
# Build y desplegar
gcloud builds submit --tag gcr.io/myproject/creacion-horarios
gcloud run deploy creacion-horarios --image gcr.io/myproject/creacion-horarios
```

---

## Base de Datos

### SQLite (Desarrollo)

```bash
# Fichero se crea en ./data/dev.db
# Limpio en cada restart si usas `ENV=test`
```

**Backup/Restore**:
```bash
# Backup
cp ./data/dev.db ./data/dev.db.backup

# Restore
cp ./data/dev.db.backup ./data/dev.db
```

### MySQL (Producción)

#### Crear BD Inicial

```bash
# En el contenedor MySQL en desarrollo
docker exec creacion-horarios-mysql mysql -uroot -ppassword << EOF
CREATE DATABASE IF NOT EXISTS schedule_db CHARACTER SET utf8mb4;
EOF
```

#### Migraciones (Manual)

Sin Alembic actualmente. Pasos si necesitas cambiar esquema:

1. **Backup**: `mysqldump -u root -p schedule_db > backup.sql`
2. **Alterar modelos**: Modifica `app/models/*.py`
3. **Script manual**: Crea `migrations/001_add_column.sql`
4. **Ejecutar**: `mysql schedule_db < migrations/001_add_column.sql`
5. **Verificar**: Testa en dev primero

#### Monitoreo

```bash
# Conectar a BD
mysql -h <host> -u <user> -p schedule_db

# Queries útiles
SHOW TABLES;
SELECT COUNT(*) FROM profiles;
SELECT COUNT(*) FROM courses;
SHOW PROCESSLIST;  # Ver conexiones activas
```

---

## Certificados SSL

### Desarrollo

No necesarios. HTTP local es suficiente.

### Producción (Azure)

El certificado Baltimore Cyber Trust ya está incluido en la imagen Docker en `/app/certs/BaltimoreCyberTrustRoot.crt.pem`.

**Si necesitas renovar**:
```bash
# Descargar cert actualizado de Azure
curl https://cacerts.digicert.com/BaltimoreCyberTrustRoot.crt.pem \
  -o BaltimoreCyberTrustRoot.crt.pem

# Copiar a Docker
COPY BaltimoreCyberTrustRoot.crt.pem /app/certs/

# Rebuild y redeploy
```

---

## Monitoreo y Logging

### Desarrollo

Logs en consola directamente:
```bash
docker compose logs -f backend
docker compose logs -f frontend
```

### Producción (Azure)

```bash
# Ver logs de App Service
az webapp log tail --resource-group mygroup --name myapp-backend

# Configurar Application Insights
az monitor app-insights component create --app myapp --location <region>
```

---

## Escalado

### Horizontal (Múltiples Instancias)

**Azure App Service**:
```bash
az appservice plan update --name plan-backend --sku S1  # Escalar SKU
az webapp update --name myapp-backend --plan plan-backend  # Asignar nuevo plan
```

**Consideraciones**:
- Backend es stateless (JWT en cliente) → Escala bien
- Frontend es estateless (SSG) → Escala bien
- MySQL: Usar Azure Database for MySQL (managed, auto-backup)

### Vertical (Mayor Capacidad)

Aumentar CPU/RAM en el SKU del App Service (B2 → S1 → S2, etc.).

---

## Troubleshooting

### Frontend no encuentra Backend

**Síntoma**: Errores en consola del navegador "CORS" o "Failed to fetch"

**Causa**: `NEXT_PUBLIC_API_URL` incorrecto

**Solución**: 
- Local: `NEXT_PUBLIC_API_URL=http://localhost:8000`
- Producción: `NEXT_PUBLIC_API_URL=https://api.yourdomain.com`
- Verificar en `next build` output o Network tab del navegador

### Backend no conecta a MySQL

**Síntoma**: `[MYSQL] Connection refused` o `ssl: CERTIFICATE_VERIFY_FAILED`

**Causa**: Credenciales incorrectas o certificado SSL

**Solución**:
```bash
# Testear conexión
mysql -h <host> -u <user> -p <database>

# Verificar en logs
docker logs creacion-horarios-backend
```

### Tests fallan con "database locked"

**Síntoma**: `sqlite3.OperationalError: database is locked`

**Causa**: Múltiples procesos accediendo a SQLite simultáneamente

**Solución**: 
```bash
# Usar in-memory en tests (ya configurado en conftest.py)
# o aumentar timeout:
pytest --timeout=10
```

---

## Checklists

### Antes de Desplegar a Producción

- [ ] Todas las variables de entorno configuradas
- [ ] Secret key fuerte (`SECRET_KEY` de 32+ chars aleatorios)
- [ ] BD MySQL creada y accesible
- [ ] Certificado SSL válido
- [ ] CORS origin (`FRONTEND_URL`) correcto
- [ ] Tests pasan: `pytest -vv --cov=app`
- [ ] Build frontend sin warnings: `npm run build`
- [ ] Imágenes Docker construidas y testeadas

### Después de Desplegar

- [ ] URLs accesibles sin CORS errors
- [ ] Login funciona: registrar usuario, obtener token
- [ ] Generación de horarios funciona sin errores
- [ ] Descargar Excel funciona
- [ ] Logs en tiempo real monitoreados
- [ ] Backup automático de BD confirmado
