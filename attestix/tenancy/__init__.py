"""Attestix tenancy - re-exports from the flat module for namespace compatibility.

    # Namespaced (recommended)
    from attestix.tenancy import TenantContext, DEFAULT_TENANT, resolve_tenant

    # Flat (also supported)
    from tenancy import TenantContext, DEFAULT_TENANT, resolve_tenant
"""

from tenancy import (
    DEFAULT_TENANT,
    TenantContext,
    default_tenant_context,
    resolve_tenant,
)

# Re-export the submodule for `from attestix.tenancy.context import X` parity.
from tenancy import context

__all__ = [
    "TenantContext",
    "DEFAULT_TENANT",
    "default_tenant_context",
    "resolve_tenant",
    "context",
]
