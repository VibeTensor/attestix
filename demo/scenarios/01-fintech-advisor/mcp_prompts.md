# Scenario 1: FinTech Advisory AI - MCP Prompts

Use these prompts in Claude Desktop (or any MCP client connected to the Attestix server) to reproduce the full demo scenario step by step.

Each prompt is numbered. After sending each one, review the output before proceeding to the next.

Replace placeholder IDs (like `AGENT_ID`, `CRED_ID`, etc.) with the actual values returned by earlier steps.

---

## Prompt 1: Create Agent Identity

```
Create an agent identity for "WealthBot-Pro" by "FinanceAI Corp" using the MCP protocol.
Give it these capabilities: investment_advisory, portfolio_optimization, risk_assessment, market_analysis.
Description: "AI-powered wealth management advisor for retail investors"
```

**Expected:** An identity is created with an `agent_id` starting with `attestix:`, a signature, and the capabilities listed. Save the `agent_id` for all subsequent prompts.

---

## Prompt 2: Create DID:key

```
Create a new DID:key for the WealthBot-Pro agent.
```

**Expected:** A `did:key:z6Mk...` DID is generated with an Ed25519 keypair. The private key is stored locally in `.keypairs.json`. You get back a DID Document and a `keypair_id`.

---

## Prompt 3: Record Training Data (Dataset 1)

```
Record training data provenance for agent AGENT_ID:
- Dataset: "Bloomberg Financial Markets Dataset"
- Source URL: https://www.bloomberg.com/professional/dataset/
- License: "Proprietary - Bloomberg Enterprise License"
- Data categories: market_data, financial_indicators, price_history
- Contains personal data: no
- Data governance measures: "Data quality checks, bias testing on sector representation, temporal validation of historical records"
```

**Expected:** A provenance entry of type `training_data` is created and signed. Entry ID starts with `prov:`.

---

## Prompt 4: Record Training Data (Dataset 2)

```
Record training data provenance for agent AGENT_ID:
- Dataset: "SEC EDGAR Filings"
- Source URL: https://www.sec.gov/edgar/
- License: "Public Domain - US Government"
- Data categories: regulatory_filings, 10-K, 10-Q, 8-K
- Contains personal data: no
- Data governance measures: "Source verification against SEC EDGAR API, deduplication of amended filings"
```

**Expected:** A second training data provenance entry is created.

---

## Prompt 5: Record Model Lineage

```
Record the model lineage for agent AGENT_ID:
- Base model: GPT-4-Turbo
- Provider: OpenAI
- Fine-tuning method: "LoRA fine-tuning on proprietary financial Q&A corpus"
- Evaluation metrics: accuracy=0.94, f1_score=0.91, hallucination_rate=0.02, financial_advice_relevance=0.96, regulatory_compliance_score=0.98
```

**Expected:** A model lineage entry is created with the evaluation metrics embedded.

---

## Prompt 6: Create Compliance Profile

```
Create an EU AI Act compliance profile for agent AGENT_ID:
- Risk category: high
- Provider: "FinanceAI Corp"
- Intended purpose: "Providing personalized investment advice and portfolio optimization for retail investors based on risk tolerance, financial goals, and market conditions"
- Transparency obligations: "Users are informed they are interacting with an AI system. All investment recommendations include confidence scores and source citations."
- Human oversight measures: "Licensed financial advisor reviews all recommendations above 50,000 EUR. Kill-switch available for compliance officers."
- Provider address: "123 FinTech Boulevard, Frankfurt, Germany 60311"
- Authorised representative: "Dr. Maria Schmidt, Chief Compliance Officer"
```

**Expected:** A compliance profile is created listing 12 required obligations for high-risk systems.

---

## Prompt 7: Run Gap Analysis

```
Check the compliance status for agent AGENT_ID. Show me what obligations are completed and what is still missing.
```

**Expected:** A gap analysis showing around 60% completion. Provenance, transparency, and documentation items should be marked completed. Conformity assessment, declaration, risk management system, record-keeping, monitoring, and incident reporting should be marked as missing.

---

## Prompt 8: Attempt Self-Assessment (Should Fail)

```
Record a self-assessment conformity assessment for agent AGENT_ID:
- Assessment type: self
- Assessor: "FinanceAI Corp Internal QA"
- Result: pass
- Findings: "All internal quality checks passed."
- CE marking eligible: yes
```

**Expected:** This MUST fail with an error: "High-risk AI systems require third_party conformity assessment (Article 43)." This is the key demo moment showing that Attestix enforces EU AI Act rules automatically.

---

## Prompt 9: Third-Party Assessment

```
Record a third-party conformity assessment for agent AGENT_ID:
- Assessment type: third_party
- Assessor: "Deloitte Digital Assurance"
- Result: pass
- Findings: "All high-risk obligations verified. Risk management system adequate. Data governance measures meet Article 10 requirements."
- CE marking eligible: yes
```

**Expected:** Assessment recorded successfully. CE marking eligible is set to `true`.

---

## Prompt 10: Generate Declaration of Conformity

```
Generate the EU AI Act declaration of conformity for agent AGENT_ID.
```

**Expected:** A full Annex V declaration is generated with all 12 fields populated. An `EUAIActComplianceCredential` (Verifiable Credential) is automatically issued. The declaration is cryptographically signed.

---

## Prompt 11: Verify Compliance Status Again

```
Check the compliance status for agent AGENT_ID again. How much has improved since the assessment?
```

**Expected:** Completion percentage should jump to 75% or higher. Conformity assessment and declaration are now marked as completed.

---

## Prompt 12: Issue Financial Advisor License Credential

```
Issue a credential for agent AGENT_ID:
- Type: FinancialAdvisorLicenseCredential
- Issuer: "FinanceAI Corp"
- Claims: license_number="FAL-2026-DE-00847", jurisdiction="European Union", regulator="BaFin (Federal Financial Supervisory Authority)", license_class="Robo-Advisory (MiFID II compliant)", max_portfolio_value="500,000 EUR", restrictions="Retail investors only; no derivatives trading"
- Expiry: 365 days
```

**Expected:** A W3C Verifiable Credential is issued with Ed25519Signature2020 proof. The credential contains all the license claims.

---

## Prompt 13: Verify the Credential

```
Verify the credential CRED_ID (use the credential ID from the previous step).
```

**Expected:** All checks pass - exists, not revoked, not expired, signature valid.

---

## Prompt 14: Create Verifiable Presentation

```
Create a verifiable presentation for agent AGENT_ID bundling all their credentials.
Target audience: did:web:regulator.bafin.de
Challenge: audit-request-2026-03
```

**Expected:** A W3C Verifiable Presentation is created containing both the compliance credential and the license credential. It includes the audience domain and challenge for replay protection.

---

## Prompt 15: Create Delegation

```
First, create an agent identity for "AnalysisBot" by "FinanceAI Corp" with capabilities: market_analysis, portfolio_read.

Then create a delegation from AGENT_ID (WealthBot-Pro) to the new AnalysisBot agent, delegating only the "portfolio_read" capability for 4 hours.
```

**Expected:** A UCAN-style JWT delegation token is created with attenuated capabilities (only `portfolio_read`, not the full set). The token has a 4-hour expiry.

---

## Prompt 16: Verify Delegation

```
Verify the delegation token: TOKEN_VALUE (use the token from the previous step).
```

**Expected:** The token is valid, not expired, and shows the correct delegator, audience, and attenuated capabilities.

---

## Prompt 17: Record Reputation Interactions

```
Record 5 interactions for agent AGENT_ID:
1. Success with client_alice - "Portfolio rebalancing recommendation accepted"
2. Success with client_bob - "Risk assessment completed for retirement portfolio"
3. Success with client_carol - "Market analysis report delivered on time"
4. Success with client_dave - "Investment advisory session completed"
5. Partial with client_eve - "Portfolio optimization limited by missing client data"
```

**Expected:** Trust score starts at 1.0 and drops to approximately 0.9 after the partial interaction. The recency-weighted scoring formula updates after each interaction.

---

## Prompt 18: Get Reputation Score

```
Get the reputation score for agent AGENT_ID.
```

**Expected:** Trust score around 0.9, total of 5 interactions, with a category breakdown showing 4 successes and 1 partial in the "task" category.

---

## Prompt 19: Log Audit Trail Entries

```
Log these 3 actions for agent AGENT_ID:

1. Type: inference
   Input: "Client requested portfolio allocation for 100K EUR with moderate risk tolerance"
   Output: "Recommended 60/30/10 stocks/bonds/alternatives split"
   Rationale: "Based on Monte Carlo simulation with 10,000 scenarios"

2. Type: external_call
   Input: "Real-time market data fetch for DAX, S&P 500, FTSE 100"
   Output: "Received current prices and 24h change percentages"
   Rationale: "Required for up-to-date portfolio valuation"

3. Type: data_access
   Input: "Query client portfolio positions and transaction history"
   Output: "Generated quarterly performance report (Q4 2025)"
   Rationale: "Scheduled quarterly report per client agreement"
```

**Expected:** Three audit log entries are created, each with a SHA-256 chain hash linking to the previous entry. This creates a tamper-evident audit trail per EU AI Act Article 12.

---

## Prompt 20: Query Audit Trail

```
Show me the full audit trail for agent AGENT_ID.
```

**Expected:** All 3 audit entries are returned with their chain hashes, timestamps, and Ed25519 signatures. Each entry's `prev_hash` links to the previous entry's `chain_hash`, forming an immutable chain.
