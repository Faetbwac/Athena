"""Aegis configuration module."""

import os
from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel, Field, field_validator


class RoutingConfig(BaseModel):
    """Routing configuration for content分流."""

    videos: str = "./notes/videos"
    articles: str = "./notes/articles"
    questions: str = "./notes/questions"


class AIConfig(BaseModel):
    """AI configuration."""

    enabled: bool = False
    backend: str = "openai"
    api_key: str = ""
    model: str = "gpt-4"


class CredentialsConfig(BaseModel):
    """Platform credentials (encrypted storage)."""

    bilibili: dict = Field(default_factory=dict)
    zhihu: dict = Field(default_factory=dict)
    juejin: dict = Field(default_factory=dict)


class GitConfig(BaseModel):
    """Git configuration."""

    auto_commit: bool = True
    remote: str = ""
    commit_message: str = "Aegis: collected {count} items"


class ProcessingConfig(BaseModel):
    """Processing configuration."""

    comment_depth: str = "all"
    batch_size: int = 10
    continue_on_error: bool = True


class Config(BaseModel):
    """Aegis configuration model."""

    output_dir: str = "./notes"
    image_format: str = "./images/{platform}/{id}/{filename}"
    routing: RoutingConfig = Field(default_factory=RoutingConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    credentials: CredentialsConfig = Field(default_factory=CredentialsConfig)
    git: GitConfig = Field(default_factory=GitConfig)
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    db_path: str = "./aegis.db"

    _config_file: Optional[Path] = None

    @classmethod
    def load(cls, config_file: Optional[str] = None) -> "Config":
        """Load configuration from YAML file or use defaults."""
        if config_file is None:
            config_file = os.environ.get("AEGIS_CONFIG", "config.yaml")

        path = Path(config_file)
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            config = cls(**data)
            config._config_file = path
            return config

        return cls()

    def save(self, config_file: Optional[str] = None) -> None:
        """Save configuration to YAML file."""
        if config_file is None:
            if self._config_file:
                config_file = str(self._config_file)
            else:
                config_file = "config.yaml"

        path = Path(config_file)
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.model_dump(exclude_none=True), f, default_flow_style=False, allow_unicode=True)

    def validate(self) -> None:
        """Validate configuration."""
        if not self.output_dir:
            raise ValueError("output_dir is required")
        if self.ai.enabled and not self.ai.api_key:
            raise ValueError("AI is enabled but api_key is not set")

    def get_routing_path(self, content_type: str) -> str:
        """Get routing path for content type."""
        return getattr(self.routing, content_type, self.output_dir)