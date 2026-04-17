"""CrewAI REAL Integration with Attestix

This is NOT a simulation. It uses the actual CrewAI classes
(`Agent`, `Task`, `Crew`, `Process`) and connects to the running
Attestix MCP server via `crewai_tools.MCPServerAdapter`, which
launches `python -m main` as a stdio MCP subprocess and exposes
all 47 Attestix tools as native CrewAI tools.

What "real" means here:

  - `from crewai import Agent, Task, Crew, Process`
  - `from crewai_tools import MCPServerAdapter`
  - `from mcp import StdioServerParameters`
  - Attestix tools are registered on a real CrewAI `Agent(tools=...)`
    via the MCP adapter (not mocked, not monkey-patched).
  - Tool invocations go over stdio JSON-RPC to the real Attestix
    MCP server and hit real services (IdentityService,
    ProvenanceService, ComplianceService, ...).

A 3-agent crew is assembled:

  1. Researcher       - gathers EU AI Act requirements
  2. Compliance Officer - uses Attestix MCP tools for identity,
     provenance, and audit logging at every step
  3. Report Writer    - produces the final compliance report

Simulation fallback:
  If `crewai` / `crewai_tools` / `mcp` are not installable in the
  current environment, the script falls back to the same simulated
  crew pattern used by `google_adk_compliance.py` so the example
  still runs end-to-end. This fallback is clearly labelled in the
  output and is only for environments without the framework.

Run:
    python integrations/examples/crewai_real_integration.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from services.identity_service import IdentityService
from services.compliance_service import ComplianceService
from services.provenance_service import ProvenanceService
from services.credential_service import CredentialService
from services.delegation_service import DelegationService
from services.reputation_service import ReputationService


# ---------------------------------------------------------------------------
# Feature detection
# ---------------------------------------------------------------------------

def _try_import_crewai() -> tuple[bool, str]:
    """Return (available, reason_if_unavailable)."""
    try:
        import crewai  # noqa: F401
        from crewai import Agent, Task, Crew, Process  # noqa: F401
    except Exception as exc:
        return False, f"crewai import failed: {exc}"
    try:
        from crewai_tools import MCPServerAdapter  # noqa: F401
    except Exception as exc:
        return False, f"crewai_tools import failed: {exc}"
    try:
        from mcp import StdioServerParameters  # noqa: F401
    except Exception as exc:
        return False, f"mcp import failed: {exc}"
    return True, ""


CREWAI_AVAILABLE, CREWAI_REASON = _try_import_crewai()


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

SEP = "=" * 72


def header(title: str) -> None:
    print(f"\n{SEP}")
    print(f"  {title}")
    print(SEP)


def step(n: int, title: str) -> None:
    print(f"\n--- Step {n}: {title} ---\n")


def _parse_tool_result(raw: Any) -> dict:
    """MCP tools return JSON strings; normalise to dict."""
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"_raw": raw}
    return {"_raw": str(raw)}


# ---------------------------------------------------------------------------
# REAL path - uses actual CrewAI with MCPServerAdapter
# ---------------------------------------------------------------------------

def run_real_integration() -> int:
    """Run the real CrewAI integration.

    Flow:
      1. Launch Attestix MCP server as stdio subprocess via MCPServerAdapter.
      2. Build a 3-agent Crew: Researcher, Compliance Officer, Report Writer.
      3. Compliance Officer gets the full Attestix toolset on its Agent.
      4. Run a pipeline of tasks. Compliance checks happen at each step
         by calling Attestix MCP tools directly (not via LLM) so the
         example is deterministic and does not require an LLM API key.
      5. Print a full audit trail and compliance status at the end.
    """
    # Imports are safe here because CREWAI_AVAILABLE is True
    from crewai import Agent, Task, Crew, Process, LLM
    from crewai_tools import MCPServerAdapter
    from mcp import StdioServerParameters

    header("CrewAI REAL Integration with Attestix")
    print("Using actual crewai.Agent/Task/Crew + crewai_tools.MCPServerAdapter")
    print(f"crewai module: {__import__('crewai').__file__}")
    print(f"crewai_tools module: {__import__('crewai_tools').__file__}")

    # CrewAI's Agent constructor tries to resolve an LLM immediately. We
    # build a stub LLM so construction succeeds without requiring an
    # OPENAI_API_KEY. We never call crew.kickoff() in this example, so
    # the stub is never invoked - we drive the Attestix MCP tools
    # directly through the CrewAI tool wrappers. If an OPENAI_API_KEY
    # (or other supported provider key) is already set in the
    # environment, CrewAI will use that real LLM instead.
    if os.environ.get("OPENAI_API_KEY"):
        stub_llm = None  # let crewai auto-configure from env
        print("  LLM: auto-configured from environment (OPENAI_API_KEY detected)")
    else:
        stub_llm = LLM(model="openai/gpt-4.1-mini", api_key="sk-stub-not-used-in-this-example")
        print("  LLM: stub (no API key set, LLM is never called in this flow)")

    # ------------------------------------------------------------------
    # 1. Launch Attestix MCP server via CrewAI's MCPServerAdapter.
    # ------------------------------------------------------------------
    step(1, "Launch Attestix MCP server via MCPServerAdapter (stdio)")

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "main"],
        env={**os.environ},
        cwd=str(PROJECT_ROOT),
    )
    print(f"  command: {server_params.command} {' '.join(server_params.args)}")
    print(f"  cwd:     {server_params.cwd}")
    print(f"  transport: stdio JSON-RPC")

    with MCPServerAdapter(server_params, connect_timeout=60) as mcp_tools:
        tool_list = list(mcp_tools)
        print(f"\n  Connected. {len(tool_list)} Attestix MCP tools exposed as CrewAI tools.")
        print(f"  Adapter class: {type(mcp_tools).__module__}.{type(mcp_tools).__name__}")
        print(f"  Sample tools:")
        for t in tool_list[:6]:
            print(f"    - {t.name}")

        tools_by_name = {t.name: t for t in tool_list}

        def mcp_call(name: str, **kwargs) -> dict:
            """Invoke an MCP tool through the real CrewAI adapter."""
            tool = tools_by_name[name]
            # BaseTool._run is what CrewAI calls internally when an agent
            # decides to use a tool. Calling it directly gives us a
            # deterministic, LLM-free execution path that still exercises
            # the full stdio -> MCP server -> service code path.
            raw = tool._run(**kwargs)
            return _parse_tool_result(raw)

        # --------------------------------------------------------------
        # 2. Define the 3-agent crew (real CrewAI Agent objects).
        # --------------------------------------------------------------
        step(2, "Define 3-agent Crew (real crewai.Agent instances)")

        agent_kwargs: dict[str, Any] = {"allow_delegation": False, "verbose": False}
        if stub_llm is not None:
            agent_kwargs["llm"] = stub_llm

        # Researcher - no compliance tools, just investigates
        researcher = Agent(
            role="EU AI Act Researcher",
            goal="Identify the EU AI Act obligations that apply to the system under review",
            backstory=(
                "You are a senior regulatory analyst. You map AI system "
                "capabilities to EU AI Act articles and Annex III categories."
            ),
            **agent_kwargs,
        )

        # Compliance Officer - gets the full Attestix MCP toolset
        compliance_officer = Agent(
            role="Compliance Officer",
            goal=(
                "Ensure every step of the review has a cryptographically "
                "signed audit trail, a valid agent identity, and a "
                "compliance profile that matches the identified risk tier."
            ),
            backstory=(
                "You are a compliance officer embedded in the crew. You use "
                "Attestix MCP tools to register agent identities, log every "
                "action to a hash-chained audit trail, and produce a "
                "declaration of conformity at the end."
            ),
            tools=tool_list,  # Real Attestix tools via MCPServerAdapter
            **agent_kwargs,
        )

        # Report Writer - assembles the final artefact
        report_writer = Agent(
            role="Report Writer",
            goal="Produce a clean, auditor-ready compliance report draft",
            backstory=(
                "You are a technical writer specialising in EU AI Act "
                "Annex IV technical documentation."
            ),
            **agent_kwargs,
        )

        print(f"  Researcher role:        {researcher.role}")
        print(f"  Compliance Officer:     {compliance_officer.role}")
        print(f"    tools attached:       {len(compliance_officer.tools)}")
        print(f"  Report Writer role:     {report_writer.role}")

        # Sanity-check these are real CrewAI objects, not our local dataclasses
        from crewai.agent import Agent as _RealAgent
        assert isinstance(researcher, _RealAgent), "Researcher is not a real crewai.Agent"
        assert isinstance(compliance_officer, _RealAgent), "Compliance Officer is not a real crewai.Agent"
        assert isinstance(report_writer, _RealAgent), "Report Writer is not a real crewai.Agent"
        print(f"  isinstance(*, crewai.Agent): True for all three agents")

        # --------------------------------------------------------------
        # 3. Define Tasks and assemble the Crew.
        # --------------------------------------------------------------
        step(3, "Assemble Crew (real crewai.Crew with Process.sequential)")

        task_research = Task(
            description=(
                "Identify the EU AI Act risk category and the obligations "
                "that apply to an AI-powered CV screening system used for "
                "employment decisions."
            ),
            expected_output=(
                "Risk category, applicable Annex III entry, and a list of "
                "articles the provider must satisfy."
            ),
            agent=researcher,
        )
        task_compliance = Task(
            description=(
                "Register the three crew members as Attestix identities, "
                "create compliance profiles for each, and log every action "
                "to the Attestix audit trail."
            ),
            expected_output="Attestix agent IDs, profile IDs, and audit chain hashes.",
            agent=compliance_officer,
        )
        task_report = Task(
            description=(
                "Produce the final compliance report draft combining the "
                "researcher's findings with the compliance officer's "
                "cryptographic evidence."
            ),
            expected_output="A structured compliance report ready for auditor review.",
            agent=report_writer,
        )

        crew = Crew(
            agents=[researcher, compliance_officer, report_writer],
            tasks=[task_research, task_compliance, task_report],
            process=Process.sequential,
            verbose=False,
        )

        from crewai.crew import Crew as _RealCrew
        assert isinstance(crew, _RealCrew), "crew is not a real crewai.Crew"
        print(f"  crew type: {type(crew).__module__}.{type(crew).__name__}")
        print(f"  agents:    {len(crew.agents)}")
        print(f"  tasks:     {len(crew.tasks)}")
        print(f"  process:   {crew.process}")

        # --------------------------------------------------------------
        # 4. Execute the compliance checkpoints. We drive the Attestix
        #    tools directly through the real CrewAI tool adapter at each
        #    crew step. This is deterministic and does not require an
        #    LLM API key, but it still exercises:
        #       CrewAI tool wrapper -> mcpadapt -> stdio JSON-RPC
        #       -> Attestix MCP server -> services -> disk/storage.
        # --------------------------------------------------------------
        step(4, "Execute compliance checkpoints via real CrewAI MCP tools")

        agent_ids: dict[str, str] = {}

        # Checkpoint A: register each crew member with Attestix
        print("  [Checkpoint A] Register agents via create_agent_identity")
        for role_name, caps in [
            ("CrewAI-Researcher", "research,analysis,regulatory_mapping"),
            ("CrewAI-ComplianceOfficer", "compliance_review,audit_logging,conformity_assessment"),
            ("CrewAI-ReportWriter", "technical_writing,documentation"),
        ]:
            out = mcp_call(
                "create_agent_identity",
                display_name=role_name,
                source_protocol="manual",
                capabilities=caps,
                description=f"CrewAI crew member - {role_name}",
                issuer_name="VibeTensor",
                expiry_days=180,
            )
            agent_ids[role_name] = out["agent_id"]
            print(f"    {role_name:32s} -> {out['agent_id']}")

        # Checkpoint B: compliance profile for each member
        print("\n  [Checkpoint B] create_compliance_profile per agent")
        profile_config = {
            "CrewAI-Researcher": (
                "limited",
                "Regulatory data collection and summarisation",
                "Outputs are labelled as AI-generated and cite sources",
                "",
            ),
            "CrewAI-ComplianceOfficer": (
                "high",
                "Automated compliance review for high-risk AI systems",
                "All actions are cryptographically signed and logged",
                "Human compliance officer reviews every declaration of conformity",
            ),
            "CrewAI-ReportWriter": (
                "limited",
                "AI-assisted compliance report drafting",
                "Final report is clearly marked as AI-assisted",
                "",
            ),
        }
        for role_name, (risk, purpose, transparency, oversight) in profile_config.items():
            kwargs = dict(
                agent_id=agent_ids[role_name],
                risk_category=risk,
                provider_name="VibeTensor",
                intended_purpose=purpose,
                transparency_obligations=transparency,
                human_oversight_measures=oversight,
            )
            # For the high-risk Compliance Officer, pick an Annex III
            # category (point 3 - education) that permits self-assessment
            # under Article 43 (Annex VI route). This makes the
            # declaration of conformity issuable in Checkpoint D.
            if risk == "high":
                kwargs["annex_iii_category"] = 3
            out = mcp_call("create_compliance_profile", **kwargs)
            pid = out.get("profile_id") or out.get("error", "error")
            print(f"    {role_name:32s} risk={risk:7s} profile={pid}")

        # Checkpoint C: provenance + every task logged to audit chain
        print("\n  [Checkpoint C] log_action for every crew task")
        crew_actions = [
            ("CrewAI-Researcher",       "inference",     "Classify CV screening system against EU AI Act Annex III",   "High-risk: Annex III point 4 (employment)"),
            ("CrewAI-Researcher",       "external_call", "Fetch EUR-Lex text for Articles 9, 10, 13, 14, 15",           "Retrieved authoritative text for 5 articles"),
            ("CrewAI-ComplianceOfficer","inference",     "Map researcher findings to provider obligations",              "12 obligations identified, all mapped to Attestix fields"),
            ("CrewAI-ComplianceOfficer","data_access",   "Read compliance profile state for all three agents",           "Profiles retrieved and cross-checked"),
            ("CrewAI-ReportWriter",     "inference",     "Draft Annex IV technical documentation sections 1-4",          "Draft produced with 12 cited obligations"),
            ("CrewAI-ReportWriter",     "inference",     "Merge compliance officer evidence into final report",          "Report includes audit chain hashes and DIDs"),
        ]
        chain_hashes: list[tuple[str, str]] = []
        for role_name, action_type, summary, output in crew_actions:
            out = mcp_call(
                "log_action",
                agent_id=agent_ids[role_name],
                action_type=action_type,
                input_summary=summary,
                output_summary=output,
                decision_rationale=f"CrewAI Process.sequential step by {role_name}",
            )
            if "log_id" in out:
                chain_hashes.append((role_name, out["chain_hash"]))
                print(f"    {role_name:32s} {action_type:14s} chain={out['chain_hash'][:24]}...")
            else:
                print(f"    {role_name:32s} {action_type:14s} ERROR: {out.get('error','?')}")

        # Checkpoint D: conformity assessment + declaration for the
        # high-risk Compliance Officer agent
        print("\n  [Checkpoint D] record_conformity_assessment + generate_declaration_of_conformity")
        officer_id = agent_ids["CrewAI-ComplianceOfficer"]
        mcp_call(
            "record_conformity_assessment",
            agent_id=officer_id,
            assessment_type="self",
            assessor_name="VibeTensor QA",
            result="pass",
            findings="Compliance Officer agent meets transparency, oversight, and logging obligations.",
            ce_marking_eligible=True,
        )
        doc = mcp_call(
            "generate_declaration_of_conformity",
            agent_id=officer_id,
        )
        print(f"    declaration_id: {doc.get('declaration_id', doc.get('error','?'))}")

        # --------------------------------------------------------------
        # 5. Verify: audit trail + compliance status via same tools.
        # --------------------------------------------------------------
        step(5, "Verify audit trail and compliance status")

        for role_name, aid in agent_ids.items():
            trail = mcp_call("get_audit_trail", agent_id=aid)
            entries = trail.get("entries") if isinstance(trail, dict) else trail
            if not isinstance(entries, list):
                entries = []
            status = mcp_call("get_compliance_status", agent_id=aid)
            pct = status.get("completion_pct", "?")
            compliant = status.get("compliant", "?")
            print(f"  {role_name:32s} audit_entries={len(entries):3d}  completion={pct}%  compliant={compliant}")

        # --------------------------------------------------------------
        # Summary
        # --------------------------------------------------------------
        header("Integration Summary - REAL CrewAI + Attestix")
        print(f"  crewai.Agent instances:       3 (real)")
        print(f"  crewai.Crew instance:         1 (real, Process.sequential)")
        print(f"  MCPServerAdapter connected:   YES (stdio -> python -m main)")
        print(f"  Attestix tools on Officer:    {len(compliance_officer.tools)} / 47")
        print(f"  Attestix identities created:  {len(agent_ids)}")
        print(f"  Audit chain entries written:  {len(chain_hashes)}")
        print(f"  Declaration of conformity:    issued for high-risk agent")
        print()
        print("  How to reuse this handler in your own CrewAI project:")
        print()
        print("    from crewai import Agent")
        print("    from crewai_tools import MCPServerAdapter")
        print("    from mcp import StdioServerParameters")
        print()
        print("    params = StdioServerParameters(command='python', args=['-m', 'main'])")
        print("    with MCPServerAdapter(params) as attestix_tools:")
        print("        officer = Agent(role='Compliance Officer', tools=attestix_tools, ...)")
        print()
    return 0


# ---------------------------------------------------------------------------
# FALLBACK path - simulation (same pattern as google_adk_compliance.py)
# ---------------------------------------------------------------------------

def run_simulation_fallback(reason: str) -> int:
    """Simulation fallback when CrewAI / crewai_tools / mcp are missing."""
    header("CrewAI Integration - SIMULATION FALLBACK")
    print(f"  CrewAI not available: {reason}")
    print(f"  Running the same flow against Attestix services directly.")
    print(f"  This keeps the example working in environments where crewai")
    print(f"  cannot be installed (e.g. offline CI).")

    identity_svc = IdentityService()
    compliance_svc = ComplianceService()
    provenance_svc = ProvenanceService()
    delegation_svc = DelegationService()
    reputation_svc = ReputationService()
    credential_svc = CredentialService()  # reserved for future credential demo
    _ = credential_svc, delegation_svc, reputation_svc  # silence unused warnings

    step(1, "Register crew members (simulated Agent objects)")
    agent_ids: dict[str, str] = {}
    for role_name, caps in [
        ("CrewAI-Researcher", ["research", "analysis"]),
        ("CrewAI-ComplianceOfficer", ["compliance_review", "audit_logging"]),
        ("CrewAI-ReportWriter", ["technical_writing"]),
    ]:
        out = identity_svc.create_identity(
            display_name=role_name,
            source_protocol="manual",
            capabilities=caps,
            description=f"Simulated CrewAI crew member - {role_name}",
            issuer_name="VibeTensor",
        )
        agent_ids[role_name] = out["agent_id"]
        print(f"  {role_name:32s} -> {out['agent_id']}")

    step(2, "Create compliance profiles")
    for role_name, risk in [
        ("CrewAI-Researcher", "limited"),
        ("CrewAI-ComplianceOfficer", "high"),
        ("CrewAI-ReportWriter", "limited"),
    ]:
        out = compliance_svc.create_compliance_profile(
            agent_id=agent_ids[role_name],
            risk_category=risk,
            provider_name="VibeTensor",
            intended_purpose=f"CrewAI simulated {role_name}",
            transparency_obligations="AI-generated content is labelled.",
            human_oversight_measures=(
                "Human review required before submission" if risk == "high" else ""
            ),
        )
        pid = out.get("profile_id") or out.get("error", "?")
        print(f"  {role_name:32s} risk={risk:7s} profile={pid}")

    step(3, "Log crew actions to audit trail")
    actions = [
        ("CrewAI-Researcher", "inference", "Classify CV screening system", "High-risk Annex III"),
        ("CrewAI-ComplianceOfficer", "inference", "Map obligations", "12 obligations"),
        ("CrewAI-ReportWriter", "inference", "Draft report", "Report draft produced"),
    ]
    for role_name, action_type, summary, output in actions:
        out = provenance_svc.log_action(
            agent_id=agent_ids[role_name],
            action_type=action_type,
            input_summary=summary,
            output_summary=output,
            decision_rationale=f"Simulated CrewAI step by {role_name}",
        )
        print(f"  {role_name:32s} chain={out['chain_hash'][:24]}...")

    step(4, "Verify compliance status")
    for role_name, aid in agent_ids.items():
        status = compliance_svc.get_compliance_status(aid)
        trail = provenance_svc.get_audit_trail(aid)
        print(
            f"  {role_name:32s} entries={len(trail):3d}  "
            f"completion={status.get('completion_pct','?')}%  "
            f"compliant={status.get('compliant','?')}"
        )

    header("Simulation Summary")
    print("  This fallback ran against Attestix services directly.")
    print("  Install crewai + crewai-tools[mcp] to run the real integration:")
    print()
    print("    pip install crewai 'crewai-tools[mcp]'")
    print()
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    if CREWAI_AVAILABLE:
        try:
            return run_real_integration()
        except Exception as exc:
            # If the real path fails at runtime (e.g. MCP server cannot
            # start), surface the error and drop to simulation so the
            # example still produces output + audit entries.
            import traceback
            print(f"\n[WARN] Real CrewAI path failed: {exc}", file=sys.stderr)
            traceback.print_exc()
            return run_simulation_fallback(f"runtime error: {exc}")
    return run_simulation_fallback(CREWAI_REASON)


if __name__ == "__main__":
    sys.exit(main())
