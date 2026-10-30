"""Reject ambiguous release metadata before uploading immutable packages."""
from __future__ import annotations

import argparse
import ast
from email.parser import BytesParser
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import tarfile
import time
import tomllib
import urllib.error
import urllib.parse
import urllib.request
import zipfile

MCP_MARKER_BYTES = re.compile(rb'mcp-name:\s*io\.github\.VibeTensor/attestix(?=\s|<|-->|$)')
MCP_MARKER_TEXT = re.compile(r'mcp-name:\s*io\.github\.VibeTensor/attestix(?=\s|<|-->|$)')


class ReleaseError(ValueError):
    """A release gate failed; publishing must stop."""


class PublishedPending(ReleaseError):
    """Registry propagation may recover within the bounded verification window."""


def project_metadata(root: Path, tag: str) -> dict:
    """Keep the installable package and registry identity on one release."""
    project = tomllib.loads((root / 'pyproject.toml').read_text(encoding='utf-8'))['project']
    version = project['version']
    if project['name'] != 'attestix' or not re.fullmatch(r'\d+\.\d+\.\d+', version) or tag != f'v{version}':
        raise ReleaseError('Package name, stable version and release tag must agree')
    source = ast.parse((root / 'attestix/__init__.py').read_text(encoding='utf-8'))
    declared = [node.value.value for node in source.body if isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == '__version__' for target in node.targets)
                and isinstance(node.value, ast.Constant)]
    if declared != [version]:
        raise ReleaseError('Canonical package version differs from project metadata')
    manifest = json.loads((root / 'server.json').read_text(encoding='utf-8'))
    expected_package = {'registryType': 'pypi', 'identifier': 'attestix', 'version': version}
    packages = manifest.get('packages')
    if manifest.get('name') != 'io.github.VibeTensor/attestix' or manifest.get('version') != version:
        raise ReleaseError('MCP identity or version differs from project metadata')
    if not isinstance(packages, list) or len(packages) != 1 or not isinstance(packages[0], dict) or any(packages[0].get(key) != value for key, value in expected_package.items()):
        raise ReleaseError('MCP package does not point to the exact Python release')
    if not project.get('requires-python'):
        raise ReleaseError('Python compatibility requirement is missing')
    return project


def registry_metadata(version: str) -> dict | None:
    """A registry outage must not be mistaken for an available version."""
    try:
        with urllib.request.urlopen(f'https://pypi.org/pypi/attestix/{version}/json', timeout=30) as response:
            data = response.read(4 * 1024 * 1024 + 1)
        if len(data) > 4 * 1024 * 1024:
            raise ReleaseError('Registry metadata exceeds the release-check limit')
        return json.loads(data)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        error_type = PublishedPending if error.code == 429 or error.code >= 500 else ReleaseError
        raise error_type(f'Registry metadata request failed with HTTP {error.code}') from None


def require_unpublished(version: str) -> None:
    """Existing releases cannot silently stand in for different source bytes."""
    if registry_metadata(version) is not None:
        raise ReleaseError('Version already exists on PyPI; choose a new version')


def safe_members(names: list[str]) -> None:
    """Inspect names before reading metadata, without opening sensitive members."""
    for name in names:
        path = PurePosixPath(name)
        lowered = {part.lower() for part in path.parts}
        if path.is_absolute() or '..' in path.parts or '\\' in name:
            raise ReleaseError('Unsafe distribution member path')
        if (any(part == '.env' or part.startswith('.env.') or part.startswith('client_secret_') for part in lowered)
                or lowered.intersection({'credentials.json', '.credentials.ps1', 'secure_vault', '.signing_key.json', '.keypairs.json'})
                or path.suffix.lower() in {'.pem', '.key'}):
            raise ReleaseError('Sensitive file name found in distribution')


def check_core_metadata(data: bytes, project: dict) -> None:
    message = BytesParser().parsebytes(data)
    expected = {'Name': project['name'], 'Version': project['version'], 'Requires-Python': project['requires-python']}
    if any(message.get(key) != value for key, value in expected.items()):
        raise ReleaseError('Built distribution metadata differs from reviewed source')
    description = message.get_payload(decode=True) or b''
    if not MCP_MARKER_BYTES.search(description):
        raise ReleaseError('Built description lacks MCP ownership marker')


def artifact_metadata(dist: Path, project: dict) -> dict[str, str]:
    """Reject stale or extra artifacts before handing a directory to a publisher."""
    version = project['version']
    wheel = dist / f'attestix-{version}-py3-none-any.whl'
    source = dist / f'attestix-{version}.tar.gz'
    if set(dist.iterdir()) != {wheel, source}:
        raise ReleaseError('Expected exactly the current wheel and source distribution')
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        safe_members(names)
        metadata = [name for name in names if name.endswith('.dist-info/METADATA')]
        if len(metadata) != 1:
            raise ReleaseError('Ambiguous wheel metadata')
        check_core_metadata(archive.read(metadata[0]), project)
    with tarfile.open(source, 'r:gz') as archive:
        names = archive.getnames()
        safe_members(names)
        metadata = [member for member in archive.getmembers() if member.name == f'attestix-{version}/PKG-INFO']
        if len(metadata) != 1 or not metadata[0].isfile():
            raise ReleaseError('Ambiguous source distribution metadata')
        stream = archive.extractfile(metadata[0])
        if stream is None:
            raise ReleaseError('Source metadata is unreadable')
        with stream:
            check_core_metadata(stream.read(), project)
    return {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in (wheel, source)}


def require_published(project: dict, expected: dict[str, str] | None = None) -> dict:
    """Verify the registry's exact files, not merely a successful upload job."""
    published = registry_metadata(project['version'])
    if not published or not published.get('urls'):
        raise PublishedPending('Expected release is not available on PyPI')
    if any(file.get('yanked') for file in published['urls']):
        raise ReleaseError('Refusing a yanked registry release')
    if expected is not None:
        for file in published['urls']:
            address = urllib.parse.urlsplit(file['url'])
            if (address.scheme != 'https' or address.hostname != 'files.pythonhosted.org'
                    or address.username is not None or address.password is not None
                    or address.port not in {None, 443}):
                raise ReleaseError('Unexpected registry artifact origin')
    info = published.get('info', {})
    if info.get('version') != project['version'] or info.get('requires_python') != project['requires-python']:
        raise PublishedPending('Published version or Python requirement differs')
    if not MCP_MARKER_TEXT.search(info.get('description') or ''):
        raise PublishedPending('Published description lacks MCP ownership marker')
    actual = {file['filename']: file['digests']['sha256'] for file in published['urls']}
    if expected is not None and actual != expected:
        raise PublishedPending('PyPI files or digests differ from the uploaded artifacts')
    for file in published['urls'] if expected is not None else []:
        digest = hashlib.sha256()
        with urllib.request.urlopen(file['url'], timeout=30) as response:
            while chunk := response.read(1024 * 1024):
                digest.update(chunk)
        if digest.hexdigest() != expected[file['filename']]:
            raise PublishedPending('Downloaded registry artifact digest differs')
    return actual


def wait_for_published(project: dict, expected: dict[str, str] | None = None, attempts: int = 5) -> dict:
    """Retry propagation failures without weakening any final validation gate."""
    for attempt in range(attempts):
        try:
            return require_published(project, expected)
        except (PublishedPending, urllib.error.URLError, TimeoutError):
            if attempt + 1 == attempts:
                raise
            time.sleep(2 ** (attempt + 1))
    raise ReleaseError('Published verification requires at least one attempt')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=['source', 'artifacts', 'published'])
    parser.add_argument('--tag', required=True)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--dist', type=Path)
    parser.add_argument('--unpublished', action='store_true')
    args = parser.parse_args()
    project = project_metadata(args.root, args.tag)
    if args.unpublished:
        require_unpublished(project['version'])
    artifacts = artifact_metadata(args.dist, project) if args.dist is not None else None
    if args.phase == 'artifacts' and artifacts is None:
        raise ReleaseError('Artifact validation requires --dist')
    if args.phase == 'published':
        artifacts = wait_for_published(project, artifacts)
    print(json.dumps({'version': project['version'], 'requires_python': project['requires-python'], 'artifacts': artifacts}, sort_keys=True))


if __name__ == '__main__':
    main()
