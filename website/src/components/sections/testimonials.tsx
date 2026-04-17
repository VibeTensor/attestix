"use client";

import { Section } from "@/components/section";
import { siteConfig } from "@/lib/config";
import Marquee from "@/components/ui/marquee";
import {
  QuoteIcon,
  XIcon,
  MessageCircleQuestionIcon,
  MapPinIcon,
  CalendarIcon,
} from "lucide-react";
import { useState } from "react";

type Highlight = (typeof siteConfig.highlights)[number];

function ValidationBadge() {
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-primary/10 px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-primary ring-1 ring-primary/20">
      Problem Validation
    </span>
  );
}

function DetailModal({
  highlight,
  onClose,
}: {
  highlight: Highlight;
  onClose: () => void;
}) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div className="absolute inset-0 bg-background/80 backdrop-blur-sm" />
      <div
        className="relative w-full max-w-lg max-h-[85vh] overflow-y-auto rounded-xl border border-primary/20 bg-card p-6 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute right-4 top-4 rounded-full p-1 text-muted-foreground hover:text-foreground hover:bg-secondary/50 transition-colors"
        >
          <XIcon className="h-4 w-4" />
        </button>

        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div>
            <p className="text-sm font-medium text-foreground">
              {highlight.name}
            </p>
            <p className="text-xs text-muted-foreground">{highlight.role}</p>
            <p className="text-xs text-muted-foreground/70">
              {highlight.company}
            </p>
          </div>
          <ValidationBadge />
        </div>

        {/* Event and venue info */}
        {(highlight.event || highlight.venue) && (
          <div className="mb-4 flex flex-col gap-1.5 rounded-lg bg-secondary/20 px-3 py-2.5 border border-border/30">
            {highlight.event && (
              <div className="flex items-center gap-2">
                <CalendarIcon className="h-3 w-3 shrink-0 text-muted-foreground/60" />
                <span className="text-xs text-muted-foreground">
                  {highlight.event}
                </span>
              </div>
            )}
            {highlight.venue && (
              <div className="flex items-center gap-2">
                <MapPinIcon className="h-3 w-3 shrink-0 text-muted-foreground/60" />
                <span className="text-xs text-muted-foreground">
                  {highlight.venue}
                </span>
              </div>
            )}
          </div>
        )}

        {/* Question asked (if exists) */}
        {highlight.question && (
          <div className="mb-4 rounded-lg bg-secondary/30 p-4 border border-border/50">
            <div className="flex items-center gap-2 mb-2">
              <MessageCircleQuestionIcon className="h-3.5 w-3.5 text-gold" />
              <span className="text-xs font-semibold uppercase tracking-wider text-gold">
                {highlight.askedBy
                  ? `Asked by ${highlight.askedBy}`
                  : "Question Asked"}
              </span>
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed">
              {highlight.question}
            </p>
          </div>
        )}

        {/* The quote */}
        <div className="mb-4 rounded-lg p-4 border bg-primary/5 border-primary/10">
          <div className="flex items-center gap-2 mb-2">
            <QuoteIcon className="h-4 w-4 text-primary/40" />
            <span className="text-xs font-semibold uppercase tracking-wider text-primary/60">
              {highlight.name}&apos;s Response
            </span>
          </div>
          <p className="text-base font-medium text-foreground leading-relaxed">
            &ldquo;{highlight.text}&rdquo;
          </p>
        </div>

        {/* Detailed analysis */}
        {highlight.detail && (
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              What This Means for Attestix
            </span>
            <p className="mt-1.5 text-sm text-muted-foreground leading-relaxed">
              {highlight.detail}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

function TestimonialCard({
  highlight,
  onClick,
}: {
  highlight: Highlight;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="relative flex w-[320px] shrink-0 cursor-pointer flex-col rounded-xl border border-border p-5 text-left bg-card/50 backdrop-blur-sm transition-all hover:bg-card/80 hover:shadow-lg hover:border-primary/30"
    >
      {/* Badge row */}
      <div className="mb-3 flex items-center justify-between">
        <QuoteIcon className="h-4 w-4 text-primary/40" />
        <ValidationBadge />
      </div>

      {/* Quote text */}
      <p className="text-sm leading-relaxed text-foreground/90 flex-1">
        &ldquo;{highlight.text}&rdquo;
      </p>
      {highlight.context && (
        <p className="mt-2 text-xs italic text-muted-foreground/70">
          {highlight.context}
        </p>
      )}

      {/* Author info */}
      <div className="mt-4 border-t border-border/50 pt-3">
        <p className="text-sm font-medium text-foreground leading-tight">
          {highlight.name}
        </p>
        <p className="text-xs text-muted-foreground mt-0.5">
          {highlight.role}
        </p>
        {highlight.event && (
          <div className="mt-1.5 flex items-center gap-1.5">
            <CalendarIcon className="h-2.5 w-2.5 shrink-0 text-muted-foreground/40" />
            <span className="text-[10px] text-muted-foreground/50 truncate">
              {highlight.event}
            </span>
          </div>
        )}
      </div>
    </button>
  );
}

export function Testimonials() {
  const [selectedHighlight, setSelectedHighlight] = useState<Highlight | null>(
    null
  );

  const highlights = siteConfig.highlights;

  return (
    <>
      <Section
        id="testimonials"
        title="Voices on AI Agent Trust"
        subtitle="What People Are Saying"
        description="Researchers, founders, and industry leaders validating the need for verifiable trust infrastructure in AI agent systems."
      >
        <div className="relative border-x border-b overflow-hidden py-8">
          <Marquee pauseOnHover repeat={2} className="[--duration:45s] [--gap:1rem]">
            {highlights.map((highlight) => (
              <TestimonialCard
                key={highlight.id}
                highlight={highlight}
                onClick={() => setSelectedHighlight(highlight)}
              />
            ))}
          </Marquee>

          {/* Gradient fade on edges */}
          <div className="pointer-events-none absolute inset-y-0 left-0 w-24 bg-gradient-to-r from-background to-transparent" />
          <div className="pointer-events-none absolute inset-y-0 right-0 w-24 bg-gradient-to-l from-background to-transparent" />
        </div>
      </Section>

      {/* Detail modal */}
      {selectedHighlight && (
        <DetailModal
          highlight={selectedHighlight}
          onClose={() => setSelectedHighlight(null)}
        />
      )}
    </>
  );
}
