export type Risk = "prohibited" | "high" | "limited" | "minimal";
export type AgentStatus = "compl" | "gap" | "rev" | "pend";

export interface ConsoleAgent {
  id: string;
  did: string;
  name: string;
  displayName: string;
  issuer: string;
  protocol: "manual" | "mcp" | "a2a" | "oauth";
  capabilities: string[];
  risk: Risk;
  status: AgentStatus;
  trust: number;
  interactions: number;
  created: string;
  expiry: string;
  description: string;
  anchored: boolean;
  anchorTxn: string | null;
  credentials: number;
  delegations: number;
}

export interface ConsoleAudit {
  ts: string;
  action: string;
  actor: string;
  target: string;
  hash: string;
  prev: string;
}

export const CONSOLE_AGENTS: ConsoleAgent[] = [
  {
    id: "attestix:f9bdb7a94ccb40f1",
    did: "did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK",
    name: "quarterly-analyst-v2",
    displayName: "Quarterly Financial Analyst",
    issuer: "VibeTensor",
    protocol: "manual",
    capabilities: ["data_analysis", "reporting", "sql_query"],
    risk: "high",
    status: "compl",
    trust: 0.94,
    interactions: 1247,
    created: "2026-03-12T09:14:02Z",
    expiry: "2027-03-12",
    description:
      "Analyses quarterly financial data, generates regulatory reports, and produces narrative summaries for board review.",
    anchored: true,
    anchorTxn:
      "0x8f2e4c9b1a0f7e3d5b8c2a9e7f6d4b1a8c5e2d9f7a3b6c0e4d8f1a5b9c2e7d3f",
    credentials: 4,
    delegations: 2,
  },
  {
    id: "attestix:3c7a11e89b624d8a",
    did: "did:key:z6MkpTHR8VNsBxYAAWHutv2iRrTcn7aZoF6Kqe3dLTVLRnuZ",
    name: "clinical-triage-bot",
    displayName: "Clinical Triage Assistant",
    issuer: "Example Health Provider",
    protocol: "a2a",
    capabilities: ["medical_triage", "symptom_check", "referral"],
    risk: "high",
    status: "gap",
    trust: 0.78,
    interactions: 8421,
    created: "2026-02-08T14:22:41Z",
    expiry: "2027-02-08",
    description:
      "First-line patient triage for non-emergency consultations. Flags high-acuity cases for human review.",
    anchored: true,
    anchorTxn:
      "0x2a4c9e1b7f8d5a3c6e0b4d2f8a1c7e5b9d3f6a2c8e4b1d7f5a9c3e6b2d4f8a1c",
    credentials: 3,
    delegations: 1,
  },
  {
    id: "attestix:a21d4f08e73c9b52",
    did: "did:web:agents.vibetensor.com:supply-optimizer",
    name: "supply-chain-optimizer",
    displayName: "Supply Chain Optimizer",
    issuer: "Example Logistics Corp",
    protocol: "oauth",
    capabilities: ["logistics", "forecast", "vendor_mgmt"],
    risk: "limited",
    status: "compl",
    trust: 0.89,
    interactions: 14302,
    created: "2026-01-20T11:03:17Z",
    expiry: "2027-01-20",
    description: "Optimises supplier routing and inventory across warehouses.",
    anchored: true,
    anchorTxn:
      "0x6e1a8c3f5b7d2e9a4c0f6b8d1e3a5c7f9b2d4e6a8c1f3b5d7e9a2c4f6b8d1e3a",
    credentials: 5,
    delegations: 4,
  },
  {
    id: "attestix:5b8e2c47f1d3a960",
    did: "did:key:z6MkfJ9tRxQ3bHP7vN8sKyGdEaW2mXcL5TrVpZoBuQnJwDrF",
    name: "hr-screener-v1",
    displayName: "CV Pre-Screening Agent",
    issuer: "Example Talent Services",
    protocol: "manual",
    capabilities: ["cv_parsing", "shortlisting"],
    risk: "high",
    status: "rev",
    trust: 0.32,
    interactions: 642,
    created: "2025-11-14T08:42:09Z",
    expiry: "2026-11-14",
    description:
      "Revoked 2026-04-03: failed Article 10 data governance review. Awaiting bias audit.",
    anchored: true,
    anchorTxn:
      "0x1f5c9d3a7e2b4f8c6a0d5e1b9f3a7c2d4e6b8f1a3c5d7e9b2f4a6c8d1e3f5a7c",
    credentials: 1,
    delegations: 0,
  },
  {
    id: "attestix:7e3c91a2d8f4b605",
    did: "did:key:z6MkrQ2xTbV9pY4nWaJ8uF3mLsE6hCdRgBkP7iAoYvZtNqWh",
    name: "doc-summarizer",
    displayName: "Document Summarization Service",
    issuer: "VibeTensor",
    protocol: "mcp",
    capabilities: ["summarize", "translate", "redact"],
    risk: "minimal",
    status: "compl",
    trust: 0.91,
    interactions: 28471,
    created: "2026-03-22T16:30:00Z",
    expiry: "2027-03-22",
    description:
      "Low-risk document summarization across internal knowledge base. GDPR-aware redaction enabled.",
    anchored: false,
    anchorTxn: null,
    credentials: 2,
    delegations: 0,
  },
  {
    id: "attestix:9c4f7d2b6a1e5308",
    did: "did:key:z6MkvL8nYsE4hKpR2tWgBf7jMxZ9QaCdUiVoP3bHsNeTrXmY",
    name: "fraud-detector",
    displayName: "Transactional Fraud Detector",
    issuer: "Example Financial Services",
    protocol: "manual",
    capabilities: ["anomaly_detect", "risk_score", "alert"],
    risk: "prohibited",
    status: "compl",
    trust: 0.96,
    interactions: 104832,
    created: "2025-12-02T07:18:44Z",
    expiry: "2026-12-02",
    description:
      "Prohibited-use-adjacent: real-time fraud scoring with mandatory human-in-loop review.",
    anchored: true,
    anchorTxn:
      "0x9d2e5b8c1f4a7e3d6b0c9f2a5d8e1b4c7f0a3d6e9b2c5f8a1d4e7b0c3f6a9d2e",
    credentials: 6,
    delegations: 3,
  },
  {
    id: "attestix:2d6a91f3c8e70b45",
    did: "did:web:agents.vibetensor.com:contract-reviewer",
    name: "contract-reviewer",
    displayName: "Contract Review Specialist",
    issuer: "Example Legal Services",
    protocol: "a2a",
    capabilities: ["clause_extract", "risk_flag", "markup"],
    risk: "limited",
    status: "pend",
    trust: 0.73,
    interactions: 211,
    created: "2026-04-11T13:55:12Z",
    expiry: "2027-04-11",
    description: "Recent deployment. Awaiting first conformity assessment review.",
    anchored: false,
    anchorTxn: null,
    credentials: 1,
    delegations: 0,
  },
  {
    id: "attestix:4a8f2c37e9b15d60",
    did: "did:key:z6MkzW4rTpK8nQcY2hBxE5jFmLvA3sGdUiCoP7bHuNeXrTpY",
    name: "travel-planner",
    displayName: "Corporate Travel Planner",
    issuer: "VibeTensor",
    protocol: "oauth",
    capabilities: ["booking", "itinerary", "expense_match"],
    risk: "minimal",
    status: "compl",
    trust: 0.87,
    interactions: 5211,
    created: "2026-02-28T10:11:33Z",
    expiry: "2027-02-28",
    description: "Books corporate travel within policy.",
    anchored: true,
    anchorTxn:
      "0x3c7f1a4d8e2b5c9f6a0d3e7b1c4f8a2d5e9b0c3f6a9d2e5b8c1f4a7e0d3b6c9f",
    credentials: 3,
    delegations: 2,
  },
];

export const CONSOLE_AUDIT_SEED: ConsoleAudit[] = [
  {
    ts: "2026-04-19T09:42:17Z",
    action: "credential.issue",
    actor: "attestix:f9bdb7a94ccb40f1",
    target: "AgentIdentityCredential#7a2e",
    hash: "sha256:4f8e2c9d1a7b3f5e8c0d4b6a9f2e1c7d5b8a3e6f9c2d4b7a0e5f8c1d3b6e9a2f",
    prev: "sha256:2b7f9c4e1a5d8b3f6c0e9a2d5b7f1c4e8a3b6d9f2c5e8a1b4d7f0c3e6a9b2d5f",
  },
  {
    ts: "2026-04-19T09:41:58Z",
    action: "compliance.check",
    actor: "attestix:f9bdb7a94ccb40f1",
    target: "EUAIAct:Article-43",
    hash: "sha256:2b7f9c4e1a5d8b3f6c0e9a2d5b7f1c4e8a3b6d9f2c5e8a1b4d7f0c3e6a9b2d5f",
    prev: "sha256:8c3e6a9b2d5f1c4e8a3b6d9f2c5e8a1b4d7f0c3e6a9b2d5f1c4e8a3b6d9f2c5e",
  },
  {
    ts: "2026-04-19T09:38:03Z",
    action: "delegation.create",
    actor: "attestix:f9bdb7a94ccb40f1",
    target: "attestix:7e3c91a2d8f4b605",
    hash: "sha256:8c3e6a9b2d5f1c4e8a3b6d9f2c5e8a1b4d7f0c3e6a9b2d5f1c4e8a3b6d9f2c5e",
    prev: "sha256:1d4f7a0c3e6b9f2d5a8c1e4b7f0a3d6c9e2b5f8a1d4c7e0b3f6a9d2c5e8b1f4a",
  },
  {
    ts: "2026-04-19T09:14:22Z",
    action: "identity.verify",
    actor: "regulator.eu:nb-0482",
    target: "attestix:f9bdb7a94ccb40f1",
    hash: "sha256:1d4f7a0c3e6b9f2d5a8c1e4b7f0a3d6c9e2b5f8a1d4c7e0b3f6a9d2c5e8b1f4a",
    prev: "sha256:5e8b1f4a0c3e6b9d2f5a8c1e4b7f0a3d6c9e2b5f8a1d4c7e0b3f6a9d2c5e8b1f",
  },
  {
    ts: "2026-04-19T08:55:41Z",
    action: "provenance.record",
    actor: "attestix:f9bdb7a94ccb40f1",
    target: "training-set:fin-q4-2025",
    hash: "sha256:5e8b1f4a0c3e6b9d2f5a8c1e4b7f0a3d6c9e2b5f8a1d4c7e0b3f6a9d2c5e8b1f",
    prev: "sha256:9a2d5e8b1f4c7a0d3e6b9f2c5a8d1e4b7f0a3c6d9e2b5f8a1c4d7e0b3f6a9c2d",
  },
  {
    ts: "2026-04-19T08:42:09Z",
    action: "action.log",
    actor: "attestix:f9bdb7a94ccb40f1",
    target: "query.sql#fin-q4-summary",
    hash: "sha256:9a2d5e8b1f4c7a0d3e6b9f2c5a8d1e4b7f0a3c6d9e2b5f8a1c4d7e0b3f6a9c2d",
    prev: "sha256:3f6a9c2d5e8b1f4c7a0d3e6b9f2c5a8d1e4b7f0a3c6d9e2b5f8a1c4d7e0b3f6a",
  },
  {
    ts: "2026-04-19T08:30:17Z",
    action: "anchor.submit",
    actor: "attestix:f9bdb7a94ccb40f1",
    target: "base-l2-testnet:0x8f2e4c9b...",
    hash: "sha256:3f6a9c2d5e8b1f4c7a0d3e6b9f2c5a8d1e4b7f0a3c6d9e2b5f8a1c4d7e0b3f6a",
    prev: "sha256:7b0c3f6a9d2e5b8c1f4a7e0d3b6c9f2a5d8e1b4c7f0a3d6e9b2c5f8a1d4e7b0c",
  },
];

export const RISK_LABEL: Record<Risk, string> = {
  prohibited: "Prohibited-adj.",
  high: "High-risk",
  limited: "Limited-risk",
  minimal: "Minimal-risk",
};

export const STATUS_LABEL: Record<AgentStatus, string> = {
  compl: "Compliant",
  gap: "Gaps",
  rev: "Revoked",
  pend: "Pending",
};

export interface ConsoleCredential {
  id: string;
  type: string;
  subject: string;
  issuer: string;
  issuerDid: string;
  issued: string;
  expiry: string;
  article: string;
  status: "valid" | "revoked";
  claims: Record<string, string | number>;
  signature: string;
}

export const CONSOLE_CREDENTIALS: ConsoleCredential[] = [
  {
    id: "urn:uuid:9e2f7a3c-1b4d-4c6e-8f0a-3d5b7c9e1f2a",
    type: "DeclarationOfConformity",
    subject: "attestix:f9bdb7a94ccb40f1",
    issuer: "VibeTensor",
    issuerDid: "did:web:vibetensor.com",
    issued: "2026-04-18T14:02:41Z",
    expiry: "2027-04-18",
    article: "Annex V",
    status: "valid",
    claims: {
      conformity_basis: "EU AI Act Article 43 (third_party)",
      notified_body: "NB-0482",
      risk_category: "high",
      assessment_id: "assmt:3c8f21e9b7a6d4c0",
    },
    signature:
      "z3Ap6K8mNwQr5bVz2Yh4jLfE1cXnPdRt9sBuGvHjKi7AxDoSnUwM4pRvTyZ8XqLbFgH2NvQrWsEdCfVbGnHmJkLpOiUy",
  },
  {
    id: "urn:uuid:4c8a1b2e-9f3d-4e7b-a5c8-1d0f3a6b9e2c",
    type: "AgentIdentityCredential",
    subject: "attestix:f9bdb7a94ccb40f1",
    issuer: "VibeTensor",
    issuerDid: "did:web:vibetensor.com",
    issued: "2026-03-12T09:14:02Z",
    expiry: "2027-03-12",
    article: "W3C VC 1.1",
    status: "valid",
    claims: {
      capabilities: "data_analysis, reporting, sql_query",
      protocol_bindings: "MCP, A2A",
      max_delegation_depth: 3,
    },
    signature:
      "z4Dq7M9nOvPr6cWz3Xi5kMgF2dYoQeRu0tCvHwIjLk8ByEpToVxN5qSwUzA9YrMcGhI3OwRsXtFeDgWcHoImKlMqPjVz",
  },
];
