"""YAML front matter processing module."""

import re as _re
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml as _yaml
from yaml import YAMLError


FRONT_MATTER_PATTERN = _re.compile(r"^---\s*\n(.*?)\n---\s*\n", _re.DOTALL)
DEFAULT_FIELDS = {
    "title": "",
    "source": "",
    "url": "",
    "author": "",
    "date": "",
    "tags": [],
    "type": "",
    "status": "pending",
}


def parse_front_matter(content: str) -> tuple[Optional[dict], str]:
    """Parse YAML front matter from markdown content.
    
    Returns (metadata_dict, remaining_content)
    """
    match = FRONT_MATTER_PATTERN.match(content)
    if not match:
        return None, content
    
    yaml_content = match.group(1)
    try:
        metadata = _yaml.safe_load(yaml_content) or {}
    except YAMLError:
        return None, content
    
    remaining = content[match.end():]
    return metadata, remaining


def add_front_matter(content: str, metadata: dict) -> str:
    """Add or update YAML front matter."""
    # Remove existing front matter
    _, content = parse_front_matter(content)
    
    # Merge with defaults and provided metadata
    merged = {**DEFAULT_FIELDS, **metadata}
    
    # Remove None values
    merged = {k: v for k, v in merged.items() if v}
    
    # Format YAML
    yaml_content = _yaml.safe_dump(merged, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    return f"---\n{yaml_content}---\n\n{content}"


def ensure_fields(metadata: dict) -> dict:
    """Ensure all required fields exist in metadata."""
    result = {**DEFAULT_FIELDS, **metadata}
    
    # Set date to today if not present
    if not result.get("date"):
        result["date"] = datetime.now().strftime("%Y-%m-%d")
    
    # Set tags to empty list if None
    if result.get("tags") is None:
        result["tags"] = []
    
    return result


def extract_metadata_from_file(file_path: Path) -> Optional[dict]:
    """Extract metadata from markdown file."""
    if not file_path.suffix.lower() == ".md":
        return None
    
    try:
        content = file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None
    
    metadata, _ = parse_front_matter(content)
    return metadata


def update_file_metadata(file_path: Path, metadata: dict) -> bool:
    """Update file with new metadata."""
    if not file_path.suffix.lower() == ".md":
        return False
    
    try:
        content = file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return False
    
    # Parse existing content
    existing_metadata, body = parse_front_matter(content)
    
    # Merge metadata
    if existing_metadata:
        merged = {**existing_metadata, **metadata}
    else:
        merged = ensure_fields(metadata)
    
    # Add front matter
    new_content = add_front_matter(body, merged)
    
    # Write back
    try:
        file_path.write_text(new_content, encoding="utf-8")
        return True
    except OSError:
        return False


def format_image_link(image_path: str, config_format: str, platform: str = "", item_id: str = "") -> str:
    """Format image link according to configuration.
    
    Args:
        image_path: Original image path or URL
        config_format: Format template like "./images/{platform}/{id}/{filename}"
        platform: Platform identifier
        item_id: Item identifier
    
    Returns:
        Formatted image path
    """
    # Handle URLs - keep as-is
    if image_path.startswith(("http://", "https://")):
        return image_path
    
    # Extract filename from path
    path = Path(image_path)
    filename = path.name
    
    # Apply format template
    result = config_format.format(
        platform=platform,
        id=item_id,
        filename=filename,
    )
    
    return result