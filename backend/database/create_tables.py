from backend.database.database import engine, Base
from backend.database import models  # noqa: F401  (import so tables register)

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done. Tables created in your Neon database.")
