"""
Provider Initialization Service
Handles startup and lifecycle management of GPU providers
"""

import logging
from typing import List

from ..providers import VastAIProvider, IONetProvider, AkashProvider, RenderProvider
from ..core.base_provider import get_provider_registry, BaseProvider
from ..core.provider_config import get_provider_config, is_provider_configured


logger = logging.getLogger(__name__)


async def initialize_providers() -> List[BaseProvider]:
    """
    Initialize and register all GPU providers

    Checks configuration and only initializes enabled providers
    with valid API keys.

    Returns:
        List of successfully initialized providers
    """
    logger.info("Initializing GPU providers...")

    config = get_provider_config()
    registry = get_provider_registry()

    # Check if already initialized
    if registry.get_all():
        logger.info("Providers already initialized")
        return registry.get_all()

    initialized_providers = []
    failed_providers = []

    # Vast.ai
    if config.vastai_enabled:
        try:
            if is_provider_configured("vastai"):
                provider = VastAIProvider()
                registry.register(provider)
                initialized_providers.append(provider)
                logger.info(f"✓ Initialized {provider.name}")
            else:
                logger.warning(f"✗ Vast.ai: API key not configured")
                failed_providers.append(("vastai", "API key not configured"))
        except Exception as e:
            logger.error(f"✗ Failed to initialize Vast.ai: {e}")
            failed_providers.append(("vastai", str(e)))
    else:
        logger.info("✗ Vast.ai: Disabled in configuration")

    # io.net
    if config.ionet_enabled:
        try:
            if is_provider_configured("ionet"):
                provider = IONetProvider()
                registry.register(provider)
                initialized_providers.append(provider)
                logger.info(f"✓ Initialized {provider.name}")
            else:
                logger.warning(f"✗ io.net: API key not configured")
                failed_providers.append(("ionet", "API key not configured"))
        except Exception as e:
            logger.error(f"✗ Failed to initialize io.net: {e}")
            failed_providers.append(("ionet", str(e)))
    else:
        logger.info("✗ io.net: Disabled in configuration")

    # Akash Network
    if config.akash_enabled:
        try:
            if is_provider_configured("akash"):
                provider = AkashProvider()
                registry.register(provider)
                initialized_providers.append(provider)
                logger.info(f"✓ Initialized {provider.name}")
            else:
                logger.warning(f"✗ Akash: No configuration required (using public RPC)")
                # Akash uses public RPC, so still initialize
                provider = AkashProvider()
                registry.register(provider)
                initialized_providers.append(provider)
        except Exception as e:
            logger.error(f"✗ Failed to initialize Akash: {e}")
            failed_providers.append(("akash", str(e)))
    else:
        logger.info("✗ Akash: Disabled in configuration")

    # Render Network
    if config.render_enabled:
        try:
            if is_provider_configured("render"):
                provider = RenderProvider()
                registry.register(provider)
                initialized_providers.append(provider)
                logger.info(f"✓ Initialized {provider.name}")
            else:
                logger.warning(f"✗ Render: API key not configured")
                failed_providers.append(("render", "API key not configured"))
        except Exception as e:
            logger.error(f"✗ Failed to initialize Render: {e}")
            failed_providers.append(("render", str(e)))
    else:
        logger.info("✗ Render: Disabled in configuration")

    # Summary
    logger.info(
        f"Provider initialization complete: "
        f"{len(initialized_providers)} active, {len(failed_providers)} failed"
    )

    if failed_providers:
        logger.warning(f"Failed providers: {', '.join(f[0] for f in failed_providers)}")

    return initialized_providers


async def health_check_all_providers() -> dict:
    """
    Run health checks on all registered providers

    Returns:
        Health check results for each provider
    """
    logger.info("Running health checks on all providers...")

    registry = get_provider_registry()
    results = await registry.health_check_all()

    healthy_count = sum(1 for is_healthy in results.values() if is_healthy)
    total_count = len(results)

    logger.info(f"Health check complete: {healthy_count}/{total_count} providers healthy")

    return {
        "providers": results,
        "summary": {
            "total": total_count,
            "healthy": healthy_count,
            "unhealthy": total_count - healthy_count,
        },
    }


async def shutdown_providers():
    """
    Gracefully shutdown all providers

    Closes connections and cleans up resources
    """
    logger.info("Shutting down all providers...")

    registry = get_provider_registry()
    await registry.close_all()

    logger.info("All providers shut down successfully")
