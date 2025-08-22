"""Database configuration and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import structlog

from services.api.config import settings
from services.api.models.base import Base

logger = structlog.get_logger(__name__)

# Create database engine
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    # Use StaticPool for SQLite in development
    poolclass=StaticPool if "sqlite" in settings.database_url else None,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Get database session dependency."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error("Database session error", error=str(e))
        db.rollback()
        raise
    finally:
        db.close()


def create_tables() -> None:
    """Create all database tables."""
    logger.info("Creating database tables")
    Base.metadata.create_all(bind=engine)


def drop_tables() -> None:
    """Drop all database tables."""
    logger.warning("Dropping all database tables")
    Base.metadata.drop_all(bind=engine)


async def init_db() -> None:
    """Initialize database with sample data."""
    logger.info("Initializing database")
    
    # Create tables
    create_tables()
    
    # TODO: Add sample data seeding
    logger.info("Database initialization complete")


async def close_db() -> None:
    """Close database connections."""
    logger.info("Closing database connections")
    engine.dispose()
