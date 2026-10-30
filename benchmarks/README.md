# Installed-release benchmark evidence

This comparison runs actual published `attestix` wheels, not the checkout's
product implementation. The initial pair is 0.4.3 and 0.5.0 on one Python 3.12
Ubuntu runner. Registry hashes and fully hashed dependency locks are recorded.
The fixed 0.4.3 baseline is selected explicitly; it is not an automatically
discovered previous release.
Different supported dependency versions are part of the release comparison;
results do not isolate a single code change's causal effect.

## Recorded 0.5.0 comparison

The [2026-10-30 standard-runner run](https://github.com/VibeTensor/attestix/actions/runs/41106422757)
produced [raw evidence artifact 13001158240](https://github.com/VibeTensor/attestix/actions/runs/41106422757/artifacts/13001158240)
from harness head `1f3e67bf25acf60dd40ea49e883ad5ca472bd24c` (executed PR merge
`7691b6193214e45385e9e8e18ba67b451773c462`). Both actual installed wheels passed
all seven correctness checks before timing. The runner used CPython 3.12.15 on
Ubuntu 24.04 with four logical CPUs. The artifact retains all 30 workload rows,
raw samples and resolved dependency hashes; its archive SHA256 is
`26f6eb02f666b7cd7c8f744a7ca3519692df47bb5b821d04daa217a4d23c47d6`.

| Workload | 0.4.3 median ms | 0.4.3 p95 ms | 0.5.0 median ms | 0.5.0 p95 ms | p95 scope |
| --- | --- | --- | --- | --- | --- |
| Crypto import, fresh process | 312.376 | 324.482 | 289.077 | 298.685 | Process invocation |
| CLI help, fresh process | 312.609 | 318.972 | 290.451 | 296.931 | Process invocation |
| Sign + verify, 1024 bytes | 0.157188 | 0.158445 | 0.157464 | 0.158555 | Batch-average operation |
| Custom JSON sign + verify, 1075 bytes | 0.180497 | 0.182809 | 0.181140 | 0.182786 | Batch-average operation |

Startup uses 30 observations per release/mode after three warmups. Crypto cases
use 100 measured batches of 100 operations after the warmups described below.
These are observations of each product plus its resolved dependencies on one
runner, not an SLA, a code-only attribution or evidence that all integrations ran.
The reviewed baseline dependency's benign temporary capability probe is included.
The Actions artifact has a 90-day retention period; this link is not a permanent
release attachment.

## Workloads and gates

Both installed canonical `attestix.auth.crypto` APIs must first pass separate
import, distribution-version, module-origin and all seven API-signature
compatibility gates. They must then pass seven correctness checks before timing:
valid signature verification, tampered-message rejection, wrong-key rejection,
malformed-signature rejection, DID derivation, custom Attestix canonical-JSON
roundtrip verification and tampered-JSON rejection.
Keys exist only in worker memory. No signing-key loader or storage-backed service
fixture is invoked. Workers reject network/subprocess activity, protected-file
opens and arbitrary file writes. The exact hash-reviewed filelock3.32.7 import
capability probe may create only its known temporary discovery/source/link files
inside fresh worker-owned scratch storage, then clean them up. Its allowed
operations are recorded separately; the comparison does not claim zero filesystem
writes. All key writes remain blocked. These Python audit hooks are not an OS
security sandbox.

- Fresh-process crypto import and installed CLI entry-point `--help`: 3 warmups
  and 30 samples per version, deterministic alternating order. CLI comparison
  is included only when both entry points pass offline gates. Process timings
  include common harness/guard overhead; inside-process timings are separate
  and include installed-distribution/API identity checks alongside the import.
  These are warm-filesystem observations, not machine-cold or MCP-ready latency.
- Key generation; sign, verify and sign+verify for 256, 1024 and 4096 bytes;
  custom canonical-JSON sign+verify: 10 alternating blocks per version, 5 warmup
  batches per block, then 10 measured batches of 100 operations per case.
  This yields 100 measured batch-average samples. The reported crypto p95 is
  the p95 of batch-average latency, never individual-operation tail latency.

No timing threshold gates a release. Correctness, identity, missing samples and
offline-policy violations fail explicitly. Raw elapsed samples, medians, p95,
artifact/dependency hashes, host/runtime metadata and exclusions are retained.
No key, signature, credential payload or customer data is included in evidence.

## Reproduce

For complete reference evidence, use the [release-evidence workflow](https://github.com/VibeTensor/attestix/blob/main/.github/workflows/release-evidence.yml)
after it is merged to main. Its manual inputs select the verified publisher run,
candidate and fixed comparison baseline. It validates and retains `publisher.json`
and records the executed harness revision in `result.json` automatically. Own-repo
PR runs exercise the same contract before merge.

The following local commands are exploratory only. They do not verify or retain
publisher evidence, and outside Actions they do not record a harness source SHA.
Their output alone does not satisfy the complete reference evidence contract.

```sh
python -m unittest discover -s tests -p test_release_benchmark_harness.py
python benchmarks/run_release.py prepare --baseline 0.4.3 --candidate 0.5.0 --output /new/empty/evidence-path
python benchmarks/run_release.py run --output /new/empty/evidence-path --startup-samples 30
```

The prepare phase uses public PyPI for artifact/dependency setup. Timed workers
do not use external product APIs. The workflow verifies the successful publisher
run and its small typed source record; it never checks out producer source or
executes artifact scripts. PR runs use the verified 0.5.0 publisher run. Manual
and successful-publication runs reuse the same harness on trusted main code.

Actions evidence is retained for 90 days; it is not a permanent release asset.
Any release-asset attachment requires a separate reviewed write-permission job.
This workflow has no release/package publication or deployment permission.

## Evidence contract and coverage

`result.json` is the machine-readable record; `summary.md` is an observed-results
table. Store `setup.json`, both `.lock` files and `publisher.json` with them.
Consumers must keep source/artifact identities, runtime, raw samples, operation
counts, percentile scope, correctness and exclusions together. Never compare
different runner reports as though they were a controlled same-host experiment.

This minimal contract covers offline crypto and conditional CLI help only.
VC persistence, audit-chain timing, Merkle inclusion proofs, on-chain throughput,
cloud/API/model/payment workflows and SDK examples are not measured here.
The older pytest timing suite uses service fixtures and is not a substitute for
an installed-release/environment/raw-sample report; `-s` shows its captured prints.
Private-product evidence must remain in its own private repository/store, even
when reusing this contract.
