"use client";

import type { ConsoleAgent } from "@/lib/atx-console-data";
import { AtxIcon } from "@/components/atx/atx-icons";

export function AnchorsPane() {
  const fallback: ConsoleAgent = {
    id: "attestix:f9bdb7a94ccb40f1",
    did: "did:web:vibetensor.com",
    name: "org-wide",
    displayName: "Organisation-wide anchors",
    issuer: "VibeTensor",
    protocol: "manual",
    capabilities: [],
    risk: "high",
    status: "compl",
    trust: 0.94,
    interactions: 0,
    created: "",
    expiry: "",
    description: "",
    anchored: true,
    anchorTxn:
      "0x8f2e4c9b1a0f7e3d5b8c2a9e7f6d4b1a8c5e2d9f7a3b6c0e4d8f1a5b9c2e7d3f",
    credentials: 0,
    delegations: 0,
  };
  return (
    <div>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="font-serif text-[32px] leading-none text-atx-ink">
            Blockchain anchors
          </h2>
          <div className="mt-1 font-mono-atx text-[11px] uppercase tracking-[0.06em] text-atx-ink-dim">
            Base L2 testnet / Ethereum Attestation Service / Merkle batched
          </div>
        </div>
        <button
          type="button"
          className="inline-flex h-8 items-center gap-1.5 rounded-atx-sm bg-atx-accent px-3 font-mono-atx text-[11.5px] font-medium text-[oklch(0.14_0.01_180)] hover:bg-atx-accent-deep"
        >
          <AtxIcon name="chain" /> anchor batch
        </button>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-3">
        <Metric k="Artefacts anchored" v="1,284" />
        <Metric k="Batches" v="42" />
        <Metric k="Gas this month" v="$18.42" />
      </div>

      <div className="mt-6">
        <AnchorsChain agent={fallback} />
      </div>
    </div>
  );
}

function Metric({ k, v }: { k: string; v: string }) {
  return (
    <div className="rounded-atx-md border border-atx-line-soft bg-atx-bg-sunken p-5">
      <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-dim">
        {k}
      </div>
      <div className="mt-2 font-serif text-[32px] leading-none text-atx-ink">
        {v}
      </div>
    </div>
  );
}

export function AnchorsChain({ agent }: { agent: ConsoleAgent }) {
  const nodes = [
    { k: "Local artefact", v: "sha256:4f8e2c9d...b7a0e5f8" },
    { k: "Merkle batch", v: "batch#42 / 128 leaves" },
    { k: "EAS attestation", v: "schema: 0x4a82...e9c1" },
    {
      k: "Base L2 txn",
      v: agent.anchorTxn
        ? `${agent.anchorTxn.slice(0, 10)}...${agent.anchorTxn.slice(-6)}`
        : "not anchored",
    },
    { k: "Status", v: "CONFIRMED / 14 blocks", ok: true },
  ];

  return (
    <div>
      <div className="flex flex-wrap items-stretch gap-0">
        {nodes.map((n, i) => (
          <div key={n.k} className="flex items-center">
            <div className="min-w-[160px] rounded-atx-sm border border-atx-line-soft bg-atx-panel px-4 py-3">
              <div className="font-mono-atx text-[10px] uppercase tracking-[0.14em] text-atx-ink-faint">
                {n.k}
              </div>
              <div
                className={`mt-1 font-mono-atx text-[11.5px] ${n.ok ? "text-atx-ok" : "text-atx-ink"}`}
              >
                {n.v}
              </div>
            </div>
            {i < nodes.length - 1 && (
              <div className="px-2 font-mono-atx text-atx-accent">&rarr;</div>
            )}
          </div>
        ))}
      </div>

      <div className="mt-6 overflow-hidden rounded-atx-md border border-atx-line-soft">
        <Row
          k="Attestation UID"
          v="0x4a82e9c1b3f8d2a6e5b1c7f0a9d3e6b2c5f8a1d4e7b0c3f6a9d2e5b8c1f4a7e0"
        />
        <Row k="Block" v="23 047 881 / 2026-04-18 14:05:17 UTC" />
        <Row k="Gas used" v="48 213 / 0.0012 ETH / $3.18 (testnet est.)" />
        <Row
          k="Schema"
          v="AttestixAgentIdentity v1 / bytes32 agentId, string did, uint256 riskTier"
        />
      </div>
    </div>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div className="grid grid-cols-[160px_1fr] items-baseline gap-4 border-b border-atx-line-soft bg-atx-panel px-4 py-3 last:border-b-0">
      <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint">
        {k}
      </div>
      <div className="break-all font-mono-atx text-[11.5px] text-atx-ink">
        {v}
      </div>
    </div>
  );
}
