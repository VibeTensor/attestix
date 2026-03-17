# Scenario 2: Supply Chain AI (Limited-Risk)

## Overview

This scenario demonstrates Attestix capabilities applied to a **multi-agent supply chain orchestration system** classified as **limited-risk** under the EU AI Act.

Three AI agents form a hierarchical supply chain:

| Agent | Role | Capabilities |
|-------|------|-------------|
| **LogiOptimize** | Main orchestrator | demand_forecasting, route_optimization, inventory_management |
| **RegionEU-Agent** | European operations | inventory_read, warehouse_status, eu_customs_check |
| **RegionASIA-Agent** | Asian operations | inventory_read, shipping_status, asia_customs_check |

All three agents operate under **GlobalSupply Ltd** and are subject to EU AI Act transparency obligations.

## Why Supply Chain AI Is Limited-Risk

Under the EU AI Act (Regulation (EU) 2024/1689), supply chain optimization AI falls under the **limited-risk** category because:

- It does not make decisions that directly affect fundamental rights (unlike high-risk systems such as credit scoring or medical diagnosis)
- It assists human operators with logistics decisions rather than making autonomous consequential decisions
- The primary obligation is **transparency**: users must know they are interacting with AI and understand the basis of recommendations

Limited-risk obligations under the EU AI Act:
- Registration in the EU database
- Transparency disclosure (users know it is AI)
- Informing users of AI interaction

## Key Differentiator: Self-Assessment Allowed

**This is the most important distinction from Scenario 1 (FinTech Advisor, high-risk).**

| Aspect | Scenario 1 (High-Risk) | Scenario 2 (Limited-Risk) |
|--------|----------------------|-------------------------|
| Risk Category | High | Limited |
| Self-Assessment | BLOCKED (Article 43) | ALLOWED |
| Required Assessment | Third-party notified body | Internal QA team |
| Obligations Count | 11+ requirements | 3 requirements |
| Human Oversight | Mandatory | Recommended |

In Step 7 of this demo, the self-assessment **succeeds**, which directly contrasts with Scenario 1 where self-assessment is blocked and a third-party notified body (such as TUV Rheinland) must perform the conformity assessment.

## What This Scenario Demonstrates

### Attestix Modules Exercised

1. **Identity** - Creating and managing 3 agent identities (multi-agent system)
2. **DID** - Generating a did:key for the orchestrator agent
3. **Provenance** - Recording training data sources and model lineage
4. **Compliance** - EU AI Act limited-risk profile, gap analysis, self-assessment, declaration of conformity
5. **Delegation** - UCAN-style capability delegation chain (orchestrator to EU to Asia)
6. **Reputation** - Interaction recording and trust score comparison across all 3 agents
7. **Credentials** - W3C Verifiable Credentials for transparency compliance
8. **Audit Trail** - Hash-chained tamper-evident action logging

### Key Workflow Steps

| Step | Description |
|------|------------|
| 1 | Create 3 agent identities forming a supply chain hierarchy |
| 2 | Generate DID:key for the orchestrator |
| 3 | Record 2 training datasets with provenance metadata |
| 4 | Record model lineage with evaluation metrics |
| 5 | Create limited-risk compliance profile |
| 6 | Run gap analysis showing transparency obligations |
| 7 | **Self-assessment succeeds** (key demo moment) |
| 8 | Generate Annex V declaration of conformity |
| 9 | Create delegation chain across 3 agents |
| 10 | Verify both delegation tokens |
| 11 | Record 10 interactions with mixed outcomes |
| 12 | Compare reputation scores across all agents |
| 13 | Issue and verify compliance credentials |
| 14 | Log 4 audit trail entries |
| 15 | Query audit trail with hash chain verification |

## How to Run

### Option A: Python Script (automated)

From the Attestix root directory:

```bash
python demo/scenarios/02-supply-chain-ai/run_demo.py
```

The script runs all 15 steps automatically and prints formatted output with a final summary table comparing all 3 agents.

### Option B: Claude Desktop (interactive)

1. Connect the Attestix MCP server to Claude Desktop
2. Follow the prompts in `mcp_prompts.md` step by step
3. Each prompt corresponds to one step of the scenario

### Prerequisites

- Python 3.10+
- Attestix dependencies installed (`pip install -e .` from root)
- For Option B: Attestix MCP server configured in Claude Desktop

## Expected Output

The script produces detailed output for each step. Key highlights:

- **Step 7**: Self-assessment succeeds with "pass" result
- **Step 12**: Reputation comparison shows RegionEU (1.0) outperforming LogiOptimize (0.875) and RegionASIA (0.5)
- **Step 15**: Audit trail entries are hash-chained, where each entry's `prev_hash` matches the previous entry's `chain_hash`

## Expected Duration

Approximately **3 minutes** for the full Python script execution.

## Files

| File | Purpose |
|------|---------|
| `run_demo.py` | Fully runnable Python script exercising all modules |
| `mcp_prompts.md` | Step-by-step prompts for reproducing via Claude Desktop |
| `README.md` | This walkthrough document |
