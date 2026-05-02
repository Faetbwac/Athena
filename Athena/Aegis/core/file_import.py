"""File import module for scanning and importing markdown files."""

import os
from pathlib import Path
from typing import Optional

from Athena.Aegis.core.config import Config
from Athena.Aegis.core.frontmatter import (
    extract_metadata_from_file,
    update_file_metadata,
    ensure_fields,
    format_image_link,
    parse_front_matter,
)


def scan_directory(directory: str, recursive: bool = True) -> list[dict]:
    """Scan directory for markdown files.
    
    Returns list of file info dicts with:
        - path: Path object
        - name: filename
        - metadata: parsed YAML front matter (or None)
    """
    dir_path = Path(directory)
    if not dir_path.exists() or not dir_path.is_dir():
        return []
    
    # Find all .md files
    pattern = "**/*.md" if recursive else "*.md"
    md_files = list(dir_path.glob(pattern))
    
    results = []
    for file_path in md_files:
        if file_path.is_file():
            metadata = extract_metadata_from_file(file_path)
            results.append({
                "path": file_path,
                "name": file_path.name,
                "relative_path": str(file_path.relative_to(dir_path)),
                "metadata": metadata or {},
            })
    
    return results


def import_files(
    files: list[dict],
    config: Optional[Config] = None,
    update_existing: bool = True,
) -> dict[str, int]:
    """Import files with metadata.
    
    Args:
        files: List of file info dicts from scan_directory
        config: Configuration object
        update_existing: Whether to update files with existing metadata
    
    Returns:
        Summary dict with counts: imported, updated, skipped, errors
    """
    if config is None:
        config = Config()
    
    summary = {"imported": 0, "updated": 0, "skipped": 0, "errors": 0}
    
    for file_info in files:
        file_path = file_info["path"]
        existing_metadata = file_info.get("metadata", {})
        
        # Check if file needs update
        if existing_metadata and not update_existing:
            summary["skipped"] += 1
            continue
        
        # Ensure required fields
        new_metadata = ensure_fields(existing_metadata)
        
        # Update if missing fields
        needs_update = not existing_metadata or not existing_metadata.get("title")
        
        if needs_update:
            # Add title from filename if not present
            if not new_metadata.get("title"):
                new_metadata["title"] = file_path.stem
            
            # Update file
            success = update_file_metadata(file_path, new_metadata)
            if success:
                summary["imported"] += 1
            else:
                summary["errors"] += 1
        else:
            summary["updated"] += 1
    
    return summary


def convert_image_links(
    content: str,
    config: Config,
    platform: str = "",
    item_id: str = "",
) -> str:
    """Convert image links in content according to config format.
    
    Args:
        content: Markdown content
        config: Configuration with image_format
        platform: Platform identifier
        item_id: Item identifier
    
    Returns:
        Content with converted image links
    """
    import re
    
    # Pattern to match markdown image links
    image_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
    
    def replace_image(match):
        alt_text = match.group(1)
        image_path = match.group(2)
        
        # Format according to config
        new_path = format_image_link(
            image_path,
            config.image_format,
            platform,
            item_id,
        )
        
        return f"![{alt_text}]({new_path})"
    
    return image_pattern.sub(replace_image, content)


def import_directory(
    directory: str,
    config: Optional[Config] = None,
    recursive: bool = True,
    update_existing: bool = True,
) -> dict:
    """Main import function for a directory.
    
    Args:
        directory: Directory path to scan
        config: Configuration object
        recursive: Whether to scan recursively
        update_existing: Whether to update files with existing metadata
    
    Returns:
        Summary dict with counts
    """
    if config is None:
        config = Config()
    
    # Scan directory
    files = scan_directory(directory, recursive)
    
    if not files:
        return {"imported": 0, "updated": 0, "skipped": 0, "errors": 0, "total": 0}
    
    # Import files
    summary = import_files(files, config, update_existing)
    summary["total"] = len(files)
    
    return summary


def check_incremental(
    directory: str,
    processed_paths: set[str],
    recursive: bool = True,
) -> list[dict]:
    """Check for new files not yet processed.
    
    Args:
        directory: Directory to scan
        processed_paths: Set of already processed file paths
        recursive: Whether to scan recursively
    
    Returns:
        List of new files to process
    """
    all_files = scan_directory(directory, recursive)
    
    new_files = []
    for file_info in all_files:
        file_path = str(file_info["path"])
        if file_path not in processed_paths:
            new_files.append(file_info)
    
    return new_files