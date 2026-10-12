# Attestix Evaluation Checklist

Use the current repository and release artifacts to evaluate these capabilities. A comparison with another product requires current vendor evidence; this page does not assert competitors lack a feature.

| Capability | Attestix behavior | Evaluation requirement |
| --- | --- | --- |
| Agent identity | DID-based identity records | Establish trusted issuers and key custody |
| Signed credentials | Ed25519 verification within the documented profile | Check key binding, signature and unsupported-input rejection |
| Delegation | Delegated authority records | Validate audience, scope and expiry |
| Provenance | Dataset, model and action records | Review completeness and accuracy of supplied evidence |
| Audit trail | Hash-chained events | Validate storage, continuity and restore behavior |
| Governance | Evidence records and provider-review declaration drafts | Legal conformity remains separately assessed |
| Local erasure | Managed records and parseable local backups | Handle remote replicas, exports and shared credentials separately |
| REST tenancy | Default single-tenant surface | Non-default tenant headers are rejected |
| Source availability | Apache 2.0 public core | Test the actual installed release and its trust limits |
