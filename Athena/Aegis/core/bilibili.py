"""BiliNote API client for video collection."""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional

from Athena.Aegis.core.config import Config


BILINOTE_BASE_URL = os.environ.get("BILINOTE_BASE_URL", "http://localhost:8483")
DEFAULT_TIMEOUT = 60  # seconds


class BiliNoteClient:
    """Client for BiliNote API."""
    
    def __init__(self, base_url: str = None, timeout: int = None):
        self.base_url = base_url or BILINOTE_BASE_URL
        self.timeout = timeout or DEFAULT_TIMEOUT
        self.session = requests.Session()
    
    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make HTTP request to BiliNote API."""
        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault("timeout", self.timeout)
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"code": -1, "message": str(e)}
    
    def health_check(self) -> bool:
        """Check if BiliNote API is available."""
        result = self._request("GET", "/health")
        return result.get("code") == 0
    
    def generate_note(
        self,
        video_url: str,
        platform: str = "bilibili",
        quality: str = "fast",
        style: str = None,
    ) -> Optional[dict]:
        """Generate note from video URL.
        
        Args:
            video_url: BiliBili video URL
            platform: Platform name
            quality: Download quality (fast/medium/high)
            style: Note style (optional)
        
        Returns:
            dict with: markdown, video_id, title
        """
        data = {
            "video_url": video_url,
            "platform": platform,
            "quality": quality,
        }
        if style:
            data["style"] = style
        
        return self._request("POST", "/api/note/generate", json=data)
    
    def get_video_info(self, video_url: str) -> Optional[dict]:
        """Get video metadata from URL."""
        return self._request("POST", "/api/video/info", json={"url": video_url})
    
    def check_available(self) -> bool:
        """Check if service is available."""
        try:
            return self.health_check()
        except:
            return False


class NoteGenerator:
    """Generates notes in llm-wiki format."""
    
    def __init__(self, config: Optional[Config] = None, client: Optional[BiliNoteClient] = None):
        self.config = config or Config()
        self.client = client or BiliNoteClient()
    
    def generate(
        self,
        video_url: str,
        platform: str = "bilibili",
        quality: str = "fast",
    ) -> dict:
        """Generate note from video.
        
        Returns:
            dict with: note_path, markdown, title, metadata
        """
        # Get note from BiliNote
        result = self.client.generate_note(video_url, platform, quality)
        
        if not result or result.get("code") != 0:
            return {
                "success": False,
                "error": result.get("message", "Failed to generate note") if result else "No response",
            }
        
        # Extract data
        markdown = result.get("markdown", "")
        video_id = result.get("video_id", "")
        title = result.get("title", "")
        
        # Save note
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename: platform-id-title.md
        safe_title = "".join(c for c in title[:50] if c.isalnum() or c in "-_ ")
        filename = f"{platform}-{video_id}-{safe_title}.md"
        note_path = output_dir / filename
        
        # Convert image links
        from Athena.Aegis.core.file_import import convert_image_links
        markdown = convert_image_links(markdown, self.config, platform, video_id)
        
        # Write note
        note_path.write_text(markdown, encoding="utf-8")
        
        return {
            "success": True,
            "note_path": str(note_path),
            "markdown": markdown,
            "title": title,
            "video_id": video_id,
            "platform": platform,
        }
    
    def batch_generate(
        self,
        video_urls: list[str],
        platform: str = "bilibili",
        quality: str = "fast",
    ) -> list[dict]:
        """Generate multiple notes."""
        results = []
        for url in video_urls:
            result = self.generate(url, platform, quality)
            results.append(result)
        return results


def create_client(base_url: str = None) -> BiliNoteClient:
    """Create BiliNote client instance."""
    return BiliNoteClient(base_url)


def create_generator(config: Config = None, client: BiliNoteClient = None) -> NoteGenerator:
    """Create note generator instance."""
    return NoteGenerator(config, client)