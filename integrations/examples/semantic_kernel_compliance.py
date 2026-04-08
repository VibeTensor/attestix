"""Microsoft Semantic Kernel + Attestix Integration Example

Shows how to add EU AI Act compliance as a Semantic Kernel plugin
using Attestix for identity, audit trails, and credentials.

Run: python integrations/examples/semantic_kernel_compliance.py

This script simulates the Semantic Kernel pattern using plain Python
classes, so it works without the semantic-kernel package installed.
All Attestix services are called directly via real service imports.
"""

import json
import sys
import textwrap
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# ---------------------------------------------------------------------------
# Path setup so Attestix services can be imported from the repo root
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from services.identity_service import IdentityService
from services.compliance_service import ComplianceService
from services.provenance_service import ProvenanceService
from services.credential_service import CredentialService


# ===========================================================================
# Simulated Semantic Kernel primitives (no semantic-kernel package required)
# ===========================================================================

@dataclass
class KernelFunction:
    """Simulates a Semantic Kernel KernelFunction.

    In a real Semantic Kernel plugin, each public method decorated with
    @kernel_function becomes a KernelFunction. Here we wrap plain callables
    with metadata so the kernel can discover and invoke them.
    """

    name: str
    description: str
    handler: Callable[..., Any]
    plugin_name: str = ""

    def invoke(self, **kwargs) -> Any:
        return self.handler(**kwargs)

    def __repr__(self) -> str:
        return f"KernelFunction(plugin={self.plugin_name!r}, name={self.name!r})"


@dataclass
class KernelPlugin:
    """Simulates a Semantic Kernel plugin (a named collection of functions)."""

    name: str
    description: str
    functions: Dict[str, KernelFunction] = field(default_factory=dict)

    def add_function(self, fn: KernelFunction) -> None:
        fn.plugin_name = self.name
        self.functions[fn.name] = fn

    def __getitem__(self, key: str) -> KernelFunction:
        return self.functions[key]

    def function_names(self) -> List[str]:
        return list(self.functions.keys())


class Kernel:
    """Simulates the Semantic Kernel orchestration engine.

    Supports plugin registration, function lookup, and a simple
    invoke-with-logging pattern that mirrors how the real Kernel
    dispatches calls to plugins.
    """

    def __init__(self):
        self.plugins: Dict[str, KernelPlugin] = {}
        self._invocation_log: List[dict] = []

    def add_plugin(self, plugin: KernelPlugin) -> None:
        self.plugins[plugin.name] = plugin

    def get_function(self, plugin_name: str, function_name: str) -> KernelFunction:
        return self.plugins[plugin_name][function_name]

    def invoke(self, plugin_name: str, function_name: str, **kwargs) -> Any:
        fn = self.get_function(plugin_name, function_name)
        start = datetime.now(timezone.utc)
        result = fn.invoke(**kwargs)
        elapsed_ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000
        self._invocation_log.append({
            "plugin": plugin_name,
            "function": function_name,
            "elapsed_ms": round(elapsed_ms, 2),
            "timestamp": start.isoformat(),
        })
        return result

    def list_plugins(self) -> List[str]:
        return list(self.plugins.keys())


# ===========================================================================
# Attestix Compliance Plugin for Semantic Kernel
# ===========================================================================

class AttestixCompliancePlugin:
    """Wraps Attestix services as a Semantic Kernel plugin.

    This plugin exposes four kernel functions that map to the core
    Attestix compliance workflow:

      1. create_agent_identity  - Register an agent with a UAIT and DID
      2. get_compliance_status  - Gap analysis against EU AI Act obligations
      3. log_action             - Article 12 tamper-evident audit logging
      4. issue_credential       - Issue a W3C Verifiable Credential
    """

    PLUGIN_NAME = "AttestixCompliance"

    def __init__(self):
        self._identity_svc = IdentityService()
        self._compliance_svc = ComplianceService()
        self._provenance_svc = ProvenanceService()
        self._credential_svc = CredentialService()

    def as_kernel_plugin(self) -> KernelPlugin:
        """Build a KernelPlugin with all Attestix kernel functions."""
        plugin = KernelPlugin(
            name=self.PLUGIN_NAME,
            description="EU AI Act compliance via Attestix - identity, audit, credentials",
        )

        plugin.add_function(KernelFunction(
            name="create_agent_identity",
            description="Create a UAIT identity with DID for an AI agent",
            handler=self._create_agent_identity,
        ))

        plugin.add_function(KernelFunction(
            name="get_compliance_status",
            description="Run a gap analysis of EU AI Act obligations for an agent",
            handler=self._get_compliance_status,
        ))

        plugin.add_function(KernelFunction(
            name="log_action",
            description="Record an agent action in the Article 12 audit trail",
            handler=self._log_action,
        ))

        plugin.add_function(KernelFunction(
            name="issue_credential",
            description="Issue a W3C Verifiable Credential for an agent",
            handler=self._issue_credential,
        ))

        return plugin

    # -----------------------------------------------------------------------
    # KernelFunction handlers (each wraps one or more Attestix service calls)
    # -----------------------------------------------------------------------

    def _create_agent_identity(
        self,
        display_name: str,
        capabilities: Optional[List[str]] = None,
        description: str = "",
        provider_name: str = "",
        risk_category: str = "limited",
        intended_purpose: str = "",
    ) -> dict:
        """Create an agent identity and an accompanying compliance profile."""
        # 1. Create the UAIT
        agent = self._identity_svc.create_identity(
            display_name=display_name,
            source_protocol="semantic-kernel",
            capabilities=capabilities or [],
            description=description,
            issuer_name=provider_name or "SemanticKernel",
        )
        agent_id = agent["agent_id"]

        # 2. Create the compliance profile
        profile = self._compliance_svc.create_compliance_profile(
            agent_id=agent_id,
            risk_category=risk_category,
            provider_name=provider_name or "SemanticKernel",
            intended_purpose=intended_purpose,
        )

        return {
            "agent_id": agent_id,
            "display_name": display_name,
            "risk_category": risk_category,
            "profile_id": profile.get("profile_id", profile.get("error")),
            "server_did": agent["issuer"]["did"],
        }

    def _get_compliance_status(self, agent_id: str) -> dict:
        """Return compliance gap analysis for an agent."""
        return self._compliance_svc.get_compliance_status(agent_id)

    def _log_action(
        self,
        agent_id: str,
        action_type: str,
        input_summary: str = "",
        output_summary: str = "",
        decision_rationale: str = "",
    ) -> dict:
        """Log an action to the tamper-evident audit trail."""
        return self._provenance_svc.log_action(
            agent_id=agent_id,
            action_type=action_type,
            input_summary=input_summary,
            output_summary=output_summary,
            decision_rationale=decision_rationale,
        )

    def _issue_credential(
        self,
        agent_id: str,
        credential_type: str = "AgentIdentityCredential",
        issuer_name: str = "",
        claims: Optional[Dict] = None,
    ) -> dict:
        """Issue a W3C Verifiable Credential."""
        return self._credential_svc.issue_credential(
            agent_id=agent_id,
            credential_type=credential_type,
            issuer_name=issuer_name,
            claims=claims or {},
        )


# ===========================================================================
# Compliance-Wrapped Execution Middleware
# ===========================================================================

class ComplianceWrappedKernel:
    """Wraps a Kernel so every function invocation is automatically logged
    to the Attestix audit trail and checked against compliance status.

    This demonstrates how compliance becomes a transparent middleware
    layer around any existing Semantic Kernel workflow.
    """

    def __init__(self, kernel: Kernel, agent_id: str):
        self.kernel = kernel
        self.agent_id = agent_id

    def invoke(self, plugin_name: str, function_name: str, **kwargs) -> Any:
        compliance_fn = self.kernel.get_function("AttestixCompliance", "log_action")

        # Pre-execution: log the intent
        compliance_fn.invoke(
            agent_id=self.agent_id,
            action_type="inference",
            input_summary=f"Invoking {plugin_name}.{function_name}",
            output_summary="",
            decision_rationale=f"Kernel dispatched {function_name} with {len(kwargs)} arguments",
        )

        # Execute the actual function
        result = self.kernel.invoke(plugin_name, function_name, **kwargs)

        # Post-execution: log the outcome
        outcome_summary = "success" if not isinstance(result, dict) or "error" not in result else "error"
        compliance_fn.invoke(
            agent_id=self.agent_id,
            action_type="inference",
            input_summary=f"Completed {plugin_name}.{function_name}",
            output_summary=f"Result: {outcome_summary}",
            decision_rationale="Automatic post-execution audit logging",
        )

        return result


# ===========================================================================
# Simulated Business Logic Plugin (the "existing" kernel functions)
# ===========================================================================

def build_document_analysis_plugin() -> KernelPlugin:
    """Simulates a business logic plugin that analyzes documents.

    In a real Semantic Kernel app, this would call an LLM or custom logic.
    Here we return canned results to demonstrate the compliance wrapping.
    """
    plugin = KernelPlugin(
        name="DocumentAnalysis",
        description="Analyze documents using AI",
    )

    def summarize_document(text: str = "", max_length: int = 100) -> dict:
        # Simulated LLM summary
        summary = text[:max_length] + "..." if len(text) > max_length else text
        return {
            "summary": summary or "Document analysis complete.",
            "word_count": len(text.split()),
            "confidence": 0.92,
        }

    def classify_risk(document_text: str = "") -> dict:
        # Simulated risk classification
        keywords = {"financial", "medical", "legal", "personal"}
        found = [kw for kw in keywords if kw in document_text.lower()]
        risk_level = "high" if len(found) >= 2 else "limited" if found else "minimal"
        return {
            "risk_level": risk_level,
            "risk_indicators": found or ["none"],
            "recommendation": f"Document classified as {risk_level}-risk based on content analysis",
        }

    plugin.add_function(KernelFunction(
        name="summarize_document",
        description="Summarize a document using AI",
        handler=summarize_document,
    ))

    plugin.add_function(KernelFunction(
        name="classify_risk",
        description="Classify document risk level",
        handler=classify_risk,
    ))

    return plugin


# ===========================================================================
# Helper utilities
# ===========================================================================

def pp(obj: Any, indent: int = 2) -> None:
    """Pretty-print a dict as indented JSON."""
    print(json.dumps(obj, indent=indent, default=str))


def section(title: str) -> None:
    """Print a section header."""
    width = 70
    print(f"\n{'=' * width}")
    print(f"  {title}")
    print(f"{'=' * width}\n")


# ===========================================================================
# Main demonstration
# ===========================================================================

def main():
    # ------------------------------------------------------------------
    # 1. Build the Kernel and register plugins
    # ------------------------------------------------------------------
    section("Step 1: Initialize Kernel and Register Plugins")

    kernel = Kernel()

    # Register the Attestix compliance plugin
    attestix_plugin = AttestixCompliancePlugin()
    kernel.add_plugin(attestix_plugin.as_kernel_plugin())

    # Register a simulated business logic plugin
    kernel.add_plugin(build_document_analysis_plugin())

    print("Registered plugins:")
    for name in kernel.list_plugins():
        plugin = kernel.plugins[name]
        print(f"  [{name}] {plugin.description}")
        for fn_name in plugin.function_names():
            fn = plugin[fn_name]
            print(f"    - {fn_name}: {fn.description}")

    # ------------------------------------------------------------------
    # 2. Create an agent identity via the compliance plugin
    # ------------------------------------------------------------------
    section("Step 2: Create Agent Identity via Compliance Plugin")

    identity_result = kernel.invoke(
        "AttestixCompliance",
        "create_agent_identity",
        display_name="SK-DocAnalyzer",
        capabilities=["document_summarization", "risk_classification", "compliance_check"],
        description="Semantic Kernel agent for EU-compliant document analysis",
        provider_name="Contoso AI Division",
        risk_category="limited",
        intended_purpose="Automated document analysis with risk classification for enterprise workflows",
    )

    agent_id = identity_result["agent_id"]
    print(f"Agent created successfully:")
    print(f"  Agent ID:      {agent_id}")
    print(f"  Display Name:  {identity_result['display_name']}")
    print(f"  Risk Category: {identity_result['risk_category']}")
    print(f"  Profile ID:    {identity_result['profile_id']}")
    print(f"  Server DID:    {identity_result['server_did'][:40]}...")

    # ------------------------------------------------------------------
    # 3. Initial compliance gap analysis
    # ------------------------------------------------------------------
    section("Step 3: Initial Compliance Gap Analysis")

    status = kernel.invoke(
        "AttestixCompliance",
        "get_compliance_status",
        agent_id=agent_id,
    )

    print(f"Compliance Status for {agent_id}:")
    print(f"  Risk Category: {status['risk_category']}")
    print(f"  Compliant:     {status['compliant']}")
    print(f"  Completion:    {status['completion_pct']}%")
    print(f"\n  Completed items ({len(status['completed'])}):")
    for item in status["completed"]:
        print(f"    [DONE] {item}")
    print(f"\n  Missing items ({len(status['missing'])}):")
    for item in status["missing"]:
        print(f"    [TODO] {item}")

    # ------------------------------------------------------------------
    # 4. Compliance-wrapped execution of business logic
    # ------------------------------------------------------------------
    section("Step 4: Compliance-Wrapped Kernel Execution")

    wrapped_kernel = ComplianceWrappedKernel(kernel, agent_id)

    print("Running document analysis with automatic audit logging...\n")

    # Invoke summarize_document through the compliance wrapper
    sample_text = (
        "This financial report contains personal data of clients "
        "and includes medical insurance claims totaling $2.4M. "
        "The legal department has flagged several entries for review "
        "under GDPR Article 9 special category data provisions."
    )

    print(f"Input document ({len(sample_text)} chars):")
    print(f"  \"{sample_text[:80]}...\"\n")

    summary_result = wrapped_kernel.invoke(
        "DocumentAnalysis",
        "summarize_document",
        text=sample_text,
        max_length=80,
    )
    print("Summarization result:")
    pp(summary_result)

    # Invoke classify_risk through the compliance wrapper
    print()
    risk_result = wrapped_kernel.invoke(
        "DocumentAnalysis",
        "classify_risk",
        document_text=sample_text,
    )
    print("Risk classification result:")
    pp(risk_result)

    # ------------------------------------------------------------------
    # 5. Risk classification and conformity assessment flow
    # ------------------------------------------------------------------
    section("Step 5: Risk Classification and Conformity Assessment")

    detected_risk = risk_result["risk_level"]
    print(f"Detected risk level from document analysis: {detected_risk}")
    print(f"Agent's registered risk category: {status['risk_category']}")

    if detected_risk == "high":
        print("\n  [WARNING] Document contains high-risk content.")
        print("  EU AI Act requires enhanced oversight for high-risk operations.")
        print("  Logging risk escalation to audit trail...\n")
    else:
        print(f"\n  Document risk level ({detected_risk}) is within agent's risk category.")
        print("  No escalation needed.\n")

    # Log the risk assessment as an audit action
    risk_log = kernel.invoke(
        "AttestixCompliance",
        "log_action",
        agent_id=agent_id,
        action_type="inference",
        input_summary=f"Risk classification of document ({len(sample_text)} chars)",
        output_summary=f"Risk level: {detected_risk}, indicators: {risk_result['risk_indicators']}",
        decision_rationale=f"Automated risk classification per EU AI Act Article 9 requirements",
    )
    print("Risk assessment logged to audit trail:")
    print(f"  Log ID:     {risk_log['log_id']}")
    print(f"  Chain Hash: {risk_log['chain_hash'][:32]}...")
    print(f"  Timestamp:  {risk_log['timestamp']}")

    # Record a conformity self-assessment (allowed for limited-risk systems)
    print("\nRecording conformity self-assessment for limited-risk system...")
    assessment = attestix_plugin._compliance_svc.record_conformity_assessment(
        agent_id=agent_id,
        assessment_type="self",
        assessor_name="Contoso AI Division - Internal QA",
        result="pass",
        findings="Agent operates within limited-risk parameters. Transparency obligations met.",
        ce_marking_eligible=False,
    )
    if "error" not in assessment:
        print(f"  Assessment ID: {assessment['assessment_id']}")
        print(f"  Type:          {assessment['assessment_type']}")
        print(f"  Result:        {assessment['result']}")
        print(f"  Assessor:      {assessment['assessor_name']}")
    else:
        print(f"  Assessment error: {assessment['error']}")

    # ------------------------------------------------------------------
    # 6. Issue a credential and verify it
    # ------------------------------------------------------------------
    section("Step 6: Issue and Verify Compliance Credential")

    credential = kernel.invoke(
        "AttestixCompliance",
        "issue_credential",
        agent_id=agent_id,
        credential_type="EUAIActComplianceCredential",
        issuer_name="Contoso AI Division",
        claims={
            "risk_category": "limited",
            "conformity_assessment_passed": True,
            "transparency_obligations_met": True,
            "audit_trail_enabled": True,
            "framework": "Microsoft Semantic Kernel + Attestix",
        },
    )

    print("Issued W3C Verifiable Credential:")
    print(f"  Credential ID: {credential['id']}")
    print(f"  Type:          {credential['type']}")
    print(f"  Issuer DID:    {credential['issuer']['id'][:40]}...")
    print(f"  Subject:       {credential['credentialSubject']['id']}")
    print(f"  Issued:        {credential['issuanceDate']}")
    print(f"  Expires:       {credential['expirationDate']}")
    print(f"  Proof Type:    {credential['proof']['type']}")

    # Verify the credential
    print("\nVerifying credential...")
    verification = attestix_plugin._credential_svc.verify_credential(credential["id"])
    print(f"  Valid: {verification['valid']}")
    for check, passed in verification.get("checks", {}).items():
        symbol = "PASS" if passed else "FAIL"
        print(f"    [{symbol}] {check}")

    # ------------------------------------------------------------------
    # 7. Final compliance status after all steps
    # ------------------------------------------------------------------
    section("Step 7: Final Compliance Status")

    final_status = kernel.invoke(
        "AttestixCompliance",
        "get_compliance_status",
        agent_id=agent_id,
    )

    print(f"Final Compliance Status for {agent_id}:")
    print(f"  Compliant:  {final_status['compliant']}")
    print(f"  Completion: {final_status['completion_pct']}%")
    print(f"\n  Completed ({len(final_status['completed'])}):")
    for item in final_status["completed"]:
        print(f"    [DONE] {item}")
    if final_status["missing"]:
        print(f"\n  Still missing ({len(final_status['missing'])}):")
        for item in final_status["missing"]:
            print(f"    [TODO] {item}")

    # ------------------------------------------------------------------
    # 8. Summary of the kernel invocation log
    # ------------------------------------------------------------------
    section("Step 8: Kernel Invocation Summary")

    print(f"Total kernel invocations: {len(kernel._invocation_log)}\n")
    for i, entry in enumerate(kernel._invocation_log, 1):
        print(f"  {i:2d}. {entry['plugin']}.{entry['function']} ({entry['elapsed_ms']:.1f}ms)")

    # ------------------------------------------------------------------
    # Done
    # ------------------------------------------------------------------
    section("Integration Complete")

    print(textwrap.dedent(f"""\
        This example demonstrated:

          1. Plugin Registration - Attestix compliance functions registered
             as a Semantic Kernel plugin alongside business logic plugins

          2. Compliance-Wrapped Execution - Every business logic call was
             automatically logged to a tamper-evident audit trail (Article 12)

          3. Risk Classification - Documents analyzed and risk-classified
             per EU AI Act categories (minimal, limited, high, unacceptable)

          4. Conformity Assessment - Self-assessment recorded for a
             limited-risk system (Article 43)

          5. Verifiable Credentials - W3C VC issued and cryptographically
             verified with Ed25519Signature2020

          6. Gap Analysis - Real-time compliance status showing completed
             and missing obligations

        Agent ID: {agent_id}
        All artifacts are cryptographically signed and stored locally.
    """))


if __name__ == "__main__":
    main()
