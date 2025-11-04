"""
Provider Configuration Management
Centralized configuration for all GPU provider integrations
"""

from typing import Dict, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class ProviderAPIConfig(BaseSettings):
    """
    Provider API Configuration
    Loads from environment variables with PROVIDER_ prefix
    """

    # Vast.ai Configuration
    vastai_api_key: Optional[str] = Field(None, env="VASTAI_API_KEY")
    vastai_base_url: str = Field("https://console.vast.ai/api/v0", env="VASTAI_BASE_URL")
    vastai_enabled: bool = Field(True, env="VASTAI_ENABLED")
    vastai_timeout: int = Field(30, env="VASTAI_TIMEOUT")
    vastai_max_retries: int = Field(3, env="VASTAI_MAX_RETRIES")
    vastai_rate_limit: int = Field(100, env="VASTAI_RATE_LIMIT")  # requests per minute

    # Akash Network Configuration
    akash_rpc_url: str = Field("https://rpc.akashnet.net:443", env="AKASH_RPC_URL")
    akash_enabled: bool = Field(True, env="AKASH_ENABLED")
    akash_timeout: int = Field(45, env="AKASH_TIMEOUT")
    akash_max_retries: int = Field(3, env="AKASH_MAX_RETRIES")
    akash_rate_limit: int = Field(60, env="AKASH_RATE_LIMIT")

    # Render Network Configuration
    render_api_key: Optional[str] = Field(None, env="RENDER_API_KEY")
    render_base_url: str = Field("https://api.rendernetwork.com", env="RENDER_BASE_URL")
    render_enabled: bool = Field(True, env="RENDER_ENABLED")
    render_timeout: int = Field(30, env="RENDER_TIMEOUT")
    render_max_retries: int = Field(3, env="RENDER_MAX_RETRIES")
    render_rate_limit: int = Field(50, env="RENDER_RATE_LIMIT")

    # io.net Configuration
    ionet_api_key: Optional[str] = Field(None, env="IONET_API_KEY")
    ionet_base_url: str = Field("https://api.io.net/v1", env="IONET_BASE_URL")
    ionet_enabled: bool = Field(True, env="IONET_ENABLED")
    ionet_timeout: int = Field(30, env="IONET_TIMEOUT")
    ionet_max_retries: int = Field(3, env="IONET_MAX_RETRIES")
    ionet_rate_limit: int = Field(150, env="IONET_RATE_LIMIT")  # 150 per 10 seconds

    # Global Provider Settings
    provider_circuit_breaker_threshold: int = Field(5, env="PROVIDER_CIRCUIT_BREAKER_THRESHOLD")
    provider_circuit_breaker_timeout: int = Field(60, env="PROVIDER_CIRCUIT_BREAKER_TIMEOUT")  # seconds
    provider_cache_ttl: int = Field(30, env="PROVIDER_CACHE_TTL")  # seconds
    provider_health_check_interval: int = Field(300, env="PROVIDER_HEALTH_CHECK_INTERVAL")  # seconds
    provider_fallback_enabled: bool = Field(True, env="PROVIDER_FALLBACK_ENABLED")

    # Performance & Monitoring
    provider_enable_metrics: bool = Field(True, env="PROVIDER_ENABLE_METRICS")
    provider_log_requests: bool = Field(True, env="PROVIDER_LOG_REQUESTS")
    provider_slow_request_threshold: float = Field(5.0, env="PROVIDER_SLOW_REQUEST_THRESHOLD")  # seconds

    class Config:
        env_file = ".env"
        case_sensitive = False


# Singleton instance
_provider_config: Optional[ProviderAPIConfig] = None


def get_provider_config() -> ProviderAPIConfig:
    """Get the provider configuration singleton"""
    global _provider_config
    if _provider_config is None:
        _provider_config = ProviderAPIConfig()
    return _provider_config


# Provider metadata for discovery and management
PROVIDER_METADATA = {
    "vastai": {
        "name": "Vast.ai",
        "description": "Direct GPU instance rental marketplace",
        "type": "marketplace",
        "supported_operations": ["search", "rent", "manage"],
        "authentication": "api_key",
        "documentation": "https://docs.vast.ai/api",
        "pricing_model": "on_demand",
        "gpu_focus": "general_compute",
    },
    "akash": {
        "name": "Akash Network",
        "description": "Decentralized cloud computing marketplace",
        "type": "blockchain",
        "supported_operations": ["search", "bid", "deploy"],
        "authentication": "blockchain_rpc",
        "documentation": "https://akash.network/docs/",
        "pricing_model": "reverse_auction",
        "gpu_focus": "general_compute",
    },
    "render": {
        "name": "Render Network",
        "description": "Decentralized GPU rendering platform",
        "type": "blockchain",
        "supported_operations": ["render", "queue"],
        "authentication": "token_based",
        "documentation": "https://rendernetwork.com/",
        "pricing_model": "token_payment",
        "gpu_focus": "rendering",
    },
    "ionet": {
        "name": "io.net",
        "description": "Decentralized GPU cloud for AI/ML",
        "type": "marketplace",
        "supported_operations": ["search", "deploy", "manage"],
        "authentication": "api_key",
        "documentation": "https://developers.io.net/docs",
        "pricing_model": "on_demand",
        "gpu_focus": "ai_ml",
    },
}


def get_enabled_providers() -> Dict[str, dict]:
    """Get list of enabled providers with their metadata"""
    config = get_provider_config()
    enabled = {}

    if config.vastai_enabled:
        enabled["vastai"] = PROVIDER_METADATA["vastai"]
    if config.akash_enabled:
        enabled["akash"] = PROVIDER_METADATA["akash"]
    if config.render_enabled:
        enabled["render"] = PROVIDER_METADATA["render"]
    if config.ionet_enabled:
        enabled["ionet"] = PROVIDER_METADATA["ionet"]

    return enabled


def is_provider_configured(provider_name: str) -> bool:
    """Check if a provider has required API keys configured"""
    config = get_provider_config()

    api_key_requirements = {
        "vastai": config.vastai_api_key is not None,
        "akash": True,  # Uses public RPC
        "render": config.render_api_key is not None,
        "ionet": config.ionet_api_key is not None,
    }

    return api_key_requirements.get(provider_name, False)
