# Attestix - AI Agent Identity and Signed Evidence

Attestix is an Apache 2.0 toolkit for agent identity, signed credentials, delegated authority and provenance records. It supports recording governance evidence; it does not establish legal conformity or certification.

## Developer workflow

1. Create an agent identity and define trusted signing keys.
2. Record provenance, delegated authority and audit events.
3. Verify signed records within the documented Attestix profile.
4. Review governance drafts with an accountable provider or assessor.

## Evaluation limits

The default REST surface is single-tenant. Local erasure covers managed records and parseable local backups; external copies require separate handling. Signatures preserve integrity but do not verify the truth of a provider assertion. Network integrations and blockchain anchoring have separate availability and trust requirements.

The EU AI Act has a staged application timeline. Consult the [current official timeline](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai) and determine obligations for the specific system and operator role.

## Get started

- [Source and releases](https://github.com/VibeTensor/attestix)
- [Documentation](https://attestix.io/docs)
- Python package: `pip install attestix`

Validate the installed version, authentication, data handling, restore procedure and operational controls before using production data.
