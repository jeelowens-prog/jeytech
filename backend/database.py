import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("ENV", "dev")
DATABASE_URL = os.getenv("DATABASE_URL")

# Sécurité prod
if ENV == "prod" and not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is required in production")

# Fallback uniquement en dev
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./jerrytech.db"

# Fix Render postgres://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
