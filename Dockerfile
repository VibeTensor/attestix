# Pinned by SHA digest to satisfy OpenSSF Scorecard's Pinned-Dependencies check
# (PinnedDependenciesID: containerImage not pinned by hash).
# Digest source: Scorecard's recommended SHA for python:3.12-slim, verified
# pullable via `docker manifest inspect python@sha256:090ba77e...` on
# 2026-05-28. Dependabot's docker ecosystem (configured in .github/
# dependabot.yml) refreshes the digest when a newer python:3.12-slim is
# published. See .github/scorecard-pinned-deps.md for the coverage matrix.
FROM python:3.14-slim@sha256:c845af9399020c7e562969a13689e929074a10fd057acd1b1fad06a2fb068e97

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first for layer caching
COPY requirements.txt requirements-api.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt -r requirements-api.txt

# Copy application code
COPY . .

# Cloud Run default port
ENV PORT=8080
EXPOSE 8080

# Drop root: run as a dedicated unprivileged user (UID 10001, primary group root
# so the image stays compatible with arbitrary-UID platforms like OpenShift).
# Fixes trivy DS002 + semgrep dockerfile.security.missing-user.missing-user (#71).
RUN useradd -r -u 10001 -g root attestix && chown -R attestix:root /app
USER attestix

# Liveness probe via stdlib urllib (no curl in the slim base image, no new deps).
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0) if urllib.request.urlopen('http://localhost:8080/health').status == 200 else sys.exit(1)" || exit 1

# Run the API server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
