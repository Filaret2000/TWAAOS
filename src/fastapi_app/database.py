from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Obținem URL-ul bazei de date din variabilele de mediu
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/twaaos"
)

# Creăm engine-ul SQLAlchemy
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Creăm clasa SessionLocal pentru a crea sesiuni de bază de date
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Creăm clasa Base pentru modelele SQLAlchemy
Base = declarative_base()

def get_db():
    """
    Funcție pentru obținerea unei sesiuni de bază de date
    """
    db = SessionLocal()
    try:
        return db
    except:
        db.close()
        raise
