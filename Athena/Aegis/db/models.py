"""Aegis database models."""

import os
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String, Text, Enum as SQLEnum, create_engine
from sqlalchemy.orm import DeclarativeBase, Session


class CollectionStatus(str, Enum):
    """Collection item status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    EXPIRED = "expired"  # Source content no longer available


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""

    pass


class CollectionItem(Base):
    """Collection item model."""

    __tablename__ = "collection_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    platform = Column(String(50), nullable=False, index=True)
    item_id = Column(String(100), nullable=False, index=True)
    url = Column(String(500), nullable=False)
    title = Column(String(500))
    author = Column(String(200))
    status = Column(SQLEnum(CollectionStatus), default=CollectionStatus.PENDING)
    note_path = Column(String(500))
    source_updated = Column(DateTime)
    collected_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(Text)  # JSON metadata

    __table_args__ = (
        {"sqlite_autoincrement": True},
    )

    @property
    def unique_key(self) -> str:
        """Get unique key for this item."""
        return f"{self.platform}:{self.item_id}"

    def is_completed(self) -> bool:
        """Check if item is completed and not modified."""
        return self.status == CollectionStatus.COMPLETED

    def mark_completed(self, note_path: str) -> None:
        """Mark item as completed."""
        self.status = CollectionStatus.COMPLETED
        self.note_path = note_path
        self.updated_at = datetime.utcnow()

    def mark_failed(self, error: str) -> None:
        """Mark item as failed."""
        self.status = CollectionStatus.FAILED
        self.metadata = error
        self.updated_at = datetime.utcnow()

    def mark_skipped(self) -> None:
        """Mark item as skipped by user."""
        self.status = CollectionStatus.SKIPPED
        self.updated_at = datetime.utcnow()


def get_engine(db_path: Optional[str] = None) -> create_engine:
    """Create database engine."""
    if db_path is None:
        db_path = os.environ.get("AEGIS_DB", "./aegis.db")
    return create_engine(f"sqlite:///{db_path}", echo=False)


def init_db(db_path: Optional[str] = None) -> None:
    """Initialize database."""
    engine = get_engine(db_path)
    Base.metadata.create_all(engine)


def get_session(db_path: Optional[str] = None) -> Session:
    """Get database session."""
    engine = get_engine(db_path)
    return Session(engine)