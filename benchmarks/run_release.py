"""Prepare immutable public wheels, then compare installed releases offline."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
import venv
import zipfile

from worker import summary


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def progress(phase, **details):
    print(json.dumps({'phase': phase, **details}, ensure_ascii=True), flush=True)


def version(value):
    require(re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', value), 'Stable numeric version required')
    return value


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        return None


def fetch(url, limit):
    parsed = urllib.parse.urlsplit(url)
    require(parsed.scheme == 'https' and parsed.netloc in {'pypi.org', 'files.pythonhosted.org'}
            and not parsed.query and not parsed.fragment, 'Unexpected registry origin')
    if parsed.netloc == 'pypi.org':
        require(re.fullmatch(r'/pypi/attestix/[0-9]+\.[0-9]+\.[0-9]+/json', parsed.path), 'Unexpected metadata path')
    else:
        require(re.fullmatch(r'/packages/[A-Za-z0-9/_.-]+\.whl', parsed.path)
                and not any(part in {'.', '..'} for part in parsed.path.split('/')), 'Unexpected artifact path')
    with urllib.request.build_opener(NoRedirect()).open(url, timeout=60) as response:
        data = response.read(limit + 1)
    require(len(data) <= limit, 'Registry response exceeds bound')
    return data


def command(args, timeout=300):
    allowed = {'PATH', 'SYSTEMROOT', 'WINDIR', 'LD_LIBRARY_PATH', 'LANG', 'LC_ALL', 'TMPDIR', 'TEMP', 'TMP'}
    environment = {key: value for key, value in os.environ.items() if key.upper() in allowed}
    environment.update({'PIP_CONFIG_FILE': os.devnull, 'PIP_INDEX_URL': 'https://pypi.org/simple',
                        'PIP_DISABLE_PIP_VERSION_CHECK': '1'})
    result = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', timeout=timeout, env=environment)
    require(result.returncode == 0, 'Setup command failed; no benchmark result produced')
    return result.stdout


def wheel_identity(path):
    with zipfile.ZipFile(path) as archive:
        names = [name for name in archive.namelist() if name.endswith('.dist-info/METADATA')]
        require(len(names) == 1, 'Ambiguous wheel metadata')
        require(archive.getinfo(names[0]).file_size <= 1_000_000, 'Oversized wheel metadata')
        text = archive.read(names[0]).decode('utf-8')
    name = re.search(r'^Name: (.+)$', text, re.M)
    release = re.search(r'^Version: (.+)$', text, re.M)
    require(name and release, 'Wheel identity absent')
    return name.group(1).strip(), release.group(1).strip()


def prepare(args):
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    records = {}
    for label, release in [('baseline', version(args.baseline)), ('candidate', version(args.candidate))]:
        progress('prepare_release', release=label, version=release)
        metadata = json.loads(fetch('https://pypi.org/pypi/attestix/' + release + '/json', 2_000_000))
        wheels = [item for item in metadata['urls'] if item['packagetype'] == 'bdist_wheel']
        require(len(wheels) == 1, 'Expected one published Attestix wheel')
        artifact = wheels[0]
        require(artifact['filename'] == 'attestix-' + release + '-py3-none-any.whl', 'Unexpected product wheel filename')
        require(urllib.parse.urlsplit(artifact['url']).path.endswith('/' + artifact['filename']), 'Artifact URL/filename mismatch')
        payload = fetch(artifact['url'], 20_000_000)
        digest = hashlib.sha256(payload).hexdigest()
        require(digest == artifact['digests']['sha256'], 'Published wheel digest mismatch')
        if release in PINNED_CURRENT:
            require(digest == PINNED_CURRENT[release], 'Reviewed current-release artifact changed')
        directory = output / label
        wheelhouse = directory / 'wheels'
        wheelhouse.mkdir(parents=True)
        target = wheelhouse / artifact['filename']
        target.write_bytes(payload)
        require(wheel_identity(target) == ('attestix', release), 'Wrong product wheel')
        environment = directory / 'venv'
        venv.EnvBuilder(with_pip=True, symlinks=os.name != 'nt').create(environment)
        python = environment / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
        command([str(python), '-m', 'pip', 'download', '--disable-pip-version-check', '--only-binary=:all:', '--dest', str(wheelhouse), str(target)])
        packages = []
        names = set()
        for path in sorted(wheelhouse.glob('*.whl')):
            name, resolved = wheel_identity(path)
            normalized = re.sub(r'[-_.]+', '-', name).lower()
            require(normalized not in names, 'Duplicate dependency wheel')
            names.add(normalized)
            packages.append({'name': name, 'version': resolved, 'filename': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        lock = output / (label + '.lock')
        lock.write_text('\n'.join(item['name'] + '==' + item['version'] + ' --hash=sha256:' + item['sha256'] for item in packages) + '\n', encoding='ascii')
        command([str(python), '-m', 'pip', 'install', '--disable-pip-version-check', '--no-index', '--find-links', str(wheelhouse), '--require-hashes', '--no-deps', '-r', str(lock)])
        command([str(python), '-m', 'pip', 'check'])
        identity = json.loads(command([str(python), '-I', '-c', 'import json,sys; print(json.dumps({"version":sys.version,"base_prefix":sys.base_prefix,"base_executable":sys._base_executable}))']))
        records[label] = {'version': release, 'python_relative': str(python.relative_to(output)), 'wheel': {'filename': artifact['filename'], 'sha256': digest, 'url': artifact['url']}, 'resolved_dependencies': packages, 'interpreter': identity}
        progress('installed_and_hash_locked', release=label)
    require(records['baseline']['interpreter'] == records['candidate']['interpreter'], 'Interpreter mismatch')
    setup = {'schema_version': 1, 'package': 'attestix', 'baseline': records['baseline'], 'candidate': records['candidate']}
    (output / 'setup.json').write_text(json.dumps(setup, indent=2), encoding='ascii')
    print('Verified and installed both public wheels; no timing has run')


def isolated_worker(output, item, mode, **parameters):
    python = output / item['python_relative']
    with tempfile.TemporaryDirectory(prefix='attestix-benchmark-') as temporary:
        scratch = Path(temporary).resolve()
        require(scratch.parent == Path(tempfile.gettempdir()).resolve(), 'Unexpected temporary root')
        data = scratch / 'data'
        data.mkdir()
        probe_directory = scratch / 'probe-tmp'
        probe_directory.mkdir()
        request = {'mode': mode, 'version': item['version'], 'data_directory': str(data),
                   'probe_directory': str(probe_directory), **parameters}
        allowed = {'PATH', 'SYSTEMROOT', 'WINDIR', 'LD_LIBRARY_PATH', 'LANG', 'LC_ALL', 'TMPDIR', 'TEMP', 'TMP'}
        environment = {key: value for key, value in os.environ.items() if key.upper() in allowed}
        environment.update({'ATTESTIX_DATA_DIR': str(data), 'PYTHONDONTWRITEBYTECODE': '1', 'NO_COLOR': '1', 'TERM': 'dumb'})
        environment.update({name: str(probe_directory) for name in ['TMPDIR', 'TEMP', 'TMP']})
        start = time.perf_counter_ns()
        result = subprocess.run([str(python), '-I', '-B', str(Path(__file__).with_name('worker.py').resolve())], input=json.dumps(request), cwd=scratch, env=environment, capture_output=True, text=True, encoding='utf-8', timeout=90)
        elapsed = time.perf_counter_ns() - start
        require(result.returncode == 0, 'Isolated worker failed; raw output withheld')
        try:
            record = json.loads(result.stdout)
        except ValueError:
            raise RuntimeError('Worker emitted unexpected output; raw output withheld') from None
        require(not any(path.is_file() for path in scratch.rglob('*')), 'Product persisted a file')
        return record, elapsed


def run(args):
    output = Path(args.output).resolve()
    setup = json.loads((output / 'setup.json').read_text())
    labels = ['baseline', 'candidate']
    probes, cli_probes = {}, {}
    policy_observations = []
    for label in labels:
        progress('installed_correctness_probe', release=label)
        probe, _ = isolated_worker(output, setup[label], 'probe')
        expected = {'valid_signature', 'tampered_payload_rejected', 'wrong_key_rejected',
                    'malformed_signature_rejected', 'did_derivation', 'json_roundtrip', 'tampered_json_rejected'}
        checks = probe.get('correctness', {})
        if not probe.get('ok'):
            print(json.dumps({'failed_release': label, 'probe': probe}, ensure_ascii=True), flush=True)
        require(probe.get('ok') and set(checks) == expected and all(value is True for value in checks.values()), 'Both installed APIs must pass before timing')
        probes[label] = probe
        progress('installed_cli_help_probe', release=label)
        cli_probes[label], _ = isolated_worker(output, setup[label], 'cli_help')
        policy_observations.extend([{'release': label, 'phase': 'probe', 'policy': probe['policy']},
                                    {'release': label, 'phase': 'cli_compatibility', 'policy': cli_probes[label].get('policy')}])
    require(probes['baseline']['namespace'] == probes['candidate']['namespace'], 'Namespace mismatch needs explicit review')
    modes = ['crypto_import']
    if all(record.get('ok') for record in cli_probes.values()):
        modes.append('cli_help')
    measurements = []
    for mode in modes:
        raw = {label: [] for label in labels}
        inner = {label: [] for label in labels}
        for index in range(3 + args.startup_samples):
            for label in labels if index % 2 == 0 else list(reversed(labels)):
                progress('startup_invocation', release=label, workload=mode, index=index, warmup=index < 3)
                record, elapsed = isolated_worker(output, setup[label], mode)
                require(record.get('ok'), 'Startup correctness/policy failure')
                policy_observations.append({'release': label, 'phase': mode, 'index': index,
                                            'warmup': index < 3, 'policy': record['policy']})
                if index >= 3:
                    raw[label].append(elapsed)
                    inner[label].append(record['import_or_entrypoint_elapsed_ns'])
        for label in labels:
            measurements.append({'release': label, 'version': setup[label]['version'], 'workload': mode + '_fresh_process', 'warmup_processes': 3, 'filesystem_cache': 'warm/OS-managed, not machine-cold', **summary(raw[label])})
            measurements.append({'release': label, 'version': setup[label]['version'], 'workload': mode + '_inside_process', 'warmup_processes': 3, **summary(inner[label])})
    batches = {label: {} for label in labels}
    order = []
    for block in range(10):
        for label in labels if block % 2 == 0 else list(reversed(labels)):
            progress('crypto_operation_block', release=label, block=block)
            record, _ = isolated_worker(output, setup[label], 'operations', warmups=5, samples=10, batch_size=100)
            require(record.get('ok'), 'Timed operation correctness/policy failure')
            policy_observations.append({'release': label, 'phase': 'operations', 'block': block, 'policy': record['policy']})
            order.append({'block': block, 'release': label})
            for measurement in record['measurements']:
                key = (measurement['workload'], measurement['payload_bytes'])
                batches[label].setdefault(key, []).extend(measurement['raw_sample_elapsed_ns'])
    for label in labels:
        for (name, payload), raw in batches[label].items():
            require(len(raw) == 100, 'Missing measured batches')
            measurements.append({'release': label, 'version': setup[label]['version'], 'workload': name, 'payload_bytes': payload, 'measured_blocks': 10, 'warmup_batches_per_block': 5, **summary(raw, 100)})
    cpu = platform.processor()
    cpuinfo = Path('/proc/cpuinfo')
    if cpuinfo.exists():
        cpu = next((line.split(':', 1)[1].strip() for line in cpuinfo.read_text().splitlines() if line.startswith('model name')), cpu)
    result = {'schema_version': 1, 'visibility': 'public', 'package': 'attestix',
              'artifacts': {label: setup[label]['wheel'] for label in labels},
              'versions': {label: setup[label]['version'] for label in labels},
              'resolved_dependencies': {label: setup[label]['resolved_dependencies'] for label in labels},
              'environment': {'python': sys.version, 'implementation': platform.python_implementation(), 'platform': platform.platform(), 'cpu': cpu, 'logical_cpus': os.cpu_count(), 'runner_image': os.environ.get('ImageVersion'), 'harness_source_sha': os.environ.get('GITHUB_SHA'), 'run_id': os.environ.get('GITHUB_RUN_ID')},
              'correctness': probes, 'cli_compatibility': cli_probes, 'block_order': order,
              'policy_observations': policy_observations,
              'measurements': measurements, 'performance_threshold': None,
              'coverage': ['canonical installed crypto API', 'memory-only Ed25519', 'custom Attestix canonical JSON signing', 'CLI help only when both entry points pass offline gates'],
              'not_covered': ['MCP-ready latency', 'VC service persistence', 'audit-chain workload', 'Merkle proof API', 'network/cloud/model/payment/customer workflows'],
              'limitations': ['One shared virtual runner; no SLA or causal attribution', 'Dependency versions differ and are recorded', 'Crypto p95 is p95 of batch-average latency, not individual-operation tail latency', 'Python audit hooks are not an OS security sandbox', 'Hash-reviewed filelock capability-probe temporary filesystem operations are allowed and recorded', 'Process timing includes harness/guard overhead; inside-process timing is separate', 'No customer data, key serialization or key logging']}
    (output / 'result.json').write_text(json.dumps(result, indent=2), encoding='ascii')
    lines = ['# Installed Attestix release comparison', '', 'Observed samples, not an SLA or a claim that every product example ran.', '', '| Release | Workload | Bytes | Median ms | p95 ms | p95 scope |', '| --- | --- | --- | --- | --- | --- |']
    for item in measurements:
        lines.append('| ' + setup[item['release']]['version'] + ' | ' + item['workload'] + ' | ' + str(item.get('payload_bytes', '-')) + ' | ' + f"{item['median_ns_per_operation']/1e6:.6f}" + ' | ' + f"{item['p95_ns_per_operation']/1e6:.6f}" + ' | ' + item['percentile_scope'] + ' |')
    lines.extend(['', 'Both artifact imports and offline positive/negative checks passed before timing.', 'CLI help comparison: ' + ('included' if 'cli_help' in modes else 'not available under the offline gates; see result.json'), '', 'See result.json for raw samples, resolved dependencies, environment and exclusions.'])
    (output / 'summary.md').write_text('\n'.join(lines) + '\n', encoding='ascii')
    print('\n'.join(lines))


PINNED_CURRENT = {'0.4.3': 'c9cc9b08f45ef3451a893238a66b81973b48f50f94befa30117c3226fd71b4cd',
                  '0.5.0': '831bf12eeb167aab260d84651c20530ad83a12eefbc88c4a676550974c986ecd'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['prepare', 'run'])
    parser.add_argument('--output', required=True)
    parser.add_argument('--baseline', default='0.4.3')
    parser.add_argument('--candidate', default='0.5.0')
    parser.add_argument('--startup-samples', type=int, default=30)
    arguments = parser.parse_args()
    require(5 <= arguments.startup_samples <= 100, 'Startup sample count outside bound')
    prepare(arguments) if arguments.mode == 'prepare' else run(arguments)
