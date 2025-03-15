from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import config

# Crear el motor de la base de datos
engine = create_engine(config.DB_URL, connect_args={"sslmode": "require"})

# Crear una clase base para nuestros modelos
Base = declarative_base()

# Crear la sesión de la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def refresh():
    #Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()