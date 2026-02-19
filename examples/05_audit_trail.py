"""Example 5: Audit Trail and Provenance

Demonstrates Article 12 automatic logging, training data provenance,
model lineage recording, and audit trail querying.

Usage:
    python examples/05_audit_trail.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.identity_service import IdentityService
from services.provenance_service import ProvenanceService


def main():
    identity_svc = IdentityService()
    provenance_svc = ProvenanceService()

    # Create agent
    print("=== Creating Agent ===\n")
    agent = identity_svc.create_identity(
        display_name="LoanScreener-AI",
        capabilities=["credit_scoring", "risk_assessment"],
        description="AI-powered loan application screening for consumer credit",
        issuer_name="FinanceAI Ltd.",
    )
    agent_id = agent["agent_id"]
    print(f"Agent ID: {agent_id}")

    # Record training data sources (Article 10)
    print("\n=== Recording Training Data (Article 10) ===\n")
    datasets = [
        {
            "dataset_name": "Historical Loan Performance Dataset",
            "source_url": "https://data.internal.financeai.com/loans-2020-2025",
            "license": "Proprietary",
            "data_categories": "financial,credit_history,demographics",
            "contains_personal_data": True,
            "data_governance_measures": "De-identified per GDPR Art. 5. Bias audit conducted quarterly. Underrepresented groups oversampled for fairness. Data retention policy: 7 years.",
        },
        {
            "dataset_name": "ECB Economic Indicators",
            "source_url": "https://data.ecb.europa.eu/",
            "license": "ECB Open Data License",
            "data_categories": "economic_indicators,public",
            "contains_personal_data": False,
            "data_governance_measures": "Public data from European Central Bank. Validated against published statistical releases.",
        },
        {
            "dataset_name": "Synthetic Stress Test Scenarios",
            "source_url": "",
            "license": "Internal",
            "data_categories": "synthetic,stress_testing",
            "contains_personal_data": False,
            "data_governance_measures": "Generated via Monte Carlo simulation. Parameters reviewed by risk management team.",
        },
    ]

    for ds in datasets:
        result = provenance_svc.record_training_data(agent_id=agent_id, **ds)
        personal = "YES" if ds["contains_personal_data"] else "no"
        print(f"  [{result['entry_id'][:12]}...] {ds['dataset_name']} (personal data: {personal})")

    # Record model lineage (Article 11)
    print("\n=== Recording Model Lineage (Article 11) ===\n")
    lineage = provenance_svc.record_model_lineage(
        agent_id=agent_id,
        base_model="XGBoost 2.1",
        base_model_provider="Open Source (Apache 2.0)",
        fine_tuning_method="Gradient boosting with hyperparameter search (Optuna). Fairness constraints via reject-option classification.",
        evaluation_metrics_json=json.dumps({
            "auc_roc": 0.892,
            "precision": 0.87,
            "recall": 0.91,
            "f1_score": 0.89,
            "demographic_parity_diff": 0.03,
            "equalized_odds_diff": 0.04,
        }),
    )
    print(f"  Base model: {lineage['base_model']} ({lineage['base_model_provider']})")
    print(f"  Entry: {lineage['entry_id'][:16]}...")

    # Simulate agent operations with audit logging (Article 12)
    print("\n=== Logging Agent Actions (Article 12) ===\n")
    actions = [
        {
            "action_type": "data_access",
            "input_summary": "Retrieved loan application #LA-2026-4821",
            "output_summary": "Application data loaded: income, employment, credit history",
            "decision_rationale": "Automated retrieval triggered by new application submission",
        },
        {
            "action_type": "inference",
            "input_summary": "Loan application #LA-2026-4821: income=65K, employment=5yr, credit_score=720",
            "output_summary": "Risk score: 0.23 (low risk). Recommended: APPROVE with standard terms.",
            "decision_rationale": "Score below 0.3 threshold. All input features within normal ranges. No anomaly flags.",
        },
        {
            "action_type": "external_call",
            "input_summary": "Credit bureau API query for applicant verification",
            "output_summary": "Credit report confirmed. No discrepancies with application data.",
            "decision_rationale": "Mandatory verification step per internal policy P-203.",
        },
        {
            "action_type": "inference",
            "input_summary": "Loan application #LA-2026-4822: income=28K, employment=0.5yr, credit_score=580",
            "output_summary": "Risk score: 0.78 (high risk). Recommended: ESCALATE for human review.",
            "decision_rationale": "Score above 0.6 threshold. Short employment history flagged. Insufficient income-to-debt ratio.",
            "human_override": True,
        },
        {
            "action_type": "inference",
            "input_summary": "Loan application #LA-2026-4823: income=95K, employment=12yr, credit_score=810",
            "output_summary": "Risk score: 0.08 (very low risk). Recommended: APPROVE with premium terms.",
            "decision_rationale": "Excellent credit profile. All features indicate low default probability.",
        },
    ]

    for action in actions:
        human = action.pop("human_override", False)
        result = provenance_svc.log_action(
            agent_id=agent_id, human_override=human, **action
        )
        override_label = " [HUMAN OVERRIDE]" if human else ""
        print(f"  [{result['log_id'][:12]}...] {action['action_type']}: "
              f"{action['output_summary'][:50]}...{override_label}")

    # Query full provenance
    print("\n=== Full Provenance Record ===\n")
    provenance = provenance_svc.get_provenance(agent_id)
    print(f"  Training datasets:    {len(provenance.get('training_data', []))}")
    print(f"  Model lineage:        {len(provenance.get('model_lineage', []))}")
    print(f"  Audit log entries:    {len(provenance.get('audit_log', []))}")

    # Query audit trail with filters
    print("\n=== Audit Trail: Inferences Only ===\n")
    inferences = provenance_svc.get_audit_trail(
        agent_id=agent_id,
        action_type="inference",
    )
    print(f"  Total inference actions: {inferences['total']}")
    for entry in inferences["entries"]:
        human = " [HUMAN]" if entry.get("human_override") else ""
        print(f"    {entry['timestamp'][:19]} | {entry['output_summary'][:60]}...{human}")

    # Query audit trail: human overrides
    print("\n=== Audit Trail: Human Overrides ===\n")
    all_entries = provenance_svc.get_audit_trail(agent_id=agent_id)
    human_overrides = [e for e in all_entries["entries"] if e.get("human_override")]
    print(f"  Total actions with human override: {len(human_overrides)}")
    for entry in human_overrides:
        print(f"    {entry['action_type']}: {entry['decision_rationale'][:60]}...")

    print("\nDone! All provenance and audit data is cryptographically signed.")


if __name__ == "__main__":
    main()
