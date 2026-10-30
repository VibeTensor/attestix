"""Regenerate provider-free callback test locks without installing frameworks."""

from pathlib import Path
import subprocess
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]
project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
requirements = project["dependencies"] + project["optional-dependencies"]["test"]
requirements += project["optional-dependencies"]["security"]
requirements += ["setuptools>=84.2.1,<85", "wheel>=0.48.0,<0.49"]
output = ROOT / ".github" / "requirements"
output.mkdir(exist_ok=True)

for profile, core in [("minimum", "1.4.6"), ("current", "1.7.3")]:
    with tempfile.TemporaryDirectory() as temporary:
        source = Path(temporary) / "candidate.in"
        source.write_text("\n".join(requirements + [f"langchain-core=={core}"]) + "\n", encoding="ascii")
        subprocess.run([
            "uv", "pip", "compile", str(source), "--universal",
            "--python-version", "3.11", "--only-binary", ":all:",
            "--generate-hashes", "--no-header", "--no-annotate", "--quiet",
            "-o", str(output / f"langchain-{profile}.txt"),
        ], check=True, timeout=180)
