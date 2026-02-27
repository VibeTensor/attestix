"use client";

import { AuroraText } from "@/components/aurora-text";
import { Icons } from "@/components/icons";
import { Section } from "@/components/section";
import { buttonVariants } from "@/components/ui/button";
import OrbitingCircles from "@/components/ui/orbiting-circles";
import { siteConfig } from "@/lib/config";
import { cn } from "@/lib/utils";
import { motion } from "motion/react";
import {
  FingerprintIcon,
  GitForkIcon,
  FileSearchIcon,
  LinkIcon,
  ScaleIcon,
  ShieldCheckIcon,
  KeyIcon,
  StarIcon,
  ContactIcon,
} from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

const ease = [0.16, 1, 0.3, 1] as [number, number, number, number];

function HeroPill() {
  return (
    <motion.a
      href="https://github.com/VibeTensor/attestix/releases"
      target="_blank"
      rel="noopener noreferrer"
      className="flex w-auto items-center space-x-2 rounded-full bg-gold/15 px-2 py-1 ring-1 ring-gold/30 whitespace-pre"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, ease }}
    >
      <div className="w-fit rounded-full bg-gold/20 px-2 py-0.5 text-left text-xs font-medium text-gold sm:text-sm">
        v0.2.2
      </div>
      <p className="text-xs font-medium text-gold sm:text-sm">
        Now Open Source
      </p>
      <svg
        width="12"
        height="12"
        className="ml-1 text-gold"
        viewBox="0 0 12 12"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M8.78141 5.33312L5.20541 1.75712L6.14808 0.814453L11.3334 5.99979L6.14808 11.1851L5.20541 10.2425L8.78141 6.66645H0.666748V5.33312H8.78141Z"
          fill="currentColor"
        />
      </svg>
    </motion.a>
  );
}

function HeroTitles() {
  return (
    <div className="flex w-full max-w-3xl flex-col overflow-hidden pt-8">
      <motion.h1
        className="text-left text-4xl font-semibold leading-tighter text-foreground sm:text-5xl md:text-6xl tracking-tighter"
        initial={{ filter: "blur(10px)", opacity: 0, y: 50 }}
        animate={{ filter: "blur(0px)", opacity: 1, y: 0 }}
        transition={{ duration: 1, ease, staggerChildren: 0.2 }}
      >
        <motion.span
          className="inline-block text-balance"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.5, ease }}
        >
          <AuroraText className="leading-normal font-bold">
            {siteConfig.hero.title}
          </AuroraText>{" "}
        </motion.span>
      </motion.h1>
      <motion.p
        className="text-left max-w-xl leading-normal text-muted-foreground sm:text-lg sm:leading-normal text-balance"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6, duration: 0.8, ease }}
      >
        {siteConfig.hero.description}
      </motion.p>
    </div>
  );
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  const handleCopy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      onClick={handleCopy}
      className={cn(
        buttonVariants({ variant: "default" }),
        "w-full sm:w-auto text-primary-foreground flex gap-2 rounded-lg font-mono text-sm"
      )}
    >
      <span aria-live="polite">{copied ? "Copied!" : text}</span>
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
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

function HeroCTA() {
  return (
    <div className="relative mt-6">
      <motion.div
        className="flex w-full max-w-2xl flex-col items-start justify-start space-y-4 sm:flex-row sm:space-x-4 sm:space-y-0"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8, duration: 0.8, ease }}
      >
        <CopyButton text="pip install attestix" />
        <Link
          href="https://github.com/VibeTensor/attestix"
          target="_blank"
          rel="noopener noreferrer"
          className={cn(
            buttonVariants({ variant: "outline" }),
            "w-full sm:w-auto flex gap-2 rounded-lg"
          )}
        >
          <Icons.github className="h-4 w-4" />
          Star on GitHub
        </Link>
      </motion.div>
      <motion.p
        className="mt-3 text-sm text-muted-foreground text-left"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.0, duration: 0.8 }}
      >
        {siteConfig.hero.ctaDescription}
      </motion.p>
    </div>
  );
}

function StatsStrip() {
  const stats = ["47 Tools", "9 Modules", "272+ Tests", "Apache 2.0"];
  return (
    <motion.div
      className="flex flex-wrap gap-3 mt-8"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 1.2, duration: 0.6, ease }}
    >
      {stats.map((stat) => (
        <span key={stat} className="text-xs font-medium text-muted-foreground bg-secondary/50 px-3 py-1 rounded-full border">
          {stat}
        </span>
      ))}
    </motion.div>
  );
}

function OrbitIcon({
  Icon,
  label,
  color,
}: {
  Icon: React.ComponentType<{ className?: string }>;
  label: string;
  color: "gold" | "primary";
}) {
  return (
    <div
      className={cn(
        "flex h-8 w-8 items-center justify-center rounded-full border backdrop-blur-sm",
        color === "gold"
          ? "bg-gold/20 border-gold/30"
          : "bg-primary/15 border-primary/25"
      )}
      title={label}
    >
      <Icon
        className={cn(
          "h-4 w-4",
          color === "gold" ? "text-gold" : "text-primary"
        )}
      />
    </div>
  );
}

export function Hero() {
  const [isMobile, setIsMobile] = useState(false);
  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 1024);
    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  return (
    <Section id="hero">
      <div className="relative grid grid-cols-1 lg:grid-cols-2 gap-x-8 w-full p-6 lg:p-12 border-x overflow-hidden">
        <div className="flex flex-col justify-start items-start lg:col-span-1">
          <HeroPill />
          <HeroTitles />
          <HeroCTA />
          <StatsStrip />
        </div>
        {!isMobile && (
          <div className="relative lg:h-full lg:col-span-1">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 1, delay: 0.8 }}
              className="relative flex items-center justify-center h-full w-full min-h-[400px]"
            >
              <div className="absolute inset-0 bg-[radial-gradient(circle,oklch(0.46_0.24_264_/_0.08)_0%,transparent_60%)]" aria-hidden="true" />

              {/* Attestix logo at center */}
              <Icons.logo className="h-10 w-10 relative z-10" />

              {/* Inner ring (radius 80) - 3 modules, forward */}
              <OrbitingCircles radius={80} duration={22} delay={0} className="border-0 bg-transparent p-0 size-auto">
                <OrbitIcon Icon={FingerprintIcon} label="Identity" color="gold" />
              </OrbitingCircles>
              <OrbitingCircles radius={80} duration={22} delay={7} className="border-0 bg-transparent p-0 size-auto">
                <OrbitIcon Icon={KeyIcon} label="DID" color="gold" />
              </OrbitingCircles>
              <OrbitingCircles radius={80} duration={22} delay={14} className="border-0 bg-transparent p-0 size-auto">
                <OrbitIcon Icon={ContactIcon} label="Agent Cards" color="gold" />
              </OrbitingCircles>

              {/* Middle ring (radius 140) - 3 modules, reverse */}
              <OrbitingCircles radius={140} duration={28} delay={0} reverse className="border-0 bg-transparent p-0 size-auto">
                <OrbitIcon Icon={ShieldCheckIcon} label="Credentials" color="primary" />
              </OrbitingCircles>
              <OrbitingCircles radius={140} duration={28} delay={9} reverse className="border-0 bg-transparent p-0 size-auto">
                <OrbitIcon Icon={GitForkIcon} label="Delegation" color="primary" />
              </OrbitingCircles>
              <OrbitingCircles radius={140} duration={28} delay={18} reverse className="border-0 bg-transparent p-0 size-auto">
                <OrbitIcon Icon={ScaleIcon} label="Compliance" color="primary" />
              </OrbitingCircles>

              {/* Outer ring (radius 200) - 3 modules, forward */}
              <OrbitingCircles radius={200} duration={34} delay={0} className="border-0 bg-transparent p-0 size-auto">
                <OrbitIcon Icon={FileSearchIcon} label="Provenance" color="primary" />
              </OrbitingCircles>
              <OrbitingCircles radius={200} duration={34} delay={11} className="border-0 bg-transparent p-0 size-auto">
                <OrbitIcon Icon={StarIcon} label="Reputation" color="gold" />
              </OrbitingCircles>
              <OrbitingCircles radius={200} duration={34} delay={22} className="border-0 bg-transparent p-0 size-auto">
                <OrbitIcon Icon={LinkIcon} label="Blockchain" color="gold" />
              </OrbitingCircles>
            </motion.div>
          </div>
        )}
      </div>
    </Section>
  );
}
