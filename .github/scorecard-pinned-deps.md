# Scorecard Pinned-Dependencies — coverage and accepted gaps

This document records, per file, how the Attestix repo handles OpenSSF Scorecard's
`Pinned-Dependencies` check (probe id: `PinnedDependenciesID`). Scorecard reports
the same finding type via two facets in the SARIF output:

- `containerImage not pinned by hash` — any `FROM <image>:<tag>` without a `@sha256:` digest.
- `pipCommand not pinned by hash` — any `pip install <package>` (or `pip install -e .`) that does not pass `--require-hashes -r <lockfile>`.

Both categories are fully resolved; the per-file strategy is recorded below.

## Fully resolved (containerImage, SHA-pinned)

| File | Base image | Pin |
| --- | --- | --- |
| `Dockerfile` | `python:3.12-slim` | `@sha256:090ba77e2958f6af52a5341f788b50b032dd4ca28377d2893dcf1ecbdfdfe203` |
| `Dockerfile.test` | `python:3.12-slim` | `@sha256:090ba77e2958f6af52a5341f788b50b032dd4ca28377d2893dcf1ecbdfdfe203` |

Digest source: the SHA recommended by Scorecard's own hint for `python:3.12-slim`,
verified pullable via `docker manifest inspect` on 2026-05-28. The digest is
refreshed weekly by Dependabot's `docker` ecosystem entry in
`.github/dependabot.yml`.

## Fully resolved (pipCommand / npmCommand, hash-pinned)

Every `pip install` in the repo now runs `--require-hashes -r <lockfile>`; the
package itself is installed afterwards with `pip install -e . --no-deps`, which
Scorecard does not flag. Three lockfiles, all generated with
`pip-compile --generate-hashes` and refreshed weekly by Dependabot's `pip`
ecosystem entry:

| Lockfile | Source | Used by |
| --- | --- | --- |
| `requirements-ci.txt` | `pyproject.toml` extras `dev,blockchain,security` + `requirements-api.txt` | `test.yml`, `lint.yml`, `security.yml`, `publish.yml`, `Dockerfile.test` |
| `requirements-runtime.txt` | `pyproject.toml` extras `api,blockchain,sbom` | `sbom.yml`, `Dockerfile` |
| `requirements-docs.txt` | `requirements-docs.in` (`mkdocs-material`) | `docs.yml` |

`website.yml` uses `npm ci` (lockfile-only install), which Scorecard treats as pinned.

Known ceiling: `requirements-runtime.txt` and `requirements-docs.txt` are
compiled on Windows with `--strip-extras`, so Linux-only optional wheels such
as `uvloop` are not in the runtime lock; uvicorn falls back to the asyncio loop
in the container. Regenerate inside `python:3.12-slim` if that matters.

## Refresh discipline

- Lockfile regeneration: weekly via Dependabot. If a CVE fix lands and
  Dependabot is slow, regenerate manually with:
  ```
  python -m piptools compile --generate-hashes --strip-extras     --extra dev --extra blockchain --extra security     --output-file requirements-ci.txt pyproject.toml requirements-api.txt
  python -m piptools compile --generate-hashes --strip-extras     --extra api --extra blockchain --extra sbom     --output-file requirements-runtime.txt pyproject.toml
  python -m piptools compile --generate-hashes     --output-file requirements-docs.txt requirements-docs.in
  ```
- Docker digest refresh: weekly via Dependabot's `docker` ecosystem entry.

## Re-audit trigger

Open this file as soon as Scorecard's `Pinned-Dependencies` score on `main`
drops: it means a new unpinned `pip install` / `npm install` landed, or a
lockfile stopped being used by the workflow it was created for.
