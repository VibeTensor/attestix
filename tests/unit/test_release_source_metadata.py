"""Reject hostile upstream selectors before downstream repository checkout."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize('override,valid', [({}, True),
                                         ({'release_tag': 'v0.4.3\nsource_sha=bad'}, False),
                                         ({'release_tag': 'main'}, False),
                                         ({'source_sha': 'not-a-commit'}, False),
                                         ({'source_event': 'pull_request'}, False),
                                         ({'extra': 'unexpected'}, False)])
def test_upstream_selector_is_validated_before_outputs(tmp_path, override, valid):
    workflow = yaml.safe_load((ROOT / '.github/workflows/sbom.yml').read_text())
    step = next(step for step in workflow['jobs']['cyclonedx']['steps'] if step.get('id') == 'release-source')
    script = step['run'].split('\n', 1)[1].rsplit('\nPY', 1)[0]
    directory = tmp_path / 'release-source'
    directory.mkdir()
    record = {'release_tag': 'v0.4.3', 'source_sha': '1' * 40, 'source_event': 'workflow_dispatch', **override}
    (directory / 'release-source.json').write_text(json.dumps(record))
    output = tmp_path / 'outputs'
    env = {key: value for key, value in os.environ.items() if key.upper() in {'SYSTEMROOT', 'WINDIR', 'TEMP', 'TMP'}}
    env.update(RUNNER_TEMP=str(tmp_path), GITHUB_OUTPUT=str(output), SOURCE_EVENT='workflow_dispatch')
    result = subprocess.run([sys.executable, '-I', '-c', script], env=env, capture_output=True, text=True, timeout=10)
    assert (result.returncode == 0) == valid
    if valid:
        assert dict(line.split('=', 1) for line in output.read_text().splitlines()) == record
    else:
        assert not output.exists()
