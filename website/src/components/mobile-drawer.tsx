import { Icons } from "@/components/icons";
import { buttonVariants } from "@/components/ui/button";
import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/ui/drawer";
import { siteConfig } from "@/lib/config";
import { cn } from "@/lib/utils";
import { MenuIcon } from "lucide-react";
import Link from "next/link";

const mobileLinks = [
  { label: "Architecture", href: "#architecture" },
  { label: "Tech Stack", href: "#tech-stack" },
  { label: "Pricing", href: "/pricing" },
  { label: "FAQ", href: "/faq" },
  { label: "Docs", href: "/docs" },
  { label: "Demos", href: "/demo" },
  { label: "Research", href: "/docs/project/research" },
  { label: "GitHub", href: "https://github.com/VibeTensor/attestix" },
];

export function MobileDrawer() {
  return (
    <Drawer>
      <DrawerTrigger aria-label="Open navigation menu">
        <MenuIcon className="h-6 w-6" />
      </DrawerTrigger>
      <DrawerContent>
        <DrawerHeader className="px-6">
          <Link
            href="/"
            aria-label="Attestix home"
            className="relative mr-6 flex items-center space-x-2"
          >
            <Icons.logo className="w-auto h-[40px]" />
            <DrawerTitle>{siteConfig.name}</DrawerTitle>
          </Link>
          <DrawerDescription>{siteConfig.description}</DrawerDescription>
        </DrawerHeader>
        <div className="px-6 py-2 flex flex-col gap-2">
          {mobileLinks.map((link) => (
            <Link
              key={link.label}
              href={link.href}
              className="text-sm font-medium text-muted-foreground hover:text-foreground py-2"
            >
              {link.label}
            </Link>
          ))}
        </div>
        <DrawerFooter>
          <Link
            href="/docs/getting-started"
            className={cn(
              buttonVariants({ variant: "default" }),
              "rounded-full group"
            )}
          >
            {siteConfig.cta}
          </Link>
        </DrawerFooter>
      </DrawerContent>
    </Drawer>
  );
}
