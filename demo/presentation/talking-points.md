# Attestix Demo - Talking Points

**Total Duration:** 30 minutes
**Format:** Live demo with Claude Code + Attestix MCP server running locally
**Setup:** Have Claude Code open with Attestix configured as an MCP server. Have three terminal tabs ready.

---

## Problem Statement (5 minutes)

Start by looking at the audience. Do not touch the keyboard yet.

"Thank you for being here. I want to talk about a problem that every company deploying AI agents will face in about four months. On August 2, 2026, the EU AI Act begins enforcement. If your AI systems are classified as high-risk and you cannot prove compliance, the fines are up to 35 million euros or 7 percent of your global annual revenue, whichever is higher. That is not a theoretical risk. That is written into Article 99 of the regulation."

Pause. Let the number sink in.

"Now, here is the gap. The EU AI Act requires machine-readable technical documentation, conformity assessments, audit trails, and declarations of conformity. These are not PDFs sitting in a SharePoint folder. Articles 11 and 12 explicitly call for systematic, machine-readable records. But every compliance tool on the market today is an organizational dashboard. Credo AI, Holistic AI, Vanta - they are all built for human reviewers clicking through checklists. None of them produce cryptographically verifiable proof that a machine can verify."

Pause briefly.

"And there is a second problem. Agent identity is fragmenting. Microsoft has Entra Agent ID. AWS launched AgentCore. Google has A2A agent cards. There is no single protocol that bridges all of these and ties them to compliance evidence. So if your agent needs to prove its identity and its compliance status to another agent, to a regulator, or to a downstream system, there is no standard way to do that today."

"Attestix solves both of these problems. It is an open-source attestation infrastructure for AI agents. 47 MCP tools across 9 modules. It produces W3C Verifiable Credentials signed with Ed25519, anchored to the Base L2 blockchain, covering the full EU AI Act compliance workflow from identity creation through declaration of conformity. Everything runs offline. No cloud dependency. Let me show you."

---

## Scenario 1: FinTech Credit Scoring Agent - High Risk (8 minutes)

**Context:** An AI agent that evaluates credit applications for a European bank. This is a high-risk system under Annex III of the EU AI Act (creditworthiness assessment).

### Opening (30 seconds)

"Let us start with the hardest case. Imagine you are a FinTech company deploying an AI agent that scores credit applications in the EU. Under Annex III, Section 5(b), that is automatically classified as high-risk. You need full compliance documentation, a third-party conformity assessment, and a declaration of conformity before you can deploy. Let me walk through the entire workflow."

### Step 1: Create Agent Identity (1.5 minutes)

Run the command. While it executes, say:

"First, we create a cryptographic identity for this agent. Attestix generates what we call a Unified Agent Identity Token, a UAIT. Under the hood, it creates an Ed25519 keypair, generates a DID:key identifier following the W3C DID Core 1.0 specification, and signs the entire identity payload."

When the output appears, pause and point to the screen.

"Notice the agent ID format - attestix colon followed by a hex identifier. The DID is a did:key starting with z6Mk, which is the multicodec prefix for Ed25519 public keys. This identity is now the anchor for everything else we do. Every credential, every assessment, every audit entry will be tied back to this DID."

### Step 2: Record Training Data Provenance (1 minute)

"Article 10 of the EU AI Act requires data governance. You need to document what data your model was trained on, where it came from, and what preprocessing was applied. Let me record that."

Run the command. Point to the output.

"The provenance record captures the dataset name, source, license, size, preprocessing steps, and a hash of the record itself. This is Article 10 compliance in a machine-readable format."

### Step 3: Record Model Lineage (1 minute)

"Article 11 requires technical documentation of the model itself - its architecture, version, performance metrics, and lineage from parent models."

Run the command.

"Now we have a complete chain: the training data that went into this model, the model metadata, and the agent identity that wraps it. All cryptographically linked."

### Step 4: Create Compliance Profile (1 minute)

"Now for the EU AI Act risk classification. Let me create a compliance profile."

Run the command. When it returns, highlight the key fields.

"Look at the risk category: high-risk. Attestix automatically maps this to the correct Annex III category and generates the list of obligations. For high-risk systems, you will see requirements for conformity assessment, risk management system, data governance, technical documentation, human oversight, accuracy, and robustness. That is Articles 9 through 15."

### Step 5: Attempt Self-Assessment (1 minute)

"Here is something important. Let me try to do a self-assessment on this high-risk system."

Run the command. Wait for the error.

"Blocked. Attestix enforces Article 43 - high-risk AI systems require third-party conformity assessment by a notified body. You cannot bypass this. The system knows the risk level and enforces the correct assessment pathway. This is not a suggestion in a dashboard. It is a hard enforcement."

### Step 6: Third-Party Assessment + Declaration (1.5 minutes)

"So let us do it correctly. Record a third-party assessment from a notified body."

Run the command.

"Now we can generate the declaration of conformity. This follows Annex V of the EU AI Act."

Run the declaration command. Point to the output.

"Two things happened. First, Attestix generated the Annex V declaration with all required fields - the AI system name, provider details, conformity assessment reference, and the list of standards applied. Second, it automatically issued a W3C Verifiable Credential wrapping this declaration. The credential is signed with Ed25519Signature2020. Any system that receives this credential can cryptographically verify it was issued by this specific identity and has not been tampered with."

### Transition (30 seconds)

"That is a complete high-risk compliance workflow. Identity, provenance, lineage, risk classification, third-party assessment, and a cryptographically signed declaration. All in under two minutes. Now let me show you a different risk level."

---

## Scenario 2: Supply Chain Optimization Agent - Limited Risk (7 minutes)

**Context:** An AI agent that optimizes warehouse logistics and interacts with human operators. This is a limited-risk system under the EU AI Act (interacts with humans, must disclose AI nature).

### Opening (30 seconds)

"Scenario two. A supply chain company deploys an AI agent that optimizes warehouse routing and communicates with human operators about schedule changes. This agent interacts with people, so it falls under limited-risk transparency obligations in Article 50. Different risk level, different requirements."

### Step 1: Identity + Compliance Profile (1.5 minutes)

"Let me create the identity and compliance profile together."

Run both commands.

"For a limited-risk system, the obligations are lighter. You see transparency requirements - the system must disclose that it is an AI. You see logging requirements. But you do not need a third-party conformity assessment. Self-assessment is sufficient."

### Step 2: Self-Assessment and Declaration (1.5 minutes)

"Watch - this time, self-assessment works."

Run the self-assessment command.

"No error. Because this is limited-risk, Article 43 allows self-assessment. Now let me generate the declaration."

Run the declaration command.

"Same structure as before - an Annex V declaration wrapped in a W3C Verifiable Credential. But the obligations documented are transparency-focused rather than the full high-risk stack."

### Step 3: Delegation Chain (1.5 minutes)

"Now here is something unique to Attestix. Suppose this agent needs to delegate a capability to a sub-agent that handles a specific warehouse zone. We can create a UCAN-style delegation token."

Run the delegation command.

"This is a JWT signed with EdDSA. It specifies exactly what capabilities the sub-agent has, which resources it can access, and when the delegation expires. The parent agent's DID is the issuer, the sub-agent's DID is the audience. This follows the UCAN v0.9.0 specification. No other compliance tool does delegation chains."

### Step 4: Blockchain Anchoring (1.5 minutes)

"Finally, let me anchor the key artifacts to the blockchain. This creates an immutable, timestamped record on Base L2 through the Ethereum Attestation Service."

Run the anchor command (or show the estimate if no wallet is configured).

"Even without a funded wallet, you can see the gas estimation. When anchored, the SHA-256 hash of the credential is stored on-chain. Anyone can verify that this specific credential existed at this specific timestamp. This is your tamper-proof evidence trail for regulators."

### Transition (30 seconds)

"Two scenarios done. High-risk with enforced third-party assessment, limited-risk with self-assessment and delegation. Now let me show you the most interesting case - what happens when an AI system is classified as prohibited."

---

## Scenario 3: HR Screening Agent - Prohibited, Then Redesigned (7 minutes)

**Context:** A company wants to deploy an AI agent that automatically rejects job candidates based on emotional analysis from video interviews. This is prohibited under Article 5.

### Opening (30 seconds)

"Final scenario. A company comes to you and says: we want an AI agent that watches candidate video interviews, analyzes their emotional state, and automatically filters out candidates who seem stressed or nervous. What does Attestix do with this?"

### Step 1: Create Prohibited Profile (2 minutes)

"Let me create a compliance profile for this system."

Run the command with emotion recognition in employment context.

"Look at the result. Risk category: unacceptable. Attestix flags this as prohibited under Article 5 of the EU AI Act. Specifically, emotion recognition in the workplace context falls under prohibited practices. The system tells you exactly which article prohibits it and what the consequences are."

Pause. Look at the audience.

"This is not a yellow warning in a dashboard. This is a hard stop. No compliance profile is created for a prohibited system. You cannot proceed through the compliance workflow. The tool prevents you from generating documentation that would give a false sense of compliance for an illegal system."

### Step 2: Redesign the System (2 minutes)

"So the company goes back, redesigns the system. Instead of emotion analysis, the new agent uses structured interview scoring - it evaluates answers against job-specific criteria, with human reviewers making all final decisions. Let me profile the redesigned system."

Run the command with the new description.

"Now it classifies as high-risk - employment and worker management falls under Annex III, Section 4. High-risk, but legal. The company can proceed through the full compliance workflow we saw in Scenario 1. Third-party assessment required, full documentation, declaration of conformity."

### Step 3: Verifiable Presentation for Regulator (2 minutes)

"Let me show one more capability. Suppose a regulator asks this company to prove compliance. Attestix can bundle multiple credentials into a Verifiable Presentation."

Run the VP creation command.

"This VP contains the identity credential, the compliance declaration, and the conformity assessment - all bundled, all individually signed, and the bundle itself is signed with a fresh proof. The regulator can verify the entire package cryptographically. No phone calls. No email chains. No document requests. Machine-readable, verifiable proof."

### Transition (30 seconds)

"Three scenarios. Three different risk levels. One tool. And every single artifact is cryptographically signed, standards-compliant, and machine-verifiable. That is what Attestix does."

---

## Q&A and Closing (3 minutes)

"Let me recap what you just saw. Attestix provides end-to-end EU AI Act compliance automation for AI agents. 47 MCP tools across 9 modules. W3C Verifiable Credentials. Ed25519 cryptographic signatures. UCAN delegation chains. Blockchain anchoring on Base L2. Everything open-source under Apache 2.0."

"We have 284 automated tests, including 91 conformance benchmarks that validate every standards claim against the actual specifications - RFC 8032 for Ed25519, W3C VC Data Model 1.1, W3C DID Core 1.0, UCAN v0.9.0."

"The enforcement deadline is August 2, 2026. Every company deploying AI agents in the EU needs this. We are available on PyPI as 'attestix', registered in the MCP Registry, and documented at attestix.io/docs."

Pause.

"I am happy to take questions."

---

## Timing Checkpoints

| Section | Target Time | Cumulative |
|---------|------------|------------|
| Problem Statement | 5:00 | 5:00 |
| Scenario 1: FinTech (high-risk) | 8:00 | 13:00 |
| Scenario 2: Supply Chain (limited-risk) | 7:00 | 20:00 |
| Scenario 3: HR Screening (prohibited) | 7:00 | 27:00 |
| Q&A and Closing | 3:00 | 30:00 |

## Pacing Notes

- If running behind by Scenario 2, skip the delegation chain step and move directly to blockchain anchoring.
- If running ahead, expand the prohibited scenario with a discussion of other Article 5 prohibited practices (social scoring, real-time biometric identification).
- Keep tool execution time in mind. If a command takes more than a few seconds, fill the silence by explaining what is happening internally.
- Have the FAQ document ready on a tablet or second screen for Q&A answers.
