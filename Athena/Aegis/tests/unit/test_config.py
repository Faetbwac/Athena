"""Tests for configuration module."""

import sys
from pathlib import Path

# Add parent directory to path for direct imports
test_dir = Path(__file__).parent
sys.path.insert(0, str(test_dir.parent.parent / "core"))

import pytest
from config import Config


def test_config_defaults():
    """Test configuration defaults."""
    config = Config()
    assert config.output_dir == "./notes"
    assert config.image_format == "./images/{platform}/{id}/{filename}"
    assert config.db_path == "./aegis.db"


def test_routing_defaults():
    """Test routing configuration defaults."""
    config = Config()
    assert config.routing.videos == "./notes/videos"
    assert config.routing.articles == "./notes/articles"
    assert config.routing.questions == "./notes/questions"


def test_ai_defaults():
    """Test AI configuration defaults."""
    config = Config()
    assert config.ai.enabled is False
    assert config.ai.backend == "openai"
    assert config.ai.model == "gpt-4"


def test_validate():
    """Test configuration validates."""
    config = Config()
    config.validate()
    assert True


def test_get_routing_path():
    """Test getting routing path for content type."""
    config = Config()
    assert config.get_routing_path("videos") == "./notes/videos"
    assert config.get_routing_path("articles") == "./notes/articles"


def test_get_routing_path():
    """Test getting routing path for content type."""
    from aegis.core.config import Config
    
    config = Config()
    assert config.get_routing_path("videos") == "./notes/videos"
    assert config.get_routing_path("articles") == "./notes/articles"


def test_validate_empty_output_dir():
    """Test validation fails for empty output_dir."""
    from aegis.core.config import Config
    
    config = Config(output_dir="")
    with pytest.raises(ValueError, match="output_dir is required"):
        config.validate()


def test_validate_ai_without_key():
    """Test validation fails when AI enabled but no key."""
    from aegis.core.config import Config
    
    config = Config(ai={"enabled": True, "api_key": "", "backend": "openai", "model": "gpt-4"})
    with pytest.raises(ValueError, match="AI is enabled but api_key is not set"):
        config.validate()