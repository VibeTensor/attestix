"""Presentations must preserve credential validity checks."""


def test_presentation_rejects_expired_credential(credential_service, sample_agent_id):
    credential = credential_service.issue_credential(
        agent_id=sample_agent_id,
        credential_type='AuditCredential',
        expiry_days=-1,
    )
    presentation = credential_service.create_verifiable_presentation(sample_agent_id, [credential['id']])
    result = credential_service.verify_presentation(presentation)
    assert result['valid'] is False
    assert result['checks']['credentials_valid'] is False


def test_presentation_rejects_locally_revoked_credential(credential_service, sample_agent_id):
    credential = credential_service.issue_credential(
        agent_id=sample_agent_id,
        credential_type='AuditCredential',
    )
    presentation = credential_service.create_verifiable_presentation(sample_agent_id, [credential['id']])
    credential_service.revoke_credential(credential['id'], 'Audit revocation')
    result = credential_service.verify_presentation(presentation)
    assert result['valid'] is False
    assert result['checks']['credentials_valid'] is False


def _bound_presentation(credential_service, sample_agent_id):
    credential = credential_service.issue_credential(
        agent_id=sample_agent_id,
        credential_type='AuditCredential',
    )
    return credential_service.create_verifiable_presentation(
        sample_agent_id, [credential['id']], audience_did='did:web:verifier.example', challenge='nonce-1',
    )


def test_presentation_rejects_mismatched_challenge(credential_service, sample_agent_id):
    presentation = _bound_presentation(credential_service, sample_agent_id)
    result = credential_service.verify_presentation(
        presentation, expected_challenge='nonce-2', expected_domain='did:web:verifier.example',
    )
    assert result['valid'] is False
    assert result['checks']['challenge_matches'] is False
    assert result['checks']['domain_matches'] is True


def test_presentation_rejects_mismatched_domain(credential_service, sample_agent_id):
    presentation = _bound_presentation(credential_service, sample_agent_id)
    result = credential_service.verify_presentation(
        presentation, expected_challenge='nonce-1', expected_domain='did:web:other.example',
    )
    assert result['valid'] is False
    assert result['checks']['domain_matches'] is False


def test_presentation_rejects_missing_expected_context(credential_service, sample_agent_id):
    credential = credential_service.issue_credential(agent_id=sample_agent_id, credential_type='AuditCredential')
    presentation = credential_service.create_verifiable_presentation(sample_agent_id, [credential['id']])
    result = credential_service.verify_presentation(
        presentation, expected_challenge='nonce-1', expected_domain='did:web:verifier.example',
    )
    assert result['valid'] is False
    assert result['checks']['challenge_matches'] is False


def test_presentation_accepts_matching_context(credential_service, sample_agent_id):
    presentation = _bound_presentation(credential_service, sample_agent_id)
    result = credential_service.verify_presentation(
        presentation, expected_challenge='nonce-1', expected_domain='did:web:verifier.example',
    )
    assert result['valid'] is True
    assert result['checks']['replay_protection'] == 'context_checked'
