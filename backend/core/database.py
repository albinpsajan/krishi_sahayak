"""
KrishiSahayak AI - Database setup (SQLite & SQLAlchemy).

Owns the engine, session factory and declarative Base shared by every feature
module, plus SQLite-safe lightweight migrations for demo databases.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

from config import settings

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def run_lightweight_migrations():
    """
    SQLite-safe column additions for existing databases (ALTER TABLE ADD COLUMN).
    Keeps demo databases usable when new fields are introduced in feature models.
    Note: SQLite forbids UNIQUE constraints inside ALTER TABLE ADD COLUMN,
    so uniqueness for username is enforced with a separate unique index.
    """
    migrations = [
        ('users', 'username', 'VARCHAR'),
        ('users', 'age', 'INTEGER'),
        ('users', 'profile_completed', 'BOOLEAN DEFAULT 0'),
    ]
    with engine.connect() as conn:
        for table, column, col_type in migrations:
            try:
                conn.execute(text(f'ALTER TABLE {table} ADD COLUMN {column} {col_type}'))
                conn.commit()
            except Exception:
                # Column already exists (or table not created yet) - safe to skip
                pass
        try:
            conn.execute(text('CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username ON users (username)'))
            conn.commit()
        except Exception:
            pass


def get_db():
    """FastAPI dependency yielding a request-scoped database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
