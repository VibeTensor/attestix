# Scenario 2: Supply Chain AI - MCP Prompts for Claude Desktop

These prompts reproduce the supply chain AI demo step by step using Claude Desktop with the Attestix MCP server connected.

## Prerequisites

- Attestix MCP server running and connected in Claude Desktop
- No prior agent data needed (each step builds on the previous)

## Step 1: Create the Multi-Agent Supply Chain

```
Create 3 agent identities for a supply chain system, all under "GlobalSupply Ltd":

1. "LogiOptimize" - the main orchestrator with capabilities: demand_forecasting, route_optimization, inventory_management. Description: "Main supply chain orchestrator for global logistics optimization"

2. "RegionEU-Agent" - European regional operations with capabilities: inventory_read, warehouse_status, eu_customs_check. Description: "European regional operations agent for warehouse and customs management"

3. "RegionASIA-Agent" - Asian regional operations with capabilities: inventory_read, shipping_status, asia_customs_check. Description: "Asian regional operations agent for shipping and customs management"

Use source_protocol "manual" for all three.
```

## Step 2: Create DID:key for the Orchestrator

```
Create a DID:key for the LogiOptimize agent. This gives it a cryptographic decentralized identifier.
```

## Step 3: Record Training Data Provenance

```
Record two training data sources for LogiOptimize (use its agent_id from Step 1):

1. Dataset: "Global Shipping Routes Dataset 2020-2025"
   - Source URL: https://data.globalsupply.example/shipping-routes
   - License: CC-BY-4.0
   - Categories: shipping_routes, port_data, transit_times
   - Contains personal data: No
   - Governance: "Aggregated from public maritime databases. No personal data included."

2. Dataset: "Warehouse Inventory Records"
   - Source URL: https://internal.globalsupply.example/warehouse-data
   - License: proprietary
   - Categories: inventory_levels, stock_movements, demand_patterns
   - Contains personal data: No
   - Governance: "Internal proprietary data. Access-controlled. No personal data."
```

## Step 4: Record Model Lineage

```
Record model lineage for LogiOptimize:
- Base model: gpt-4-turbo
- Provider: OpenAI
- Fine-tuning method: "Supervised fine-tuning on logistics optimization tasks with domain expert feedback"
- Evaluation metrics:
  - demand_forecast_mape: 0.08
  - route_optimization_savings: 0.15
  - inventory_accuracy: 0.96
  - latency_p99_ms: 450
```

## Step 5: Create Compliance Profile (Limited Risk)

```
Create an EU AI Act compliance profile for LogiOptimize:
- Risk category: limited
- Provider: GlobalSupply Ltd
- Intended purpose: "AI-powered supply chain optimization including demand forecasting, route planning, and inventory management for global logistics operations."
- Transparency obligations: "System discloses AI-generated recommendations to human operators. All forecasts include confidence intervals. Route suggestions are clearly labeled as AI-generated."
```

## Step 6: Run Gap Analysis

```
Check the compliance status for LogiOptimize. Show me what obligations are completed and what is still missing.
```

## Step 7: Self-Assessment (Key Moment)

```
Record a conformity self-assessment for LogiOptimize:
- Assessment type: self
- Assessor: "GlobalSupply Ltd Internal QA"
- Result: pass
- Findings: "System meets transparency requirements. All AI-generated outputs are clearly labeled. Confidence intervals provided on forecasts. Human operators have full override capability."
- CE marking eligible: Yes

Note: This is the key differentiator from the FinTech high-risk scenario. Limited-risk systems are allowed to self-assess per Article 43, while high-risk systems require third-party notified body assessment.
```

## Step 8: Generate Declaration of Conformity

```
Generate the EU AI Act Annex V declaration of conformity for LogiOptimize. This should succeed since the self-assessment passed.
```

## Step 9: Create Delegation Chain

```
Create a delegation chain for inventory access:

1. LogiOptimize delegates "inventory_read" capability to RegionEU-Agent with an 8-hour expiry.

2. Then RegionEU-Agent chain-delegates "inventory_read" to RegionASIA-Agent with a 4-hour expiry, using the first delegation token as the parent.

This demonstrates UCAN-style chained capability delegation across regional boundaries.
```

## Step 10: Verify Both Delegations

```
Verify both delegation tokens from Step 9. For the chained delegation, confirm the proof chain contains the parent token.
```

## Step 11: Record Interactions

```
Record these interactions to build reputation data:

For LogiOptimize:
- success with RegionEU: "Route optimization for EU shipment batch" (task)
- success with RegionEU: "Delegated inventory access to EU agent" (delegation)
- success with RegionASIA: "Demand forecast for Asia region Q2" (task)
- partial with RegionASIA: "Asia route optimization - partial due to data lag" (task)

For RegionEU-Agent:
- success with LogiOptimize: "EU warehouse inventory sync completed" (task)
- success with LogiOptimize: "EU customs clearance check passed" (task)
- success with RegionASIA: "Chain-delegated inventory read to Asia" (delegation)

For RegionASIA-Agent:
- success with LogiOptimize: "Asia shipping status report generated" (task)
- failure with LogiOptimize: "Asia customs API timeout - service unavailable" (task)
- partial with RegionEU: "Cross-region inventory reconciliation incomplete" (task)
```

## Step 12: Compare Reputation Scores

```
Get the reputation scores for all three agents (LogiOptimize, RegionEU-Agent, RegionASIA-Agent) and compare them. Show the trust scores and category breakdowns.
```

## Step 13: Issue Compliance Credentials

```
Issue a TransparencyObligationCredential for each of the 3 agents with these claims:
- transparency_status: compliant
- risk_category: limited
- disclosure_method: "AI-labeled outputs with confidence intervals"
- agent_role: (the agent's name)

Then verify all three credentials.
```

## Step 14: Log Audit Entries

```
Log these audit trail entries for LogiOptimize:

1. inference: Input "Q2 demand data for 12 EU warehouses", Output "Demand forecast with 92% confidence", Rationale "Historical pattern matching plus seasonal adjustment"

2. delegation: Input "Delegation request from RegionEU-Agent for inventory_read", Output "Delegation token issued with 8-hour expiry", Rationale "Agent verified, capability within allowed scope"

3. external_call: Input "API call to GlobalShipping rate service", Output "Retrieved 47 shipping rate quotes", Rationale "Rate comparison needed for route optimization step"

4. data_access: Input "Read warehouse inventory levels for Frankfurt, Rotterdam, Mumbai", Output "Retrieved current stock levels for 3 facilities", Rationale "Inventory data needed for demand-supply gap analysis"
```

## Step 15: Query Audit Trail

```
Query the full audit trail for LogiOptimize. Show me all entries with their hash chains to demonstrate tamper evidence.
```

## Summary Prompt

```
Give me a summary of this supply chain AI scenario:
- Show a comparison table of all 3 agents' reputation scores
- What is LogiOptimize's final compliance status?
- What are the key differences between this limited-risk scenario and a high-risk scenario?
```
