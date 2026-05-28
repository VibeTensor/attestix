"""Release-gate tests for the packaged wheel.

Each test in this package guards a known-broken release-blocker from a prior
RC validation (see paper/internal/v0.4.0rc*-rc-validation*.md). They are
deliberately fast: they build the wheel into a tmp dir, unzip its METADATA
and namelist, and assert structural invariants — no venv install required
(see tests/install/test_pip_install_smoke.py for the heavier opt-in venv
install).
"""
