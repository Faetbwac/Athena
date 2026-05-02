"""Tests for YAML processing module."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))

from frontmatter import (
    parse_front_matter,
    add_front_matter,
    ensure_fields,
    extract_metadata_from_file,
    format_image_link,
)


def test_parse_front_matter_with_metadata():
    """Test parsing content with YAML front matter."""
    content = """---
title: "Test Title"
source: "bilibili"
url: "https://example.com"
tags: [tag1, tag2]
---

Body content here.
"""
    metadata, body = parse_front_matter(content)
    assert metadata is not None
    assert metadata["title"] == "Test Title"
    assert metadata["source"] == "bilibili"
    assert "Body content here" in body


def test_parse_front_matter_without_metadata():
    """Test parsing content without YAML front matter."""
    content = """# Just a heading

Body content.
"""
    metadata, body = parse_front_matter(content)
    assert metadata is None
    assert "Just a heading" in body


def test_add_front_matter():
    """Test adding front matter to content."""
    content = "# Hello World\n\nSome content."
    metadata = {"title": "Test Note", "source": "test"}
    result = add_front_matter(content, metadata)
    
    assert result.startswith("---")
    assert "title: Test Note" in result
    assert "source: test" in result
    assert "Hello World" in result


def test_ensure_fields():
    """Test ensuring required fields."""
    metadata = {"title": "Test"}
    result = ensure_fields(metadata)
    
    assert result["title"] == "Test"
    assert "date" in result
    assert result["status"] == "pending"
    assert result["tags"] == []


def test_ensure_fields_with_date():
    """Test ensuring fields preserves existing date."""
    metadata = {"title": "Test", "date": "2025-01-01"}
    result = ensure_fields(metadata)
    
    assert result["date"] == "2025-01-01"


def test_format_image_link_http():
    """Test HTTP image links are kept as-is."""
    url = "https://example.com/image.png"
    result = format_image_link(url, "./images/{platform}/{id}/{filename}")
    assert result == url


def test_format_image_link_local():
    """Test local image link formatting."""
    path = "images/photo.jpg"
    result = format_image_link(
        path,
        "./images/{platform}/{id}/{filename}",
        platform="bilibili",
        item_id="12345"
    )
    assert "./images/bilibili/12345/photo.jpg" in result


def test_format_image_link_with_path():
    """Test image link with directory in filename."""
    path = "./assets/photos/image.png"
    result = format_image_link(
        path,
        "./images/{platform}/{filename}",
        platform="zhihu",
        item_id=""
    )
    assert "image.png" in result


if __name__ == "__main__":
    test_parse_front_matter_with_metadata()
    test_parse_front_matter_without_metadata()
    test_add_front_matter()
    test_ensure_fields()
    test_ensure_fields_with_date()
    test_format_image_link_http()
    test_format_image_link_local()
    test_format_image_link_with_path()
    print("All YAML tests passed!")