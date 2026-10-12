# Attestix - Frequently Asked Questions

## What does Attestix provide?

Attestix provides AI agent identity and signed evidence tooling: DIDs, Verifiable Credentials, delegated authority, provenance records and audit trails. The public core is licensed under Apache 2.0.

## Does a signed credential prove legal compliance?

A signature can establish integrity and association with a signing key under the verifier's trust policy. It does not establish that recorded claims are true, that an assessor is authorized, or that a system meets legal requirements.

## What does the governance workflow produce?

The workflow records risk information, documentation and assessment evidence. Generated declarations are provider-review drafts. Workflow completion is separate from legal conformity and does not certify SOC 2, ISO, GDPR or EU AI Act compliance.

## Does erasure delete every copy of agent data?

`IdentityService().purge_agent_data(agent_id)` removes managed local records and parseable local backups. It does not remove remote replicas, previously shared credentials or external backups. Revocation marks an identity revoked; it does not erase its records. Local deletion does not establish GDPR conformity.

## Can the default REST service isolate multiple tenants?

The default REST surface is single-tenant and rejects non-default tenant headers. A tenant header is not cross-tenant authorization. Configure authentication and validate any deployment-specific access controls separately.

## Is this a production or independent security signoff?

No. Source tests and negative-path regression checks support evaluation of the tested changes. Deployment acceptance, restore testing, key custody, incident response and appropriate independent review remain separate requirements.

## Where can users evaluate it?

See the [public repository](https://github.com/VibeTensor/attestix), [documentation](https://attestix.io/docs) and each SDK's release page. Validate the actual installed package version and its documented trust limits.
