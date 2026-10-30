"""Isolated, memory-only installed-product workloads; emits no key material."""
import contextlib
import hashlib
import importlib
import importlib.metadata
import inspect
import io
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import time


class BenchmarkError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise BenchmarkError(message)


def protected(path):
    if not isinstance(path, (str, bytes, os.PathLike)):
        return False
    item = Path(os.fsdecode(path))
    name = item.name.lower()
    return (
        name.startswith('.env') or name.endswith(('.env', '.pem', '.key'))
        or name in {'credentials.json', '.credentials.ps1', '.signing_key.json', '.npmrc', '.pypirc', '.netrc', '.git-credentials'}
        or name.startswith('client_secret_') and name.endswith('.json')
        or any(part.lower() in {'secure_vault', '.aws', '.azure', '.ssh', '.kube'} for part in item.parts)
    )


class OfflinePolicy:
    def __init__(self, data_directory, probe_directory=None, probe_source=None):
        self.data_directory = Path(data_directory).resolve()
        self.probe_directory = Path(probe_directory).resolve() if probe_directory else None
        self.probe_source = Path(probe_source).resolve() if probe_source else None
        self.probe_directories = set()
        self.allowed_probe_operations = {}
        self.denied = []

    def probe_context(self):
        if self.probe_source is None:
            return False
        frame = sys._getframe()
        while frame is not None:
            if (frame.f_code.co_name == '_probe_link_follow_symlinks'
                    and frame.f_globals.get('__name__') == 'filelock._strict'
                    and Path(frame.f_code.co_filename).resolve() == self.probe_source):
                return True
            frame = frame.f_back
        return False

    def probe_path(self, path, directory_fd=None):
        if not isinstance(path, (str, bytes, os.PathLike)):
            return None
        item = Path(os.fsdecode(path))
        if item.is_absolute():
            return item.resolve()
        if isinstance(directory_fd, int) and directory_fd >= 0:
            identity = os.fstat(directory_fd)
            for directory in self.probe_directories:
                if directory.is_dir():
                    known = directory.stat()
                    if (known.st_dev, known.st_ino) == (identity.st_dev, identity.st_ino):
                        return (directory / item).resolve()
        return None

    def temporary_context(self, function):
        frame = sys._getframe()
        while frame is not None:
            if (frame.f_code.co_name == function and frame.f_globals.get('__name__') == 'tempfile'
                    and Path(frame.f_code.co_filename).resolve() == Path(tempfile.__file__).resolve()):
                return True
            frame = frame.f_back
        return False

    def allow_probe(self, event, args):
        if self.probe_directory is None or not self.probe_context():
            return False
        directory_fd = args[1] if event in {'os.remove', 'os.rmdir'} and len(args) > 1 else None
        target = self.probe_path(args[0], directory_fd)
        if target is None or not target.is_relative_to(self.probe_directory):
            return False
        discovery = (target.parent == self.probe_directory and re.fullmatch(r'[a-z0-9_]{8}', target.name)
                     and self.temporary_context('_get_default_tempdir'))
        in_probe = target.parent in self.probe_directories and target.name in {'probe-source', 'probe-link'}
        allowed = False
        if event == 'os.mkdir':
            allowed = (target.parent == self.probe_directory and re.fullmatch(r'tmp[a-z0-9_]{8}', target.name)
                       and self.temporary_context('mkdtemp'))
            if allowed:
                self.probe_directories.add(target)
        elif event == 'open':
            allowed = bool(discovery or in_probe and target.name == 'probe-source')
        elif event == 'os.link':
            destination = self.probe_path(args[1])
            allowed = (in_probe and target.name == 'probe-source' and destination is not None
                       and destination.parent == target.parent and destination.name == 'probe-link')
        elif event == 'os.remove':
            allowed = bool(discovery or in_probe)
        elif event == 'os.rmdir':
            allowed = target in self.probe_directories
        elif event in {'os.utime', 'os.chmod'}:
            allowed = bool(in_probe or target in self.probe_directories)
        if allowed:
            self.allowed_probe_operations[event] = self.allowed_probe_operations.get(event, 0) + 1
        return bool(allowed)

    def deny(self, kind):
        self.denied.append(kind)
        raise BenchmarkError('Offline policy rejected ' + kind)

    def audit(self, event, args):
        if event == 'os.mkdir' and len(args) > 2 and args[2] not in (None, -1):
            self.deny('directory-fd-write')
        if event.startswith('socket.') or event in {'subprocess.Popen', 'os.system', 'os.posix_spawn', 'os.fork'}:
            self.deny('network-or-subprocess')
        if event == 'open':
            path, mode, flags = args
            if protected(path):
                self.deny('protected-file-read')
            if isinstance(mode, str) and any(letter in mode for letter in 'wax+'):
                if not self.allow_probe(event, args):
                    self.deny('file-write')
                return
            if isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
                if not self.allow_probe(event, args):
                    self.deny('file-write')
        if event == 'os.mkdir':
            if Path(os.fsdecode(args[0])).resolve() != self.data_directory and not self.allow_probe(event, args):
                self.deny('directory-write')
        if event in {'os.remove', 'os.rename', 'os.rmdir', 'os.link', 'os.symlink', 'os.utime', 'os.chmod'}:
            if not self.allow_probe(event, args):
                self.deny('filesystem-mutation')


def summary(raw, operations=1):
    require(bool(raw) and operations > 0, 'Empty or invalid sample set')
    samples = sorted(value / operations for value in raw)
    count = len(samples)
    middle = count // 2
    median = samples[middle] if count % 2 else (samples[middle - 1] + samples[middle]) / 2
    return {'sample_count': count, 'operations_per_sample': operations,
            'median_ns_per_operation': median,
            'p95_ns_per_operation': samples[math.ceil(count * 0.95) - 1],
            'percentile_definition': 'nearest-rank',
            'percentile_scope': 'batch-average latency' if operations > 1 else 'one process invocation',
            'raw_sample_elapsed_ns': raw}


def validate_api(module):
    expected = {'generate_ed25519_keypair': [], 'sign_message': ['private_key', 'message'],
                'verify_signature': ['public_key', 'signature', 'message'],
                'public_key_to_did_key': ['public_key'], 'canonicalize_json': ['payload'],
                'sign_json_payload': ['private_key', 'payload'],
                'verify_json_signature': ['public_key', 'payload', 'signature_b64']}
    for name, parameters in expected.items():
        function = getattr(module, name, None)
        require(callable(function), 'Public API absent: ' + name)
        require(list(inspect.signature(function).parameters) == parameters, 'Public API signature mismatch')


def product_api(version):
    require(importlib.metadata.version('attestix') == version, 'Installed distribution version mismatch')
    module = importlib.import_module('attestix.auth.crypto')
    site = Path(importlib.metadata.distribution('attestix').locate_file('')).resolve()
    require(Path(module.__file__).resolve().is_relative_to(site), 'Source-tree import rejected')
    validate_api(module)
    return module


def correctness(api):
    private, public = api.generate_ed25519_keypair()
    _, wrong_public = api.generate_ed25519_keypair()
    payload = b'attestix-offline-release-check'
    signature = api.sign_message(private, payload)
    require(api.verify_signature(public, signature, payload) is True, 'Valid signature rejected')
    require(api.verify_signature(public, signature, payload + b'!') is False, 'Tampered payload accepted')
    require(api.verify_signature(wrong_public, signature, payload) is False, 'Wrong key accepted')
    require(api.verify_signature(public, b'bad', payload) is False, 'Malformed signature accepted')
    require(api.public_key_to_did_key(public).startswith('did:key:z'), 'DID derivation failed')
    document = {'kind': 'synthetic-release-benchmark', 'padding': 'x' * 1024}
    encoded = api.sign_json_payload(private, document)
    require(api.verify_json_signature(public, document, encoded) is True, 'JSON roundtrip rejected')
    require(api.verify_json_signature(public, {**document, 'padding': 'tampered'}, encoded) is False, 'Tampered JSON accepted')
    return {'valid_signature': True, 'tampered_payload_rejected': True,
            'wrong_key_rejected': True, 'malformed_signature_rejected': True,
            'did_derivation': True, 'json_roundtrip': True, 'tampered_json_rejected': True}


def cli_help():
    entries = [entry for entry in importlib.metadata.distribution('attestix').entry_points
               if entry.group == 'console_scripts' and entry.name == 'attestix']
    require(len(entries) == 1, 'Expected one installed CLI entry point')
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured), contextlib.redirect_stderr(captured):
        sys.argv = ['attestix', '--help']
        try:
            entries[0].load()()
        except SystemExit as error:
            require(error.code in (0, None), 'CLI help failed')
    require('Usage:' in captured.getvalue(), 'CLI help output absent')
    return entries[0].value


def operations(api, warmups, samples, batch_size):
    private, public = api.generate_ed25519_keypair()
    cases = [('key_generation', 0, api.generate_ed25519_keypair)]
    for size in [256, 1024, 4096]:
        payload = b'x' * size
        signature = api.sign_message(private, payload)

        def sign(payload=payload):
            return api.sign_message(private, payload)

        def verify(payload=payload, signature=signature):
            require(api.verify_signature(public, signature, payload) is True, 'Timed verification failed')

        def roundtrip(payload=payload):
            require(api.verify_signature(public, api.sign_message(private, payload), payload) is True, 'Timed roundtrip failed')

        cases.extend([('sign', size, sign), ('verify', size, verify), ('sign_verify', size, roundtrip)])
    document = {'kind': 'synthetic-release-benchmark', 'padding': 'x' * 1024}

    def json_roundtrip():
        require(api.verify_json_signature(public, document, api.sign_json_payload(private, document)) is True, 'Timed JSON roundtrip failed')

    cases.append(('json_sign_verify', len(api.canonicalize_json(document)), json_roundtrip))
    result = []
    for name, size, operation in cases:
        for _ in range(warmups):
            for _ in range(batch_size):
                operation()
        raw = []
        for _ in range(samples):
            start = time.perf_counter_ns()
            for _ in range(batch_size):
                operation()
            raw.append(time.perf_counter_ns() - start)
        result.append({'workload': name, 'payload_bytes': size, 'warmup_batches': warmups,
                       **summary(raw, batch_size)})
    return result


def main():
    request = json.loads(sys.stdin.read())
    data = Path(request['data_directory']).resolve()
    require(data.is_dir() and not any(data.iterdir()), 'Data directory must be precreated and empty')
    probe = Path(request['probe_directory']).resolve()
    require(probe == data.parent / 'probe-tmp' and Path.cwd() == data.parent
            and probe.is_dir() and not any(probe.iterdir()), 'Probe directory must be fresh and owned')
    require(all(os.environ.get(name) == str(probe) for name in ['TMPDIR', 'TEMP', 'TMP']), 'Temporary directory escapes scratch')
    probe_source = None
    distribution = importlib.metadata.distribution('filelock')
    if distribution.version == '3.32.7':
        candidate = Path(distribution.locate_file('filelock/_strict.py')).resolve()
        require(hashlib.sha256(candidate.read_bytes()).hexdigest()
                == '41564e8e8253a0ac0ed146fdaebdbed94afa3f7d604bd6b0ce25410f8dc436df', 'Unreviewed capability-probe source')
        probe_source = candidate
    policy = OfflinePolicy(data, probe, probe_source)
    sys.addaudithook(policy.audit)
    captured = io.StringIO()
    try:
        with contextlib.redirect_stdout(captured), contextlib.redirect_stderr(captured):
            start = time.perf_counter_ns()
            if request['mode'] == 'cli_help':
                require(importlib.metadata.version('attestix') == request['version'], 'CLI distribution mismatch')
                detail = {'entrypoint': cli_help()}
            else:
                api = product_api(request['version'])
                detail = {'namespace': api.__name__}
            import_elapsed = time.perf_counter_ns() - start
            if request['mode'] == 'probe':
                detail['correctness'] = correctness(api)
            elif request['mode'] == 'operations':
                detail['measurements'] = operations(api, request['warmups'], request['samples'], request['batch_size'])
        require(not policy.denied, 'Offline policy was exercised by product code')
        result = {'ok': True, 'version': request['version'], 'mode': request['mode'],
                  'import_or_entrypoint_elapsed_ns': import_elapsed, **detail,
                  'policy': {'network_attempts': 0, 'protected_file_opens': 0,
                             'non_probe_file_writes': 0,
                             'allowed_capability_probe_operations': policy.allowed_probe_operations}}
    except Exception as error:
        trace = []
        frame = error.__traceback__
        while frame is not None:
            code = frame.tb_frame.f_code
            if not code.co_filename.startswith('<'):
                trace.append({'file': Path(code.co_filename).name, 'function': code.co_name, 'line': frame.tb_lineno})
            frame = frame.tb_next
        result = {'ok': False, 'version': request['version'], 'mode': request['mode'],
                  'error_type': type(error).__name__, 'denied_kinds': sorted(set(policy.denied)),
                  'source_frames': trace[:16] + trace[-8:] if len(trace) > 24 else trace}
    sys.stdout.write(json.dumps(result, ensure_ascii=True))


if __name__ == '__main__':
    main()
