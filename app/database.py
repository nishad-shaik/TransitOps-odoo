from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from app.config import Config

# SQLite optimization: 
engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False} if Config.SQLALCHEMY_DATABASE_URI.startswith("sqlite") else {}
)

SessionLocal = scoped_session(
    sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
)