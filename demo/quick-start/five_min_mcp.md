# Attestix 5-Minute MCP Demo

Five prompts for Claude Desktop that showcase the full Attestix toolkit.
Copy each prompt into Claude Desktop with the Attestix MCP server connected.

---

## Prompt 1: Identity + Compliance Profile

Create a new agent identity called "MedScanAI" issued by "NovaCare Health" with capabilities compliance_checking and risk_assessment, then create a high-risk compliance profile for it with intended purpose "AI-assisted radiology triage for clinical decision support", transparency obligations "System discloses AI-generated content with confidence scores on every output", and human oversight measures "All diagnoses require attending physician sign-off before delivery to patients".

**Expected response:** Attestix creates a UAIT (Unified Agent Identity Token) with a DID key, Ed25519 signature, and a linked EU AI Act compliance profile with 12 required obligations for high-risk systems. The profile ID is linked to the identity automatically.

---

## Prompt 2: Training Data + Conformity Assessment

For the agent you just created, record a training dataset called "MIMIC-IV Clinical Database" from source https://physionet.org/content/mimiciv/ with license "PhysioNet Credentialed Health Data License 1.5.0", data categories clinical_records and de_identified, personal data flag true, and data governance measures "De-identified per HIPAA Safe Harbor with IRB approval". Then record a third-party conformity assessment by assessor "TUV Rheinland AG" with result pass, findings "System meets all Annex III requirements for high-risk medical AI", and CE marking eligible.

**Expected response:** Attestix records the training data provenance entry (Article 10 compliance) and a third-party conformity assessment (Article 43). The assessment updates the compliance profile to mark conformity as completed with CE marking eligibility. Note that self-assessment would be blocked for high-risk systems.

---

## Prompt 3: Declaration of Conformity + Credential Verification

Generate a declaration of conformity for the MedScanAI agent, then list all credentials for that agent and verify the EU AI Act compliance credential that was auto-issued.

**Expected response:** Attestix generates a full EU AI Act Annex V declaration of conformity with all 12 required fields (provider info, AI system identification, intended purpose, risk classification, conformity assessment reference, harmonized standards, transparency obligations, human oversight measures, CE marking status, sole responsibility statement, and digital signature). A W3C Verifiable Credential of type EUAIActComplianceCredential is automatically issued. Verification confirms: exists, not revoked, not expired, signature valid.

---

## Prompt 4: Delegation + Reputation

Create a second agent called "TriageHelper" issued by "NovaCare Health" with capability data_collection. Then delegate the compliance_checking capability from MedScanAI to TriageHelper with a 24-hour expiry. After that, record three interactions for MedScanAI: one success in category task with details "Completed chest X-ray analysis", one success in category delegation with details "Delegated triage task completed on time", and one partial in category task with details "Low confidence result on edge case". Finally show MedScanAI's reputation score.

**Expected response:** Attestix creates TriageHelper's identity, issues a UCAN delegation JWT signed with EdDSA, and records three interactions. The reputation score uses recency-weighted exponential decay (30-day half-life) and should be approximately 0.83 with a category breakdown showing 2 task interactions and 1 delegation interaction.

---

## Prompt 5: Audit Trail + Compliance Status

Log an inference action for MedScanAI with input summary "Chest X-ray batch of 10 images", output summary "4 flagged for specialist review", and decision rationale "Confidence below 0.85 threshold for pneumothorax detection". Then show the full audit trail and the current compliance status for MedScanAI.

**Expected response:** Attestix logs the action with a tamper-evident hash chain (SHA-256 linking each entry to the previous one). The audit trail shows all logged entries with chain hashes. The compliance status provides a gap analysis listing completed obligations and any remaining items needed for full EU AI Act compliance, along with a completion percentage.
