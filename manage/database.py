from dotenv import load_dotenv
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

load_dotenv()  # <-- This line is important!
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
sync_engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,          # default 5
    max_overflow=20,       # default 10
    pool_timeout=60,       # default 30s
    pool_recycle=1800,     # recycle every 30 min
    pool_pre_ping=True,    # validate stale conns
)

SessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

