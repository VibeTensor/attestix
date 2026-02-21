# Research Paper

Attestix is described in a peer-reviewed research paper that covers the system architecture, cryptographic pipeline, EU AI Act compliance automation, and evaluation results.

## Paper

**Attestix: A Unified Attestation Infrastructure for Autonomous AI Agents**

Pavan Kumar Dubasi (VibeTensor Private Limited)

> The rapid proliferation of autonomous AI agents operating across organizational boundaries introduces fundamental challenges in identity verification, trust establishment, and regulatory compliance. We present Attestix, an open-source attestation infrastructure that provides a unified trust layer for AI agents through nine integrated modules. Attestix is implemented as a Model Context Protocol (MCP) server exposing 47 tools, validated by 284 automated tests including 91 conformance benchmarks against RFC 8032, W3C VC/DID, and UCAN specifications.

**Links:**

- [PDF (GitHub)](https://github.com/VibeTensor/attestix/blob/main/paper/attestix-paper.pdf)
- [LaTeX source](https://github.com/VibeTensor/attestix/blob/main/paper/attestix-paper.tex)

---

## Citing Attestix

If you use Attestix in your research, please cite:

### BibTeX

```bibtex
@article{dubasi2026attestix,
  title     = {Attestix: A Unified Attestation Infrastructure for Autonomous AI Agents},
  author    = {Dubasi, Pavan Kumar},
  year      = {2026},
  url       = {https://github.com/VibeTensor/attestix},
  note      = {Open-source. Apache License 2.0}
}
```

### APA

Dubasi, P. K. (2026). Attestix: A Unified Attestation Infrastructure for Autonomous AI Agents. VibeTensor Private Limited. https://github.com/VibeTensor/attestix

### IEEE

P. K. Dubasi, "Attestix: A Unified Attestation Infrastructure for Autonomous AI Agents," VibeTensor, 2026. [Online]. Available: https://github.com/VibeTensor/attestix

---

## Key Contributions

The paper presents four main contributions:

1. **Unified attestation architecture** integrating DID-based identity, W3C Verifiable Credentials, UCAN delegation, reputation scoring, EU AI Act compliance, provenance tracking, and blockchain anchoring into a single framework.

2. **Compliance automation engine** implementing Articles 5, 9-15, 43, 72-73, and Annex V of the EU AI Act, including automated risk classification, conformity assessment enforcement, and declaration generation.

3. **Open-source MCP implementation** with 47 tools validated by 284 automated tests (91 conformance benchmarks against RFC 8032, W3C VC, W3C DID, and UCAN specifications).

4. **Tamper-evident audit mechanism** combining SHA-256 hash-chained logs with Merkle tree aggregation and on-chain anchoring via the Ethereum Attestation Service on Base L2.

---

## Evaluation Highlights

### Standards Conformance (91 benchmarks)

| Standard | What is validated | Tests |
|----------|------------------|:-----:|
| RFC 8032 Section 7.1 | 4 IETF Ed25519 canonical vectors | 18 |
| W3C VC Data Model 1.1 | Credential structure, proof, presentations | 24 |
| W3C DID Core 1.0 | did:key/web structure, roundtrip resolution | 16 |
| UCAN v0.9.0 | JWT header, payload, attenuation, revocation | 16 |
| MCP Protocol | 47 tools, 9 modules, async, naming | 5 |
| Performance | Latency thresholds | 7 |

### Performance (median, Docker)

| Operation | Latency |
|-----------|---------|
| Ed25519 key generation | 0.08 ms |
| JSON canonicalization | 0.02 ms |
| Ed25519 sign + verify | 0.28 ms |
| Identity creation | ~14 ms |
| Credential issuance | ~17 ms |
| Credential verification | ~2 ms |

---

## Related Work

The paper discusses Attestix in relation to:

- Agent infrastructure frameworks (Chan et al., 2025)
- W3C Verifiable Credentials and DIDs
- UCAN authorization (Fission, 2023)
- EU AI Act (Regulation 2024/1689)
- Ethereum Attestation Service
- Google A2A and Anthropic MCP protocols
- Exponential decay reputation models
