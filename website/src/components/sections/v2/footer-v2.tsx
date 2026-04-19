import Link from "next/link";
import { AtxIcon } from "@/components/atx/atx-icons";
import { siteConfig } from "@/lib/config";

interface FooterLink {
  label: string;
  href: string;
  external?: boolean;
}

interface FooterColumn {
  heading: string;
  links: FooterLink[];
}

const COLUMNS: FooterColumn[] = [
  {
    heading: "Product",
    links: [
      { label: "Console", href: "/console" },
      { label: "Compliance", href: "/docs/guides/eu-ai-act-compliance" },
      { label: "API reference", href: "/docs/reference/api-reference" },
      { label: "Examples", href: "/docs/examples" },
    ],
  },
  {
    heading: "Docs",
    links: [
      { label: "Getting started", href: "/docs/getting-started" },
      { label: "EU AI Act guide", href: "/docs/guides/eu-ai-act-compliance" },
      { label: "Risk classification", href: "/docs/guides/risk-classification" },
      { label: "Architecture", href: "/docs/guides/architecture" },
    ],
  },
  {
    heading: "Community",
    links: [
      { label: "GitHub", href: siteConfig.links.github, external: true },
      { label: "Research", href: "/research" },
      { label: "Blog", href: "/blog" },
      { label: "Community", href: "/community" },
    ],
  },
  {
    heading: "Company",
    links: [
      { label: "Pricing", href: "/pricing" },
      { label: "FAQ", href: "/faq" },
      { label: "Changelog", href: "/changelog" },
      { label: "Security", href: "/security" },
    ],
  },
  {
    heading: "Legal",
    links: [
      {
        label: "Apache 2.0",
        href: `${siteConfig.links.github}/blob/main/LICENSE`,
        external: true,
      },
      { label: "Privacy", href: "/legal/privacy" },
      { label: "Terms", href: "/legal/terms" },
      { label: "Cookies", href: "/legal/cookies" },
      { label: "SBOM", href: "/sbom" },
    ],
  },
];

export function FooterV2() {
  return (
    <footer className="border-t border-atx-line-soft bg-atx-bg py-16">
      <div className="mx-auto max-w-[1320px] px-7">
        <div className="grid gap-12 md:grid-cols-2 lg:grid-cols-[1.4fr_repeat(5,1fr)]">
          <div>
            <Link
              href="/"
              className="inline-flex items-center gap-2 text-atx-ink"
            >
              <span className="text-[20px] text-atx-accent">
                <AtxIcon name="did" />
              </span>
              <span className="font-serif text-[22px]">
                Attestix<sub className="ml-0.5 text-[10px] text-atx-ink-dim">io</sub>
              </span>
            </Link>
            <p className="mt-4 max-w-[280px] text-[13px] leading-[1.6] text-atx-ink-dim">
              Attestation infrastructure for autonomous AI agents. Built by
              VibeTensor. Apache License 2.0.
            </p>
          </div>

          {COLUMNS.map((col) => (
            <div key={col.heading}>
              <h4 className="font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-faint">
                {col.heading}
              </h4>
              <ul className="mt-4 space-y-2">
                {col.links.map((l) => (
                  <li key={l.label}>
                    <Link
                      href={l.href}
                      target={l.external ? "_blank" : undefined}
                      rel={l.external ? "noopener noreferrer" : undefined}
                      className="text-[13px] text-atx-ink-mid transition-colors hover:text-atx-accent"
                    >
                      {l.label}
                      {l.external ? (
                        <span className="sr-only"> (opens in new tab)</span>
                      ) : null}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 flex flex-col items-start justify-between gap-4 border-t border-atx-line-soft pt-6 font-mono-atx text-[11px] uppercase tracking-[0.1em] text-atx-ink-faint md:flex-row md:items-center">
          <span>
            &copy; 2026 VibeTensor Private Limited / Attestix v{siteConfig.version}
          </span>
          <span>apache 2.0 / open source</span>
        </div>
      </div>
    </footer>
  );
}
