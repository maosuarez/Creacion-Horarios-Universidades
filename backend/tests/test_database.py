# tests/test_database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

print(">>> ENV LOADED =", os.getenv("ENV"))
print(">>> DB_ENGINE =", os.getenv("DB_ENGINE"))

# Forzamos ENV=test para asegurar memoria
os.environ["ENV"] = "test"
os.environ["DB_ENGINE"] = "sqlite"

from app.database import Base, get_db   # <-- después de setear ENV
from app.main import app                # <-- después de setear ENV
from fastapi.testclient import TestClient

# Engine exclusivo para tests
engine_test = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_test
)

Base.metadata.create_all(bind=engine_test)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides.clear()
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

