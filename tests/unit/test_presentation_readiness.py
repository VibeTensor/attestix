"""Presentations must preserve credential validity checks."""


def test_presentation_rejects_expired_credential(credential_service, sample_agent_id):
    credential = credential_service.issue_credential(
        agent_id=sample_agent_id,
        credential_type='AuditCredential',
        expiry_days=-1,
    )
    presentation = credential_service.create_verifiable_presentation(sample_agent_id, [credential['id']])
    assert credential_service.verify_presentation(presentation)['valid'] is False


def test_presentation_rejects_locally_revoked_credential(credential_service, sample_agent_id):
    credential = credential_service.issue_credential(
        agent_id=sample_agent_id,
        credential_type='AuditCredential',
    )
    presentation = credential_service.create_verifiable_presentation(sample_agent_id, [credential['id']])
    credential_service.revoke_credential(credential['id'], 'Audit revocation')
    assert credential_service.verify_presentation(presentation)['valid'] is False
