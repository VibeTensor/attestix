"""Offline safety/statistics tests, not benchmark measurements."""
import ast
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

BENCHMARKS = Path(__file__).resolve().parents[1] / 'benchmarks'
sys.path.insert(0, str(BENCHMARKS))
import run_release
import verify_publisher
from worker import BenchmarkError, OfflinePolicy, protected, summary


class BenchmarkContractTests(unittest.TestCase):
    def test_batch_percentile_is_of_batch_means(self):
        value = summary(list(range(1, 101)), operations=10)
        self.assertEqual(value['median_ns_per_operation'], 5.05)
        self.assertEqual(value['p95_ns_per_operation'], 9.5)
        self.assertEqual(value['percentile_scope'], 'batch-average latency')

    def test_empty_samples_fail(self):
        with self.assertRaises(BenchmarkError):
            summary([])

    def test_protected_paths_rejected_before_open(self):
        policy = OfflinePolicy(Path.cwd() / 'synthetic-data')
        for path in ['.env', 'nested/.env.local', 'a.env', 'credentials.json',
                     'x.pem', 'x.key', 'SECURE_VAULT/x', 'client_secret_x.json', '.credentials.ps1',
                     '.signing_key.json', '.aws/credentials', '.azure/accessTokens.json']:
            with self.subTest(path=path), self.assertRaises(BenchmarkError):
                policy.audit('open', (path, 'r', 0))
        self.assertFalse(protected('ordinary.json'))

    def test_network_subprocess_and_key_writes_rejected(self):
        policy = OfflinePolicy(Path.cwd() / 'synthetic-data')
        for event, arguments in [('socket.connect', ()), ('subprocess.Popen', ()),
                                 ('open', ('.signing_key.json', 'w', os.O_WRONLY))]:
            with self.subTest(event=event), self.assertRaises(BenchmarkError):
                policy.audit(event, arguments)

    def test_versions_and_registry_origins_are_not_command_inputs(self):
        with self.assertRaises(RuntimeError):
            run_release.version('0.5.0; bad')
        with patch.object(run_release.urllib.request, 'build_opener', side_effect=AssertionError('Network forbidden')):
            with self.assertRaises(RuntimeError):
                run_release.fetch('https://example.invalid/payload', 1024)

    def test_reviewed_probe_only_allows_owned_literal_operations(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            probe = root / 'probe-tmp'
            policy = OfflinePolicy(root / 'data', probe, root / 'reviewed.py')
            owned = probe / 'tmpabcdefgh'
            with patch.object(policy, 'probe_context', return_value=True), patch.object(policy, 'temporary_context', return_value=True):
                policy.audit('os.mkdir', (str(owned), 0o700, -1))
                policy.audit('open', (str(owned / 'probe-source'), 'w', os.O_WRONLY | os.O_CREAT))
                policy.audit('os.link', (str(owned / 'probe-source'), str(owned / 'probe-link'), -1, -1))
                policy.audit('os.remove', (str(owned / 'probe-link'), -1))
            self.assertEqual(policy.allowed_probe_operations, {'os.mkdir': 1, 'open': 1, 'os.link': 1, 'os.remove': 1})

    def test_probe_never_allows_keys_escape_or_unverified_callers(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            probe = root / 'probe-tmp'
            policy = OfflinePolicy(root / 'data', probe, root / 'reviewed.py')
            owned = probe / 'tmpabcdefgh'
            policy.probe_directories.add(owned)
            with self.assertRaises(BenchmarkError):
                policy.audit('open', (str(owned / 'probe-source'), 'w', os.O_WRONLY))
            with patch.object(policy, 'probe_context', return_value=True), patch.object(policy, 'temporary_context', return_value=True):
                for target in [owned / '.signing_key.json', owned / '.env', root / 'outside', owned / 'other']:
                    with self.subTest(target=target), self.assertRaises(BenchmarkError):
                        policy.audit('open', (str(target), 'w', os.O_WRONLY))
                with self.assertRaises(BenchmarkError):
                    policy.audit('os.link', (str(owned / 'probe-source'), str(root / 'escape'), -1, -1))

    def test_only_typed_source_json_is_accepted(self):
        record = {'release_tag': 'v0.5.0', 'source_sha': 'a' * 40, 'source_event': 'release'}
        def archive(name, body):
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, 'w') as stream:
                stream.writestr(name, json.dumps(body))
            return buffer.getvalue()
        self.assertEqual(verify_publisher.source_record(archive('release-source.json', record)), record)
        for name, body in [('.env', record), ('release-source.json', {**record, 'executable': 'bad'}),
                           ('release-source.json', {**record, 'source_sha': 'main'})]:
            with self.subTest(name=name), self.assertRaises(RuntimeError):
                verify_publisher.source_record(archive(name, body))

    def test_registry_urls_reject_ambiguous_authorities_and_paths(self):
        urls = ['https://user@pypi.org/pypi/attestix/0.5.0/json',
                'https://pypi.org:443/pypi/attestix/0.5.0/json',
                'https://pypi.org/pypi/attestix/0.5.0/json?x=1',
                'https://pypi.org/pypi/attestix/0.5.0/json#fragment',
                'https://files.pythonhosted.org/other/file.whl',
                'https://files.pythonhosted.org/packages/../file.whl']
        with patch.object(run_release.urllib.request, 'build_opener', side_effect=AssertionError('Network forbidden')):
            for url in urls:
                with self.subTest(url=url), self.assertRaises(RuntimeError):
                    run_release.fetch(url, 1024)

    def test_runtime_gates_do_not_use_optimizable_asserts(self):
        for name in ['worker.py', 'run_release.py', 'verify_publisher.py']:
            tree = ast.parse((BENCHMARKS / name).read_text())
            self.assertFalse(any(isinstance(node, ast.Assert) for node in ast.walk(tree)), name)


if __name__ == '__main__':
    unittest.main()
