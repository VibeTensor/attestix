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
    display_name="compliance-auditor",
    source_protocol="manual",
    capabilities="audit, verify, report",
    description="Automated compliance auditing agent",
    issuer_name="Acme Corp",
    expiry_days=365
)

# Returns:
# - agent_id: "attestix:a1b2c3..."
# - did: "did:key:z6Mk..."
# - public_key: Ed25519 public key`,
  },
  {
    id: 2,
    title: "Issue Credential",
    description: "Issue a W3C Verifiable Credential with Ed25519 signatures.",
    code: `# Issue a W3C Verifiable Credential
# Signed with Ed25519Signature2020

credential = await issue_credential(
    subject_agent_id="attestix:agent456",
    credential_type="ComplianceCertification",
    issuer_name="Acme Corp",
    claims_json='{"risk_level": "limited", "framework": "EU AI Act"}',
    expiry_days=365
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
    issuer_agent_id="attestix:parent_agent",
    audience_agent_id="attestix:child_agent",
    capabilities="credential/issue, compliance/read",
    expiry_hours=24
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
    agent_id="attestix:agent456",
    risk_category="limited",
    provider_name="Acme Corp",
    intended_purpose="automated content moderation",
    transparency_obligations="AI-generated content disclosure",
    human_oversight_measures="human review before publish"
)

declaration = await generate_declaration_of_conformity(
    agent_id="attestix:agent456"
)

# Machine-readable Annex V declaration
# Auto-issues a W3C VC as proof
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
      <div className="px-4 py-6 md:px-6">
        <FeatureSelector features={features} />
      </div>
    </Section>
  );
}
