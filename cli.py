"""Attestix CLI - Command-line interface for AI agent attestation infrastructure.

Wraps core Attestix services for interactive use: identity management,
compliance checks, audit trails, credential operations, and system status.
"""

import json
import sys
from importlib.metadata import version as pkg_version, PackageNotFoundError

import click

from config import DATA_DIR, load_identities, load_credentials, load_compliance, load_provenance
from services.cache import get_service
from services.identity_service import IdentityService
from services.compliance_service import ComplianceService
from services.credential_service import CredentialService
from services.provenance_service import ProvenanceService


# Valid source protocols for identity creation
SOURCE_PROTOCOLS = [
    "mcp", "a2a", "oauth2", "did", "api_key", "saml", "openid_connect", "custom",
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
@click.option("--name", prompt="Agent display name", help="Human-readable agent name.")
@click.option(
    "--protocol",
    prompt="Source protocol",
    type=click.Choice(SOURCE_PROTOCOLS, case_sensitive=False),
    help="Identity source protocol.",
)
@click.option("--description", prompt="Description (optional)", default="", help="Agent description.")
@click.option(
    "--capabilities",
    prompt="Capabilities (comma-separated, optional)",
    default="",
    help="Comma-separated capability list.",
)
@click.option("--issuer", prompt="Issuer name (optional)", default="", help="Name of the identity issuer.")
@click.option("--expiry-days", default=365, type=int, show_default=True, help="Days until identity expires.")
def init(name, protocol, description, capabilities, issuer, expiry_days):
    """Create a new agent identity (interactive prompts)."""
    svc = get_service(IdentityService)

    caps = [c.strip() for c in capabilities.split(",") if c.strip()] if capabilities else []

    result = svc.create_identity(
        display_name=name,
        source_protocol=protocol,
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

    if result.get("valid"):
        _success(f"Identity {agent_id} is VALID")
    else:
        _warn(f"Identity {agent_id} is INVALID")

    _header("\nVerification Checks")
    for check_name, passed in result.get("checks", {}).items():
        icon = click.style("PASS", fg="green") if passed else click.style("FAIL", fg="red")
        click.echo(f"  {check_name}: {icon}")

    click.echo()
    _print_json(result)


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
        results = svc.list_credentials(agent_id=agent_id)
        if results and "error" in results[0]:
            _error(results[0]["error"])

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
    audit_entries = provenance_data.get("audit_log", [])

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


if __name__ == "__main__":
    cli()
