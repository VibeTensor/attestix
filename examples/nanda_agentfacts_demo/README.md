# Attestix x NANDA AgentFacts demo

A self-contained demo of Attestix as the proof/trust layer for [Project NANDA](https://github.com/projnanda).

NANDA is the discovery layer (the index and the AgentFacts metadata for agents). The AgentFacts schema defines three trust fields but leaves them for tooling to populate:

- `trust_certifications`
- `reputation_scores`
- `content_flags`

Attestix is that tooling. It issues signed, independently verifiable values for those fields, so NANDA can tell you where an agent is and Attestix can prove what it is and whether to trust it.

## What the demo does

`demo.py` runs end to end with no network and no setup (it isolates Attestix file storage to a temp directory):

1. Creates an Attestix agent identity.
2. Issues a W3C Verifiable Credential (an EU AI Act conformity attestation) and places it under AgentFacts `trust_certifications`.
3. Creates an Attestix EU AI Act compliance profile and derives `content_flags` from it (risk category, compliance status).
4. Records a few interactions and reads an Attestix reputation/trust score into `reputation_scores`.
5. Assembles an AgentFacts document with those fields populated.
6. Offline-verifies the credential with the Attestix verifier, so any third party (a regulator, another agent) can check the proof without trusting the issuer's server.

## Run

```
pip install attestix
python examples/nanda_agentfacts_demo/demo.py
```

It prints each step and writes `sample_agentfacts.json`, an AgentFacts document with the three trust fields filled by Attestix.

## The mapping

| AgentFacts field | Attestix source |
|---|---|
| `trust_certifications` | a signed W3C Verifiable Credential (Ed25519, JCS canonical form) |
| `reputation_scores` | the Attestix reputation engine (interaction-weighted trust score) |
| `content_flags` | an Attestix EU AI Act compliance profile (risk category, status) |

Every value is cryptographically verifiable offline, in any of the six Attestix verifier languages, against the shared conformance vectors at [`spec/verify/v1`](https://github.com/VibeTensor/attestix/tree/main/spec/verify/v1).

## Verification, in any language

The credential issued here verifies byte-for-byte with the Python, Go, Rust, Java, JavaScript, and R verifiers, so a NANDA consumer can check an AgentFacts credential without running Attestix or trusting our server.

Links: [attestix.io](https://attestix.io) | [github.com/VibeTensor/attestix](https://github.com/VibeTensor/attestix)
