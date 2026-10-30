"""Keep the published verification example bound to verifier-owned context."""

import ast
from copy import deepcopy
import json
from pathlib import Path
import socket
from types import SimpleNamespace

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import pytest

from attestix import config
from attestix.audit import AuditEventEmitter
from attestix.auth.crypto import public_key_to_did_key
from attestix.services.credential_service import CredentialService
from attestix.services.identity_service import IdentityService
from attestix.signing.inprocess_signer import InProcessSigner
from attestix.storage.memory_repository import MemoryRepository


@pytest.mark.parametrize('optimization', [0, 2])
@pytest.mark.parametrize('scenario', ['matching', 'wrong_nonce', 'tampered', 'unchecked'])
def test_documented_verification_rejects_untrusted_context(tmp_path, monkeypatch, optimization, scenario):
    def refuse_network(*args, **kwargs):
        raise AssertionError('The documentation smoke must remain offline')

    monkeypatch.setattr(socket.socket, 'connect', refuse_network)
    monkeypatch.chdir(tmp_path)
    document = Path(__file__).resolve().parents[2] / 'website/content/docs/guides/offline-verify.mdx'
    snippet = document.read_text(encoding='utf-8').split('## Step 3 /')[1].split('```python')[1].split('```')[0]
    constants = {
        node.targets[0].id: node.value.value
        for node in ast.parse(snippet).body
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
        and isinstance(node.value, ast.Constant)
    }
    challenge = constants['expected_challenge']
    domain = constants['expected_domain']
    key = Ed25519PrivateKey.generate()
    signer = InProcessSigner(private_key=key, did=public_key_to_did_key(key.public_key()))
    emitter = AuditEventEmitter(repository=MemoryRepository())
    identity = IdentityService(signer=signer, emitter=emitter).create_identity('Documentation smoke', 'test')
    service = CredentialService(signer=signer, emitter=emitter)
    credential = service.issue_credential(agent_id=identity['agent_id'], credential_type='AgentIdentityCredential')
    presentation = service.create_verifiable_presentation(
        identity['agent_id'], [credential['id']], audience_did=domain,
        challenge='another-request' if scenario == 'wrong_nonce' else challenge,
    )
    if scenario == 'tampered':
        presentation = deepcopy(presentation)
        presentation['challenge'] = 'modified-after-signing'
    if scenario == 'unchecked':
        unchecked = service.verify_presentation(presentation)
        assert unchecked['valid'] is True
        assert unchecked['checks']['replay_protection'] == 'unchecked'
        # An adapter that drops the trusted request context must not bypass the guard.
        verifier = SimpleNamespace(verify_presentation=lambda value, **kwargs: service.verify_presentation(value))
    else:
        verifier = service
    (tmp_path / 'presentation.json').write_text(json.dumps(presentation), encoding='utf-8')
    namespace = {'credential_svc': verifier, 'json': json}
    example = compile(snippet, str(document), 'exec', optimize=optimization)
    if scenario == 'matching':
        exec(example, namespace)
        assert namespace['result']['valid'] is True
        assert namespace['result']['checks']['replay_protection'] == 'context_checked'
    else:
        with pytest.raises(ValueError, match='request-context binding failed'):
            exec(example, namespace)
    assert not config.SIGNING_KEY_FILE.exists()
