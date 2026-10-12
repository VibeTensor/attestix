import Link from "next/link";
import { Icons } from "@/components/icons";
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
      { label: "Offline verify", href: "/docs/guides/offline-verify" },
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
      <div className="mx-auto max-w-[1200px] px-6">
        <div className="grid gap-12 md:grid-cols-2 lg:grid-cols-[1.5fr_repeat(5,1fr)]">
          <div>
            <Link href="/" aria-label="Attestix home" className="inline-flex items-center gap-2.5">
              <span className="text-atx-accent">
                <Icons.logo className="h-7 w-auto" />
              </span>
              <span className="flex flex-col leading-none">
                <span className="text-[17px] font-medium tracking-[-0.01em] text-atx-ink">Attestix</span>
                <span className="mt-1 text-[11px] text-atx-ink-dim">by VibeTensor</span>
              </span>
            </Link>
            <p className="mt-6 text-[13px] leading-[1.7] text-atx-ink-dim">
              VIBETENSOR PRIVATE LIMITED
              <br />
              CIN U74909TS2025PTC197692
              <br />
              Warangal, Telangana, India
            </p>
            <div className="mt-5 flex items-center gap-4 text-atx-ink-mid">
              <Link href={siteConfig.links.github} target="_blank" rel="noopener noreferrer" aria-label="GitHub" className="transition-colors duration-200 hover:text-atx-ink">
                <Icons.github className="h-4 w-4" />
              </Link>
              <a href="mailto:info@vibetensor.com" aria-label="Email" className="text-[13px] transition-colors duration-200 hover:text-atx-ink">
                info@vibetensor.com
              </a>
            </div>
          </div>

          {COLUMNS.map((col) => (
            <div key={col.heading}>
              <h4 className="text-[13px] font-medium text-atx-ink">{col.heading}</h4>
              <ul className="mt-4 space-y-2.5">
                {col.links.map((l) => (
                  <li key={l.label}>
                    <Link
                      href={l.href}
                      target={l.external ? "_blank" : undefined}
                      rel={l.external ? "noopener noreferrer" : undefined}
                      className="text-[14px] text-atx-ink-mid transition-colors duration-200 hover:text-atx-ink"
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

        <div className="mt-12 flex flex-col items-start justify-between gap-4 border-t border-atx-line-soft pt-6 text-[13px] text-atx-ink-dim md:flex-row md:items-center">
          <span>&copy; 2026 VibeTensor Private Limited &middot; Attestix v{siteConfig.version}</span>
          <span>Open source under Apache 2.0</span>
        </div>
      </div>
    </footer>
  );
}
