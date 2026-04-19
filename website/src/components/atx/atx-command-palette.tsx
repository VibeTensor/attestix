"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { ATX_MODULES, ATX_WORKFLOW } from "@/lib/atx-data";

interface Entry {
  label: string;
  section: string;
  href: string;
}

const ROUTES: Entry[] = [
  { label: "Home", section: "Routes", href: "/" },
  { label: "Console", section: "Routes", href: "/console" },
  { label: "Docs", section: "Routes", href: "/docs" },
  { label: "Docs / Getting started", section: "Routes", href: "/docs/getting-started" },
  { label: "Docs / EU AI Act compliance", section: "Routes", href: "/docs/guides/eu-ai-act-compliance" },
  { label: "Docs / API reference", section: "Routes", href: "/docs/reference/api-reference" },
  { label: "Blog", section: "Routes", href: "/blog" },
  { label: "Pricing", section: "Routes", href: "/pricing" },
  { label: "FAQ", section: "Routes", href: "/faq" },
  { label: "Community", section: "Routes", href: "/community" },
  { label: "Research", section: "Routes", href: "/research" },
  { label: "Changelog", section: "Routes", href: "/changelog" },
  { label: "Security", section: "Routes", href: "/security" },
  { label: "SBOM", section: "Routes", href: "/sbom" },
  { label: "Demos", section: "Routes", href: "/demo" },
  { label: "Legal / Privacy", section: "Routes", href: "/legal/privacy" },
  { label: "Legal / Terms", section: "Routes", href: "/legal/terms" },
  { label: "Legal / Cookies", section: "Routes", href: "/legal/cookies" },
];

const ANCHORS: Entry[] = [
  { label: "Problem", section: "Landing sections", href: "/#problem" },
  { label: "Modules", section: "Landing sections", href: "/#modules" },
  { label: "Workflow", section: "Landing sections", href: "/#workflow" },
  { label: "Validation quotes", section: "Landing sections", href: "/#validation" },
  { label: "Framework integrations", section: "Landing sections", href: "/#frameworks" },
  { label: "Use cases", section: "Landing sections", href: "/#use-cases" },
  { label: "Benchmarks", section: "Landing sections", href: "/#benchmarks" },
  { label: "Compliance matrix", section: "Landing sections", href: "/#compliance-matrix" },
];

export function AtxCommandPalette() {
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState("");
  const [idx, setIdx] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  const entries = useMemo<Entry[]>(() => {
    const modules: Entry[] = ATX_MODULES.map((m) => ({
      label: `Module / ${m.name} (${m.tools} tools)`,
      section: "Modules",
      href: "/#modules",
    }));
    const workflow: Entry[] = ATX_WORKFLOW.map((w) => ({
      label: `Workflow / Step ${w.n} / ${w.title}`,
      section: "Workflow",
      href: "/#workflow",
    }));
    return [...ROUTES, ...ANCHORS, ...modules, ...workflow];
  }, []);

  const filtered = useMemo(() => {
    const query = q.trim().toLowerCase();
    if (!query) return entries;
    return entries.filter((e) =>
      (e.label + " " + e.section).toLowerCase().includes(query)
    );
  }, [entries, q]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setOpen((v) => !v);
      }
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  useEffect(() => {
    if (open) {
      setQ("");
      setIdx(0);
      window.setTimeout(() => inputRef.current?.focus(), 30);
    }
  }, [open]);

  useEffect(() => {
    setIdx(0);
  }, [q]);

  if (!open) return null;

  const go = (href: string) => {
    setOpen(false);
    router.push(href);
  };

  return (
    <div
      className="fixed inset-0 z-[110] flex items-start justify-center bg-black/60 backdrop-blur-sm"
      onClick={() => setOpen(false)}
    >
      <div
        className="mt-24 w-full max-w-[640px] overflow-hidden rounded-atx-md border border-atx-line bg-atx-panel shadow-[var(--atx-shadow-md)]"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-3 border-b border-atx-line-soft px-5 py-3">
          <span className="font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-faint">
            Jump to
          </span>
          <input
            ref={inputRef}
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "ArrowDown") {
                e.preventDefault();
                setIdx((v) => Math.min(filtered.length - 1, v + 1));
              } else if (e.key === "ArrowUp") {
                e.preventDefault();
                setIdx((v) => Math.max(0, v - 1));
              } else if (e.key === "Enter" && filtered[idx]) {
                e.preventDefault();
                go(filtered[idx].href);
              }
            }}
            placeholder="Search pages, modules, workflow steps"
            className="flex-1 bg-transparent font-mono-atx text-[13px] text-atx-ink outline-none placeholder:text-atx-ink-dim"
          />
          <kbd className="rounded-atx-xs border border-atx-line-soft bg-atx-bg-sunken px-1.5 py-0.5 font-mono-atx text-[10px] text-atx-ink-dim">
            ESC
          </kbd>
        </div>
        <ul className="max-h-[420px] overflow-auto">
          {filtered.length === 0 && (
            <li className="px-5 py-6 text-center font-mono-atx text-[11.5px] text-atx-ink-dim">
              No results.
            </li>
          )}
          {filtered.map((e, i) => {
            const active = i === idx;
            return (
              <li key={`${e.section}-${e.label}-${i}`}>
                <button
                  type="button"
                  onMouseEnter={() => setIdx(i)}
                  onClick={() => go(e.href)}
                  className={`flex w-full items-center justify-between gap-4 px-5 py-2.5 text-left transition-colors ${
                    active ? "bg-atx-panel-hi" : ""
                  }`}
                >
                  <span className="truncate font-mono-atx text-[12.5px] text-atx-ink">
                    {e.label}
                  </span>
                  <span className="shrink-0 font-mono-atx text-[10.5px] uppercase tracking-[0.12em] text-atx-ink-faint">
                    {e.section}
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
        <div className="flex items-center justify-between border-t border-atx-line-soft px-5 py-2 font-mono-atx text-[10.5px] text-atx-ink-dim">
          <span>
            <kbd className="mr-1 rounded-atx-xs border border-atx-line-soft bg-atx-bg-sunken px-1">
              &uarr;
            </kbd>
            <kbd className="mr-1 rounded-atx-xs border border-atx-line-soft bg-atx-bg-sunken px-1">
              &darr;
            </kbd>
            navigate
          </span>
          <span>
            <kbd className="mr-1 rounded-atx-xs border border-atx-line-soft bg-atx-bg-sunken px-1">
              &crarr;
            </kbd>
            open
          </span>
          <span>
            <kbd className="mr-1 rounded-atx-xs border border-atx-line-soft bg-atx-bg-sunken px-1">
              Cmd
            </kbd>
            <kbd className="rounded-atx-xs border border-atx-line-soft bg-atx-bg-sunken px-1">
              K
            </kbd>
            toggle
          </span>
        </div>
      </div>
    </div>
  );
}
