"""Regression test for v0.4.0rc2 P0 #5: GRC quickstart -> audit_log_count == 0.

The rc.2 validation (paper/internal/v0.4.0rc2-rc-validation-isolated-2026-05-28.md
P0-F) caught that running the live grc-consultant quickstart end-to-end
left ``get_provenance(agent_id)["audit_log_count"]`` at ``0`` and
``attestix status`` showing ``Audit log entries: 0`` — because only
``log_action`` wrote to the legacy ``provenance.json::audit_log`` chain,
while ``record_*`` / ``create_*`` / ``record_conformity_assessment`` /
``generate_declaration_of_conformity`` only wrote to their own collections.
For the GRC persona — which specifically procures audit trails — the
headline product claim returned zero rows.

v0.4.0rc3 fixes this in two ways:

1. Every state-changing service method already emits to the new
   ``audit.json::events`` chain via the per-service ``safe_emit`` hook
   (T033/T034 wiring landed in #84).
2. :meth:`ProvenanceService.get_provenance` now COUNTS rows in both chains
   (legacy + new audit collection) so the user-visible field reflects all
   audit activity, not just the legacy chain.

This test mirrors the live grc-consultant quickstart in
``website/content/docs/quickstart/grc-consultant.mdx`` and asserts the
counts that the RC validation would have caught.
"""

from __future__ import annotations

import json

import attestix.config as _attestix_config
from attestix.services.compliance_service import ComplianceService
from attestix.services.credential_service import CredentialService
from attestix.services.identity_service import IdentityService
from attestix.services.provenance_service import ProvenanceService


def test_grc_quickstart_audit_chain_is_nonempty(tmp_attestix):
    """End-to-end GRC workflow produces a non-empty audit chain.

    Mirrors the published quickstart minus the on-chain anchor step. The
    assertion is that after the documented workflow:

    * the new audit collection (``audit.json::events``) has at least one
      event per state-changing operation, and
    * ``ProvenanceService.get_provenance`` reports ``audit_log_count > 0``
      so an evaluator copy-pasting the doc never sees the silent-zero bug
      again.
    """
    # Step 1: create the agent.
    agent_id = IdentityService().create_identity(
        display_name="client-hr-screener",
        source_protocol="manual",
        capabilities=["cv_screening", "candidate_ranking"],
        issuer_name="Client Co. (assessed by VibeTensor)",
    )["agent_id"]

    # Step 2: training data (Article 10).
    ProvenanceService().record_training_data(
        agent_id=agent_id,
        dataset_name="Client historical hiring records 2020-2024",
        source_url="internal://client/hr",
        license="Proprietary",
        data_categories=["employment", "demographics"],
        contains_personal_data=True,
        data_governance_measures=(
            "Removed protected attributes per Art. 10(2)(f). Bias audit Q4-2025."
        ),
    )

    # Step 3: compliance profile (Annex III §4(a) — high-risk HR screening).
    ComplianceService().create_compliance_profile(
        agent_id=agent_id,
        risk_category="high",
        provider_name="Client Co.",
        intended_purpose="Initial CV screening with human reviewer in the loop.",
        human_oversight_measures=(
            "Recruiter reviews shortlist; no automated rejection."
        ),
        transparency_obligations=(
            "Candidates informed of AI assistance per Article 50."
        ),
        annex_iii_category=4,
    )

    # Step 4: third-party conformity assessment (Article 43).
    ComplianceService().record_conformity_assessment(
        agent_id=agent_id,
        assessment_type="third_party",
        assessor_name="Notified Body NB-0482",
        result="pass",
        findings="System meets Annex III §4(a) requirements with documented oversight.",
        ce_marking_eligible=True,
    )

    # Step 5: declaration of conformity (Annex V).
    declaration = ComplianceService().generate_declaration_of_conformity(agent_id)
    assert declaration.get("declaration_id"), (
        "v0.4.0rc3 (P0 #4): the declaration must be issued — the fintech "
        f"silent-None bug must not regress. Got: {declaration}"
    )

    # ----- assertions -----

    # (a) Direct read of the new audit chain — what the brief's spec test
    # uses: `len(load_audit()["events"]) > 0` after the documented workflow.
    # Read AUDIT_FILE through the config module so the conftest monkeypatch
    # (which redirects every *_FILE path to a tmp dir) is honored. A
    # top-level `from attestix.config import AUDIT_FILE` would capture the
    # production path at import time and silently read pollution from prior
    # runs.
    audit_file = _attestix_config.AUDIT_FILE
    assert audit_file.exists(), (
        "audit.json must be created by the per-service audit emitter — "
        "if this fails the safe_emit wiring is broken (FR-015)."
    )
    audit_doc = json.loads(audit_file.read_text(encoding="utf-8"))
    events = audit_doc.get("events", [])
    assert len(events) > 0, (
        "v0.4.0rc3 (P0 #5): the GRC quickstart must produce at least one "
        "audit event. Got 0 events — this is the rc.2 silent-zero bug."
    )

    # (b) The actions emitted MUST include the high-signal compliance events
    # so the audit chain reflects the documented workflow, not just identity
    # creation. Mismatching action names here is also a regression signal.
    actions = {ev.get("action") for ev in events}
    expected_actions = {
        "identity.create",
        "provenance.record_training_data",
        "compliance.create_profile",
        "compliance.record_assessment",
        "compliance.generate_declaration",
    }
    missing = expected_actions - actions
    assert not missing, (
        "v0.4.0rc3 (P0 #5): the audit chain is missing actions that the "
        f"GRC workflow must emit: {sorted(missing)}. Actions present: "
        f"{sorted(actions)}."
    )

    # (c) The user-visible audit_log_count from get_provenance must reflect
    # the new audit chain so the doc's `bundle["audit_log_count"]` does not
    # print 0.
    bundle = ProvenanceService().get_provenance(agent_id)
    assert bundle["audit_log_count"] > 0, (
        "v0.4.0rc3 (P0 #5): ProvenanceService.get_provenance must report "
        "a non-zero audit_log_count when the new audit chain has rows for "
        f"the agent. Got bundle={bundle}."
    )


def test_grc_quickstart_audit_events_are_chain_linked(tmp_attestix):
    """The audit chain emitted during the GRC workflow must verify cleanly.

    P0 #5 fix MUST NOT break chain integrity — every event must carry a
    valid prev_hash / chain_hash linkage and ``verify_chain`` must return
    True. This is the explicit constraint in the v0.4.0rc3 brief: chain
    integrity MUST hold after record_* emissions.
    """
    from attestix.audit import AuditEvent, AuditEventEmitter, verify_chain

    # Run a tiny subset of the workflow — just enough to emit 3+ chained
    # events through the default emitter.
    agent_id = IdentityService().create_identity(
        display_name="chain-check-agent",
        source_protocol="manual",
    )["agent_id"]
    ProvenanceService().record_training_data(
        agent_id=agent_id, dataset_name="ds1", source_url="internal://ds",
    )
    ProvenanceService().record_model_lineage(
        agent_id=agent_id, base_model="gpt-4o-mini",
    )

    # Read back the chain via the default emitter and verify it.
    chain = AuditEventEmitter().read_chain()
    assert len(chain) >= 3
    assert all(isinstance(ev, AuditEvent) for ev in chain)
    assert verify_chain(chain), (
        "v0.4.0rc3 (P0 #5): the audit chain integrity check must still "
        "pass after record_* emissions. This is a hard constraint — if "
        "this fails the side-channel emitter is producing broken links."
    )
