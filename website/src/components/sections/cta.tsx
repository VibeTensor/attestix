"use client";

import { Section } from "@/components/section";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { buttonVariants } from "@/components/ui/button";
import Link from "next/link";
import { useState } from "react";

function CopyInstallButton() {
  const [copied, setCopied] = useState(false);
  const text = "pip install attestix";

  const handleCopy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      onClick={handleCopy}
      className={cn(
        buttonVariants({ variant: "default", size: "lg" }),
        "flex items-center gap-2 font-mono"
      )}
    >
      <span aria-live="polite">{copied ? "Copied!" : text}</span>
      <svg
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        {copied ? (
          <polyline points="20 6 9 17 4 12" />
        ) : (
          <>
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
          </>
        )}
      </svg>
    </button>
  );
}

export function CTA() {
  return (
    <Section id="cta">
      <div className="border overflow-hidden relative text-center py-16 mx-auto">
        <p className="max-w-3xl text-foreground mb-6 text-balance mx-auto font-medium text-3xl">
          Ready to add verifiable trust to your AI agents?
        </p>

        <div className="flex flex-wrap justify-center gap-3">
          <CopyInstallButton />
          <Link
            href="https://docs.attestix.io"
            target="_blank"
            rel="noopener noreferrer"
          >
            <Button variant="outline" size="lg">
              Read the Docs
            </Button>
          </Link>
        </div>
      </div>
    </Section>
  );
}
