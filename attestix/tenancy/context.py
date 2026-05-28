"""Tenant context + resolver hook (data-model.md §3, FR-011…FR-014).

A :class:`TenantContext` is the ambient scope for an operation: which tenant new
resources and audit events belong to, and the acting identity. It is deliberately
tiny — the OSS provides the *slot* and a default; integrators (and the hosted
cloud) plug in a richer resolver at the boundary.

Resolution decision (T046 — "default REST tenant resolution"): the OSS ships a
concrete default resolver that resolves to ``"default"`` so single-tenant
self-host has zero behavior change. It also reads an optional ``X-Attestix-Tenant``
header (case-insensitive) when present, giving multi-tenant operators a working
default without forcing them to write a resolver; an integrator may still inject
their own resolution upstream. A blank / missing tenant resolves to ``"default"``;
a context that *requires* an explicit tenant validates via :meth:`require_tenant`
(FR-012 acceptance scenario 3) rather than silently borrowing another tenant's
scope.
"""

from dataclasses import dataclass, field
from typing import Mapping, Optional

#: The default tenant. Re-exported from :mod:`storage.repository` so there is a
#: single source of truth for the sentinel across the storage and tenancy seams.
from attestix.storage.repository import DEFAULT_TENANT

#: The header the default resolver reads to map an HTTP request to a tenant.
#: Integrators/cloud may ignore it and inject their own resolution.
TENANT_HEADER = "X-Attestix-Tenant"


@dataclass(frozen=True)
class TenantContext:
    """The resolved scope for one operation.

    ``tenant_id`` defaults to ``"default"`` (FR-011). ``actor`` is the acting
    identity (e.g. a caller DID or the server DID) and is recorded on audit
    events; it is optional because many self-host operations act as the server
    itself.
    """

    tenant_id: str = DEFAULT_TENANT
    actor: Optional[str] = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    def require_tenant(self) -> str:
        """Return the tenant id, or raise if it is missing / blank.

        Use at boundaries that MUST NOT silently fall back to another tenant's
        scope (FR-012, spec acceptance scenario 3). The default context resolves
        to ``"default"`` and therefore passes; an explicitly blank tenant is
        rejected.
        """
        if not self.tenant_id or not str(self.tenant_id).strip():
            raise ValueError(
                "TenantContext has no resolvable tenant_id; refusing to default "
                "silently to another tenant's scope."
            )
        return self.tenant_id


def default_tenant_context(actor: Optional[str] = None) -> TenantContext:
    """Return the OSS default context (tenant ``"default"``), v0.3.0 parity."""
    return TenantContext(tenant_id=DEFAULT_TENANT, actor=actor)


def resolve_tenant(
    headers: Optional[Mapping[str, str]] = None,
    *,
    actor: Optional[str] = None,
    default: str = DEFAULT_TENANT,
) -> TenantContext:
    """Resolve a :class:`TenantContext` from request headers (default resolver).

    Reads ``X-Attestix-Tenant`` case-insensitively; a missing or blank value
    resolves to ``default`` (``"default"``). This is the OSS-shipped default
    (T046): it gives multi-tenant operators a working header-based mapping while
    keeping single-tenant self-host on ``"default"`` with no configuration.
    """
    tenant = default
    if headers:
        # Case-insensitive header lookup without assuming a Starlette Headers obj.
        for key, value in headers.items():
            if key.lower() == TENANT_HEADER.lower():
                if value and str(value).strip():
                    tenant = str(value).strip()
                break
    return TenantContext(tenant_id=tenant, actor=actor)
