"use client";

import { Icons } from "@/components/icons";
import { MobileDrawer } from "@/components/mobile-drawer";
import { buttonVariants } from "@/components/ui/button";
import { siteConfig } from "@/lib/config";
import { cn } from "@/lib/utils";
import Link from "next/link";

const navLinks = [
  { label: "Architecture", href: "#architecture" },
  { label: "Tech Stack", href: "#tech-stack" },
  { label: "Docs", href: "/docs", external: false },
  { label: "Demos", href: "/demo", external: false },
  { label: "Research", href: "/docs/project/research", external: false },
];

export function Header() {
  return (
    <header className="sticky top-0 h-[var(--header-height)] z-50 p-0 bg-background/60 backdrop-blur">
      <div className="flex justify-between items-center container mx-auto p-2">
        <Link
          href="/"
          aria-label="Attestix home"
          className="relative mr-6 flex items-center space-x-2"
        >
          <Icons.logo className="w-auto h-7" />
          <span className="font-semibold text-lg">{siteConfig.name}</span>
        </Link>
        <nav className="hidden lg:flex items-center gap-8">
          {navLinks.map((link) => (
            <Link
              key={link.label}
              href={link.href}
              target={link.external ? "_blank" : undefined}
              rel={link.external ? "noopener noreferrer" : undefined}
              className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors relative after:absolute after:-bottom-1 after:left-0 after:h-[2px] after:w-0 after:bg-primary after:transition-all hover:after:w-full"
            >
              {link.label}
            </Link>
          ))}
          <Link
            href="https://github.com/VibeTensor/attestix"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            <Icons.github className="h-4 w-4" />
            GitHub
          </Link>
        </nav>
        <div className="hidden lg:block">
          <Link
            href="/docs/getting-started"
            className={cn(
              buttonVariants({ variant: "default" }),
              "h-8 text-primary-foreground rounded-lg group tracking-tight font-medium"
            )}
          >
            {siteConfig.cta}
          </Link>
        </div>
        <div className="mt-2 cursor-pointer block lg:hidden">
          <MobileDrawer />
        </div>
      </div>
      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />
    </header>
  );
}
