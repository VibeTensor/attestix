"""Service instance cache with TTL for AURA Protocol.

Reuses the pattern from productivity-mcp: singleton service instances
with a configurable time-to-live to avoid stale state.
"""

import time
from typing import Any, Dict, Optional, Tuple, Type

_cache: Dict[str, Tuple[Any, float]] = {}
DEFAULT_TTL = 600  # 10 minutes


def get_service(
    service_class: Type,
    instance_id: str = "default",
    ttl: int = DEFAULT_TTL,
    **kwargs,
) -> Any:
    """Get or create a cached service instance.

    Args:
        service_class: The class to instantiate.
        instance_id: Key for distinguishing multiple instances.
        ttl: Time-to-live in seconds.
        **kwargs: Passed to the constructor if creating new instance.

    Returns:
        Cached or newly created service instance.
    """
    cache_key = f"{service_class.__name__}:{instance_id}"
    now = time.time()

    if cache_key in _cache:
        instance, created_at = _cache[cache_key]
        if now - created_at < ttl:
            return instance

    instance = service_class(**kwargs)
    _cache[cache_key] = (instance, now)
    return instance


def clear_cache(service_class: Optional[Type] = None):
    """Clear cached instances. If service_class given, only clear that type."""
    if service_class is None:
        _cache.clear()
    else:
        prefix = f"{service_class.__name__}:"
        keys_to_remove = [k for k in _cache if k.startswith(prefix)]
        for k in keys_to_remove:
            del _cache[k]
