import { Icons } from "@/components/icons";
import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/ui/drawer";
import { siteConfig } from "@/lib/config";
import { MenuIcon } from "lucide-react";
import Link from "next/link";

const mobileLinks = [
  { label: "Overview", href: "/" },
  { label: "Modules", href: "/#modules" },
  { label: "Workflow", href: "/#workflow" },
  { label: "Docs", href: "/docs" },
  { label: "Blog", href: "/blog" },
  { label: "Pricing", href: "/pricing" },
  { label: "FAQ", href: "/faq" },
  { label: "Community", href: "/community" },
  { label: "Demos", href: "/demo" },
];

export function MobileDrawer() {
  return (
    <Drawer>
      <DrawerTrigger
        aria-label="Open navigation menu"
        className="text-atx-ink-dim transition-colors hover:text-atx-ink"
      >
        <MenuIcon className="h-5 w-5" />
      </DrawerTrigger>
      <DrawerContent className="border-t border-atx-line-soft bg-atx-bg">
        <DrawerHeader className="border-b border-atx-line-soft px-7 py-5 text-left">
          <Link
            href="/"
            aria-label="Attestix home"
            className="flex items-center gap-2"
          >
            <Icons.logo className="h-6 w-auto text-atx-accent" />
            <DrawerTitle className="font-serif text-[22px] font-normal leading-none text-atx-ink">
              Attestix
              <sub className="ml-0.5 font-mono-atx text-[10px] text-atx-ink-dim">
                v{siteConfig.version}
              </sub>
            </DrawerTitle>
          </Link>
          <DrawerDescription className="mt-3 text-[13px] leading-[1.55] text-atx-ink-mid">
            Attestation infrastructure for autonomous AI agents.
          </DrawerDescription>
        </DrawerHeader>

        <nav className="flex flex-col px-2 py-3">
          {mobileLinks.map((link) => (
            <Link
              key={link.label}
              href={link.href}
              className="rounded-atx-sm px-5 py-3 font-mono-atx text-[12px] uppercase tracking-[0.14em] text-atx-ink-dim transition-colors hover:bg-atx-panel-hi hover:text-atx-accent"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="flex flex-col gap-2 border-t border-atx-line-soft px-7 py-5">
          <Link
            href="/docs/getting-started"
            className="inline-flex h-10 items-center justify-center gap-2 rounded-atx-md bg-atx-accent px-5 text-[13px] font-medium text-[oklch(0.14_0.01_180)] transition-colors hover:bg-atx-accent-deep"
          >
            <span className="font-mono-atx">$</span> pip install attestix
          </Link>
          <Link
            href={siteConfig.links.github}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex h-10 items-center justify-center gap-2 rounded-atx-md border border-atx-line px-5 text-[13px] font-medium text-atx-ink transition-colors hover:border-atx-ink-dim hover:bg-atx-panel"
          >
            <Icons.github className="h-4 w-4" />
            Star on GitHub
          </Link>
        </div>
      </DrawerContent>
    </Drawer>
  );
}
