# EU AI Act Compliance with Attestix

Step-by-step guide to achieving EU AI Act compliance for your AI agent using Attestix.

## Important Disclaimer

Attestix generates machine-readable, cryptographically signed compliance documentation for AI agents. It is a documentation and evidence tooling system.

**Attestix does not replace legal counsel, notified body assessments, or official regulatory submissions.** The declarations and artifacts produced by Attestix are structured evidence to support your compliance process, not legally binding regulatory filings on their own. Always consult qualified legal professionals for compliance decisions.

## Before You Start

You will need the following information gathered from different teams:

### From Your Legal/Compliance Team

- [ ] **Risk category determination** -- Is your AI system minimal, limited, or high-risk? See [Risk Classification Guide](risk-classification.md)
- [ ] **Intended purpose statement** -- What the AI system is designed to do
- [ ] **Transparency measures** -- How you inform users they're interacting with AI
- [ ] **Human oversight measures** -- How humans monitor and can intervene (required for high-risk)

### From Your ML/Engineering Team

- [ ] **Training datasets** -- Name, source, license for each dataset used
- [ ] **Personal data flag** -- Whether training data contains personal data
- [ ] **Data governance measures** -- Quality checks, bias mitigation, cleaning processes
- [ ] **Base model** -- What foundation model you built on (e.g., GPT-4, Claude, LLaMA)
- [ ] **Fine-tuning method** -- How the model was adapted (LoRA, RLHF, etc.)
- [ ] **Evaluation metrics** -- Accuracy, F1, AUC-ROC, or domain-specific metrics

### From Your Business Team

- [ ] **Provider company legal name** -- The entity responsible for the AI system
- [ ] **Notified body** -- For high-risk: which organization will assess you? (TUV Rheinland, BSI, Bureau Veritas, etc.)

## Step-by-Step Workflow

### Step 1: Create Agent Identity

Every AI system needs an identity first.

```
create_agent_identity(
  display_name="MedAssist-AI",
  capabilities="medical_diagnosis,patient_triage",
  description="AI-assisted medical diagnosis for clinical decision support",
  issuer_name="YourCompany Inc."
)
```

**Output:** An `agent_id` like `attestix:f9bdb7a94ccb40f1`. Save this -- you'll use it in every subsequent step.

### Step 2: Record Training Data Provenance (Article 10)

Article 10 requires documentation of training data governance. Record each dataset:

```
record_training_data(
  agent_id="attestix:f9bdb7a94ccb40f1",
  dataset_name="PubMed Central Open Access",
  source_url="https://www.ncbi.nlm.nih.gov/pmc/tools/openftlist/",
  license="CC-BY-4.0",
  contains_personal_data=false,
  data_governance_measures="Peer-reviewed articles only. Quality-checked for relevance. Bias review conducted for demographic representation."
)
```

Repeat for each training dataset. Attestix signs each record with Ed25519 to create tamper-proof evidence.

### Step 3: Record Model Lineage (Article 11)

Article 11 requires technical documentation of the model:

```
record_model_lineage(
  agent_id="attestix:f9bdb7a94ccb40f1",
  base_model="claude-opus-4-6",
  base_model_provider="Anthropic",
  fine_tuning_method="LoRA + RLHF with physician feedback",
  evaluation_metrics_json='{"diagnostic_accuracy": 0.94, "sensitivity": 0.91, "specificity": 0.96}'
)
```

### Step 4: Create Compliance Profile

This is where you declare your risk category and document your compliance posture:

```
create_compliance_profile(
  agent_id="attestix:f9bdb7a94ccb40f1",
  risk_category="high",
  provider_name="YourCompany Inc.",
  intended_purpose="AI-assisted medical diagnosis for clinical decision support in radiology",
  transparency_obligations="System discloses AI-generated content. Provides confidence scores. Explains reasoning chain.",
  human_oversight_measures="All diagnoses require physician approval. Flagged cases escalated to senior radiologist. Override mechanism always available."
)
```

Attestix will return a list of all required obligations based on your risk category. For high-risk, this includes 12 obligations.

### Step 5: Check Compliance Status (Gap Analysis)

See what's done and what's missing:

```
get_compliance_status(agent_id="attestix:f9bdb7a94ccb40f1")
```

**Output:**
```json
{
  "agent_id": "attestix:f9bdb7a94ccb40f1",
  "risk_category": "high",
  "compliant": false,
  "completion_pct": 71.4,
  "completed": [
    "compliance_profile_created",
    "intended_purpose_documented",
    "transparency_obligations_declared",
    "human_oversight_measures",
    "training_data_provenance"
  ],
  "missing": [
    "conformity_assessment_passed",
    "declaration_of_conformity_issued",
    "model_lineage_recorded"
  ]
}
```

### Step 6: Record Conformity Assessment (Article 43)

For high-risk systems, you need a third-party assessment from a notified body:

```
record_conformity_assessment(
  agent_id="attestix:f9bdb7a94ccb40f1",
  assessment_type="third_party",
  assessor_name="TUV Rheinland AG",
  result="pass",
  findings="System meets all Annex III requirements for medical AI. Minor recommendation: increase test coverage for rare conditions.",
  ce_marking_eligible=true
)
```

**Note:** High-risk systems cannot use self-assessment. Attestix will block this:

```
record_conformity_assessment(
  agent_id="attestix:f9bdb7a94ccb40f1",
  assessment_type="self",
  ...
)
--> ERROR: "High-risk AI systems require third_party conformity assessment (Article 43)."
```

### Step 7: Generate Declaration of Conformity (Annex V)

Once the assessment passes, generate the declaration:

```
generate_declaration_of_conformity(agent_id="attestix:f9bdb7a94ccb40f1")
```

This does two things:
1. Creates an Annex V declaration with all required fields
2. Auto-issues a W3C Verifiable Credential (`EUAIActComplianceCredential`) as cryptographic proof

### Step 8: Verify Full Compliance

```
get_compliance_status(agent_id="attestix:f9bdb7a94ccb40f1")
```

```json
{
  "compliant": true,
  "completion_pct": 100.0,
  "completed": ["all 7 items"],
  "missing": []
}
```

### Step 9: Present Compliance to a Verifier

Bundle your credentials into a Verifiable Presentation for a regulator or partner:

```
create_verifiable_presentation(
  agent_id="attestix:f9bdb7a94ccb40f1",
  credential_ids="urn:uuid:7161cb5e-...",
  audience_did="did:web:eu-regulator.europa.eu",
  challenge="nonce-from-verifier-12345"
)
```

The output is a signed VP that any party can cryptographically verify without contacting Attestix.

## What Attestix Produces

At the end of this workflow, you have:

| Artifact | What It Is | Signed? |
|----------|-----------|---------|
| UAIT | Agent identity with capabilities | Ed25519 |
| Training data records | Per-dataset provenance entries | Ed25519 |
| Model lineage record | Base model, fine-tuning, metrics | Ed25519 |
| Compliance profile | Risk category + obligations | Ed25519 |
| Conformity assessment | Third-party assessment result | Ed25519 |
| Annex V declaration | Declaration of conformity | Ed25519 |
| Verifiable Credential | W3C VC proving compliance | Ed25519Signature2020 |
| Verifiable Presentation | Bundle for a specific verifier | Ed25519Signature2020 |

All artifacts are stored locally in JSON files and can be exported, shared, or anchored on-chain (Phase 3).

## Key Dates

| Date | What Happens |
|------|-------------|
| August 2, 2026 | EU AI Act enforcement begins for high-risk systems (Annex III) |
| August 2, 2026 | Article 50 transparency obligations take effect |
| August 2, 2027 | Obligations for AI in regulated products (Annex I: medical devices, machinery) |

## FAQ

**Q: Can Attestix replace a notified body assessment?**
No. Attestix documents and signs the results of assessments. The actual assessment must be conducted by qualified assessors.

**Q: Is the declaration legally valid?**
Attestix's declaration is a structured, signed documentation aid. It captures the required Annex V information in machine-readable form. Whether it satisfies your specific regulatory obligations depends on your jurisdiction and should be confirmed with legal counsel.

**Q: What if my system is minimal or limited risk?**
You can still use Attestix for documentation best practice. Minimal-risk systems can self-assess and the workflow is simpler (fewer required fields). Limited-risk systems primarily need transparency disclosure.

**Q: Can I update my compliance profile later?**
Currently, profiles are created once. To update, revoke the existing identity and create a new one with updated information. Profile update support is planned for a future release.
