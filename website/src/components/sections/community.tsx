import Link from "next/link";
import { AtxEyebrow } from "@/components/atx/atx-eyebrow";
import { Icons } from "@/components/icons";
import { siteConfig } from "@/lib/config";

interface ResourceLink {
  label: string;
  href: string;
  description: string;
  external?: boolean;
}

const RESOURCES: ResourceLink[] = [
  {
    label: "GitHub",
    href: siteConfig.links.github,
    description: "Source code, issues, and pull requests.",
    external: true,
  },
  {
    label: "Contributing guide",
    href: `${siteConfig.links.github}/blob/main/CONTRIBUTING.md`,
    description: "How to propose changes, write tests, and ship a module.",
    external: true,
  },
  {
    label: "PyPI",
    href: siteConfig.links.pypi,
    description: "Install the Attestix Python package.",
    external: true,
  },
  {
    label: "MCP Registry",
    href: siteConfig.links.mcpRegistry,
    description: "Discover Attestix in the MCP registry listing.",
    external: true,
  },
  {
    label: "Documentation",
    href: "/docs",
    description: "Getting started, guides, reference.",
  },
  {
    label: "Blog",
    href: "/blog",
    description: "Release notes, research, and field updates.",
  },
];

export function Community() {
  return (
    <section className="mx-auto max-w-[1320px] px-7 py-24">
      <div className="grid items-start gap-10 lg:grid-cols-[1fr_1.2fr]">
        <div>
          <AtxEyebrow>Community</AtxEyebrow>
          <h1 className="mt-3 font-serif text-[clamp(36px,4.8vw,60px)] leading-[1.05] tracking-[-0.012em] text-atx-ink">
            Built in
            <br />
            <em className="italic text-atx-accent">the open.</em>
          </h1>
        </div>
        <p className="text-[15px] leading-[1.65] text-atx-ink-mid">
          Attestix is Apache 2.0. Star the repo, open an issue, or contribute a
          module. Every contribution helps build the trust layer for
          autonomous AI agents.
        </p>
      </div>

      <div className="mt-10 flex flex-wrap gap-3">
        <Link
          href={siteConfig.links.github}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex h-10 items-center gap-2 rounded-atx-md bg-atx-accent px-5 text-[13px] font-medium text-[oklch(0.14_0.01_180)] transition-colors hover:bg-atx-accent-deep"
        >
          <Icons.github className="h-4 w-4" />
          Star on GitHub
        </Link>
        <Link
          href={`${siteConfig.links.github}/blob/main/CONTRIBUTING.md`}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex h-10 items-center rounded-atx-md border border-atx-line px-5 text-[13px] font-medium text-atx-ink transition-colors hover:border-atx-ink-dim hover:bg-atx-panel"
        >
          Become a contributor
        </Link>
      </div>

      <div className="mt-14 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {RESOURCES.map((r) => (
          <Link
            key={r.label}
            href={r.href}
            target={r.external ? "_blank" : undefined}
            rel={r.external ? "noopener noreferrer" : undefined}
            className="group flex flex-col gap-2 rounded-atx-md border border-atx-line-soft bg-atx-panel p-6 transition-colors hover:border-atx-accent/60 hover:bg-atx-panel-hi"
          >
            <div className="flex items-center justify-between font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
              <span>{r.label}</span>
              {r.external ? (
                <span className="text-atx-accent">&uarr;</span>
              ) : (
                <span className="text-atx-accent transition-transform group-hover:translate-x-0.5">
                  &rarr;
                </span>
              )}
            </div>
            <p className="text-[13.5px] leading-[1.55] text-atx-ink-mid">
              {r.description}
            </p>
          </Link>
        ))}
      </div>
    </section>
  );
}
