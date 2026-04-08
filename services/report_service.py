"""Report generation service for Attestix.

Generates self-contained HTML compliance reports (and optional PDF via
weasyprint) for regulators and auditors. Each report consolidates an
agent's identity, risk classification, obligation status, declaration
of conformity, training data provenance, model lineage, audit trail,
and credential inventory into a single file with inline CSS.
"""

import html
from datetime import datetime, timezone
from typing import List, Optional

from errors import ErrorCategory, log_and_format_error


class ReportService:
    """Generates HTML and PDF compliance reports for a given agent."""

    def __init__(self):
        self._compliance_svc = None
        self._identity_svc = None
        self._credential_svc = None
        self._provenance_svc = None

    # -- lazy-loaded service references (avoids circular imports) ----------

    @property
    def compliance_svc(self):
        if self._compliance_svc is None:
            from services.cache import get_service
            from services.compliance_service import ComplianceService
            self._compliance_svc = get_service(ComplianceService)
        return self._compliance_svc

    @property
    def identity_svc(self):
        if self._identity_svc is None:
            from services.cache import get_service
            from services.identity_service import IdentityService
            self._identity_svc = get_service(IdentityService)
        return self._identity_svc

    @property
    def credential_svc(self):
        if self._credential_svc is None:
            from services.cache import get_service
            from services.credential_service import CredentialService
            self._credential_svc = get_service(CredentialService)
        return self._credential_svc

    @property
    def provenance_svc(self):
        if self._provenance_svc is None:
            from services.cache import get_service
            from services.provenance_service import ProvenanceService
            self._provenance_svc = get_service(ProvenanceService)
        return self._provenance_svc

    # -- public API --------------------------------------------------------

    def generate_html_report(self, agent_id: str) -> dict:
        """Build a self-contained HTML compliance report for *agent_id*.

        Returns ``{"html": "<full document>", "agent_id": ...}`` on
        success, or ``{"error": "..."}`` on failure.
        """
        try:
            # 1. Agent identity
            agent = self.identity_svc.get_identity(agent_id)
            if not agent:
                return {"error": f"Agent {agent_id} not found"}

            # 2. Compliance profile
            profile = self.compliance_svc.get_compliance_profile(agent_id)

            # 3. Gap analysis / compliance status
            status = (
                self.compliance_svc.get_compliance_status(agent_id)
                if profile
                else None
            )

            # 4. Declaration of conformity
            declaration = None
            if profile and profile["conformity"].get("declaration_id"):
                from config import load_compliance
                comp_data = load_compliance()
                decl_id = profile["conformity"]["declaration_id"]
                declaration = next(
                    (d for d in comp_data["declarations"] if d["declaration_id"] == decl_id),
                    None,
                )

            # 5. Provenance (training data + model lineage + audit)
            provenance = self.provenance_svc.get_provenance(agent_id)

            # 6. Full audit trail (last 10)
            audit_trail = self.provenance_svc.get_audit_trail(agent_id, limit=10)

            # 7. Credentials
            credentials = self.credential_svc.list_credentials(agent_id=agent_id)

            # Assemble HTML
            generated_at = datetime.now(timezone.utc).isoformat()
            report_html = self._render_html(
                agent=agent,
                profile=profile,
                status=status,
                declaration=declaration,
                provenance=provenance,
                audit_trail=audit_trail,
                credentials=credentials,
                generated_at=generated_at,
            )

            return {
                "html": report_html,
                "agent_id": agent_id,
                "generated_at": generated_at,
            }
        except Exception as e:
            msg = log_and_format_error(
                "generate_html_report", e, ErrorCategory.COMPLIANCE,
                agent_id=agent_id,
            )
            return {"error": msg}

    def generate_pdf_report(self, agent_id: str, output_path: Optional[str] = None) -> dict:
        """Generate a PDF compliance report.

        Requires the optional ``weasyprint`` dependency
        (``pip install attestix[reports]``).  If weasyprint is not
        installed the method returns the HTML string instead so the
        caller can still save or display it.

        Parameters
        ----------
        agent_id : str
            The agent whose report to generate.
        output_path : str, optional
            File path for the PDF.  When *None* the PDF bytes are
            returned directly under the ``"pdf_bytes"`` key.

        Returns
        -------
        dict
            ``{"pdf_path": "...", ...}`` or ``{"pdf_bytes": bytes, ...}``
            on success.  Falls back to ``{"html": "...", "fallback": True}``
            when weasyprint is missing.
        """
        html_result = self.generate_html_report(agent_id)
        if "error" in html_result:
            return html_result

        try:
            from weasyprint import HTML as WeasyprintHTML  # type: ignore[import-untyped]
        except (ImportError, OSError):
            return {
                "html": html_result["html"],
                "agent_id": agent_id,
                "generated_at": html_result["generated_at"],
                "fallback": True,
                "message": (
                    "weasyprint is not installed. Install it with: "
                    "pip install attestix[reports]"
                ),
            }

        try:
            wp_doc = WeasyprintHTML(string=html_result["html"])
            if output_path:
                wp_doc.write_pdf(output_path)
                return {
                    "pdf_path": output_path,
                    "agent_id": agent_id,
                    "generated_at": html_result["generated_at"],
                }
            else:
                pdf_bytes = wp_doc.write_pdf()
                return {
                    "pdf_bytes": pdf_bytes,
                    "agent_id": agent_id,
                    "generated_at": html_result["generated_at"],
                }
        except Exception as e:
            msg = log_and_format_error(
                "generate_pdf_report", e, ErrorCategory.COMPLIANCE,
                agent_id=agent_id,
            )
            return {"error": msg}

    def generate_bulk_html_report(self, agent_ids: List[str]) -> dict:
        """Generate a single HTML document covering multiple agents.

        Each agent gets its own labelled section inside a single
        self-contained HTML file.  Individual agent errors are recorded
        inline so a partial failure never blocks the rest of the batch.

        Parameters
        ----------
        agent_ids : list of str
            IDs of the agents to include in the report.

        Returns
        -------
        dict
            ``{"html": "<full document>", "agent_ids": [...],
               "generated_at": "...", "errors": {...}}``
            where *errors* maps agent_id to an error message for any
            agent that could not be rendered.
        """
        if not agent_ids:
            return {"error": "agent_ids must be a non-empty list"}

        generated_at = datetime.now(timezone.utc).isoformat()
        agent_sections: List[str] = []
        errors: dict = {}

        for agent_id in agent_ids:
            try:
                result = self.generate_html_report(agent_id)
                if "error" in result:
                    errors[agent_id] = result["error"]
                    agent_sections.append(
                        self._bulk_error_section(agent_id, result["error"])
                    )
                else:
                    agent_sections.append(
                        self._bulk_wrap_agent_section(agent_id, result["html"])
                    )
            except Exception as e:
                msg = log_and_format_error(
                    "generate_bulk_html_report", e, ErrorCategory.COMPLIANCE,
                    agent_id=agent_id,
                )
                errors[agent_id] = msg
                agent_sections.append(self._bulk_error_section(agent_id, msg))

        body = "\n".join(agent_sections)
        count = len(agent_ids)
        error_count = len(errors)
        ok_count = count - error_count

        bulk_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Attestix Bulk Compliance Report ({count} agents)</title>
{_INLINE_CSS}
{_BULK_EXTRA_CSS}
</head>
<body>
<header>
  <div class="logo">ATTESTIX</div>
  <div class="subtitle">Bulk EU AI Act Compliance Report</div>
  <div class="bulk-meta">
    {self._esc(count)} agent(s) &nbsp;|&nbsp;
    {self._esc(ok_count)} rendered &nbsp;|&nbsp;
    {self._esc(error_count)} error(s)
  </div>
</header>
<main>
{body}
<section class="meta">
  <p>Report generated: {self._esc(generated_at)}</p>
  <p>Attestix v0.2.4 - attestix.io</p>
</section>
</main>
</body>
</html>"""

        return {
            "html": bulk_html,
            "agent_ids": agent_ids,
            "generated_at": generated_at,
            "errors": errors,
        }

    # -- bulk rendering helpers --------------------------------------------

    @staticmethod
    def _bulk_wrap_agent_section(agent_id: str, single_report_html: str) -> str:
        """Extract the <main> content from a single-agent report and wrap it."""
        # Pull the content between <main> and </main> tags
        start_tag = "<main>"
        end_tag = "</main>"
        start = single_report_html.find(start_tag)
        end = single_report_html.rfind(end_tag)
        if start != -1 and end != -1:
            inner = single_report_html[start + len(start_tag):end]
            # Strip the trailing meta section (already added at bulk level)
            meta_start = inner.rfind('<section class="meta">')
            if meta_start != -1:
                inner = inner[:meta_start]
        else:
            inner = single_report_html

        escaped_id = html.escape(agent_id)
        return f"""<div class="bulk-agent-block">
  <div class="bulk-agent-header">Agent: <span class="mono">{escaped_id}</span></div>
  {inner}
</div>"""

    @staticmethod
    def _bulk_error_section(agent_id: str, error_msg: str) -> str:
        escaped_id = html.escape(agent_id)
        escaped_msg = html.escape(str(error_msg))
        return f"""<div class="bulk-agent-block bulk-agent-error">
  <div class="bulk-agent-header">Agent: <span class="mono">{escaped_id}</span></div>
  <section>
    <p class="status-fail">Error generating report: {escaped_msg}</p>
  </section>
</div>"""

    # -- private rendering helpers -----------------------------------------

    @staticmethod
    def _esc(value) -> str:
        """HTML-escape a value, converting None to empty string."""
        if value is None:
            return ""
        return html.escape(str(value))

    def _render_html(
        self,
        agent: dict,
        profile: Optional[dict],
        status: Optional[dict],
        declaration: Optional[dict],
        provenance: dict,
        audit_trail: list,
        credentials: list,
        generated_at: str,
    ) -> str:
        """Return a complete, self-contained HTML document."""
        sections = [
            self._section_identity(agent),
        ]

        if profile:
            sections.append(self._section_risk(profile))

        if status:
            sections.append(self._section_compliance_status(status))

        if declaration:
            sections.append(self._section_declaration(declaration))

        sections.append(self._section_provenance(provenance))
        sections.append(self._section_audit_trail(audit_trail))
        sections.append(self._section_credentials(credentials))
        sections.append(self._section_signature(agent))

        body = "\n".join(sections)
        agent_name = self._esc(agent.get("display_name", agent["agent_id"]))

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Attestix Compliance Report - {agent_name}</title>
{_INLINE_CSS}
</head>
<body>
<header>
  <div class="logo">ATTESTIX</div>
  <div class="subtitle">EU AI Act Compliance Report</div>
</header>
<main>
{body}
<section class="meta">
  <p>Report generated: {self._esc(generated_at)}</p>
  <p>Attestix v0.2.4 - attestix.io</p>
</section>
</main>
</body>
</html>"""

    # -- individual section builders ---------------------------------------

    def _section_identity(self, agent: dict) -> str:
        capabilities = agent.get("capabilities", [])
        cap_badges = "".join(
            f'<span class="badge">{self._esc(c)}</span>' for c in capabilities
        )
        did_value = agent.get("did", agent.get("issuer_did", ""))
        return f"""<section>
  <h2>Agent Identity</h2>
  <table>
    <tr><th>Name</th><td>{self._esc(agent.get("display_name", ""))}</td></tr>
    <tr><th>Agent ID</th><td class="mono">{self._esc(agent["agent_id"])}</td></tr>
    <tr><th>DID</th><td class="mono">{self._esc(did_value)}</td></tr>
    <tr><th>Protocol</th><td>{self._esc(agent.get("source_protocol", ""))}</td></tr>
    <tr><th>Description</th><td>{self._esc(agent.get("description", ""))}</td></tr>
    <tr><th>Capabilities</th><td>{cap_badges if cap_badges else "None"}</td></tr>
    <tr><th>Created</th><td>{self._esc(agent.get("created_at", ""))}</td></tr>
  </table>
</section>"""

    def _section_risk(self, profile: dict) -> str:
        risk = profile.get("risk_category", "unknown")
        risk_class = f"risk-{risk}"
        obligations = profile.get("required_obligations", [])
        obl_list = "".join(
            f"<li>{self._esc(o)}</li>" for o in obligations
        )
        return f"""<section>
  <h2>Risk Classification</h2>
  <p>Category: <span class="badge {risk_class}">{self._esc(risk.upper())}</span></p>
  <p>Provider: {self._esc(profile.get("provider", {}).get("name", ""))}</p>
  <p>Intended purpose: {self._esc(profile.get("ai_system", {}).get("intended_purpose", ""))}</p>
  <h3>Required Obligations</h3>
  <ul>{obl_list}</ul>
</section>"""

    def _section_compliance_status(self, status: dict) -> str:
        pct = status.get("completion_pct", 0)
        compliant = status.get("compliant", False)
        status_label = "COMPLIANT" if compliant else "INCOMPLETE"
        status_class = "status-pass" if compliant else "status-fail"

        completed = status.get("completed", [])
        missing = status.get("missing", [])

        completed_rows = "".join(
            f'<tr><td>{self._esc(item)}</td><td class="status-pass">Done</td></tr>'
            for item in completed
        )
        missing_rows = "".join(
            f'<tr><td>{self._esc(item)}</td><td class="status-fail">Missing</td></tr>'
            for item in missing
        )

        return f"""<section>
  <h2>Compliance Status</h2>
  <p>Overall: <span class="badge {status_class}">{status_label}</span></p>
  <div class="progress-bar"><div class="progress-fill" style="width:{pct}%"></div></div>
  <p>{self._esc(pct)}% complete ({len(completed)} of {len(completed) + len(missing)} items)</p>
  <table>
    <tr><th>Obligation</th><th>Status</th></tr>
    {completed_rows}
    {missing_rows}
  </table>
</section>"""

    def _section_declaration(self, declaration: dict) -> str:
        fields = declaration.get("annex_v_fields", {})
        rows = ""
        for key, value in fields.items():
            display_key = key.replace("_", " ").lstrip("0123456789 ")
            if isinstance(value, list):
                value = ", ".join(str(v) for v in value)
            rows += f"<tr><th>{self._esc(display_key)}</th><td>{self._esc(value)}</td></tr>\n"

        return f"""<section>
  <h2>Declaration of Conformity (Annex V)</h2>
  <p class="mono">{self._esc(declaration.get("declaration_id", ""))}</p>
  <p>{self._esc(declaration.get("regulation_reference", ""))}</p>
  <table>
    {rows}
  </table>
</section>"""

    def _section_provenance(self, provenance: dict) -> str:
        training_data = provenance.get("training_data", [])
        model_lineage = provenance.get("model_lineage", [])

        td_rows = ""
        for td in training_data:
            td_rows += (
                f"<tr>"
                f"<td>{self._esc(td.get('dataset_name', ''))}</td>"
                f"<td>{self._esc(td.get('source_url', ''))}</td>"
                f"<td>{self._esc(td.get('license', ''))}</td>"
                f"<td>{'Yes' if td.get('contains_personal_data') else 'No'}</td>"
                f"</tr>\n"
            )

        ml_rows = ""
        for ml in model_lineage:
            metrics = ml.get("evaluation_metrics", {})
            metrics_str = ", ".join(f"{k}: {v}" for k, v in metrics.items()) if metrics else "None"
            ml_rows += (
                f"<tr>"
                f"<td>{self._esc(ml.get('base_model', ''))}</td>"
                f"<td>{self._esc(ml.get('base_model_provider', ''))}</td>"
                f"<td>{self._esc(ml.get('fine_tuning_method', ''))}</td>"
                f"<td>{self._esc(metrics_str)}</td>"
                f"</tr>\n"
            )

        return f"""<section>
  <h2>Training Data Provenance</h2>
  {
      f'''<table>
    <tr><th>Dataset</th><th>Source</th><th>License</th><th>Personal Data</th></tr>
    {td_rows}
  </table>''' if td_rows else '<p class="empty">No training data recorded.</p>'
  }
  <h2>Model Lineage</h2>
  {
      f'''<table>
    <tr><th>Base Model</th><th>Provider</th><th>Fine-tuning</th><th>Metrics</th></tr>
    {ml_rows}
  </table>''' if ml_rows else '<p class="empty">No model lineage recorded.</p>'
  }
</section>"""

    def _section_audit_trail(self, audit_trail: list) -> str:
        if not audit_trail:
            return """<section>
  <h2>Audit Trail (Last 10)</h2>
  <p class="empty">No audit entries.</p>
</section>"""

        rows = ""
        for entry in audit_trail:
            rows += (
                f"<tr>"
                f"<td>{self._esc(entry.get('timestamp', ''))}</td>"
                f"<td>{self._esc(entry.get('action_type', ''))}</td>"
                f"<td>{self._esc(entry.get('input_summary', ''))}</td>"
                f"<td>{self._esc(entry.get('output_summary', ''))}</td>"
                f"<td>{'Yes' if entry.get('human_override') else 'No'}</td>"
                f"</tr>\n"
            )

        return f"""<section>
  <h2>Audit Trail (Last 10)</h2>
  <table>
    <tr><th>Timestamp</th><th>Action</th><th>Input</th><th>Output</th><th>Human Override</th></tr>
    {rows}
  </table>
</section>"""

    def _section_credentials(self, credentials: list) -> str:
        if not credentials:
            return """<section>
  <h2>Credentials</h2>
  <p class="empty">No credentials issued.</p>
</section>"""

        rows = ""
        for cred in credentials:
            cred_types = cred.get("type", [])
            # Filter out base VerifiableCredential to show the specific type
            specific = [t for t in cred_types if t != "VerifiableCredential"]
            type_str = ", ".join(specific) if specific else ", ".join(cred_types)
            revoked = cred.get("credentialStatus", {}).get("revoked", False)
            status_class = "status-fail" if revoked else "status-pass"
            status_label = "Revoked" if revoked else "Active"

            # Proof details
            proof = cred.get("proof", {})
            proof_type = proof.get("type", "")
            proof_value_raw = proof.get("proofValue", "")
            proof_value_display = (
                proof_value_raw[:40] + "..." if len(proof_value_raw) > 40 else proof_value_raw
            )
            verification_method = proof.get("verificationMethod", "")

            rows += (
                f"<tr>"
                f"<td class='mono'>{self._esc(cred.get('id', ''))}</td>"
                f"<td>{self._esc(type_str)}</td>"
                f"<td>{self._esc(cred.get('issuanceDate', ''))}</td>"
                f"<td class='{status_class}'>{status_label}</td>"
                f"<td class='mono'>{self._esc(proof_type)}</td>"
                f"<td class='mono'>{self._esc(proof_value_display)}</td>"
                f"<td class='mono'>{self._esc(verification_method)}</td>"
                f"</tr>\n"
            )

        return f"""<section>
  <h2>Credentials</h2>
  <table>
    <tr><th>ID</th><th>Type</th><th>Issued</th><th>Status</th><th>Proof Type</th><th>Proof Value</th><th>Verification Method</th></tr>
    {rows}
  </table>
</section>"""

    def _section_signature(self, agent: dict) -> str:
        """Render the Digital Signature Verification section for auditors."""
        signing_key_did = self._esc(agent.get("issuer", {}).get("did", ""))

        signature_raw = agent.get("signature", "") or ""
        signature_display = (
            signature_raw[:40] + "..." if len(signature_raw) > 40 else signature_raw
        )

        verify_result = self.identity_svc.verify_identity(agent["agent_id"])
        sig_valid = verify_result.get("checks", {}).get("signature_valid", False)
        verification_status_class = "status-pass" if sig_valid else "status-fail"
        verification_status_label = "VALID" if sig_valid else "UNVERIFIED"

        agent_id_esc = self._esc(agent["agent_id"])

        return f"""<section>
  <h2>Digital Signature Verification</h2>
  <table>
    <tr>
      <th>Signing Key DID</th>
      <td class="mono">{signing_key_did}</td>
    </tr>
    <tr>
      <th>Signature Algorithm</th>
      <td class="mono">Ed25519Signature2020</td>
    </tr>
    <tr>
      <th>Identity Signature</th>
      <td class="mono">{self._esc(signature_display)}</td>
    </tr>
    <tr>
      <th>Verification Status</th>
      <td class="{verification_status_class}">{verification_status_label}</td>
    </tr>
  </table>
  <p style="margin-top:1rem;color:var(--text-muted);font-size:0.85rem;">
    This report was cryptographically generated by Attestix. Verify using:
    <span class="mono">attestix verify {agent_id_esc}</span>
  </p>
</section>"""


# ---------------------------------------------------------------------------
# Inline CSS (self-contained, no external dependencies)
# ---------------------------------------------------------------------------

_INLINE_CSS = """<style>
  :root {
    --indigo: #4F46E5;
    --indigo-light: #6366F1;
    --bg: #0f1219;
    --surface: #1a1f2e;
    --border: #2d3348;
    --text: #e2e8f0;
    --text-muted: #94a3b8;
    --green: #059669;
    --red: #dc2626;
    --gold: #E1A32C;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    padding: 2rem;
  }

  header {
    text-align: center;
    padding: 2rem 0 1.5rem;
    border-bottom: 2px solid var(--indigo);
    margin-bottom: 2rem;
  }
  .logo {
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: 0.15em;
    color: var(--gold);
  }
  .subtitle {
    font-size: 1.1rem;
    color: var(--text-muted);
    margin-top: 0.25rem;
  }

  main { max-width: 900px; margin: 0 auto; }

  section {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }
  h2 {
    color: var(--indigo-light);
    font-size: 1.25rem;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
  }
  h3 {
    color: var(--text);
    font-size: 1rem;
    margin: 1rem 0 0.5rem;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 0.5rem;
  }
  th, td {
    text-align: left;
    padding: 0.5rem 0.75rem;
    border-bottom: 1px solid var(--border);
    font-size: 0.9rem;
  }
  th {
    color: var(--text-muted);
    font-weight: 600;
    white-space: nowrap;
    width: 1%;
  }

  .mono { font-family: "Fira Code", "Consolas", monospace; font-size: 0.85rem; word-break: break-all; }
  .empty { color: var(--text-muted); font-style: italic; }

  .badge {
    display: inline-block;
    padding: 0.15rem 0.6rem;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 600;
    background: var(--indigo);
    color: #fff;
    margin: 0.1rem 0.2rem;
  }
  .risk-minimal  { background: var(--green); }
  .risk-limited  { background: var(--indigo); }
  .risk-high     { background: var(--red); }

  .status-pass { color: var(--green); font-weight: 600; }
  .status-fail { color: var(--red); font-weight: 600; }

  .progress-bar {
    background: var(--border);
    border-radius: 4px;
    height: 8px;
    margin: 0.5rem 0;
    overflow: hidden;
  }
  .progress-fill {
    background: var(--indigo);
    height: 100%;
    border-radius: 4px;
    transition: width 0.3s;
  }

  ul { margin-left: 1.5rem; }
  li { margin-bottom: 0.25rem; color: var(--text-muted); font-size: 0.9rem; }

  .meta {
    background: transparent;
    border: none;
    text-align: center;
    color: var(--text-muted);
    font-size: 0.8rem;
    padding-top: 1rem;
  }

  @media print {
    body { background: #fff; color: #111; padding: 1rem; }
    header { border-color: var(--indigo); }
    .logo { color: var(--indigo); }
    section { border-color: #ddd; background: #fafafa; }
    h2 { color: var(--indigo); border-color: #ddd; }
    th { color: #555; }
    .progress-bar { background: #ddd; }
    .badge { color: #fff; }
  }
</style>"""

# ---------------------------------------------------------------------------
# Extra CSS for bulk reports (appended to _INLINE_CSS inside bulk documents)
# ---------------------------------------------------------------------------

_BULK_EXTRA_CSS = """<style>
  .bulk-meta {
    font-size: 0.9rem;
    color: var(--text-muted);
    margin-top: 0.5rem;
  }
  .bulk-agent-block {
    border: 2px solid var(--indigo);
    border-radius: 10px;
    padding: 1rem 1rem 0.25rem;
    margin-bottom: 2.5rem;
  }
  .bulk-agent-block.bulk-agent-error {
    border-color: var(--red);
  }
  .bulk-agent-header {
    font-size: 1rem;
    font-weight: 700;
    color: var(--gold);
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
  }
  .bulk-agent-block section:first-of-type {
    margin-top: 0;
  }
</style>"""
