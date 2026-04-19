"use client";

import { Icons } from "@/components/icons";
import { MobileDrawer } from "@/components/mobile-drawer";
import { siteConfig } from "@/lib/config";
import Link from "next/link";
import { usePathname } from "next/navigation";

const navLinks = [
  { label: "Overview", href: "/", anchor: true },
  { label: "Modules", href: "/#modules", anchor: true },
  { label: "Workflow", href: "/#workflow", anchor: true },
  { label: "Docs", href: "/docs" },
  { label: "Blog", href: "/blog" },
];

export function Header() {
  const pathname = usePathname();
  return (
    <header className="sticky top-0 z-50 border-b border-atx-line-soft bg-atx-bg/80 backdrop-blur-md">
      <div className="mx-auto flex h-[60px] max-w-[1320px] items-center gap-7 px-7">
        <Link
          href="/"
          aria-label="Attestix home"
          className="flex items-center gap-2"
        >
          <span className="text-[22px] text-atx-accent">
            <Icons.logo className="h-6 w-auto" />
          </span>
          <span className="font-serif text-[20px] leading-none text-atx-ink">
            Attestix
            <sub className="ml-0.5 font-mono-atx text-[10px] text-atx-ink-dim">
              v{siteConfig.version}
            </sub>
          </span>
        </Link>

        <nav className="hidden items-center gap-6 lg:flex">
          {navLinks.map((link) => {
            const active =
              link.href === pathname ||
              (link.href !== "/" && pathname.startsWith(link.href.split("#")[0]) && !link.anchor);
            return (
              <Link
                key={link.label}
                href={link.href}
                aria-current={active ? "page" : undefined}
                className={`font-mono-atx text-[11px] uppercase tracking-[0.14em] transition-colors hover:text-atx-accent ${
                  active ? "text-atx-ink" : "text-atx-ink-dim"
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>

        <div className="ml-auto hidden items-center gap-4 lg:flex">
          <div className="flex items-center gap-2 font-mono-atx text-[10.5px] uppercase tracking-[0.12em] text-atx-ink-dim">
            <span className="inline-block h-1.5 w-1.5 rounded-full bg-atx-ok" />
            <span>main</span>
          </div>
          <Link
            href={siteConfig.links.github}
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Attestix on GitHub"
            className="text-atx-ink-dim transition-colors hover:text-atx-ink"
          >
            <Icons.github className="h-4 w-4" />
          </Link>
          <Link
            href="/docs/getting-started"
            className="inline-flex h-8 items-center gap-2 rounded-atx-sm border border-atx-line bg-atx-bg-sunken px-3 font-mono-atx text-[11.5px] text-atx-ink transition-colors hover:border-atx-accent hover:text-atx-accent"
          >
            <span className="text-atx-accent">$</span> pip install
          </Link>
        </div>

        <div className="ml-auto cursor-pointer lg:hidden">
          <MobileDrawer />
        </div>
      </div>
    </header>
  );
}
