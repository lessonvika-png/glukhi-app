import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime, timezone

# Завантажуємо змінні з файлу .env (там лежить адреса бази даних Neon)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="korystuvach")  # "korystuvach" або "perekladach"

    recordings = relationship("Recording", back_populates="translator")


class Recording(Base):
    __tablename__ = "recordings"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, nullable=False)
    youtube_video_id = Column(String, nullable=False)
    translator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, default="pending")  # "pending" / "confirmed" / "rejected"
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    translator = relationship("User", back_populates="recordings")


# Ця команда створює таблиці у базі даних Neon, якщо їх ще нема
Base.metadata.create_all(bind=engine)