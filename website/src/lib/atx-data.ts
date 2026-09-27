/*
 * Attestix v2 landing data.
 * Numbers here are the real project surface:
 *   - Stable 0.4.1, 47 MCP tools, 9 modules, 44 REST endpoints.
 *     Single-maintainer project.
 *   - Base L2 anchoring defaults to Sepolia testnet (mainnet selectable via BASE_NETWORK).
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
    desc: "UCAN-style delegation tokens: server-signed EdDSA JWTs with attenuation checks and revocation.",
    pills: ["create_delegation", "verify_delegation", "list_delegations", "revoke_delegation"],
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
    desc: "EU AI Act risk profiles, conformity assessment records (Article 43), signed Annex V declarations with auto-issued credentials.",
    pills: ["create_compliance_profile", "record_conformity_assessment", "generate_declaration_of_conformity", "+4"],
  },
  {
    n: "07",
    name: "Credentials",
    tools: 8,
    icon: "cred",
    desc: "Credentials and presentations in the W3C VC data model, with Ed25519 proofs over Attestix canonical JSON, checked by the Attestix verifiers.",
    pills: ["issue_credential", "verify_credential", "create_verifiable_presentation", "+5"],
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
    desc: "Anchor artifact hashes to Base L2 (Sepolia testnet by default) via the Ethereum Attestation Service, with Merkle batching for audit logs.",
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
    desc: "Issue a Unified Agent Identity Token (UAIT) that bridges MCP OAuth, A2A, DIDs and API keys. The UAIT is signed with the Attestix server's Ed25519 key; agents do not get their own keypair.",
    bullets: [
      "Unique agent_id assigned",
      "UAIT signed by the server key (did:key)",
      "Stored locally under ~/.attestix",
    ],
    code: `<span class="c"># attestix.services.identity_service</span>
<span class="k">agent</span> = identity_svc.create_identity(
  <span class="k">display_name</span>=<span class="s">"quarterly-analyst-v2"</span>,
  <span class="k">source_protocol</span>=<span class="s">"manual"</span>,
  <span class="k">capabilities</span>=[<span class="s">"credit_scoring"</span>, <span class="s">"reporting"</span>],
  <span class="k">issuer_name</span>=<span class="s">"VibeTensor"</span>,
  <span class="k">expiry_days</span>=<span class="n">365</span>,
)

<span class="c"># output (abridged)</span>
{
  <span class="k">"agent_id"</span>: <span class="s">"attestix:f9bdb7a94ccb40f1"</span>,
  <span class="k">"did"</span>: <span class="s">"did:key:z6MkhaXgBZDvotDkL5..."</span>,  <span class="c"># server DID</span>
  <span class="k">"source_protocol"</span>: <span class="s">"manual"</span>,
  <span class="k">"created_at"</span>: <span class="s">"2026-04-19T09:14:02.412871+00:00"</span>,
  <span class="k">"expires_at"</span>: <span class="s">"2027-04-19T09:14:02.412871+00:00"</span>,
  <span class="k">"signature"</span>: <span class="s">"jAcsOXPq9JqV...GC49g7Q=="</span>
}`,
  },
  {
    n: "02",
    title: "Record training data",
    article: "Article 10 \u00B7 Data governance",
    desc: "Document training data sources, licences, personal-data categories and governance measures as evidence for EU AI Act Article 10.",
    bullets: [
      "Dataset name, version, source and licence",
      "Personal-data flag and data categories",
      "Governance measures, signed by the server key",
    ],
    code: `<span class="c"># attestix.services.provenance_service</span>
provenance_svc.record_training_data(
  <span class="k">agent_id</span>=<span class="s">"attestix:f9bdb7a94ccb40f1"</span>,
  <span class="k">dataset_name</span>=<span class="s">"fin-q4-2025"</span>,
  <span class="k">dataset_version</span>=<span class="s">"2025-12-31"</span>,
  <span class="k">source_url</span>=<span class="s">"s3://datasets/fin-q4-2025"</span>,
  <span class="k">license</span>=<span class="s">"proprietary"</span>,
  <span class="k">data_categories</span>=[<span class="s">"financial"</span>, <span class="s">"demographic"</span>],
  <span class="k">contains_personal_data</span>=<span class="k">True</span>,
  <span class="k">data_governance_measures</span>=<span class="s">"GDPR 6(1)(f); sector-balanced sampling"</span>,
)
<span class="c"># returns a signed provenance entry (entry_type="training_data")</span>`,
  },
  {
    n: "03",
    title: "Record model lineage",
    article: "Article 11 \u00B7 Documentation",
    desc: "Capture the base model, provider, fine-tuning method, training config and evaluation metrics for the Article 11 technical documentation.",
    bullets: [
      "Base model and provider",
      "Fine-tuning method and training config",
      "Eval metrics (F1, precision, recall)",
    ],
    code: `<span class="c"># attestix.services.provenance_service</span>
provenance_svc.record_model_lineage(
  <span class="k">agent_id</span>=<span class="s">"attestix:f9bdb7a94ccb40f1"</span>,
  <span class="k">base_model</span>=<span class="s">"vibetensor-base@2026-03-01"</span>,
  <span class="k">base_model_provider</span>=<span class="s">"VibeTensor"</span>,
  <span class="k">fine_tuning_method</span>=<span class="s">"LoRA"</span>,
  <span class="k">evaluation_metrics</span>={
    <span class="k">"f1"</span>: <span class="n">0.894</span>, <span class="k">"precision"</span>: <span class="n">0.912</span>,
    <span class="k">"recall"</span>: <span class="n">0.877</span>, <span class="k">"eval_set"</span>: <span class="s">"hel-fin-1k"</span>,
  },
  <span class="k">training_config</span>={<span class="k">"epochs"</span>: <span class="n">3</span>, <span class="k">"lr"</span>: <span class="n">2e-4</span>},
)`,
  },
  {
    n: "04",
    title: "Create compliance profile",
    article: "Article 6 \u00B7 Risk categorisation",
    desc: "Record the risk category (high, limited or minimal; prohibited systems are refused) and the Annex III point, and get the list of obligations for that tier.",
    bullets: [
      "Risk category: high, Annex III point 5",
      "12 required obligations listed",
      "Intended purpose and oversight measures captured",
    ],
    code: `<span class="c"># attestix.services.compliance_service</span>
profile = compliance_svc.create_compliance_profile(
  <span class="k">agent_id</span>=<span class="s">"attestix:f9bdb7a94ccb40f1"</span>,
  <span class="k">risk_category</span>=<span class="s">"high"</span>,
  <span class="k">provider_name</span>=<span class="s">"VibeTensor"</span>,
  <span class="k">intended_purpose</span>=<span class="s">"Creditworthiness scoring for consumer loans"</span>,
  <span class="k">transparency_obligations</span>=<span class="s">"Applicants told an AI system scores them"</span>,
  <span class="k">human_oversight_measures</span>=<span class="s">"Credit officer reviews every decline"</span>,
  <span class="k">annex_iii_category</span>=<span class="n">5</span>,
)

<span class="c"># output (abridged)</span>
{
  <span class="k">"risk_category"</span>: <span class="s">"high"</span>,
  <span class="k">"annex_iii_category"</span>: <span class="n">5</span>,
  <span class="k">"required_obligations"</span>: [
    <span class="s">"registration_in_eu_database"</span>, <span class="s">"conformity_assessment"</span>,
    <span class="s">"risk_management_system"</span>, <span class="s">"data_governance"</span>,
    <span class="s">"technical_documentation"</span>, <span class="s">"record_keeping"</span>, ...
  ]
}`,
  },
  {
    n: "05",
    title: "Conformity assessment",
    article: "Article 43",
    desc: "Record the conformity route each system takes. Most Annex III systems use internal control (Annex VI); Attestix treats Annex III point 1 biometrics as needing a notified body and refuses self-assessment there.",
    bullets: [
      "Annex III points 2-8: internal control (Annex VI)",
      "Annex III point 1: notified body (Annex VII)",
      "Result, findings, and CE-marking eligibility recorded",
    ],
    code: `<span class="c"># attestix.services.compliance_service</span>
compliance_svc.record_conformity_assessment(
  <span class="k">agent_id</span>=<span class="s">"attestix:f9bdb7a94ccb40f1"</span>,
  <span class="k">assessment_type</span>=<span class="s">"self"</span>,  <span class="c"># internal control, Annex VI</span>
  <span class="k">assessor_name</span>=<span class="s">"Internal QA board"</span>,
  <span class="k">result</span>=<span class="s">"pass"</span>,
  <span class="k">ce_marking_eligible</span>=<span class="k">True</span>,
)

<span class="c"># Annex III point 1 (biometrics): a notified body is required</span>
compliance_svc.record_conformity_assessment(<span class="k">assessment_type</span>=<span class="s">"self"</span>, ...)
<span class="y">error: Self-assessment not permitted: Annex III Point 1 (biometrics) requires
third-party conformity assessment via notified body per Article 43 (Annex VII
procedure). Use assessment_type='third_party' with a notified body.</span>`,
  },
  {
    n: "06",
    title: "Declaration of conformity",
    article: "Annex V \u00B7 Signed record",
    desc: "Generate the Annex V declaration, signed by the server key. Attestix also issues an EUAIActComplianceCredential (W3C VC data model, Ed25519 proof) and returns its id.",
    bullets: [
      "Annex V fields rendered as JSON",
      "Declaration signed with Ed25519",
      "Companion credential id returned",
    ],
    code: `<span class="c"># attestix.services.compliance_service</span>
decl = compliance_svc.generate_declaration_of_conformity(
  <span class="k">agent_id</span>=<span class="s">"attestix:f9bdb7a94ccb40f1"</span>
)

<span class="c"># output (abridged)</span>
{
  <span class="k">"declaration_id"</span>: <span class="s">"decl:7c1e94a0b2d3"</span>,
  <span class="k">"regulation_reference"</span>: <span class="s">"Regulation (EU) 2024/1689 (EU AI Act) Annex V"</span>,
  <span class="k">"annex_v_fields"</span>: { <span class="k">"1_provider_name"</span>: <span class="s">"VibeTensor"</span>, ... },
  <span class="k">"issuer_did"</span>: <span class="s">"did:key:z6MkhaXgBZDvotDkL5..."</span>,
  <span class="k">"signature"</span>: <span class="s">"iVEneRuw_k6-...JNc9zw=="</span>,
  <span class="k">"credential_id"</span>: <span class="s">"urn:uuid:9e2f7a3c-..."</span>
}`,
  },
  {
    n: "07",
    title: "Verifiable presentation",
    article: "W3C VP data model \u00B7 Signed bundle",
    desc: "Bundle credentials into a Verifiable Presentation for a specific verifier (a regulator, another agent or an auditor). The presentation is signed by the server key.",
    bullets: [
      "Audience-bound (domain = verifier DID)",
      "Replay-protected (challenge)",
      "Signature checkable offline with the Attestix verifiers",
    ],
    code: `<span class="c"># attestix.services.credential_service</span>
vp = credential_svc.create_verifiable_presentation(
  <span class="k">agent_id</span>=<span class="s">"attestix:f9bdb7a94ccb40f1"</span>,
  <span class="k">credential_ids</span>=[<span class="s">"urn:uuid:9e2f7a3c-..."</span>, <span class="s">"urn:uuid:4c8a1b2e-..."</span>],
  <span class="k">audience_did</span>=<span class="s">"did:web:regulator.example"</span>,
  <span class="k">challenge</span>=<span class="s">"ch_8f2e4c9b1a0f"</span>,
)

<span class="c"># signed VP (abridged)</span>
{
  <span class="k">"type"</span>: [<span class="s">"VerifiablePresentation"</span>],
  <span class="k">"holder"</span>: <span class="s">"attestix:f9bdb7a94ccb40f1"</span>,
  <span class="k">"verifiableCredential"</span>: [ ..., ... ],
  <span class="k">"proof"</span>: { <span class="k">"type"</span>: <span class="s">"Ed25519Signature2020"</span>, <span class="k">"challenge"</span>: <span class="s">"ch_8f2e4c9b1a0f"</span>, ... }
}
<span class="c"># proof is Ed25519 over Attestix canonical JSON; check it with the Attestix verifiers</span>`,
  },
];

// Strip entries fall into two tiers: specs Attestix builds on and checks in
// its own conformance benchmark suite (RFC 8032, W3C VC and DID data models,
// UCAN-style tokens, MCP) and integration surfaces (EAS, framework SDKs).
// Proofs are Ed25519 over Attestix's RFC 8785-style canonical JSON, so they
// are checked with the Attestix verifiers, not generic W3C verifiers.
// Aspirational items (IEEE 7000, ISO/IEC 42001, ERC-8004) were removed
// pending actual implementation.
export const ATX_STANDARDS: string[] = [
  "MCP Protocol / 47 tools",
  "W3C VC Data Model 1.1",
  "W3C DID Core 1.0",
  "UCAN-style delegation (JWT)",
  "RFC 8032 / Ed25519",
  "RFC 8785-style canonical JSON",
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
  // Attestix signs with one server key: the agent's UAIT carries the server
  // DID, so the agent DID and issuer DID are the same did:key here.
  issuerDid: "did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK",
  riskTier: "HIGH \u00B7 EU AI Act Article 6(2)",
  basis: "Article 43(2) internal control \u00B7 Annex VI",
  issued: "2026-04-18T14:02:41Z",
  validThru: "2027-04-18",
  proofValue:
    "ao-BCXbZz9KAJmcSY1cK4abXmtkRihup522srZg4cFF1_d__DnjNHkJiN2HEuf7diZJOtb2jzALEDyDE_sskzg==",
};

// Durable, verifiable facts only (qualified on the homepage). No test counts
// (they drift per commit) and no crypto-library benchmarks (they measure the
// library, not Attestix).
export const ATX_HERO_STATS = [
  { v: "47", k: "MCP tools across 9 modules" },
  { v: "6", k: "verifier SDKs share one test-vector suite" },
  { v: "0", k: "bytes uploaded to verify a credential" },
  { v: "Apache 2.0", k: "open source, self-host free" },
];
