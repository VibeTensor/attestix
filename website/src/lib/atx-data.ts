/*
 * Attestix v2 landing data.
 * Numbers here are the real project surface:
 *   - v0.4.0-rc.2 release candidate, 481 tests (390 functional + 91 conformance benchmarks),
 *     47 MCP tools, 9 modules, 44 REST endpoints. Single-maintainer project.
 *   - Base L2 is testnet (integration complete, mainnet schema not yet registered).
 *   - Real framework integrations: LangChain, OpenAI Agents SDK, CrewAI.
 * Mock agents/credentials/audit entries are clearly marked as illustrative.
 */

export type AtxIconName =
  | "identity"
  | "card"
  | "did"
  | "deleg"
  | "trust"
  | "check"
  | "cred"
  | "prov"
  | "chain"
  | "search"
  | "plus"
  | "arrow"
  | "arrowBack"
  | "chev"
  | "chevR"
  | "ext"
  | "copy"
  | "close"
  | "lock"
  | "eye"
  | "book";

export interface AtxModule {
  n: string;
  name: string;
  tools: number;
  desc: string;
  pills: string[];
  icon: AtxIconName;
}

export const ATX_MODULES: AtxModule[] = [
  {
    n: "01",
    name: "Identity",
    tools: 8,
    icon: "identity",
    desc: "Unified Agent Identity Tokens (UAIT) bridging MCP OAuth, A2A, DIDs and API keys. GDPR Article 17 erasure.",
    pills: ["create_agent_identity", "verify_identity", "translate_identity", "+5"],
  },
  {
    n: "02",
    name: "Agent Cards",
    tools: 3,
    icon: "card",
    desc: "Parse, generate and discover A2A-compatible agent cards via /.well-known/agent.json.",
    pills: ["parse_agent_card", "generate_agent_card", "discover_agent"],
  },
  {
    n: "03",
    name: "DID",
    tools: 3,
    icon: "did",
    desc: "Create and resolve W3C Decentralized Identifiers (did:key, did:web) with Ed25519VerificationKey2020.",
    pills: ["create_did_key", "create_did_web", "resolve_did"],
  },
  {
    n: "04",
    name: "Delegation",
    tools: 4,
    icon: "deleg",
    desc: "UCAN-style capability delegation with EdDSA-signed JWT tokens, attenuation and revocation.",
    pills: ["create_delegation", "verify_delegation", "list_delegations", "revoke"],
  },
  {
    n: "05",
    name: "Reputation",
    tools: 3,
    icon: "trust",
    desc: "Recency-weighted trust scoring (0.0 to 1.0) with category breakdown and search.",
    pills: ["record_interaction", "get_reputation", "query_reputation"],
  },
  {
    n: "06",
    name: "Compliance",
    tools: 7,
    icon: "check",
    desc: "EU AI Act risk profiles, conformity assessments (Article 43), Annex V declarations with auto-issued VCs.",
    pills: ["create_profile", "record_conformity", "declaration", "+4"],
  },
  {
    n: "07",
    name: "Credentials",
    tools: 8,
    icon: "cred",
    desc: "W3C Verifiable Credentials with Ed25519Signature2020 proofs, Verifiable Presentations and external verification.",
    pills: ["issue_credential", "verify_credential", "presentation", "+5"],
  },
  {
    n: "08",
    name: "Provenance",
    tools: 5,
    icon: "prov",
    desc: "Training data provenance (Article 10), model lineage (Article 11), hash-chained audit trail (Article 12).",
    pills: ["record_training_data", "record_model_lineage", "log_action", "+2"],
  },
  {
    n: "09",
    name: "Blockchain",
    tools: 6,
    icon: "chain",
    desc: "Anchor artifact hashes to Base L2 testnet via Ethereum Attestation Service with Merkle batching.",
    pills: ["anchor_identity", "anchor_credential", "anchor_audit_batch", "+3"],
  },
];

export interface AtxWorkflowStep {
  n: string;
  title: string;
  article: string;
  desc: string;
  bullets: string[];
  code: string;
}

export const ATX_WORKFLOW: AtxWorkflowStep[] = [
  {
    n: "01",
    title: "Create agent identity",
    article: "Identity \u00B7 Ed25519",
    desc: "Issue a Unified Agent Identity Token (UAIT) with a fresh did:key, Ed25519 keypair and bindings to MCP OAuth or A2A.",
    bullets: [
      "Ed25519 keypair generated",
      "did:key document published",
      "UAIT JSON signed and registered",
    ],
    code: `<span class="c">// attestix.identity.create_agent_identity</span>
<span class="k">agent</span> = identity_svc.create_identity(
  <span class="k">display_name</span>=<span class="s">"quarterly-analyst-v2"</span>,
  <span class="k">source_protocol</span>=<span class="s">"manual"</span>,
  <span class="k">capabilities</span>=[<span class="s">"data_analysis"</span>, <span class="s">"reporting"</span>],
  <span class="k">issuer_name</span>=<span class="s">"VibeTensor"</span>,
  <span class="k">expiry_days</span>=<span class="n">365</span>,
)

<span class="c"># output</span>
{
  <span class="k">"agent_id"</span>: <span class="s">"attestix:f9bdb7a94ccb40f1"</span>,
  <span class="k">"did"</span>: <span class="s">"did:key:z6MkhaXgBZDvotDkL5..."</span>,
  <span class="k">"verification_method"</span>: <span class="s">"Ed25519VerificationKey2020"</span>,
  <span class="k">"created"</span>: <span class="s">"2026-04-19T09:14:02Z"</span>,
  <span class="k">"signature"</span>: <span class="s">"z3Ap6K8m...xDoSnUwM"</span>
}`,
  },
  {
    n: "02",
    title: "Record training data",
    article: "Article 10 \u00B7 Data governance",
    desc: "Document training data sources, quality controls, representativeness and bias testing under EU AI Act Article 10.",
    bullets: [
      "Dataset checksum captured",
      "Rights-basis recorded (GDPR)",
      "Bias-testing results attached",
    ],
    code: `<span class="c">// attestix.provenance.record_training_data</span>
provenance_svc.record_training_data(
  <span class="k">agent_id</span>=<span class="s">"attestix:f9bdb7a94ccb40f1"</span>,
  <span class="k">dataset</span>={
    <span class="k">"name"</span>: <span class="s">"fin-q4-2025"</span>,
    <span class="k">"checksum"</span>: <span class="s">"sha256:4f8e2c9d...b7a0e5f8"</span>,
    <span class="k">"rows"</span>: <span class="n">18421095</span>,
    <span class="k">"rights_basis"</span>: <span class="s">"GDPR 6(1)(f)"</span>,
    <span class="k">"representativeness"</span>: <span class="s">"balanced-by-sector"</span>,
  },
  <span class="k">bias_tests</span>=[<span class="s">"demographic_parity"</span>, <span class="s">"equal_opportunity"</span>],
)
<span class="c"># Article 10 compliance recorded</span>`,
  },
  {
    n: "03",
    title: "Record model lineage",
    article: "Article 11 \u00B7 Documentation",
    desc: "Capture the model chain, base, fine-tunes, evaluation metrics, version hashes as required by Article 11.",
    bullets: [
      "Base model hash",
      "Fine-tune deltas",
      "Eval metrics (F1, precision, recall)",
    ],
    code: `<span class="c">// attestix.provenance.record_model_lineage</span>
provenance_svc.record_model_lineage(
  <span class="k">agent_id</span>=<span class="s">"attestix:f9bdb7a94ccb40f1"</span>,
  <span class="k">base_model</span>=<span class="s">"vibetensor-base@2026-03-01"</span>,
  <span class="k">fine_tunes</span>=[<span class="s">"vibetensor-fin-lora-v3"</span>],
  <span class="k">metrics</span>={
    <span class="k">"f1"</span>: <span class="n">0.894</span>, <span class="k">"precision"</span>: <span class="n">0.912</span>,
    <span class="k">"recall"</span>: <span class="n">0.877</span>, <span class="k">"eval_set"</span>: <span class="s">"hel-fin-1k"</span>,
  },
)`,
  },
  {
    n: "04",
    title: "Create compliance profile",
    article: "Article 6 \u00B7 Risk categorisation",
    desc: "Classify the system (prohibited, high-risk, limited, minimal) and auto-derive obligations for that tier.",
    bullets: [
      "Risk category: HIGH",
      "Obligations unfolded: 34",
      "Intended purpose captured",
    ],
    code: `<span class="c">// attestix.compliance.create_compliance_profile</span>
profile = compliance_svc.create_compliance_profile(
  <span class="k">agent_id</span>=<span class="s">"attestix:f9bdb7a94ccb40f1"</span>,
  <span class="k">risk_category</span>=<span class="s">"high"</span>,
  <span class="k">provider_name</span>=<span class="s">"VibeTensor"</span>,
  <span class="k">intended_purpose</span>=<span class="s">"Analyse quarterly financial data for board review"</span>,
)

<span class="c"># Obligations unfolded</span>
{
  <span class="k">"total"</span>: <span class="n">34</span>,
  <span class="k">"articles"</span>: [<span class="s">"9"</span>, <span class="s">"10"</span>, <span class="s">"11"</span>, <span class="s">"12"</span>, <span class="s">"13"</span>, <span class="s">"14"</span>, <span class="s">"15"</span>, <span class="s">"43"</span>],
  <span class="k">"completed"</span>: <span class="n">17</span>,
  <span class="k">"missing"</span>: <span class="n">17</span>
}`,
  },
  {
    n: "05",
    title: "Conformity assessment",
    article: "Article 43 \u00B7 Third-party",
    desc: "High-risk systems are blocked from self-assessment. Record the notified body third-party assessment.",
    bullets: [
      "Notified body (example): NB-XXXX \u00B7 Your certified auditor",
      "Assessment type: third_party",
      "Evidence attached",
    ],
    code: `<span class="c">// attestix.compliance.record_conformity_assessment</span>
compliance_svc.record_conformity_assessment(
  <span class="k">agent_id</span>=<span class="s">"attestix:f9bdb7a94ccb40f1"</span>,
  <span class="k">assessment_type</span>=<span class="s">"third_party"</span>,
  <span class="k">notified_body</span>={<span class="k">"id"</span>: <span class="s">"NB-XXXX"</span>, <span class="k">"name"</span>: <span class="s">"Your certified auditor"</span>},
  <span class="k">evidence_urls</span>=[<span class="s">"ipfs://QmX4...fB2"</span>],
)

<span class="c"># blocked path</span>
compliance_svc.record_conformity_assessment(<span class="k">assessment_type</span>=<span class="s">"self"</span>, ...)
<span class="y">ERROR: high-risk AI systems require third_party conformity assessment</span>`,
  },
  {
    n: "06",
    title: "Declaration of conformity",
    article: "Annex V \u00B7 Auto-VC",
    desc: "Generate the Annex V declaration. Attestix auto-issues a W3C Verifiable Credential with an Ed25519Signature2020 proof.",
    bullets: [
      "Annex V JSON rendered",
      "W3C VC issued automatically",
      "Machine-readable for regulators",
    ],
    code: `<span class="c">// attestix.compliance.generate_declaration_of_conformity</span>
decl = compliance_svc.generate_declaration_of_conformity(
  <span class="k">agent_id</span>=<span class="s">"attestix:f9bdb7a94ccb40f1"</span>
)

{
  <span class="k">"@context"</span>: [<span class="s">"https://www.w3.org/2018/credentials/v1"</span>],
  <span class="k">"type"</span>: [<span class="s">"VerifiableCredential"</span>, <span class="s">"DeclarationOfConformity"</span>],
  <span class="k">"issuer"</span>: <span class="s">"did:web:vibetensor.com"</span>,
  <span class="k">"proof"</span>: {
    <span class="k">"type"</span>: <span class="s">"Ed25519Signature2020"</span>,
    <span class="k">"proofValue"</span>: <span class="s">"z3Ap6K8mNwQr5bVz2Yh4jLfE1cXnPdRt9sBu..."</span>
  }
}`,
  },
  {
    n: "07",
    title: "Verifiable presentation",
    article: "W3C VP \u00B7 Signed bundle",
    desc: "Bundle credentials into a Verifiable Presentation for a specific verifier (a regulator, another agent or an auditor).",
    bullets: [
      "Audience-bound (did:web:eu.regulator)",
      "Replay-protected (nonce + challenge)",
      "Offline verifiable",
    ],
    code: `<span class="c">// attestix.credentials.create_verifiable_presentation</span>
vp = credential_svc.create_verifiable_presentation(
  <span class="k">holder_id</span>=<span class="s">"attestix:f9bdb7a94ccb40f1"</span>,
  <span class="k">credentials</span>=[<span class="s">"urn:uuid:9e2f7a3c-..."</span>, <span class="s">"urn:uuid:4c8a1b2e-..."</span>],
  <span class="k">verifier</span>=<span class="s">"did:web:eu.regulator"</span>,
  <span class="k">challenge</span>=<span class="s">"ch_8f2e4c9b1a0f"</span>,
)

<span class="c"># signed VP, ready to present</span>
{
  <span class="k">"type"</span>: [<span class="s">"VerifiablePresentation"</span>],
  <span class="k">"verifiableCredential"</span>: [ ..., ... ],
  <span class="k">"proof"</span>: { <span class="k">"type"</span>: <span class="s">"Ed25519Signature2020"</span>, ... }
}`,
  },
];

// Strip entries fall into two tiers: standards Attestix validates against
// via the conformance benchmark suite (RFC 8032, W3C VC, W3C DID, UCAN v0.9,
// MCP) and integration surfaces Attestix interoperates with (EAS, framework
// SDKs). Aspirational items (IEEE 7000, ISO/IEC 42001, ERC-8004) were
// removed pending actual implementation.
export const ATX_STANDARDS: string[] = [
  "MCP Protocol / 47 tools",
  "W3C Verifiable Credentials 1.1",
  "W3C DID Core 1.0",
  "UCAN v0.9 delegation",
  "RFC 8032 / Ed25519",
  "RFC 8785 / JSON canonicalization",
  "RFC 6962 / Merkle trees",
  "EU AI Act Annex V",
  "GDPR Article 17 / erasure",
  "Ethereum Attestation Service",
  "LangChain / CrewAI / OpenAI Agents SDK",
];

export interface AtxCertSample {
  agentName: string;
  agentId: string;
  did: string;
  issuerName: string;
  issuerDid: string;
  riskTier: string;
  basis: string;
  issued: string;
  validThru: string;
  proofValue: string;
  uuid: string;
}

export const ATX_CERT_SAMPLE: AtxCertSample = {
  uuid: "urn:uuid:9e2f7a3c",
  agentName: "quarterly-analyst-v2",
  agentId: "attestix:f9bdb7a94ccb40f1",
  did: "did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK",
  issuerName: "VibeTensor",
  issuerDid: "did:web:vibetensor.com",
  riskTier: "HIGH \u00B7 EU AI Act Article 6(2)",
  basis: "Article 43 third-party conformity \u00B7 NB-XXXX Your certified auditor",
  issued: "2026-04-18T14:02:41Z",
  validThru: "2027-04-18",
  proofValue:
    "z3Ap6K8mNwQr5bVz2Yh4jLfE1cXnPdRt9sBuGvHjKi7AxDoSnUwM4pRvTyZ8XqLbFgH2NvQrWsEd",
};

export const ATX_HERO_STATS = [
  { v: "47", k: "MCP Tools \u00B7 9 Modules" },
  { v: "481", k: "Automated Tests \u00B7 91 Conformance" },
  { v: "0.28 ms", k: "Ed25519 Sign + Verify (median)" },
  { v: "6", k: "IETF \u00B7 W3C \u00B7 UCAN Standards" },
];
