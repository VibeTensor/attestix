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
    <>
      <section className="bg-atx-bg px-6 pb-16 pt-16 text-center md:pt-20">
        <div className="mx-auto max-w-[860px]">
          <AtxEyebrow>Community</AtxEyebrow>
          <h1 className="mt-3 text-[clamp(34px,5vw,52px)] font-normal leading-[1.09] tracking-[-0.03em] text-atx-ink [text-wrap:balance]">
            Built in <span className="text-atx-accent">the open.</span>
          </h1>
          <p className="mx-auto mt-5 max-w-[640px] text-[17.5px] leading-[1.6] text-atx-ink-mid [text-wrap:balance]">
            Attestix is Apache 2.0. Star the repo, open an issue, or contribute a
            module. Every contribution helps build the trust layer for
            autonomous AI agents.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <Link
              href={siteConfig.links.github}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-full bg-atx-accent px-6 py-3 text-[15px] font-medium text-[oklch(0.14_0.01_180)] transition-colors duration-200 hover:bg-atx-accent-deep"
            >
              <Icons.github className="h-4 w-4" />
              Star on GitHub
            </Link>
            <Link
              href={`${siteConfig.links.github}/blob/main/CONTRIBUTING.md`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center rounded-full border border-atx-line px-6 py-3 text-[15px] font-medium text-atx-ink-mid transition-colors duration-200 hover:border-atx-ink-dim hover:text-atx-ink"
            >
              Become a contributor
            </Link>
          </div>
        </div>
      </section>

      <section className="bg-atx-bg-elev py-20">
        <div className="mx-auto grid w-full max-w-[1200px] gap-4 px-6 md:grid-cols-2 lg:grid-cols-3">
          {RESOURCES.map((r) => (
            <Link
              key={r.label}
              href={r.href}
              target={r.external ? "_blank" : undefined}
              rel={r.external ? "noopener noreferrer" : undefined}
              className="group flex flex-col gap-2 rounded-2xl border border-atx-line bg-atx-panel/60 p-6 transition-colors duration-200 hover:border-atx-ink-dim"
            >
              <div className="flex items-center justify-between">
                <h2 className="text-[19px] font-semibold tracking-[-0.48px] text-atx-ink">
                  {r.label}
                </h2>
                {r.external ? (
                  <span aria-hidden className="text-atx-ink-dim transition-colors duration-200 group-hover:text-atx-accent">
                    &#8599;
                  </span>
                ) : (
                  <span aria-hidden className="text-atx-ink-dim transition-colors duration-200 group-hover:text-atx-accent">
                    &rarr;
                  </span>
                )}
              </div>
              <p className="text-[15px] leading-[1.6] text-atx-ink-mid">
                {r.description}
              </p>
            </Link>
          ))}
        </div>
      </section>
    </>
  );
}
