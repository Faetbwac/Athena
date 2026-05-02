"""DAO layer for collection items."""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session


def get_engine(db_path: str):
    """Create database engine."""
    return create_engine(f"sqlite:///{db_path}", echo=False)


class CollectionItem:
    """Collection item (simple model)."""
    
    def __init__(self, platform, item_id, url, title="", author="", status="pending", note_path=None):
        self.platform = platform
        self.item_id = item_id
        self.url = url
        self.title = title
        self.author = author
        self.status = status
        self.note_path = note_path
        self.updated_at = datetime.utcnow()
        self.id = None
    
    def mark_completed(self, note_path):
        self.status = "completed"
        self.note_path = note_path
        self.updated_at = datetime.utcnow()
    
    def mark_skipped(self):
        self.status = "skipped"
        self.updated_at = datetime.utcnow()


class CollectionDAO:
    """Data Access Object for collection items."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or "aegis.db"
        self._engine = None
    
    @property
    def engine(self):
        if self._engine is None:
            self._engine = get_engine(self.db_path)
        return self._engine
    
    def init_db(self):
        """Initialize database tables."""
        conn = self.engine.connect()
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS collection_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                item_id TEXT NOT NULL,
                url TEXT NOT NULL,
                title TEXT,
                author TEXT,
                status TEXT DEFAULT 'pending',
                note_path TEXT,
                updated_at TEXT
            )
        """))
        conn.commit()
        conn.close()
    
    def add_item(self, platform, item_id, url, title="", author=""):
        """Add a new item."""
        self.init_db()
        
        conn = self.engine.connect()
        
        # Check if exists
        result = conn.execute(text(
            f"SELECT id, platform, item_id, url, title, author, status, note_path FROM collection_items WHERE platform='{platform}' AND item_id='{item_id}'"
        )).fetchone()
        
        if result:
            conn.close()
            item = CollectionItem(result[1], result[2], result[3], result[4], result[5], result[6], result[7])
            item.id = result[0]
            return item
        
        # Insert
        now = datetime.utcnow().isoformat()
        conn.execute(text(f"""
            INSERT INTO collection_items (platform, item_id, url, title, author, status, updated_at)
            VALUES ('{platform}', '{item_id}', '{url}', '{title}', '{author}', 'pending', '{now}')
        """))
        conn.commit()
        conn.close()
        
        return self.get_item(platform, item_id)
    
    def get_item(self, platform, item_id):
        """Get item by platform and ID."""
        conn = self.engine.connect()
        result = conn.execute(text(
            f"SELECT id, platform, item_id, url, title, author, status, note_path FROM collection_items WHERE platform='{platform}' AND item_id='{item_id}'"
        )).fetchone()
        conn.close()
        
        if not result:
            return None
        
        item = CollectionItem(result[1], result[2], result[3], result[4], result[5], result[6])
        item.id = result[0]
        item.note_path = result[7]
        return item
    
    def get_stats(self):
        """Get statistics."""
        conn = self.engine.connect()
        try:
            result = conn.execute(text("""
                SELECT status, COUNT(*) as cnt 
                FROM collection_items 
                GROUP BY status
            """)).fetchall()
            
            stats = {"total": 0, "pending": 0, "processing": 0, "completed": 0, "failed": 0, "skipped": 0}
            for row in result:
                stats[row[0]] = row[1]
                stats["total"] += row[1]
        except:
            stats = {"total": 0, "pending": 0, "processing": 0, "completed": 0, "failed": 0, "skipped": 0}
        
        conn.close()
        return stats
    
    def mark_completed(self, platform, item_id, note_path):
        """Mark item as completed."""
        conn = self.engine.connect()
        now = datetime.utcnow().isoformat()
        conn.execute(text(f"""
            UPDATE collection_items 
            SET status='completed', note_path='{note_path}', updated_at='{now}'
            WHERE platform='{platform}' AND item_id='{item_id}'
        """))
        conn.commit()
        conn.close()
        return True
    
    def mark_skipped(self, platform, item_id):
        """Mark item as skipped."""
        conn = self.engine.connect()
        now = datetime.utcnow().isoformat()
        conn.execute(text(f"""
            UPDATE collection_items 
            SET status='skipped', updated_at='{now}'
            WHERE platform='{platform}' AND item_id='{item_id}'
        """))
        conn.commit()
        conn.close()
        return True
    
    def is_completed(self, platform, item_id):
        """Check if item is completed."""
        conn = self.engine.connect()
        result = conn.execute(text(
            f"SELECT status FROM collection_items WHERE platform='{platform}' AND item_id='{item_id}'"
        )).fetchone()
        conn.close()
        
        if not result:
            return False
        return result[0] == "completed"


def create_dao(db_path=None):
    return CollectionDAO(db_path)