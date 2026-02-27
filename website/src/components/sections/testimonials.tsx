"use client";

import { Section } from "@/components/section";
import { siteConfig } from "@/lib/config";
import { cn } from "@/lib/utils";
import { motion } from "motion/react";
import Image from "next/image";
import { QuoteIcon } from "lucide-react";

export function Testimonials() {
  return (
    <Section id="testimonials" title="From the Project">
      <div className="grid grid-cols-1 md:grid-cols-3 border border-b-0">
        {siteConfig.highlights.map((highlight, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.05 }}
            className={cn(
              "flex flex-col border-b md:border-b-0 md:border-r md:last:border-r-0",
              "transition-colors hover:bg-secondary/20"
            )}
          >
            <div className="px-4 py-5 sm:p-6 flex-grow flex flex-col">
              <QuoteIcon className="h-5 w-5 text-gold/40 mb-3 shrink-0" />
              <p className="text-muted-foreground text-sm leading-relaxed mb-4 flex-grow">
                {highlight.text}
              </p>
              <div className="flex items-center gap-3 pt-3 border-t border-border/50 mt-auto">
                {highlight.image && (
                  <Image
                    src={highlight.image}
                    alt={highlight.name}
                    width={36}
                    height={36}
                    className="w-9 h-9 rounded-full object-cover"
                  />
                )}
                {!highlight.image && (
                  <div className="w-9 h-9 rounded-full bg-primary/15 flex items-center justify-center shrink-0">
                    <span className="text-primary font-semibold text-sm">
                      {highlight.name.charAt(0)}
                    </span>
                  </div>
                )}
                <div>
                  <p className="text-sm font-medium text-foreground">
                    {highlight.name}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {highlight.role} · {highlight.company}
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </Section>
  );
}
