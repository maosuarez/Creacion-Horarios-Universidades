# Importar todos los modelos para que SQLAlchemy los registre antes del create_all
from app.models.profile import Profile  # noqa: F401
from app.models.saved_schedule import SavedSchedule  # noqa: F401
from app.models.shared_schedule import SharedSchedule  # noqa: F401
