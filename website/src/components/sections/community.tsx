"use client";

import { Icons } from "@/components/icons";
import { Section } from "@/components/section";
import { Button } from "@/components/ui/button";
import { Globe } from "@/components/ui/globe";
import { siteConfig } from "@/lib/config";
import Link from "next/link";

export function Community() {
  return (
    <Section id="community" title="Community">
      <div className="border-x border-t overflow-hidden relative">
        <div className="absolute inset-0 opacity-40" aria-hidden="true">
          <Globe />
        </div>
        <div className="relative z-10 p-6 text-center py-12">
          <p className="text-muted-foreground mb-6 text-balance max-w-prose mx-auto font-medium">
            Attestix is built in the open. Star the repo, open an issue, or
            contribute a module. Every contribution helps build the trust
            layer for AI agents.
          </p>
          <div className="flex flex-wrap justify-center gap-3 mb-8">
            <Link
              href={siteConfig.links.github}
              target="_blank"
              rel="noopener noreferrer"
            >
              <Button className="flex items-center gap-2">
                <Icons.github className="h-5 w-5" />
                Star on GitHub
              </Button>
            </Link>
            <Link
              href={`${siteConfig.links.github}/blob/main/CONTRIBUTING.md`}
              target="_blank"
              rel="noopener noreferrer"
            >
              <Button variant="secondary" className="flex items-center gap-2">
                Become a Contributor
              </Button>
            </Link>
          </div>
          <div className="flex flex-wrap justify-center gap-6 text-sm text-muted-foreground">
            <Link
              href={siteConfig.links.docs}
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-foreground transition-colors"
            >
              Documentation
            </Link>
            <Link
              href={siteConfig.links.mcpRegistry}
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-foreground transition-colors"
            >
              MCP Registry
            </Link>
            <Link
              href={siteConfig.links.pypi}
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-foreground transition-colors"
            >
              PyPI Package
            </Link>
          </div>
        </div>
      </div>
    </Section>
  );
}
