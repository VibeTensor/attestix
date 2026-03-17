# Scenario 3: HR Screening AI - Enforcement Then Compliance

## Why This Is the Most Powerful Demo

Most compliance tools only document what already exists. This scenario shows
Attestix doing something stronger: **enforcement**. When TalentScan-v1 tries
to register as an unacceptable-risk system, Attestix blocks it. The system
cannot get a compliance profile, cannot get a declaration of conformity, and
cannot get a credential. It is dead on arrival.

Then the demo shows the path forward. The same company redesigns the system,
and Attestix guides TalentMatch-v2 through full compliance. The contrast
between Part A (blocked) and Part B (compliant) is the most compelling
argument for why automated compliance tooling matters.

## What Social Scoring Means Under Article 5

EU AI Act Article 5(1)(c) prohibits AI systems that evaluate or classify
natural persons based on their social behavior or personal characteristics,
leading to detrimental treatment disproportionate to the context. In plain
terms:

- Scoring people based on social media activity: **prohibited**
- Profiling candidates by personal connections: **prohibited**
- Ranking job applicants by lifestyle patterns: **prohibited**
- Matching resume skills to job requirements: **allowed** (but high-risk)

The line is clear. Social scoring targets the person. Skill matching targets
the job fit. TalentScan-v1 crosses that line. TalentMatch-v2 does not.

## The Redesign Story

```
TalentScan-v1                          TalentMatch-v2
  social_scoring           -->           skill_matching
  behavioral_profiling     -->           resume_parsing
  candidate_ranking        -->           job_requirement_analysis

  Risk: Unacceptable                     Risk: High
  Status: PROHIBITED                     Status: COMPLIANT
  Declaration: BLOCKED                   Declaration: ISSUED
  Credential: NONE                       Credential: VERIFIED
```

The scenario walks through 15 steps across both systems:

**Part A (5 steps):** Create agent, attempt compliance profile (blocked),
attempt declaration (blocked), log enforcement, revoke identity.

**Part B (10 steps):** Create agent, record training data (2 datasets),
record model lineage, create compliance profile, run gap analysis,
third-party assessment by Bureau Veritas, generate declaration, verify
credential, log audit entries, final status check.

## How to Run

### Python Script (standalone)

From the Attestix root directory:

```bash
python demo/scenarios/03-hr-screening/run_demo.py
```

### MCP via Claude Desktop

See `mcp_prompts.md` for step-by-step prompts you can paste into Claude
Desktop with the Attestix MCP server connected.

## Expected Duration

- Python script: under 5 seconds
- MCP walkthrough (all 11 prompts): approximately 3 minutes
- MCP single-prompt version: approximately 1 minute

## What to Look For

1. **The block moment** - Step 2 shows Attestix refusing to create a compliance
   profile for a prohibited system. This is enforcement, not documentation.

2. **The gap analysis** - Step 10 shows exactly what has been completed and what
   is still missing after the redesign, before the conformity assessment.

3. **The declaration** - Step 12 produces a full Annex V declaration of
   conformity with all 12 required fields populated.

4. **The credential** - Step 13 shows a W3C Verifiable Credential automatically
   issued and cryptographically verified (Ed25519Signature2020).

5. **The comparison** - The final table makes the enforcement story visceral:
   same company, same hiring domain, completely different outcomes based on
   system design.

## Relevance

Employment and recruitment AI is one of the most scrutinized categories under
the EU AI Act (Annex III, Category 4). Companies building HR tech need to
understand the boundary between prohibited and high-risk systems. This demo
shows that boundary in action.
