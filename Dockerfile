# Pinned by SHA digest to satisfy OpenSSF Scorecard's Pinned-Dependencies check
# (PinnedDependenciesID: containerImage not pinned by hash).
# Digest source: Scorecard's recommended SHA for python:3.12-slim, verified
# pullable via `docker manifest inspect python@sha256:090ba77e...` on
# 2026-05-28. Dependabot's docker ecosystem (configured in .github/
# dependabot.yml) refreshes the digest when a newer python:3.12-slim is
# published. See .github/scorecard-pinned-deps.md for the coverage matrix.
FROM python:3.12-slim@sha256:090ba77e2958f6af52a5341f788b50b032dd4ca28377d2893dcf1ecbdfdfe203

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

# Run the API server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
