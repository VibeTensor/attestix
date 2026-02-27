"use client";

import { Section } from "@/components/section";
import { AnimatePresence, motion } from "motion/react";

const standards = [
  { name: "W3C VCs", label: "W3C Verifiable Credentials" },
  { name: "W3C DIDs", label: "W3C Decentralized Identifiers" },
  { name: "UCAN", label: "UCAN Delegation" },
  { name: "Ed25519", label: "Ed25519 (RFC 8032)" },
  { name: "EU AI Act", label: "EU AI Act Compliance" },
  { name: "MCP", label: "Model Context Protocol" },
];

const standards2 = [
  { name: "A2A", label: "Agent-to-Agent Protocol" },
  { name: "Base L2", label: "Base L2 / EAS" },
  { name: "JSON-LD", label: "JSON-LD Context" },
  { name: "JWT", label: "JSON Web Tokens" },
  { name: "EAS", label: "Ethereum Attestation Service" },
  { name: "DID:key", label: "DID Key Method" },
];

import { useEffect, useState } from "react";

export function Logos() {
  const [currentSet, setCurrentSet] = useState(standards);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSet((prev) => (prev === standards ? standards2 : standards));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <Section id="logos">
      <div className="border-x border-t">
        <div className="text-center py-3 border-b">
          <p className="text-xs font-medium text-muted-foreground tracking-wider">
            Standards and Protocols Supported
          </p>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6">
          {standards.map((_, idx) => (
            <div
              key={idx}
              className="flex group items-center justify-center p-4 border-r border-t last:border-r-0 sm:last:border-r md:[&:nth-child(3n)]:border-r md:[&:nth-child(6n)]:border-r-0 md:[&:nth-child(3)]:border-r [&:nth-child(-n+2)]:border-t-0 sm:[&:nth-child(-n+3)]:border-t-0 sm:[&:nth-child(3n)]:border-r-0 md:[&:nth-child(-n+6)]:border-t-0 [&:nth-child(2n)]:border-r-0 sm:[&:nth-child(2n)]:border-r"
            >
              <AnimatePresence mode="wait">
                <motion.div
                  key={currentSet[idx]?.name}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  transition={{
                    duration: 0.5,
                    ease: "easeInOut",
                    delay: Math.random() * 0.5,
                  }}
                  className="flex flex-col items-center gap-1"
                  title={currentSet[idx]?.label}
                >
                  <span className="text-sm font-semibold text-foreground/60 group-hover:text-gold transition-colors duration-200">
                    {currentSet[idx]?.name}
                  </span>
                </motion.div>
              </AnimatePresence>
            </div>
          ))}
        </div>
      </div>
    </Section>
  );
}
