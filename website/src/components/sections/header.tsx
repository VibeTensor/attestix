"use client";

import { Icons } from "@/components/icons";
import { MobileDrawer } from "@/components/mobile-drawer";
import { siteConfig } from "@/lib/config";
import Link from "next/link";
import { usePathname } from "next/navigation";

const navLinks = [
  { label: "How it works", href: "/#how-it-works", anchor: true },
  { label: "Platform", href: "/platform" },
  { label: "Research", href: "/research" },
  { label: "Docs", href: "/docs" },
  { label: "Blog", href: "/blog" },
];

export function Header() {
  const pathname = usePathname();
  return (
    <header className="sticky top-0 z-50 border-b border-atx-line-soft bg-atx-bg/80 backdrop-blur-md">
      <div className="mx-auto flex h-[68px] max-w-[1200px] items-center gap-7 px-7">
        <Link
          href="/"
          aria-label="Attestix home"
          className="flex items-center gap-2.5"
        >
          <span className="text-atx-accent">
            <Icons.logo className="h-7 w-auto" />
          </span>
          <span className="flex flex-col leading-none">
            <span className="text-[17px] font-medium tracking-[-0.01em] text-atx-ink">
              Attestix
            </span>
            <span className="mt-1 text-[11px] text-atx-ink-dim">by VibeTensor</span>
          </span>
        </Link>

        <nav className="ml-auto hidden items-center gap-8 lg:flex">
          {navLinks.map((link) => {
            const active =
              link.href === pathname ||
              (link.href !== "/" && pathname.startsWith(link.href.split("#")[0]) && !link.anchor);
            return (
              <Link
                key={link.label}
                href={link.href}
                aria-current={active ? "page" : undefined}
                className={`text-[14px] transition-colors hover:text-atx-ink ${
                  active ? "text-atx-ink" : "text-atx-ink-mid"
                }`}
              >
                {link.label}
              </Link>
            );
          })}
          <Link
            href={siteConfig.links.github}
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Attestix on GitHub"
            className="text-atx-ink-mid transition-colors hover:text-atx-ink"
          >
            <Icons.github className="h-4 w-4" />
          </Link>
          <Link
            href="/docs/getting-started"
            className="inline-flex h-9 items-center rounded-full bg-atx-accent px-5 text-[13px] font-medium text-[oklch(0.14_0.01_180)] transition-colors hover:bg-atx-accent-deep"
          >
            Get started
          </Link>
        </nav>

        <div className="ml-auto cursor-pointer lg:hidden">
          <MobileDrawer />
        </div>
      </div>
    </header>
  );
}
