import os
from fastapi import Depends, FastAPI
from sqlalchemy import text

from app.routers import comment, courses, schedule, auth
from app.routers import saved_schedules, shared_schedules
from app.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware
from app.database import get_db
from sqlalchemy.orm import Session

# Importar todos los modelos para que SQLAlchemy los registre
import app.models  # noqa: F401

# Nota: create_all se ejecuta en entrypoint.sh (una sola vez, antes de
# que los workers arranquen) para evitar race conditions con --workers > 1.
# En dev local sin Docker: ejecutar `python -m app.init_db` o usar SQLite.
ENV_MODE = os.getenv("ENV", "local").lower()
if ENV_MODE in ("local", "test"):
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Creacion de Horarios",
    description="API con autenticación JWT y base de datos con los horarios posibles",
    version="1.0.0",
    redirect_slashes=False,
)

# ---------------------------------------------------------
# CORS dinámico según entorno
# ---------------------------------------------------------

ENV = os.getenv("ENV", "local").lower()

if ENV == "local":
    allow_origins = ["http://localhost:3000", "*"]
else:
    allow_origins = [
        os.getenv("FRONTEND_URL", "http://localhost:3000")
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Rutas
# ---------------------------------------------------------

app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(comment.router)
app.include_router(schedule.router)
app.include_router(saved_schedules.router)
app.include_router(shared_schedules.router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "API funcionando correctamente"}

@app.get("/debug/routes-markdown")
def list_routes_markdown():
    if os.getenv("ENV") != "local":
        return {"content": "Tan re bobo"}
    markdown = "# Endpoints disponibles\n\n"
    for route in app.routes:
        markdown += f"- `{route.path}` → {', '.join(route.methods)}\n"
    return {"markdown": markdown}

@app.get("/health-db")
def health_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "unreachable",
            "detail": str(e),
            "Version": "10:01 12/03/25"
        }

# ---------------------------------------------------------
# Uvicorn en modo standalone
# ---------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
