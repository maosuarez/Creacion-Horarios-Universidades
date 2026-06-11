from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("ENV", "local").lower()
DB_ENGINE = os.getenv("DB_ENGINE", "mysql").lower()

# ==========================================
# Selección automática del motor
# ==========================================

# 1. Tests SIEMPRE deben usar SQLite in-memory
if ENV == "test":
    DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

# 2. SQLite para entorno local
elif DB_ENGINE == "sqlite":
    sqlite_path = os.getenv("SQLITE_PATH", "./data/dev.db")
    os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
    DATABASE_URL = f"sqlite:///{sqlite_path}?check_same_thread=False"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

# 3. MySQL para producción / local
else:
    _base_url = (
        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    # SSL es opt-in: se activa solo si DB_SSL_CA apunta a un archivo existente.
    # En local (Docker sin cert) no se define DB_SSL_CA → sin SSL.
    # En Azure u otro proveedor con cert, definir DB_SSL_CA=/ruta/al/cert.pem.
    _ssl_ca = os.getenv("DB_SSL_CA", "")
    if _ssl_ca and os.path.isfile(_ssl_ca):
        DATABASE_URL = f"{_base_url}?ssl_ca={_ssl_ca}"
    else:
        DATABASE_URL = _base_url
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# ==========================================
# Dependency injection
# ==========================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
