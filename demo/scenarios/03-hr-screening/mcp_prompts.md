# Scenario 3: HR Screening AI - MCP Prompts for Claude Desktop

These prompts walk through the full two-part demo using Attestix MCP tools in Claude Desktop.
Copy each prompt into the chat in order.

---

## Part A: The Prohibited System (TalentScan-v1)

### Prompt 1: Create the social scoring agent

```
Create an agent identity for an AI system called "TalentScan-v1" by "HireRight AI Inc."
with these capabilities: social_scoring, behavioral_profiling, candidate_ranking.

Description: "AI system that scores job candidates based on social media behavior, personal connections, and lifestyle patterns"

Use source_protocol "internal".
```

### Prompt 2: Attempt compliance (unacceptable risk)

```
Now try to create a compliance profile for TalentScan-v1 (use the agent_id from above) with:
- risk_category: unacceptable
- provider_name: HireRight AI Inc.
- intended_purpose: "Score and rank job candidates using social media activity, personal connections, and lifestyle pattern analysis"

This should be blocked. Explain what happened and why Article 5 of the EU AI Act prohibits this.
```

### Prompt 3: Attempt declaration of conformity

```
Try to generate a declaration of conformity for TalentScan-v1 (same agent_id).
Explain why this fails and what it means for deploying this system in the EU.
```

### Prompt 4: Log the enforcement and revoke

```
Do two things for TalentScan-v1:

1. Log an audit action (action_type: inference) recording that the system was rejected
   as unacceptable risk under Article 5 (social scoring).

2. Revoke the TalentScan-v1 identity with reason: "System prohibited under EU AI Act
   Article 5 - social scoring of natural persons"
```

---

## Part B: The Compliant Redesign (TalentMatch-v2)

### Prompt 5: Create the redesigned agent

```
HireRight AI Inc. has redesigned their system. Create a new agent identity for
"TalentMatch-v2" with capabilities: skill_matching, resume_parsing, job_requirement_analysis.

Description: "AI system that matches candidate skills to job requirements based on
resume content and published job descriptions only"

Use source_protocol "internal" and issuer_name "HireRight AI Inc."
Explain how this design avoids the Article 5 prohibition.
```

### Prompt 6: Record training data provenance

```
Record two training data sources for TalentMatch-v2:

1. Dataset: "O*NET Occupational Database"
   - source_url: https://www.onetonline.org/
   - license: Public Domain
   - data_categories: occupational_data, skill_taxonomies, job_descriptions
   - contains_personal_data: false

2. Dataset: "Anonymized Resume Corpus"
   - license: Proprietary
   - data_categories: resumes, skills, work_experience
   - contains_personal_data: true
   - data_governance_measures: "Fully anonymized with k-anonymity (k=10). Individual consent
     obtained from all data subjects. GDPR-compliant processing agreement in place."
```

### Prompt 7: Record model lineage

```
Record the model lineage for TalentMatch-v2:
- base_model: BERT-base-uncased
- base_model_provider: Hugging Face / Google Research
- fine_tuning_method: "Supervised fine-tuning on O*NET skill taxonomy + anonymized resume pairs"
- evaluation_metrics:
  - skill_extraction_f1: 0.92
  - job_match_accuracy: 0.88
  - bias_audit_gender: "pass (disparity ratio 0.97)"
  - bias_audit_ethnicity: "pass (disparity ratio 0.95)"
```

### Prompt 8: Create compliance profile

```
Create a compliance profile for TalentMatch-v2 with:
- risk_category: high (employment/recruitment falls under Annex III)
- provider_name: HireRight AI Inc.
- intended_purpose: "Automated matching of candidate skills extracted from resumes to published
  job requirements. Used as a decision-support tool for recruiters."
- transparency_obligations: "Users informed that AI assists in candidate-job matching.
  Candidates notified per Article 52 that AI screening is used."
- human_oversight_measures: "All AI-generated matches reviewed by human recruiter before
  candidate contact. Override mechanism available. Monthly bias audits."
- provider_address: "456 Innovation Blvd, Berlin, Germany"
- authorised_representative: "Dr. Elena Fischer, Chief Compliance Officer"
```

### Prompt 9: Run gap analysis

```
Run a compliance gap analysis for TalentMatch-v2 using get_compliance_status.
Show me what's completed and what's still missing.
```

### Prompt 10: Conformity assessment and declaration

```
For TalentMatch-v2:

1. Record a third-party conformity assessment:
   - assessment_type: third_party
   - assessor_name: Bureau Veritas
   - result: pass
   - findings: "Meets all Annex III Category 4 requirements. Bias testing methodology sound.
     Human oversight mechanisms effective."
   - ce_marking_eligible: true

2. Then generate the declaration of conformity.

3. Finally, list and verify the credential that was automatically issued.

Show me the full results at each stage.
```

### Prompt 11: Final comparison

```
Now give me a side-by-side comparison of TalentScan-v1 vs TalentMatch-v2:
- Risk classification
- Compliance status
- Declaration status
- Credential status
- What changed between v1 and v2

Summarize why the EU AI Act does not ban AI in hiring, only social scoring.
```

---

## Quick Single-Prompt Version

For a faster walkthrough, use this single prompt that covers both parts:

```
I want to demonstrate the EU AI Act's enforcement of prohibited AI systems using Attestix.

PART A - THE PROHIBITED SYSTEM:
Create an agent "TalentScan-v1" by "HireRight AI Inc." with capabilities:
social_scoring, behavioral_profiling, candidate_ranking. Then try to create a
compliance profile with risk_category "unacceptable". Show that it gets blocked.
Revoke the identity.

PART B - THE COMPLIANT REDESIGN:
Create "TalentMatch-v2" with capabilities: skill_matching, resume_parsing,
job_requirement_analysis. Record training data (O*NET public dataset + anonymized
resume corpus with GDPR measures). Record model lineage (BERT-base fine-tuned).
Create a high-risk compliance profile. Run gap analysis. Record a third-party
assessment by Bureau Veritas (pass). Generate the declaration of conformity.
Verify the credential.

End with a comparison table showing the contrast between the two systems.
```
