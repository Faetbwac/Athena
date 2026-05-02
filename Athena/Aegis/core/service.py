"""Collection API for aggregating all collection sources."""

from pathlib import Path
from typing import Optional

from Athena.Aegis.core.config import Config, create_config
from Athena.Aegis.core.collector import CollectionState, create_state
from Athena.Aegis.core.file_import import import_directory, scan_directory
from Athena.Aegis.core.bilibili import create_generator, BiliNoteClient, NoteGenerator


class CollectionService:
    """Main service for all collection operations."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or create_config()
        self.state = create_state(config=self.config)
        self.bili_client = create_client()
        self.generator = NoteGenerator(self.config, self.bili_client)
    
    def collect_video(
        self,
        video_url: str,
        platform: str = "bilibili",
        quality: str = "fast",
    ) -> dict:
        """Collect a single video."""
        # Extract video ID from URL
        video_id = self._extract_video_id(video_url, platform)
        
        # Check if already collected
        if self.state.is_collected(platform, video_id):
            return {
                "success": False,
                "error": "Already collected",
                "skipped": True,
            }
        
        # Start processing
        self.state.start_processing(platform, video_id)
        
        try:
            # Generate note
            result = self.generator.generate(video_url, platform, quality)
            
            if result.get("success"):
                # Mark as completed
                self.state.complete(platform, video_id, result["note_path"])
                return result
            else:
                # Mark as failed
                self.state.fail(platform, video_id, result.get("error", "Unknown error"))
                return result
                
        except Exception as e:
            self.state.fail(platform, video_id, str(e))
            return {"success": False, "error": str(e)}
    
    def batch_collect(
        self,
        video_urls: list[str],
        platform: str = "bilibili",
        quality: str = "fast",
    ) -> dict:
        """Collect multiple videos."""
        results = {
            "processed": 0,
            "skipped": 0,
            "failed": 0,
            "errors": [],
        }
        
        for url in video_urls:
            result = self.collect_video(url, platform, quality)
            
            if result.get("success"):
                results["processed"] += 1
            elif result.get("skipped"):
                results["skipped"] += 1
            else:
                results["failed"] += 1
                results["errors"].append({
                    "url": url,
                    "error": result.get("error"),
                })
        
        return results
    
    def import_local(self, directory: str, recursive: bool = True) -> dict:
        """Import local markdown files."""
        self.config.validate()
        return import_directory(directory, self.config, recursive)
    
    def get_status(self) -> dict:
        """Get collection status."""
        return self.state.get_stats()
    
    def get_pending(self, platform: Optional[str] = None) -> list:
        """Get pending items."""
        return self.state.get_pending_items(platform)
    
    def _extract_video_id(self, url: str, platform: str) -> str:
        """Extract video ID from URL."""
        import re
        
        if platform == "bilibili":
            # Extract CV number or BV ID
            match = re.search(r'/(?:video\/)?(BV[\w]+|cv\d+)', url)
            if match:
                return match.group(1)
        
        # Fallback: use hash of URL
        return str(hash(url))[:12]


def create_service(config: Optional[Config] = None) -> CollectionService:
    """Create collection service instance."""
    return CollectionService(config)