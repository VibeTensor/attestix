# Scorecard Pinned-Dependencies — coverage and accepted gaps

This document records, per file, how the Attestix repo handles OpenSSF Scorecard's
`Pinned-Dependencies` check (probe id: `PinnedDependenciesID`). Scorecard reports
the same finding type via two facets in the SARIF output:

- `containerImage not pinned by hash` — any `FROM <image>:<tag>` without a `@sha256:` digest.
- `pipCommand not pinned by hash` — any `pip install <package>` (or `pip install -e .`) that does not pass `--require-hashes -r <lockfile>`.

The first category is fully resolved. The second category is partially resolved
and the gaps are documented below so reviewers can audit the trade-off without
re-deriving it from the SARIF output.

## Fully resolved (containerImage, SHA-pinned)

| File | Base image | Pin |
| --- | --- | --- |
| `Dockerfile` | `python:3.12-slim` | `@sha256:090ba77e2958f6af52a5341f788b50b032dd4ca28377d2893dcf1ecbdfdfe203` |
| `Dockerfile.test` | `python:3.12-slim` | `@sha256:090ba77e2958f6af52a5341f788b50b032dd4ca28377d2893dcf1ecbdfdfe203` |

Digest source: the SHA recommended by Scorecard's own hint for `python:3.12-slim`,
verified pullable via `docker manifest inspect` on 2026-05-28. The digest is
refreshed weekly by Dependabot's `docker` ecosystem entry in
`.github/dependabot.yml`.

## Fully resolved (pipCommand, hash-pinned via `--require-hashes`)

| Workflow | Strategy |
| --- | --- |
| `.github/workflows/test.yml` | `pip install --require-hashes -r requirements-ci.txt` followed by `pip install -e . --no-deps`. `requirements-ci.txt` is generated from `pyproject.toml` + `requirements-api.txt` with `pip-compile --generate-hashes` and refreshed weekly by Dependabot's `pip` ecosystem entry. |

`test.yml` is the most security-critical workflow (it imports application code,
runs the full pytest matrix across Python 3.11/3.12/3.13 × Ubuntu/Windows, and
ships coverage to Codecov), so it gets the full lockfile treatment. The
verification run on 2026-05-28 passed all 525 tests against the hash-pinned
environment.

## Accepted gap (pipCommand, NOT hash-pinned)

The following workflows still use unpinned `pip install <package>` invocations.
Each is listed explicitly so the exclusion is per-file, not blanket. The
accepted-risk rationale is identical for all of them:

1. The install set is tiny (1–3 packages) compared to `test.yml`'s 127-package
   transitive closure, so the marginal supply-chain attack surface is small.
2. Each package floor in these workflows is already version-bounded (lower
   floor with CVE-driven justification in `pyproject.toml`, where applicable).
3. `pip-audit` runs on every PR and weekly (see `.github/workflows/security.yml`),
   so any known-CVE in these transitive deps is caught regardless of pinning.
4. Maintaining a separate hash-pinned lockfile per workflow (each with its own
   Python version + install profile) is not worth the maintenance cost while
   the dep set stays this small.

| File | Lines (approx) | Unpinned install(s) | Notes |
| --- | --- | --- | --- |
| `.github/workflows/lint.yml` | 35, 60-61 | `ruff>=0.6.0`; `pip install -e ".[dev,blockchain]"` for the advisory mypy job | mypy job is `continue-on-error`-style (`|| true`) — failure here is not gating. |
| `.github/workflows/security.yml` | 37-39, 71-72, 94-95 | `pip-audit>=2.7`, `bandit[toml]>=1.7`, `safety>=3.2`, plus `pip install -e ".[blockchain]"` for the pip-audit job | These tools' own job is to scan dependencies — installing them via the same hash-pinned lockfile they're auditing creates a chicken-and-egg dependency that defeats the audit. |
| `.github/workflows/sbom.yml` | 38-40 | `cyclonedx-bom>=5.0.0,<6.0.0`, plus `pip install -e ".[blockchain]"` | The SBOM must reflect the *real* installed environment a user gets from `pip install attestix[blockchain]`, not a hash-pinned-CI-only environment. Hash-pinning would falsify the SBOM. |
| `.github/workflows/publish.yml` | 22-23 | `build` | Triggered only on `release: published`; secrets-scoped to PYPI_API_TOKEN; runs once per release. |
| `.github/workflows/docs.yml` | 32 | `mkdocs-material` | Build-only workflow that emits a static site; no application code paths involved. |

## Refresh discipline

- Lockfile (`requirements-ci.txt`) regeneration: weekly via Dependabot. If a CVE
  fix lands and Dependabot is slow, regenerate manually with:
  ```
  python -m piptools compile --generate-hashes --strip-extras \
    --extra dev --extra blockchain \
    --output-file requirements-ci.txt pyproject.toml requirements-api.txt
  ```
- Docker digest refresh: weekly via Dependabot's `docker` ecosystem entry.

## Re-audit trigger

Open this file as soon as Scorecard's `Pinned-Dependencies` score on `main`
shifts away from the post-2026-05-28 baseline. If the next attempt to close
the gap finds the install set in one of the workflows above has grown beyond
~5 packages (or starts pulling in security-sensitive transitive deps),
upgrade that workflow to Option A (per-workflow lockfile).
