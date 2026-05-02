"""Tests for incremental sync and collection state."""

import sys
import os
import tempfile
from pathlib import Path

# Add parent directories to path
test_dir = Path(__file__).parent
sys.path.insert(0, str(test_dir.parent / "db"))
sys.path.insert(0, str(test_dir.parent / "core"))

import pytest


def test_dao_basic_operations():
    """Test basic DAO operations."""
    from db.dao import create_dao
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        dao = create_dao(db_path)
        
        # Initialize
        dao.init_db()
        
        # Add item
        item = dao.add_item("bilibili", "123", "url", "Title")
        assert item is not None
        assert item.platform == "bilibili"
        
        # Get item
        retrieved = dao.get_item("bilibili", "123")
        assert retrieved is not None
        
        # Get stats
        stats = dao.get_stats()
        assert stats["pending"] == 1


def test_collection_state():
    """Test CollectionState with temp DB."""
    from core.collector import CollectionState
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        state = CollectionState(db_path=db_path)
        
        # Get initial stats
        stats = state.get_stats()
        assert stats["total"] == 0


def test_register_and_complete():
    """Test registering and completing item."""
    from core.collector import CollectionState
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        state = CollectionState(db_path=db_path)
        
        # Register
        result = state.register_item(
            platform="bilibili",
            item_id="12345",
            url="https://b.com/v/12345",
            title="Test",
        )
        assert result is True
        
        # Complete
        result = state.complete("bilibili", "12345", "/notes/test.md")
        assert result is True
        
        # Check is collected
        assert state.is_collected("bilibili", "12345") is True


def test_is_collected_false():
    """Test is_collected returns False for new items."""
    from core.collector import CollectionState
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        state = CollectionState(db_path=db_path)
        
        assert state.is_collected("bilibili", "99999") is False


if __name__ == "__main__":
    test_dao_basic_operations()
    test_collection_state()
    test_register_and_complete()
    test_is_collected_false()
    print("All sync tests passed!")