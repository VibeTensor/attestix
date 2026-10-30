"""Read-only publisher evidence validation; never executes producer artifacts."""
import io
import json
import os
from pathlib import Path
import re
import subprocess
import zipfile

REPO = 'VibeTensor/attestix'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def api(path, binary=False):
    result = subprocess.run(['gh', 'api', path], capture_output=True, timeout=60)
    require(result.returncode == 0, 'Publisher metadata unavailable')
    return result.stdout if binary else json.loads(result.stdout)


def source_record(payload):
    require(len(payload) <= 1_000_000, 'Publisher source archive exceeds bound')
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        require(archive.namelist() == ['release-source.json'], 'Unexpected publisher archive members')
        member = archive.getinfo('release-source.json')
        require(member.file_size <= 16_384 and not member.flag_bits & 1, 'Unsafe source metadata member')
        record = json.loads(archive.read(member))
    require(set(record) == {'release_tag', 'source_sha', 'source_event'}, 'Unexpected source schema')
    require(re.fullmatch(r'v[0-9]+\.[0-9]+\.[0-9]+', record['release_tag']), 'Invalid stable tag')
    require(re.fullmatch(r'[0-9a-f]{40}', record['source_sha']), 'Invalid source identity')
    require(record['source_event'] in {'release', 'workflow_dispatch'}, 'Unexpected publisher event')
    return record


def main():
    require(os.environ.get('GITHUB_REPOSITORY') == REPO, 'Wrong repository')
    event = os.environ['GITHUB_EVENT_NAME']
    require(event in {'pull_request', 'workflow_dispatch', 'workflow_run'}, 'Unsupported evidence event')
    if event != 'pull_request':
        require(os.environ.get('GITHUB_REF') == 'refs/heads/main', 'Only exact main may run release automation')
    run_id = os.environ['SOURCE_RUN_ID']
    require(re.fullmatch(r'[0-9]+', run_id), 'Invalid publisher run selector')
    run = api('repos/' + REPO + '/actions/runs/' + run_id)
    workflow = api('repos/' + REPO + '/actions/workflows/publish.yml')
    require(run['workflow_id'] == workflow['id'] and workflow['path'] == '.github/workflows/publish.yml', 'Wrong producer workflow')
    require(run['repository']['full_name'] == REPO and run['head_repository']['full_name'] == REPO, 'Foreign producer')
    require(run['status'] == 'completed' and run['conclusion'] == 'success', 'Publication verification did not succeed')
    require(run['event'] in {'release', 'workflow_dispatch'}, 'Untrusted producer event')
    jobs = api('repos/' + REPO + '/actions/runs/' + run_id + '/jobs')['jobs']
    verified = [job for job in jobs if job['name'] == 'verify-published']
    require(len(verified) == 1 and verified[0]['conclusion'] == 'success', 'Verified PyPI job absent')
    artifacts = api('repos/' + REPO + '/actions/runs/' + run_id + '/artifacts')['artifacts']
    matches = [item for item in artifacts if item['name'] == 'python-release-source' and not item['expired']]
    require(len(matches) == 1 and matches[0]['size_in_bytes'] <= 1_000_000, 'Verified source artifact unavailable')
    record = source_record(api('repos/' + REPO + '/actions/artifacts/' + str(matches[0]['id']) + '/zip', binary=True))
    require(record['source_sha'] == run['head_sha'] and record['source_event'] == run['event'], 'Producer/source identity mismatch')
    comparison = api('repos/' + REPO + '/compare/' + record['source_sha'] + '...main')
    require(comparison['status'] in {'ahead', 'identical'}, 'Published source is not merged to main')
    candidate = record['release_tag'][1:]
    requested = os.environ.get('REQUESTED_CANDIDATE', '')
    require(not requested or candidate == requested, 'Wrong requested candidate')
    if candidate == '0.5.0':
        require(record['source_sha'] == '8c564cf8ae66265255a843675d565d772f9c69f2', 'Reviewed0.5 source mismatch')
    destination = Path(os.environ['EVIDENCE_DIRECTORY'])
    destination.mkdir(parents=True, exist_ok=False)
    (destination / 'publisher.json').write_text(json.dumps({'run_id': run_id, **record}, indent=2), encoding='ascii')
    with Path(os.environ['GITHUB_OUTPUT']).open('a', encoding='utf-8') as stream:
        stream.write('candidate=' + candidate + '\n')


if __name__ == '__main__':
    main()
