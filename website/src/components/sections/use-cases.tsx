"use client";

import { Icons } from "@/components/icons";
import { Section } from "@/components/section";
import OrbitingCircles from "@/components/ui/orbiting-circles";
import { cn } from "@/lib/utils";
import { cubicBezier, motion } from "motion/react";
import {
  AwardIcon,
  ContactIcon,
  FileCheckIcon,
  FingerprintIcon,
  GitForkIcon,
  FileSearchIcon,
  KeyIcon,
  LinkIcon,
  ScaleIcon,
  ShieldCheckIcon,
  ShieldIcon,
  StarIcon,
} from "lucide-react";

const containerVariants = {
  initial: {},
  whileHover: { transition: { staggerChildren: 0.1 } },
};

export function Card1() {
  const variant1 = {
    initial: { scale: 0.87, transition: { delay: 0.05, duration: 0.2, ease: "linear" as const } },
    whileHover: {
      scale: 0.8,
      boxShadow: "oklch(0.76 0.155 73 / 0.2) 0px 20px 70px -10px, oklch(0.2 0.02 264 / 0.06) 0px 1px 4px -1px",
      transition: { delay: 0.05, duration: 0.2, ease: "linear" as const },
    },
  };
  const variant2 = {
    initial: { y: -27, scale: 0.95, transition: { delay: 0, duration: 0.2, ease: "linear" as const } },
    whileHover: {
      y: -55, scale: 0.87,
      boxShadow: "oklch(0.46 0.24 264 / 0.15) 0px 20px 70px -10px, oklch(0.2 0.02 264 / 0.06) 0px 1px 4px -1px",
      transition: { delay: 0, duration: 0.2, ease: "linear" as const },
    },
  };
  const variant3 = {
    initial: { y: -25, opacity: 0, scale: 1, transition: { delay: 0.05, duration: 0.2, ease: "linear" as const } },
    whileHover: {
      y: -45, opacity: 1, scale: 1,
      boxShadow: "oklch(0.46 0.24 264 / 0.1) 10px 20px 70px -20px, oklch(0.2 0.02 264 / 0.06) 0px 1px 4px -1px",
      transition: { delay: 0.05, duration: 0.2, ease: "easeInOut" as const },
    },
  };

  return (
    <div className="p-0 h-full overflow-hidden border-b lg:border-b-0 lg:border-r">
      <motion.div
        variants={{ initial: {}, whileHover: { transition: { staggerChildren: 0.1 } } }}
        initial="initial"
        whileHover="whileHover"
        className="flex flex-col gap-y-5 items-center justify-between h-full w-full cursor-pointer"
      >
        <div className="flex h-full w-full items-center justify-center rounded-t-xl border-b">
          <div className="relative flex flex-col items-center justify-center gap-y-2 p-10">
            <motion.div variants={variant1} className="z-[1] flex h-full w-full items-center justify-between gap-x-2 rounded-md border bg-background p-5 px-2.5">
              <div className="h-8 w-8 rounded-full bg-gold flex items-center justify-center">
                <ShieldIcon className="h-5 w-5 text-gold-foreground" />
              </div>
              <div className="flex flex-col gap-y-2">
                <div className="h-2 w-32 rounded-full bg-foreground/20"></div>
                <div className="h-2 w-48 rounded-full bg-muted-foreground/25"></div>
                <div className="text-xs text-muted-foreground">Agent identity created</div>
              </div>
            </motion.div>
            <motion.div variants={variant2} className="z-[2] flex h-full w-full items-center justify-between gap-x-2 rounded-md border bg-background p-5 px-2.5">
              <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center">
                <FileCheckIcon className="h-5 w-5 text-primary-foreground" />
              </div>
              <div className="flex flex-col gap-y-2">
                <div className="h-2 w-32 rounded-full bg-foreground/20"></div>
                <div className="h-2 w-48 rounded-full bg-muted-foreground/25"></div>
                <div className="h-2 w-20 rounded-full bg-muted-foreground/25"></div>
                <div className="text-xs text-muted-foreground">Compliance profile assessed</div>
              </div>
            </motion.div>
            <motion.div variants={variant3} className="absolute bottom-0 z-[3] m-auto flex h-fit w-fit items-center justify-between gap-x-2 rounded-md border bg-background p-5 px-2.5">
              <div className="h-8 w-8 rounded-full bg-primary/80 flex items-center justify-center">
                <AwardIcon className="h-5 w-5 text-primary-foreground" />
              </div>
              <div className="flex flex-col gap-y-2">
                <div className="h-2 w-32 rounded-full bg-foreground/20"></div>
                <div className="h-2 w-48 rounded-full bg-muted-foreground/25"></div>
                <div className="h-2 w-20 rounded-full bg-muted-foreground/25"></div>
                <div className="h-2 w-48 rounded-full bg-muted-foreground/25"></div>
                <div className="text-xs text-muted-foreground">Credential issued and anchored</div>
              </div>
            </motion.div>
          </div>
        </div>
        <div className="flex flex-col gap-y-1 px-5 pb-4 items-start w-full">
          <h2 className="font-semibold tracking-tight text-lg">Compliance Pipeline</h2>
          <p className="text-sm text-muted-foreground">Identity creation to compliance assessment to credential issuance in one flow.</p>
        </div>
      </motion.div>
    </div>
  );
}

const Card2 = () => {
  const logs = [
    { id: 1, type: "identity", timestamp: "2026-02-27 09:15:22", message: "Agent identity created. UAIT assigned.",
      icon: <div className="h-8 w-8 rounded-full bg-gold flex items-center justify-center"><FingerprintIcon className="h-5 w-5 text-gold-foreground" /></div> },
    { id: 2, type: "provenance", timestamp: "2026-02-27 09:15:24", message: "Training data recorded. Hash chain extended.",
      icon: <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center"><FileSearchIcon className="h-5 w-5 text-primary-foreground" /></div> },
    { id: 3, type: "credential", timestamp: "2026-02-27 09:15:27", message: "Verifiable credential issued. Ed25519 signed.",
      icon: <div className="h-8 w-8 rounded-full bg-primary/80 flex items-center justify-center"><ShieldCheckIcon className="h-5 w-5 text-primary-foreground" /></div> },
    { id: 4, type: "compliance", timestamp: "2026-02-27 09:15:30", message: "Conformity declaration generated.",
      icon: <div className="h-8 w-8 rounded-full bg-gold flex items-center justify-center"><ScaleIcon className="h-5 w-5 text-gold-foreground" /></div> },
    { id: 5, type: "anchor", timestamp: "2026-02-27 09:15:33", message: "Anchored to Base L2 via EAS. Tx confirmed.",
      icon: <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center"><LinkIcon className="h-5 w-5 text-primary-foreground" /></div> },
  ];

  return (
    <div className="p-0 h-full overflow-hidden border-b lg:border-b-0 lg:border-r">
      <motion.div variants={containerVariants} initial="initial" whileHover="whileHover" className="flex flex-col gap-y-5 items-center justify-between h-full w-full cursor-pointer">
        <div className="border-b items-center justify-center overflow-hidden bg-transparent rounded-t-xl h-4/5 w-full flex">
          <motion.div className="p-5 rounded-t-md cursor-pointer overflow-hidden h-[270px] flex flex-col gap-y-3.5 w-full">
            {logs.map((log, index) => (
              <motion.div
                key={log.id}
                className="p-4 bg-transparent backdrop-blur-md shadow-[0px_0px_40px_-25px_oklch(0.2_0.02_264_/_0.25)] border border-border origin-right w-full rounded-md flex items-center"
                custom={index}
                variants={{
                  initial: (i: number) => ({ y: 0, scale: i === 4 ? 0.9 : 1, opacity: 1, transition: { delay: 0.05, duration: 0.2, ease: cubicBezier(0.22, 1, 0.36, 1) } }),
                  whileHover: (i: number) => ({ y: -85, opacity: i === 4 ? 1 : 0.6, scale: i === 0 ? 0.85 : i === 4 ? 1.1 : 1, transition: { delay: 0.05, duration: 0.2, ease: cubicBezier(0.22, 1, 0.36, 1) } }),
                }}
                transition={{ type: "spring", damping: 40, stiffness: 600 }}
              >
                <div className="mr-3">{log.icon}</div>
                <div className="flex-grow">
                  <p className="text-foreground text-xs font-medium">[{log.timestamp}] {log.type.toUpperCase()}</p>
                  <p className="text-muted-foreground text-xs">{log.message}</p>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
        <div className="flex flex-col gap-y-1 px-5 pb-4 items-start w-full">
          <h2 className="font-semibold tracking-tight text-lg">Audit Trail</h2>
          <p className="text-sm text-muted-foreground">Hash-chained provenance tracking from identity to blockchain anchoring.</p>
        </div>
      </motion.div>
    </div>
  );
};

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

const Card3 = () => {
  const orbitVariant = {
    initial: { scale: 1, transition: { duration: 0.3, ease: "easeInOut" as const } },
    whileHover: {
      scale: 1.08,
      transition: { duration: 0.3, ease: "easeInOut" as const },
    },
  };
  const centerVariant = {
    initial: { scale: 1, transition: { duration: 0.2, ease: "easeInOut" as const } },
    whileHover: {
      scale: 1.25,
      transition: { duration: 0.2, ease: "easeInOut" as const },
    },
  };

  return (
    <div className="p-0 h-full overflow-hidden border-b lg:border-b-0">
      <motion.div
        variants={{ initial: {}, whileHover: { transition: { staggerChildren: 0.05 } } }}
        initial="initial"
        whileHover="whileHover"
        className="relative flex flex-col gap-y-5 items-center justify-between h-full w-full cursor-pointer"
      >
        <div className="border-b items-center justify-center overflow-hidden rounded-t-xl h-4/5 w-full flex">
          <motion.div variants={orbitVariant} className="relative flex items-center justify-center h-full w-full">
            <div className="absolute inset-0 bg-[radial-gradient(circle,oklch(0.46_0.24_264_/_0.08)_0%,transparent_60%)]"></div>
            <motion.span variants={centerVariant} className="z-10">
              <Icons.logo className="h-8 w-8" />
            </motion.span>

            {/* Inner ring (radius 55) - forward */}
            <OrbitingCircles radius={55} duration={22} delay={0} className="border-0 bg-transparent p-0 size-auto">
              <OrbitIcon Icon={FingerprintIcon} label="Identity" color="gold" />
            </OrbitingCircles>
            <OrbitingCircles radius={55} duration={22} delay={7} className="border-0 bg-transparent p-0 size-auto">
              <OrbitIcon Icon={KeyIcon} label="DID" color="gold" />
            </OrbitingCircles>
            <OrbitingCircles radius={55} duration={22} delay={14} className="border-0 bg-transparent p-0 size-auto">
              <OrbitIcon Icon={ContactIcon} label="Agent Cards" color="gold" />
            </OrbitingCircles>

            {/* Middle ring (radius 100) - reverse */}
            <OrbitingCircles radius={100} duration={28} delay={0} reverse className="border-0 bg-transparent p-0 size-auto">
              <OrbitIcon Icon={ShieldCheckIcon} label="Credentials" color="primary" />
            </OrbitingCircles>
            <OrbitingCircles radius={100} duration={28} delay={9} reverse className="border-0 bg-transparent p-0 size-auto">
              <OrbitIcon Icon={GitForkIcon} label="Delegation" color="primary" />
            </OrbitingCircles>
            <OrbitingCircles radius={100} duration={28} delay={18} reverse className="border-0 bg-transparent p-0 size-auto">
              <OrbitIcon Icon={ScaleIcon} label="Compliance" color="primary" />
            </OrbitingCircles>

            {/* Outer ring (radius 145) - forward */}
            <OrbitingCircles radius={145} duration={34} delay={0} className="border-0 bg-transparent p-0 size-auto">
              <OrbitIcon Icon={FileSearchIcon} label="Provenance" color="primary" />
            </OrbitingCircles>
            <OrbitingCircles radius={145} duration={34} delay={11} className="border-0 bg-transparent p-0 size-auto">
              <OrbitIcon Icon={StarIcon} label="Reputation" color="gold" />
            </OrbitingCircles>
            <OrbitingCircles radius={145} duration={34} delay={22} className="border-0 bg-transparent p-0 size-auto">
              <OrbitIcon Icon={LinkIcon} label="Blockchain" color="gold" />
            </OrbitingCircles>
          </motion.div>
        </div>
        <div className="flex flex-col gap-y-1 px-5 pb-4 items-start w-full">
          <h2 className="font-semibold tracking-tight text-lg">9-Module Ecosystem</h2>
          <p className="text-sm text-muted-foreground">Identity, DIDs, Credentials, Delegation, Compliance, Provenance, Reputation, Blockchain, and Agent Cards.</p>
        </div>
      </motion.div>
    </div>
  );
};

export function UseCases() {
  return (
    <Section id="use-cases" title="Use Cases">
      <div className="grid lg:grid-cols-3 h-full border border-b-0">
        <Card1 />
        <Card2 />
        <Card3 />
      </div>
    </Section>
  );
}
