#!/bin/bash
set -euxo pipefail

exec > /tmp/attestix-test.log 2>&1

echo "=== Attestix Test Runner on EC2 ==="
echo "Start time: $(date -u)"

# Install Python 3.12
dnf install -y python3.12 python3.12-pip tar gzip

# Download project from S3
aws s3 cp s3://attestix-test-runner-tmp/attestix-test.tar.gz /tmp/attestix-test.tar.gz
mkdir -p /tmp/attestix && cd /tmp/attestix
tar xzf /tmp/attestix-test.tar.gz

# Install dependencies
python3.12 -m pip install -e ".[test,blockchain]" 2>&1

echo ""
echo "=========================================="
echo "  RUNNING FULL TEST SUITE"
echo "=========================================="
echo ""

# Run full test suite with verbose output
python3.12 -m pytest tests/ -v --tb=long -m "not live_blockchain" --color=no 2>&1 | tee /tmp/test-results.txt
TEST_EXIT=$?

echo ""
echo "=========================================="
echo "  TEST SUITE COMPLETE - Exit code: $TEST_EXIT"
echo "=========================================="
echo ""

# Also run the comprehensive validation test separately for detailed output
echo "=== Running comprehensive E2E validation ==="
python3.12 -m pytest tests/e2e/test_full_validation.py -v --tb=long --color=no 2>&1 | tee -a /tmp/test-results.txt

echo ""
echo "=== Running examples (smoke test) ==="
cd /tmp/attestix
for example in examples/0*.py; do
    echo "--- Running $example ---"
    timeout 30 python3.12 "$example" 2>&1 || echo "FAILED: $example (exit $?)"
    echo ""
done | tee /tmp/example-results.txt

echo "End time: $(date -u)"

# Upload results to S3
aws s3 cp /tmp/test-results.txt s3://attestix-test-runner-tmp/test-results.txt
aws s3 cp /tmp/example-results.txt s3://attestix-test-runner-tmp/example-results.txt 2>/dev/null || true
aws s3 cp /tmp/attestix-test.log s3://attestix-test-runner-tmp/full-log.txt

# Signal completion
echo "ATTESTIX_TESTS_COMPLETE" > /tmp/done.txt
aws s3 cp /tmp/done.txt s3://attestix-test-runner-tmp/done.txt

# Self-terminate
shutdown -h now
