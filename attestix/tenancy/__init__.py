"""Tenant context for Attestix (v0.4.0 extensibility layer, US2 / P2).

This package introduces the ambient :class:`TenantContext` and the
``DEFAULT_TENANT`` sentinel so the engine can be operated multi-tenant without
forking. The OSS default resolves every request to ``"default"`` (FR-014), so a
self-host install that never sets a tenant behaves exactly as v0.3.0.

Tenant *scoping* is enforced at the persistence boundary (the
:class:`~storage.Repository`, which already filters by ``tenant_id``); this
package supplies the *context* — the resolved tenant id + acting identity — that
the service / API layer threads into Repository calls and audit events.
"""

from attestix.tenancy.context import (
    DEFAULT_TENANT,
    TenantContext,
    default_tenant_context,
    resolve_tenant,
)

# Re-export the submodule for `from attestix.tenancy.context import X` parity.
from attestix.tenancy import context

__all__ = [
    "DEFAULT_TENANT",
    "TenantContext",
    "default_tenant_context",
    "resolve_tenant",
    "context",
]
