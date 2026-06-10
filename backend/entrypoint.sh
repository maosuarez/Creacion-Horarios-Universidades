#!/bin/sh
set -e

# Ejecutar create_all una sola vez antes de que arranquen los workers.
# Esto evita el race condition que ocurre cuando --workers N > 1
# y cada worker intenta CREATE TABLE simultáneamente.
python -c "import app.models; from app.database import Base, engine; Base.metadata.create_all(bind=engine)"

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
