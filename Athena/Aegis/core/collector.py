"""Collection state management module."""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from Athena.Aegis.db.dao import CollectionDAO, create_dao
from Athena.Aegis.core.config import Config


class CollectionState:
    """Manages collection state and incremental processing."""
    
    def __init__(self, config: Optional[Config] = None, db_path: Optional[str] = None):
        self.config = config or Config()
        self.db_path = db_path or self.config.db_path
        self.dao = create_dao(self.db_path)
    
    def register_item(
        self,
        platform: str,
        item_id: str,
        url: str,
        title: str = "",
        author: str = "",
    ) -> bool:
        """Register a new item for collection.
        
        Returns True if item was newly registered, False if already exists.
        """
        existing = self.dao.get_item(platform, item_id)
        if existing:
            # Check if we should re-process
            if existing.status == "completed":
                return False  # Already processed
            return False  # Already pending
        else:
            self.dao.add_item(platform, item_id, url, title, author)
            return True
    
    def get_pending_items(self, platform: Optional[str] = None) -> list:
        """Get items pending collection."""
        return self.dao.get_pending(platform)
    
    def start_processing(self, platform: str, item_id: str) -> bool:
        """Mark item as being processed."""
        return self.dao.mark_processing(platform, item_id)
    
    def complete(self, platform: str, item_id: str, note_path: str) -> bool:
        """Mark item as completed."""
        return self.dao.mark_completed(platform, item_id, note_path)
    
    def fail(self, platform: str, item_id: str, error: str) -> bool:
        """Mark item as failed."""
        return self.dao.mark_failed(platform, item_id, error)
    
    def skip(self, platform: str, item_id: str) -> bool:
        """Mark item as skipped by user."""
        return self.dao.mark_skipped(platform, item_id)
    
    def is_collected(self, platform: str, item_id: str) -> bool:
        """Check if item was already collected."""
        return self.dao.is_completed(platform, item_id)
    
    def get_stats(self) -> dict:
        """Get collection statistics."""
        return self.dao.get_stats()
    
    def filter_new_items(
        self,
        items: list[dict],
        check_source: bool = True,
    ) -> list[dict]:
        """Filter items to only include new ones.
        
        Args:
            items: List of items with platform/item_id/url
            check_source: If True, check against database
        
        Returns:
            Items that need processing
        """
        new_items = []
        
        for item in items:
            platform = item.get("platform", "")
            item_id = item.get("item_id", "")
            
            if check_source:
                # Check in database
                if self.dao.get_item(platform, item_id):
                    continue  # Already exists
            
            # Check if already processed
            if self.is_collected(platform, item_id):
                continue
            
            new_items.append(item)
        
        return new_items
    
    def process_batch(
        self,
        items: list[dict],
        processor_func,
        update_source: bool = True,
    ) -> dict:
        """Process a batch of items with incremental support.
        
        Args:
            items: List of items to process
            processor_func: Function to call for each item
            update_source: If True, register items in database
        
        Returns:
            Summary dict with: processed, skipped, failed
        """
        results = {
            "processed": 0,
            "skipped": 0,
            "failed": 0,
            "errors": [],
        }
        
        for item in items:
            platform = item.get("platform", "")
            item_id = item.get("item_id", "")
            url = item.get("url", "")
            
            # Skip if already collected
            if self.is_collected(platform, item_id):
                results["skipped"] += 1
                continue
            
            # Mark as processing
            if update_source:
                self.start_processing(platform, item_id)
            
            try:
                # Process item
                note_path = processor_func(item)
                
                # Mark as completed
                if update_source and note_path:
                    self.complete(platform, item_id, note_path)
                    results["processed"] += 1
                elif not note_path:
                    # No note generated, mark as skipped
                    if update_source:
                        self.skip(platform, item_id)
                    results["skipped"] += 1
                    
            except Exception as e:
                error_msg = str(e)
                if update_source:
                    self.fail(platform, item_id, error_msg)
                results["failed"] += 1
                results["errors"].append({
                    "platform": platform,
                    "item_id": item_id,
                    "error": error_msg,
                })
        
        return results


class IncrementalChecker:
    """Checks for new/changed items relative to processed items."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or "aegis.db"
        self.dao = create_dao(self.db_path)
        self.dao.init_db()
    
    def get_processed_count(self, platform: Optional[str] = None) -> int:
        """Get count of processed items."""
        items = self.dao.get_by_platform(platform) if platform else self.dao.get_stats()
        if isinstance(items, dict):
            return items.get("completed", 0)
        return sum(1 for i in items if i.status.value == "completed")
    
    def has_new_items(self, new_count: int) -> bool:
        """Check if there are new items to process."""
        return new_count > 0
    
    def get_incremental_summary(self, total_count: int) -> dict:
        """Get summary of incremental status."""
        stats = self.dao.get_stats()
        processed = stats.get("completed", 0)
        
        return {
            "total_in_source": total_count,
            "already_processed": processed,
            "new_to_process": total_count - processed,
            "progress_percent": round(processed / total_count * 100, 1) if total_count > 0 else 0,
        }


def create_state(config: Optional[Config] = None, db_path: Optional[str] = None) -> CollectionState:
    """Create a CollectionState instance."""
    return CollectionState(config, db_path)