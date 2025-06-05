"""Application configuration module.

Loads configuration from environment variables or an optional YAML file.
"""

from pydantic import BaseModel, Field
from pathlib import Path
import logging
import os
import yaml

logger = logging.getLogger(__name__)

CONFIG_PATH = Path(os.environ.get("PCRC_CONFIG", "config.yaml"))

class AppConfig(BaseModel):
    """Configuration options for the app.

    Attributes
    ----------
    model_name: str
        Name of the model to use.
    ollama_url: str
        Base URL for the Ollama service.
    batch_size: int
        Number of files processed per batch.
    max_lines: int
        Number of lines of content to pass to the model.
    """

    model_name: str = Field(
        default="pierce-county-records-classifier-phi2:latest",
        description="Name of the model to use.",
    )
    ollama_url: str = Field(
        default="http://localhost:11434",
        description="Base URL for the Ollama service.",
    )
    batch_size: int = Field(
        default=10,
        description="Number of files processed per batch.",
        ge=1,
    )
    max_lines: int = Field(
        default=100,
        description="Number of lines of content to pass to the model.",
        ge=1,
    )
    hf_cache_dir: str = Field(
        default=str(Path.home() / ".cache" / "huggingface"),
        description="Directory for Hugging Face model cache.",
    )


def load_config() -> AppConfig:
    """Load configuration from YAML file and environment variables.

    Returns
    -------
    AppConfig
        Configuration populated from `config.yaml` and environment variables.
    """
    data = {}
    if CONFIG_PATH.exists():
        try:
            with CONFIG_PATH.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except Exception as exc:
            logger.warning("Failed to load %s: %s", CONFIG_PATH, exc)
            data = {}
    env_model = os.environ.get("PCRC_MODEL")
    env_url = os.environ.get("PCRC_OLLAMA_URL")
    env_batch = os.environ.get("PCRC_BATCH_SIZE")
    env_max_lines = os.environ.get("PCRC_MAX_LINES")
    env_cache = os.environ.get("PCRC_HF_CACHE")
    if env_model:
        data["model_name"] = env_model
    if env_url:
        data["ollama_url"] = env_url
    if env_batch:
        try:
            data["batch_size"] = int(env_batch)
        except ValueError:
            logger.warning("Invalid PCRC_BATCH_SIZE: %s", env_batch)
    if env_max_lines:
        try:
            data["max_lines"] = int(env_max_lines)
        except ValueError:
            logger.warning("Invalid PCRC_MAX_LINES: %s", env_max_lines)
    if env_cache:
        data["hf_cache_dir"] = env_cache
    return AppConfig(**data)

CONFIG = load_config()
