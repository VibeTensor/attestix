# Configuration

Attestix is configured via environment variables. No config file is needed for basic usage.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ATTESTIX_DATA_DIR` | No | Same directory as `main.py` | Directory for JSON storage files |
| `ATTESTIX_KEY_FILE` | No | `.signing_key.json` | Path to Ed25519 signing key file |
| `BASE_RPC_URL` | For blockchain | - | Base L2 RPC endpoint (e.g., `https://sepolia.base.org`) |
| `BASE_WALLET_KEY` | For blockchain | - | Private key for blockchain transactions (hex string, no `0x` prefix) |
| `EAS_CONTRACT` | For blockchain | Sepolia default | Ethereum Attestation Service contract address |
| `ATTESTIX_LOG_LEVEL` | No | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

## Setting Environment Variables

=== "Linux/macOS"

    ```bash
    export ATTESTIX_DATA_DIR=/var/lib/attestix
    export ATTESTIX_LOG_LEVEL=DEBUG
    python main.py
    ```

=== "Windows"

    ```powershell
    $env:ATTESTIX_DATA_DIR = "C:\attestix-data"
    $env:ATTESTIX_LOG_LEVEL = "DEBUG"
    python main.py
    ```

=== ".env file"

    Create a `.env` file in the Attestix directory:

    ```
    ATTESTIX_DATA_DIR=/var/lib/attestix
    ATTESTIX_LOG_LEVEL=DEBUG
    ```

    Attestix uses `python-dotenv` and loads `.env` automatically.

## Storage Configuration

By default, Attestix stores all data in JSON files alongside `main.py`:

```
attestix/
  main.py
  identities.json        # Created on first identity creation
  credentials.json       # Created on first credential issuance
  compliance.json        # Created on first compliance profile
  provenance.json        # Created on first provenance record
  reputation.json        # Created on first interaction recording
  delegations.json       # Created on first delegation
  .signing_key.json      # Created on first run (DO NOT SHARE)
  .keypairs.json         # Created on first DID key generation (DO NOT SHARE)
```

To use a custom directory:

```bash
export ATTESTIX_DATA_DIR=/var/lib/attestix
```

All JSON files will be created in that directory instead.

## Signing Key Management

On first run, Attestix generates an Ed25519 keypair and stores it in `.signing_key.json`. This key is used to sign every UAIT, credential, compliance record, and audit entry.

**Important:** Back up `.signing_key.json` securely. If you lose it, you cannot create new artifacts that chain to the same DID.

To use a specific key file:

```bash
export ATTESTIX_KEY_FILE=/secure/path/attestix-key.json
```

## Blockchain Configuration

Blockchain anchoring is optional. To enable it, you need a funded wallet on Base L2.

### Base Sepolia (Testnet)

```bash
export BASE_RPC_URL=https://sepolia.base.org
export BASE_WALLET_KEY=your_private_key_hex_no_0x_prefix
```

### Base Mainnet

```bash
export BASE_RPC_URL=https://mainnet.base.org
export BASE_WALLET_KEY=your_private_key_hex_no_0x_prefix
```

!!! warning "Wallet Security"
    The `BASE_WALLET_KEY` is a private key that controls funds. Never commit it to version control. Use environment variables or a secrets manager.

### Gas Estimation

Use `estimate_anchor_cost` to check costs before anchoring:

```
estimate_anchor_cost(artifact_type="identity")
```

Returns estimated gas in ETH at current gas prices.

## MCP Client Configuration

### Claude Code

Add to `~/.claude.json` (macOS/Linux) or `%USERPROFILE%\.claude.json` (Windows):

```json
{
  "mcpServers": {
    "attestix": {
      "type": "stdio",
      "command": "python",
      "args": ["/absolute/path/to/attestix/main.py"]
    }
  }
}
```

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "attestix": {
      "command": "python",
      "args": ["/absolute/path/to/attestix/main.py"]
    }
  }
}
```

### Any MCP Client

Attestix communicates over stdio using the MCP protocol. Start the server with:

```bash
python main.py
```

Connect your MCP client to the process's stdin/stdout.

## Multi-Instance Setup

To share data across multiple Attestix instances (e.g., development and staging):

1. Set `ATTESTIX_DATA_DIR` to a shared directory
2. Copy `.signing_key.json` to the shared directory
3. Each instance reads/writes the same JSON files with file locking

```bash
# Instance 1
export ATTESTIX_DATA_DIR=/shared/attestix
python main.py

# Instance 2 (different process or machine with shared filesystem)
export ATTESTIX_DATA_DIR=/shared/attestix
python main.py
```

## Docker

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
ENV ATTESTIX_DATA_DIR=/data
VOLUME /data
CMD ["python", "main.py"]
```

```bash
docker build -t attestix .
docker run -v attestix-data:/data attestix
```
