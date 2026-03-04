"use client";

import { Section } from "@/components/section";
import { MagicCard } from "@/components/ui/magic-card";
import { cn } from "@/lib/utils";
import { cubicBezier, motion } from "motion/react";
import {
  AwardIcon,
  FileCheckIcon,
  FingerprintIcon,
  FileSearchIcon,
  LinkIcon,
  ScaleIcon,
  ShieldCheckIcon,
  ShieldIcon,
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
    <div className="p-0 h-full overflow-hidden border-b lg:border-b-0">
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

export function UseCases() {
  return (
    <Section id="use-cases" title="Use Cases">
      <div className="grid grid-cols-1 lg:grid-cols-2 h-full border border-b-0">
        <MagicCard
          gradientColor="#4F46E5"
          gradientOpacity={0.15}
          gradientFrom="#4F46E5"
          gradientTo="#E1A32C"
          className="rounded-none"
        >
          <Card1 />
        </MagicCard>
        <MagicCard
          gradientColor="#E1A32C"
          gradientOpacity={0.15}
          gradientFrom="#E1A32C"
          gradientTo="#4F46E5"
          className="rounded-none"
        >
          <Card2 />
        </MagicCard>
      </div>
    </Section>
  );
}
