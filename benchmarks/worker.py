"""Isolated, memory-only installed-product workloads; emits no key material."""
import contextlib
import importlib
import importlib.metadata
import inspect
import io
import json
import math
import os
from pathlib import Path
import sys
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
        or name in {'credentials.json', '.credentials.ps1'}
        or name.startswith('client_secret_') and name.endswith('.json')
        or any(part.lower() == 'secure_vault' for part in item.parts)
    )


class OfflinePolicy:
    def __init__(self, data_directory):
        self.data_directory = Path(data_directory).resolve()
        self.denied = []

    def deny(self, kind):
        self.denied.append(kind)
        raise BenchmarkError('Offline policy rejected ' + kind)

    def audit(self, event, args):
        if event.startswith('socket.') or event in {'subprocess.Popen', 'os.system', 'os.posix_spawn', 'os.fork'}:
            self.deny('network-or-subprocess')
        if event == 'open':
            path, mode, flags = args
            if protected(path):
                self.deny('protected-file-read')
            if isinstance(mode, str) and any(letter in mode for letter in 'wax+'):
                self.deny('file-write')
            if isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
                self.deny('file-write')
        if event == 'os.mkdir':
            if Path(os.fsdecode(args[0])).resolve() != self.data_directory:
                self.deny('directory-write')
        if event in {'os.remove', 'os.rename', 'os.rmdir', 'os.link', 'os.symlink'}:
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


def product_api(version):
    require(importlib.metadata.version('attestix') == version, 'Installed distribution version mismatch')
    module = importlib.import_module('attestix.auth.crypto')
    site = Path(importlib.metadata.distribution('attestix').locate_file('')).resolve()
    require(Path(module.__file__).resolve().is_relative_to(site), 'Source-tree import rejected')
    expected = {'generate_ed25519_keypair': [], 'sign_message': ['private_key', 'message'],
                'verify_signature': ['public_key', 'signature', 'message']}
    for name, parameters in expected.items():
        require(list(inspect.signature(getattr(module, name)).parameters) == parameters, 'Public API signature mismatch')
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
    policy = OfflinePolicy(data)
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
                  'policy': {'network_attempts': 0, 'protected_file_opens': 0, 'file_writes': 0}}
    except Exception as error:
        result = {'ok': False, 'version': request['version'], 'mode': request['mode'],
                  'error_type': type(error).__name__, 'denied_kinds': sorted(set(policy.denied))}
    sys.stdout.write(json.dumps(result, ensure_ascii=True))


if __name__ == '__main__':
    main()
