"""Exercise release gates without registry writes or real credentials."""
import json
from pathlib import Path
from unittest.mock import patch
import urllib.error

import pytest

import release_guard as guard


ROOT = Path(__file__).resolve().parents[2]


def test_current_source_metadata_agrees():
    assert guard.project_metadata(ROOT, 'v0.5.0')['requires-python'] == '>=3.11'


@pytest.mark.parametrize('tag', ['v0.4.3', '0.5.0', 'v0.5.0rc1', 'v0.5.0; echo bad'])
def test_wrong_release_selector_is_rejected(tag):
    with pytest.raises(guard.ReleaseError):
        guard.project_metadata(ROOT, tag)


def test_malformed_mcp_package_is_rejected(tmp_path):
    (tmp_path / 'attestix').mkdir()
    for name in ['pyproject.toml', 'attestix/__init__.py']:
        (tmp_path / name).write_bytes((ROOT / name).read_bytes())
    manifest = json.loads((ROOT / 'server.json').read_text())
    manifest['packages'] = ['invalid']
    (tmp_path / 'server.json').write_text(json.dumps(manifest))
    with pytest.raises(guard.ReleaseError, match='MCP package'):
        guard.project_metadata(tmp_path, 'v0.5.0')


def test_existing_version_cannot_be_silently_skipped():
    with patch.object(guard, 'registry_metadata', return_value={'info': {}}):
        with pytest.raises(guard.ReleaseError, match='already exists'):
            guard.require_unpublished('0.5.0')


def test_registry_outage_is_not_an_available_version():
    failure = urllib.error.HTTPError('https://pypi.org', 503, 'Unavailable', {}, None)
    with patch.object(guard.urllib.request, 'urlopen', side_effect=failure):
        with pytest.raises(guard.ReleaseError, match='503'):
            guard.require_unpublished('0.5.0')


@pytest.mark.parametrize('name', ['../escape', '/absolute', 'x/credentials.json', 'x/.env.production', 'x/SECURE_VAULT/a', 'x/private.key'])
def test_sensitive_or_escaping_archive_names_are_rejected(name):
    with pytest.raises(guard.ReleaseError):
        guard.safe_members([name])


def test_stale_distribution_directory_is_rejected(tmp_path):
    (tmp_path / 'attestix-0.4.3.tar.gz').touch()
    with pytest.raises(guard.ReleaseError, match='exactly'):
        guard.artifact_metadata(tmp_path, {'version': '0.5.0'})


def test_published_file_hash_must_match_reviewed_artifact():
    project = guard.project_metadata(ROOT, 'v0.5.0')
    published = {'info': {'version': '0.5.0', 'requires_python': '>=3.11',
                         'description': 'mcp-name: io.github.VibeTensor/attestix'},
                 'urls': [{'filename': 'attestix.whl', 'digests': {'sha256': 'wrong'}, 'yanked': False}]}
    with patch.object(guard, 'registry_metadata', return_value=published):
        with pytest.raises(guard.ReleaseError, match='digests'):
            guard.require_published(project, {'attestix.whl': 'reviewed'})
