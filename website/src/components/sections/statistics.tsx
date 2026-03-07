"use client";

import { Section } from "@/components/section";
import { NumberTicker } from "@/components/ui/number-ticker";
import {
  WrenchIcon,
  FlaskConicalIcon,
  BookOpenIcon,
} from "lucide-react";
import Link from "next/link";

const stats = [
  {
    value: 47,
    suffix: "",
    subtitle: "MCP Tools across 9 modules",
    icon: <WrenchIcon className="h-5 w-5" />,
    href: "https://docs.attestix.io",
  },
  {
    value: 284,
    suffix: "",
    subtitle: "Tests with conformance benchmarks",
    icon: <FlaskConicalIcon className="h-5 w-5" />,
    href: "https://github.com/VibeTensor/attestix",
  },
  {
    value: 6,
    suffix: "",
    subtitle: "Conformance test suites (W3C, IETF, UCAN, MCP)",
    icon: <BookOpenIcon className="h-5 w-5" />,
    href: "https://docs.attestix.io/research/",
  },
];

export function Statistics() {
  return (
    <Section id="statistics" title="By the Numbers">
      <div
        className="border-x border-t"
        style={{
          backgroundImage:
            "radial-gradient(circle at bottom center, color-mix(in oklch, var(--secondary) 40%, transparent), var(--background))",
        }}
      >
        <div className="grid grid-cols-1 sm:grid-cols-3">
          {stats.map((stat, idx) => (
            <Link
              href={stat.href}
              target="_blank"
              rel="noopener noreferrer"
              key={idx}
              className="flex flex-col items-center justify-center py-8 px-4 border-b sm:border-b-0 last:border-b-0 sm:border-r sm:last:border-r-0 [&:nth-child(-n+2)]:border-t-0 sm:[&:nth-child(-n+3)]:border-t-0 relative group overflow-hidden"
            >
              <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-all transform translate-x-full -translate-y-full group-hover:translate-x-0 group-hover:translate-y-0 duration-300 ease-in-out">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <line x1="7" y1="17" x2="17" y2="7"></line>
                  <polyline points="7 7 17 7 17 17"></polyline>
                </svg>
              </div>
              <div className="text-center relative">
                <div className="flex items-center justify-center">
                  <NumberTicker
                    value={stat.value}
                    className="font-mono pointer-events-none text-center text-[6rem] font-bold leading-none before:bg-gradient-to-b before:from-border before:to-border/50 dark:before:from-border dark:before:to-border/30 bg-gradient-to-b from-foreground/60 to-foreground/30 bg-clip-text text-transparent"
                  />
                </div>
                <div className="flex items-center justify-center gap-2 mt-2">
                  {stat.icon}
                  <p className="text-sm text-muted-foreground">
                    {stat.subtitle}
                  </p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </Section>
  );
}
