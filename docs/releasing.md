# Python release procedure

Assignee: Release maintainer
Status: Required gates for the next release
Priority: High
Due: Before publishing

1. Merge the reviewed release PR only after the full test matrix, security checks,
   documentation builds and package installation check pass. Confirm the intended
   version in `pyproject.toml`, `attestix/__init__.py` and `server.json` agrees.
2. Check that the version is absent on PyPI. Never reuse a published version for
   different bytes. Python 0.4.3 is already published; this source prepares 0.5.0.
3. Create the matching stable tag, such as `v0.5.0`, on the reviewed main commit
   and publish its GitHub release. A recovery dispatch of `Publish to PyPI` must
   run from main and supply that existing `release_tag`.
4. The publisher checks tag ancestry, metadata and registry absence, then builds
   with hash-locked tools and validates exactly one wheel and source distribution.
   It preserves the existing PyPI environment and authentication configuration;
   an empty API token selects already-configured trusted publishing. Do not put
   credentials in source or workflow inputs.
5. Require the post-publication job to match registry and downloaded SHA-256
   hashes against the validated artifacts, then pass an installed-wheel smoke
   test outside the checkout. If publishing partially succeeds, inspect registry
   files before any retry; duplicate files deliberately fail rather than skip.
6. Confirm the successful publisher triggers the SBOM workflow using the exact
   upstream run metadata and selected tag commit. Release events attach the SBOM
   to that release; manual publisher dispatches retain workflow artifacts and
   skip attachment. Existing release evidence is never overwritten automatically.
7. Dispatch `Publish to MCP Registry` from main only after the exact Python
   release is available, non-yanked and has the expected compatibility metadata.
   The workflow retains its existing GitHub OIDC authentication.

Notes: SDK and offline-verifier releases have independent version schedules.
Package publication does not establish legal compliance or production readiness.
