"""Attestix CLI - Command-line interface for AI agent attestation infrastructure.

Wraps core Attestix services for interactive use: identity management,
compliance checks, audit trails, credential operations, and system status.
"""

import hashlib
import json
import sys
from importlib.metadata import version as pkg_version, PackageNotFoundError
from pathlib import Path

import click

# Windows: ensure UTF-8 stdout/stderr so progress glyphs (->, arrows, etc.)
# and any unicode in CLI output don't crash under cp1252 (Git Bash inherits
# the legacy console encoding).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from attestix.config import (
    AUDIT_FILE,
    DATA_DIR,
    load_compliance,
    load_credentials,
    load_identities,
    load_provenance,
)
from attestix.services.cache import get_service
from attestix.services.identity_service import IdentityService
from attestix.services.compliance_service import ComplianceService
from attestix.services.credential_service import CredentialService
from attestix.services.provenance_service import ProvenanceService


# Valid source protocols for identity creation
SOURCE_PROTOCOLS = [
    "manual", "mcp", "a2a", "oauth2", "did", "api_key", "saml", "openid_connect", "custom",
]


def _print_json(data, indent=2):
    """Pretty-print a dict as JSON to stdout."""
    click.echo(json.dumps(data, indent=indent, default=str))


def _success(msg):
    """Print a success message in green."""
    click.echo(click.style(msg, fg="green"))


def _error(msg):
    """Print an error message in red and exit."""
    click.echo(click.style(f"Error: {msg}", fg="red"), err=True)
    sys.exit(1)


def _warn(msg):
    """Print a warning message in yellow."""
    click.echo(click.style(msg, fg="yellow"), err=True)


def _header(msg):
    """Print a section header in bold cyan."""
    click.echo(click.style(msg, fg="cyan", bold=True))


@click.group()
@click.version_option(package_name="attestix")
def cli():
    """Attestix - Attestation Infrastructure for AI Agents.

    Manage agent identities, compliance profiles, credentials, and
    audit trails from the command line.
    """


# ---------------------------------------------------------------------------
# attestix init
# ---------------------------------------------------------------------------

@cli.command()
@click.option("--name", required=True, prompt=True, help="Human-readable agent name.")
@click.option(
    "--protocol",
    default="manual",
    type=click.Choice(SOURCE_PROTOCOLS, case_sensitive=False),
    show_default=True,
    help="Identity source protocol.",
)
@click.option("--description", default="", help="Agent description.")
@click.option(
    "--capabilities",
    default="",
    help="Comma-separated capability list.",
)
@click.option("--identity-token", default="", help="Identity token from the source protocol.")
@click.option("--issuer", default="", help="Name of the identity issuer.")
@click.option("--expiry-days", default=365, type=int, show_default=True, help="Days until identity expires.")
def init(name, protocol, description, capabilities, identity_token, issuer, expiry_days):
    """Create a new agent identity. Use --name flag for non-interactive mode."""
    svc = get_service(IdentityService)

    caps = [c.strip() for c in capabilities.split(",") if c.strip()] if capabilities else []

    result = svc.create_identity(
        display_name=name,
        source_protocol=protocol,
        identity_token=identity_token,
        capabilities=caps,
        description=description,
        issuer_name=issuer,
        expiry_days=expiry_days,
    )

    if "error" in result:
        _error(result["error"])

    _success(f"Agent identity created: {result['agent_id']}")
    _header("\nIdentity Details")
    _print_json(result)


# ---------------------------------------------------------------------------
# attestix verify
# ---------------------------------------------------------------------------

@cli.command()
@click.argument("agent_id")
def verify(agent_id):
    """Verify an agent identity by its ID.

    Checks existence, revocation status, expiry, and cryptographic signature.
    """
    svc = get_service(IdentityService)
    result = svc.verify_identity(agent_id)

    valid = result.get("valid", False)

    if valid:
        _success(f"Identity {agent_id} is VALID")
    else:
        _warn(f"Identity {agent_id} is INVALID")

    _header("\nVerification Checks")
    for check_name, passed in result.get("checks", {}).items():
        icon = click.style("PASS", fg="green") if passed else click.style("FAIL", fg="red")
        click.echo(f"  {check_name}: {icon}")

    click.echo()
    _print_json(result)

    if not valid:
        sys.exit(1)


# ---------------------------------------------------------------------------
# attestix compliance
# ---------------------------------------------------------------------------

@cli.command()
@click.argument("agent_id")
@click.option("--create", "create_profile", is_flag=True, help="Create a new compliance profile instead of viewing status.")
@click.option("--risk-category", type=click.Choice(["minimal", "limited", "high"], case_sensitive=False), help="EU AI Act risk category (for --create).")
@click.option("--provider-name", default="", help="Provider name (for --create).")
@click.option("--intended-purpose", default="", help="Intended purpose (for --create).")
def compliance(agent_id, create_profile, risk_category, provider_name, intended_purpose):
    """Show compliance status for an agent, or create a new compliance profile.

    Without --create, displays a gap analysis of EU AI Act obligations.
    With --create, interactively creates a compliance profile.
    """
    svc = get_service(ComplianceService)

    if create_profile:
        if not risk_category:
            risk_category = click.prompt(
                "Risk category",
                type=click.Choice(["minimal", "limited", "high"], case_sensitive=False),
            )
        if not provider_name:
            provider_name = click.prompt("Provider name")
        if not intended_purpose:
            intended_purpose = click.prompt("Intended purpose (optional)", default="")

        result = svc.create_compliance_profile(
            agent_id=agent_id,
            risk_category=risk_category,
            provider_name=provider_name,
            intended_purpose=intended_purpose,
        )
        if "error" in result:
            _error(result["error"])

        _success(f"Compliance profile created: {result['profile_id']}")
        _print_json(result)
        return

    # Default: show compliance status (gap analysis)
    result = svc.get_compliance_status(agent_id)

    if "error" in result:
        _error(result["error"])

    _header(f"Compliance Status for {agent_id}")
    click.echo(f"  Risk category : {result.get('risk_category', 'N/A')}")
    click.echo(f"  Compliant     : {click.style('YES', fg='green') if result.get('compliant') else click.style('NO', fg='red')}")
    click.echo(f"  Completion    : {result.get('completion_pct', 0)}%")

    if result.get("completed"):
        _header("\nCompleted Obligations")
        for item in result["completed"]:
            click.echo(f"  {click.style('*', fg='green')} {item}")

    if result.get("missing"):
        _header("\nMissing Obligations")
        for item in result["missing"]:
            click.echo(f"  {click.style('*', fg='red')} {item}")

    click.echo()
    _print_json(result)


# ---------------------------------------------------------------------------
# attestix audit
# ---------------------------------------------------------------------------

@cli.command()
@click.argument("agent_id")
@click.option("--action-type", default=None, help="Filter by action type (inference, delegation, data_access, external_call).")
@click.option("--limit", default=20, type=int, show_default=True, help="Maximum entries to return.")
def audit(agent_id, action_type, limit):
    """Show audit trail for an agent.

    Displays the tamper-evident, hash-chained action log recorded
    under EU AI Act Article 12 automatic logging requirements.
    """
    svc = get_service(ProvenanceService)
    entries = svc.get_audit_trail(agent_id, action_type=action_type, limit=limit)

    if not entries:
        _warn(f"No audit entries found for {agent_id}")
        return

    if entries and "error" in entries[0]:
        _error(entries[0]["error"])

    _header(f"Audit Trail for {agent_id} ({len(entries)} entries)")
    click.echo()

    for entry in entries:
        ts = entry.get("timestamp", "N/A")
        action = entry.get("action_type", "N/A")
        log_id = entry.get("log_id", "N/A")
        click.echo(f"  [{ts}] {click.style(action, fg='cyan')}  ({log_id})")
        if entry.get("input_summary"):
            click.echo(f"    Input  : {entry['input_summary']}")
        if entry.get("output_summary"):
            click.echo(f"    Output : {entry['output_summary']}")
        if entry.get("decision_rationale"):
            click.echo(f"    Reason : {entry['decision_rationale']}")
        if entry.get("human_override"):
            click.echo(f"    {click.style('Human override applied', fg='yellow')}")
        click.echo()

    # Verify hash chain integrity.
    # TODO(v0.5.0): this CLI re-verifies a ProvenanceService action-log chain
    # (different row shape than `attestix.audit.AuditEvent`): keys are
    # `log_id`/`action_type`/`timestamp` rather than `event_id`/`action`/
    # `occurred_at`. Routing it through `attestix.audit.verify_chain` would
    # require projecting these rows into the AuditEvent shape, which is more
    # work than just emitting the existing inline diagnostics here. Tracked
    # in the e2e walkthrough (P1 #4) — for now this stays inline; the
    # structured forensic upgrade lives on `attestix.audit.verify_chain` and
    # is surfaced via the portability importer.
    genesis_hash = "0" * 64
    chain_ok = True
    for i, entry in enumerate(entries):
        expected_prev = entries[i - 1].get("chain_hash", "") if i > 0 else genesis_hash
        actual_prev = entry.get("prev_hash", "")
        if actual_prev and actual_prev != expected_prev:
            chain_ok = False
            click.echo(
                click.style(f"  Chain break at entry {i} ({entry.get('log_id', 'N/A')}): "
                            f"prev_hash does not match previous entry's chain_hash", fg="red")
            )

        # Also verify the chain_hash itself if both fields are present
        if actual_prev and entry.get("chain_hash"):
            verify_data = {k: v for k, v in entry.items() if k not in ("chain_hash", "signature")}
            canonical = json.dumps(verify_data, sort_keys=True, separators=(",", ":"))
            recomputed = hashlib.sha256(f"{actual_prev}:{canonical}".encode("utf-8")).hexdigest()
            if recomputed != entry["chain_hash"]:
                chain_ok = False
                click.echo(
                    click.style(f"  Hash mismatch at entry {i} ({entry.get('log_id', 'N/A')}): "
                                f"recomputed chain_hash differs from stored value", fg="red")
                )

    if chain_ok:
        _success("Chain integrity: VERIFIED")
    else:
        click.echo(click.style("Chain integrity: BROKEN", fg="red"), err=True)


# ---------------------------------------------------------------------------
# attestix credential
# ---------------------------------------------------------------------------

@cli.command()
@click.option("--issue", "do_issue", is_flag=True, help="Issue a new credential.")
@click.option("--verify-cred", "cred_id_to_verify", default=None, help="Verify a credential by its ID.")
@click.option("--list", "do_list", is_flag=True, help="List credentials for an agent.")
@click.option("--revoke", "cred_id_to_revoke", default=None, help="Revoke a credential by its ID.")
@click.option("--agent-id", default=None, help="Agent ID (for --issue or --list).")
@click.option("--type", "credential_type", default="AgentIdentityCredential", show_default=True, help="Credential type (for --issue).")
@click.option("--issuer", default="", help="Issuer name (for --issue).")
@click.option("--claims", default="{}", help="JSON string of claims (for --issue).")
def credential(do_issue, cred_id_to_verify, do_list, cred_id_to_revoke, agent_id, credential_type, issuer, claims):
    """Issue, verify, list, or revoke W3C Verifiable Credentials.

    Examples:

        attestix credential --issue --agent-id attestix:abc123 --issuer "Acme Corp"

        attestix credential --verify-cred urn:uuid:some-id

        attestix credential --list --agent-id attestix:abc123

        attestix credential --revoke urn:uuid:some-id
    """
    svc = get_service(CredentialService)

    if do_issue:
        if not agent_id:
            agent_id = click.prompt("Agent ID (subject)")
        if not issuer:
            issuer = click.prompt("Issuer name")

        try:
            parsed_claims = json.loads(claims)
        except json.JSONDecodeError:
            _error("Invalid JSON for --claims. Provide a valid JSON string.")

        result = svc.issue_credential(
            subject_id=agent_id,
            credential_type=credential_type,
            issuer_name=issuer,
            claims=parsed_claims,
        )
        if "error" in result:
            _error(result["error"])

        _success(f"Credential issued: {result.get('id')}")
        _print_json(result)

    elif cred_id_to_verify:
        result = svc.verify_credential(cred_id_to_verify)

        if result.get("valid"):
            _success(f"Credential {cred_id_to_verify} is VALID")
        else:
            _warn(f"Credential {cred_id_to_verify} is INVALID")

        _header("\nVerification Checks")
        for check_name, passed in result.get("checks", {}).items():
            if isinstance(passed, bool):
                icon = click.style("PASS", fg="green") if passed else click.style("FAIL", fg="red")
                click.echo(f"  {check_name}: {icon}")

        click.echo()
        _print_json(result)

    elif do_list:
        if not agent_id:
            agent_id = click.prompt("Agent ID (optional, leave blank to list all)", default="")
            if not agent_id:
                agent_id = None
        results = svc.list_credentials(agent_id=agent_id)
        if results and "error" in results[0]:
            _error(results[0]["error"])

        if not results:
            _warn(f"No credentials found{' for ' + agent_id if agent_id else ''}.")
            return

        _header(f"Credentials{' for ' + agent_id if agent_id else ''} ({len(results)} found)")
        for cred in results:
            cred_id = cred.get("id", "N/A")
            cred_types = ", ".join(cred.get("type", []))
            subject = cred.get("credentialSubject", {}).get("id", "N/A")
            revoked = cred.get("credentialStatus", {}).get("revoked", False)
            status_str = click.style("REVOKED", fg="red") if revoked else click.style("ACTIVE", fg="green")
            click.echo(f"  {cred_id}")
            click.echo(f"    Type    : {cred_types}")
            click.echo(f"    Subject : {subject}")
            click.echo(f"    Status  : {status_str}")
            click.echo()

    elif cred_id_to_revoke:
        reason = click.prompt("Revocation reason (optional)", default="")
        result = svc.revoke_credential(cred_id_to_revoke, reason=reason)
        if "error" in result:
            _error(result["error"])
        _success(f"Credential revoked: {cred_id_to_revoke}")
        _print_json(result)

    else:
        click.echo(click.get_current_context().get_help())


# ---------------------------------------------------------------------------
# attestix status
# ---------------------------------------------------------------------------

@cli.command()
def status():
    """Show system status: data directory, version, and resource counts."""
    # Version
    try:
        ver = pkg_version("attestix")
    except PackageNotFoundError:
        try:
            from attestix import __version__
            ver = __version__
        except ImportError:
            ver = "unknown"

    _header("Attestix System Status")
    click.echo(f"  Version    : {ver}")
    click.echo(f"  Data dir   : {DATA_DIR}")
    click.echo()

    # Count resources
    identities = load_identities()
    agents = identities.get("agents", [])
    active_agents = [a for a in agents if not a.get("revoked")]
    revoked_agents = [a for a in agents if a.get("revoked")]

    credentials = load_credentials()
    creds = credentials.get("credentials", [])
    active_creds = [c for c in creds if not c.get("credentialStatus", {}).get("revoked")]

    compliance_data = load_compliance()
    profiles = compliance_data.get("profiles", [])
    declarations = compliance_data.get("declarations", [])

    provenance_data = load_provenance()
    prov_entries = provenance_data.get("entries", [])

    # Audit chain (v0.4.0+) is persisted in audit.json with schema
    # {"events": [...]}. Previously this read provenance.json["audit_log"],
    # which silently reported 0 after every `attestix import` because the
    # importer writes to audit.json.
    audit_data: dict = {}
    if AUDIT_FILE.exists():
        try:
            audit_data = json.loads(AUDIT_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            audit_data = {}
    audit_entries = audit_data.get("events", [])

    _header("Resource Counts")
    click.echo(f"  Agents (active)    : {len(active_agents)}")
    click.echo(f"  Agents (revoked)   : {len(revoked_agents)}")
    click.echo(f"  Credentials        : {len(creds)} ({len(active_creds)} active)")
    click.echo(f"  Compliance profiles: {len(profiles)}")
    click.echo(f"  Declarations       : {len(declarations)}")
    click.echo(f"  Provenance entries : {len(prov_entries)}")
    click.echo(f"  Audit log entries  : {len(audit_entries)}")


# ---------------------------------------------------------------------------
# attestix list
# ---------------------------------------------------------------------------

@cli.command(name="list")
@click.option("--protocol", default=None, help="Filter by source protocol.")
@click.option("--include-revoked", is_flag=True, help="Include revoked identities.")
@click.option("--limit", default=50, type=int, show_default=True, help="Maximum entries to return.")
def list_identities(protocol, include_revoked, limit):
    """List all agent identities."""
    svc = get_service(IdentityService)
    agents = svc.list_identities(
        source_protocol=protocol,
        include_revoked=include_revoked,
        limit=limit,
    )

    if not agents:
        _warn("No agent identities found.")
        return

    _header(f"Agent Identities ({len(agents)} found)")
    click.echo()

    for agent in agents:
        aid = agent.get("agent_id", "N/A")
        name = agent.get("display_name", "N/A")
        proto = agent.get("source_protocol", "N/A")
        revoked = agent.get("revoked", False)
        status_str = click.style("REVOKED", fg="red") if revoked else click.style("ACTIVE", fg="green")
        rep = agent.get("reputation_score")
        rep_str = f"{rep}" if rep is not None else "N/A"

        click.echo(f"  {click.style(aid, bold=True)}")
        click.echo(f"    Name       : {name}")
        click.echo(f"    Protocol   : {proto}")
        click.echo(f"    Status     : {status_str}")
        click.echo(f"    Reputation : {rep_str}")
        click.echo()

    # Show risk-category summary from compliance profiles
    compliance_data = load_compliance()
    profiles = compliance_data.get("profiles", [])
    agent_ids = {a.get("agent_id") for a in agents}
    risk_counts = {"minimal": 0, "limited": 0, "high": 0, "unacceptable": 0}
    for profile in profiles:
        if profile.get("agent_id") in agent_ids:
            cat = profile.get("risk_category", "").lower()
            if cat in risk_counts:
                risk_counts[cat] += 1

    _header("Risk Category Summary")
    for category in ("minimal", "limited", "high", "unacceptable"):
        count = risk_counts[category]
        color = {"minimal": "green", "limited": "yellow", "high": "red", "unacceptable": "magenta"}[category]
        click.echo(f"  {click.style(category.capitalize(), fg=color):30s}: {count}")
    click.echo()


# ---------------------------------------------------------------------------
# attestix import (M6 portability bundle ingest)
# ---------------------------------------------------------------------------

@cli.command(name="import")
@click.argument("bundle_path", type=click.Path(exists=True, dir_okay=False, readable=True))
@click.option("--force", is_flag=True, help="Allow import even if local data is non-empty (rows are appended, not merged).")
@click.option("--workspace", default=None, help="Target local workspace label (defaults to the bundle's workspace slug).")
@click.option("--verify-only", is_flag=True, help="Verify bundle integrity (manifest + per-table sha + chain) and report; do not write.")
def import_cmd(bundle_path, force, workspace, verify_only):
    """Import an Attestix portability bundle (M6 cloud export) into local OSS storage.

    Reads the gzipped USTAR bundle at BUNDLE_PATH, verifies the manifest +
    per-table SHA-256 + audit-chain end-to-end, and writes every row into the
    local Attestix storage (``~/.attestix/``) through the v0.4.0 Repository
    boundary. By default the command refuses if any local identities,
    credentials, or audit events already exist; pass --force to override.
    """
    # Local import: keep the CLI startup path snappy when this command is not used.
    from attestix.portability import (
        BundleError,
        BundleSchemaTooNewError,
        Importer,
        LocalDataExistsError,
        read_bundle,
    )

    # 1) Parse the bundle.
    try:
        bundle = read_bundle(bundle_path)
    except BundleError as e:
        _error(str(e))

    target_tenant = workspace or bundle.workspace.get("slug") or "default"
    importer = Importer(tenant_id=target_tenant)

    # 2) Refuse on non-empty unless --force.
    if not force and not verify_only and not importer.local_data_is_empty():
        summary = importer.local_data_summary()
        non_empty = [f"{k}={v}" for k, v in summary.items() if v]
        _error(
            "local Attestix storage is not empty ("
            + ", ".join(non_empty)
            + "). Re-run with --force to import alongside the existing rows, or "
            + "with --verify-only to inspect the bundle without writing."
        )

    _header(f"Attestix bundle: {bundle.path.name}")
    click.echo(f"  Format       : {bundle.bundle_format}")
    click.echo(f"  Manifest ver : {bundle.manifest_version}")
    click.echo(f"  Workspace    : {bundle.workspace.get('slug', '?')} ({bundle.workspace.get('id', '?')})")
    click.echo(f"  Region       : {bundle.workspace.get('region', '?')} / residency={bundle.workspace.get('data_residency', '?')}")
    click.echo(f"  Exported at  : {bundle.exported_at}")
    click.echo(f"  Exported by  : {bundle.exported_by.get('email') or bundle.exported_by.get('user_id') or '?'}")
    click.echo(f"  Core version : {bundle.core_version}")
    click.echo(f"  DB migration : {bundle.db_migration_max}")
    click.echo(f"  Target tenant: {target_tenant}")
    if target_tenant != bundle.workspace.get("slug", target_tenant):
        click.echo(
            f"  (audit_events stay under their original tenant "
            f"{bundle.workspace.get('slug')!r} so the chain hash remains valid)"
        )
    click.echo()

    # 3) Run the import (which also re-verifies schema + sha + chain).
    try:
        result = importer.run(bundle, force=force, verify_only=verify_only)
    except BundleSchemaTooNewError as e:
        _error(str(e))
    except LocalDataExistsError as e:
        _error(str(e))
    except BundleError as e:
        _error(str(e))

    _header("Tables")
    for t in result.tables:
        if t.oss_collection is None:
            note = click.style("skipped", fg="yellow")
            label = f"{t.name:<24}"
            click.echo(f"  [-] {label} {t.rows_seen} rows  {note} (cloud-only)")
            continue
        check = click.style("OK", fg="green")
        label = f"{t.name:<24}"
        sha_short = t.sha256[:12] + "…" if t.sha256 else ""
        click.echo(f"  [{check}] {label} {t.rows_written} rows  sha256:{sha_short}")
    click.echo()

    if result.chain_verified:
        _success("Audit chain reconciliation: VERIFIED")
    else:
        click.echo("  (no audit_events in bundle — nothing to chain-verify)")

    if verify_only:
        _success("\nVerify-only mode: bundle is intact. No data written.")
        return

    _success(f"\nImport complete. {result.total_written} rows written under tenant {result.target_tenant!r}.")
    click.echo()
    _header("Next steps")
    click.echo("  attestix list                # see imported identities")
    click.echo("  attestix audit <agent_id>    # verify the imported audit chain")
    click.echo("  attestix status              # confirm aggregate counts")


# ---------------------------------------------------------------------------
# attestix export (OSS portability bundle export)
# ---------------------------------------------------------------------------

@cli.command(name="export")
@click.argument("output_path", type=click.Path(dir_okay=False, writable=True))
@click.option(
    "--workspace",
    default=None,
    help="Only export rows tagged with this local workspace tenant (default: every row).",
)
@click.option(
    "--include-anchors/--no-include-anchors",
    default=True,
    show_default=True,
    help="Include the anchors collection in the bundle.",
)
@click.option(
    "--include-audit/--no-include-audit",
    default=True,
    show_default=True,
    help="Include the audit_events collection in the bundle.",
)
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite output_path if it already exists.",
)
@click.option(
    "--no-pretty",
    is_flag=True,
    help="Suppress the per-table progress lines (JSON-only summary at the end).",
)
def export_cmd(output_path, workspace, include_anchors, include_audit, force, no_pretty):
    """Export local OSS state as an Attestix portability bundle (M6-compatible).

    Writes a USTAR + gzip tarball at OUTPUT_PATH containing one JCS-canonical
    JSONL file per table, a ``manifest.json``, and a side-car
    ``manifest.sha256`` — the exact format the cloud worker emits and the
    importer (``attestix import``) accepts.

    The output is byte-stable across re-runs against the same OSS state:
    members are sorted alphabetically, tar mtimes are pinned to 0, and the
    gzip header carries mtime=0. Two consecutive exports of the same data
    produce identical bytes — useful for diffing audit-chain drift across
    backups.
    """
    from attestix.portability import BundleWriteError, write_bundle

    out = Path(output_path)
    if out.exists() and not force:
        _error(
            f"refusing to overwrite existing file {out!s}. "
            f"Re-run with --force to replace it."
        )

    if not no_pretty:
        _header(f"Attestix export → {out}")
        if workspace:
            click.echo(f"  Workspace filter : {workspace}")
        else:
            click.echo(f"  Workspace filter : (every tenant)")
        click.echo(f"  Include anchors  : {include_anchors}")
        click.echo(f"  Include audit    : {include_audit}")
        click.echo()

    try:
        result = write_bundle(
            out,
            workspace=workspace,
            include_anchors=include_anchors,
            include_audit=include_audit,
        )
    except BundleWriteError as e:
        _error(str(e))

    if not no_pretty:
        _header("Tables")
        for t in result.tables:
            check = click.style("OK", fg="green")
            label = f"{t.name:<24}"
            sha_short = t.sha256[:12] + "…"
            click.echo(
                f"  [{check}] {label} {t.row_count} rows  sha256:{sha_short}"
            )
        click.echo()

    _success(
        f"wrote {result.path}  {result.bytes} bytes  manifest_sha256={result.manifest_sha256}"
    )


if __name__ == "__main__":
    cli()
