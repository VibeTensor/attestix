# Attestix Demo Suite

End-to-end demonstration scenarios for Attestix. Each scenario shows a different EU AI Act risk category and compliance workflow.

## Quick Setup

```bash
cd /path/to/attestix
pip install -e .
```

No API keys, no cloud services, no internet required. Everything runs locally.

## Demo Scenarios

| # | Scenario | Risk Category | Key Demo Point |
|---|----------|--------------|----------------|
| 1 | [FinTech Advisory AI](scenarios/01-fintech-advisor/) | High-risk (Annex III) | Full compliance lifecycle, self-assessment blocked |
| 2 | [Supply Chain AI](scenarios/02-supply-chain-ai/) | Limited-risk | Multi-agent delegation, self-assessment allowed |
| 3 | [HR Screening AI](scenarios/03-hr-screening/) | Unacceptable-risk | Prohibited system detection, redesign to compliant |

## Quick Start (5 minutes)

For time-limited demos:

```bash
python demo/quick-start/five_min_demo.py
```

Or use MCP prompts in [quick-start/five_min_mcp.md](quick-start/five_min_mcp.md) with Claude Desktop.

## Running a Scenario

Each scenario has two ways to run:

### Option A: Python Script (recommended for reproducibility)

```bash
python demo/scenarios/01-fintech-advisor/run_demo.py
```

### Option B: MCP Prompts (recommended for live demos)

Open Claude Desktop with Attestix configured, then follow the prompts in:
```
demo/scenarios/01-fintech-advisor/mcp_prompts.md
```

## Presentation Materials

- [Talking Points](presentation/talking-points.md) - verbal script with timing
- [Comparison Table](presentation/comparison-table.md) - vs competitors
- [FAQ](presentation/faq.md) - investor and client questions
- [One-Pager](presentation/one-pager.md) - leave-behind summary

## What Each Demo Covers

All 9 Attestix modules are exercised across the demo suite:

| Module | Scenario 1 | Scenario 2 | Scenario 3 |
|--------|:----------:|:----------:|:----------:|
| Identity | x | x | x |
| DID | x | x | x |
| Compliance | x | x | x |
| Provenance | x | x | x |
| Credentials | x | x | x |
| Delegation | x | x | - |
| Reputation | x | x | - |
| Audit Trail | x | x | x |
| Blockchain | x | - | - |

## Notes

- Each script creates fresh data (no shared state between scenarios)
- Storage is in-memory by default, resets on each run
- All output is formatted for screen presentation
- Scripts exit cleanly with a summary
