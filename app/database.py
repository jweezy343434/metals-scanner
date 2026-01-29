"""
Database models and session management
"""
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    Index,
    UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from contextlib import contextmanager
from typing import Generator
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Create engine with WAL mode for better concurrency
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class Listing(Base):
    """eBay listing data"""
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False, default="ebay")
    external_id = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    metal_type = Column(String, nullable=False)  # 'gold' or 'silver'
    weight_oz = Column(Float, nullable=True)
    weight_extraction_failed = Column(Boolean, default=False)
    url = Column(String, nullable=False)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    spread_percentage = Column(Float, nullable=True)  # Computed field

    # Indexes for performance
    __table_args__ = (
        Index('idx_metal_type', 'metal_type'),
        Index('idx_spread_percentage', 'spread_percentage'),
        Index('idx_fetched_at', 'fetched_at'),
        Index('idx_metal_spread', 'metal_type', 'spread_percentage'),  # Composite
    )

    def __repr__(self):
        return f"<Listing(id={self.id}, title='{self.title[:30]}...', price=${self.price})>"


class SpotPrice(Base):
    """Current metal spot prices"""
    __tablename__ = "spot_prices"

    id = Column(Integer, primary_key=True, index=True)
    metal_type = Column(String, nullable=False)  # 'gold' or 'silver'
    price_per_oz = Column(Float, nullable=False)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    # Index for cache lookups
    __table_args__ = (
        Index('idx_metal_fetched', 'metal_type', 'fetched_at'),
    )

    def __repr__(self):
        return f"<SpotPrice(metal={self.metal_type}, price=${self.price_per_oz:.2f})>"


class RateLimitTracker(Base):
    """API quota management"""
    __tablename__ = "rate_limit_tracker"

    id = Column(Integer, primary_key=True, index=True)
    api_name = Column(String, nullable=False, unique=True)
    daily_limit = Column(Integer, nullable=True)  # NULL for monthly limits
    monthly_limit = Column(Integer, nullable=True)  # NULL for daily limits
    daily_calls_used = Column(Integer, default=0)
    monthly_calls_used = Column(Integer, default=0)
    reset_at = Column(DateTime, nullable=False)
    last_call_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<RateLimitTracker(api={self.api_name}, used={self.daily_calls_used or self.monthly_calls_used})>"


class APICallLog(Base):
    """Debug and monitoring logs"""
    __tablename__ = "api_call_logs"

    id = Column(Integer, primary_key=True, index=True)
    api_name = Column(String, nullable=False)
    endpoint = Column(String, nullable=False)
    status_code = Column(Integer, nullable=True)
    success = Column(Boolean, nullable=False)
    error_message = Column(String, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    called_at = Column(DateTime, default=datetime.utcnow)

    # Index for monitoring queries
    __table_args__ = (
        Index('idx_api_called', 'api_name', 'called_at'),
    )

    def __repr__(self):
        return f"<APICallLog(api={self.api_name}, success={self.success})>"


def init_db():
    """Initialize database tables"""
    try:
        # Enable WAL mode for SQLite
        with engine.connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.commit()

        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

        # Initialize rate limit trackers if they don't exist
        with get_db_context() as db:
            # eBay tracker
            ebay_tracker = db.query(RateLimitTracker).filter(
                RateLimitTracker.api_name == "ebay"
            ).first()
            if not ebay_tracker:
                ebay_tracker = RateLimitTracker(
                    api_name="ebay",
                    daily_limit=settings.EBAY_DAILY_LIMIT,
                    daily_calls_used=0,
                    reset_at=datetime.utcnow().replace(hour=0, minute=0, second=0)
                )
                db.add(ebay_tracker)

            # Metals API tracker
            metals_tracker = db.query(RateLimitTracker).filter(
                RateLimitTracker.api_name == "metals-api"
            ).first()
            if not metals_tracker:
                metals_tracker = RateLimitTracker(
                    api_name="metals-api",
                    monthly_limit=settings.METALS_API_MONTHLY_LIMIT,
                    monthly_calls_used=0,
                    reset_at=datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
                )
                db.add(metals_tracker)

            db.commit()
            logger.info("Rate limit trackers initialized")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI to get database session
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager for database session
    Usage: with get_db_context() as db: ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
