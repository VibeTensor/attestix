import { FeatureSelector } from "@/components/feature-selector";
import { Section } from "@/components/section";
import { codeToHtml } from "shiki";

interface FeatureOption {
  id: number;
  title: string;
  description: string;
  code: string;
}

const featureOptions: FeatureOption[] = [
  {
    id: 1,
    title: "Create Agent Identity",
    description: "Generate a unique agent identity with UAIT and DID.",
    code: `# Create a verifiable identity for your AI agent
# Generates a UAIT (Unique Agent Identity Token) and DID

result = await create_agent_identity(
    agent_name="compliance-auditor",
    capabilities=["audit", "verify", "report"],
    agent_type="compliance",
    version="1.0.0"
)

# Returns:
# - uait: "uait:atx:a1b2c3..."
# - did: "did:key:z6Mk..."
# - public_key: Ed25519 public key
# - agent_card: A2A-compatible agent card`,
  },
  {
    id: 2,
    title: "Issue Credential",
    description: "Issue a W3C Verifiable Credential with Ed25519 signatures.",
    code: `# Issue a W3C Verifiable Credential
# Signed with Ed25519Signature2020

credential = await issue_credential(
    issuer_id="uait:atx:issuer123",
    subject_id="uait:atx:agent456",
    credential_type="ComplianceCertification",
    claims={
        "risk_level": "limited",
        "framework": "EU AI Act",
        "assessment_date": "2026-01-15",
        "conformity_status": "compliant"
    },
    expiration_days=365
)

# Returns a full W3C VC with:
# - Ed25519Signature2020 proof
# - JSON-LD context
# - Credential status for revocation`,
  },
  {
    id: 3,
    title: "Delegate Capability",
    description: "Create a UCAN delegation token with scoped permissions.",
    code: `# Create a UCAN delegation chain
# Scoped capability delegation with JWT tokens

delegation = await create_delegation(
    issuer_id="uait:atx:parent_agent",
    audience_id="uait:atx:child_agent",
    capabilities=[
        {
            "with": "attestix://credentials/*",
            "can": "credential/issue"
        },
        {
            "with": "attestix://compliance/*",
            "can": "compliance/read"
        }
    ],
    expiration_hours=24,
    not_before=None  # Active immediately
)

# Returns a signed UCAN JWT token
# Supports chained delegation and revocation`,
  },
  {
    id: 4,
    title: "Verify Compliance",
    description: "Generate EU AI Act conformity declarations.",
    code: `# EU AI Act compliance pipeline
# Risk classification + conformity assessment + declaration

profile = await create_compliance_profile(
    agent_id="uait:atx:agent456",
    risk_level="limited",
    intended_purpose="automated content moderation",
    transparency_measures=[
        "AI-generated content disclosure",
        "human oversight mechanism",
        "bias monitoring dashboard"
    ]
)

declaration = await generate_declaration_of_conformity(
    agent_id="uait:atx:agent456",
    profile_id=profile["profile_id"],
    standards=["ISO 42001", "EU AI Act Annex V"],
    authorized_representative="VibeTensor GmbH"
)

# Machine-readable Annex V declaration
# Can be anchored to blockchain for immutability`,
  },
];

export async function Examples() {
  const features = await Promise.all(
    featureOptions.map(async (feature) => ({
      ...feature,
      code: await codeToHtml(feature.code, {
        lang: "python",
        theme: "github-dark",
      }),
    }))
  );

  return (
    <Section id="examples" title="Code Examples">
      <div className="border-x border-t">
        <FeatureSelector features={features} />
      </div>
    </Section>
  );
}
