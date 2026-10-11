"""Tenant context and resolver hook for authenticated integrations.

The header resolver extracts caller-provided context; it does not authenticate
or authorize tenant access. The default REST installation is single-tenant and
rejects non-default tenant headers. Integrators must bind tenant identity to
verified credentials and use tenant-scoped repositories throughout operations.
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
    """Extract tenant context from headers; this is not authorization.

    Missing or blank context resolves to the supplied default. Authenticated
    integrations must validate access before trusting a caller-provided tenant.
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
