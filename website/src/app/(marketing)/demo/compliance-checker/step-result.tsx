"use client";

import Link from "next/link";
import { motion } from "motion/react";
import type { RiskAssessment } from "./risk-engine";

interface StepResultProps {
  result: RiskAssessment;
  onStartOver: () => void;
}

export function StepResult({ result, onStartOver }: StepResultProps) {
  return (
    <div className="space-y-6">
      {/* Top-of-page legal advisory (not a footer disclaimer) */}
      <div className="rounded-2xl border border-atx-warn/30 bg-atx-warn/[0.05] p-5 text-[14px] text-atx-ink-mid">
        <div className="font-semibold text-atx-warn">Educational tool, not legal advice.</div>
        <div className="mt-1 leading-[1.6]">
          The classification below is a first-pass heuristic. It does not
          replace a qualified EU AI Act lawyer. Your actual obligations depend
          on your full system design, deployment context, and intended use.
        </div>
      </div>

      {/* Risk Level Card */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
        className={`rounded-2xl border p-6 sm:p-8 ${result.borderColor} ${result.bgColor}`}
      >
        <div className="flex flex-col sm:flex-row sm:items-center gap-4 mb-4">
          <RiskIcon level={result.level} className={result.iconColor} />
          <div>
            <span
              className={`mb-2 inline-flex rounded-full border px-3 py-0.5 text-[13px] font-medium ${result.bgColor} ${result.color} ${result.borderColor}`}
            >
              {result.level.toUpperCase()} RISK
            </span>
            <h2 className={`text-[32px] font-medium leading-[1.15] tracking-[-0.8px] ${result.color}`}>
              {result.title}
            </h2>
          </div>
        </div>
        <p className="text-[15px] leading-[1.6] text-atx-ink-mid">
          {result.description}
        </p>
      </motion.div>

      {/* Applicable Articles */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.1, ease: "easeOut" }}
        className="rounded-2xl border border-atx-line bg-atx-panel/60 p-6"
      >
        <h3 className="mb-3 flex items-center gap-2 text-[19px] font-semibold tracking-[-0.48px] text-atx-ink">
          <svg
            className="h-5 w-5 text-atx-accent"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25"
            />
          </svg>
          Applicable EU AI Act articles
        </h3>
        <ul className="space-y-2">
          {result.articles.map((article) => (
            <li
              key={article}
              className="flex items-start gap-2 text-[15px] leading-[1.6] text-atx-ink-mid"
            >
              <span className="mt-2.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-atx-accent/70" />
              {article}
            </li>
          ))}
        </ul>
      </motion.div>

      {/* Key Obligations */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.2, ease: "easeOut" }}
        className="rounded-2xl border border-atx-line bg-atx-panel/60 p-6"
      >
        <h3 className="mb-3 flex items-center gap-2 text-[19px] font-semibold tracking-[-0.48px] text-atx-ink">
          <svg
            className="h-5 w-5 text-atx-accent"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z"
            />
          </svg>
          Key obligations
        </h3>
        <ul className="space-y-2">
          {result.obligations.map((obligation) => (
            <li
              key={obligation}
              className="flex items-start gap-2 text-[15px] leading-[1.6] text-atx-ink-mid"
            >
              <span className="mt-2.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-atx-accent/70" />
              {obligation}
            </li>
          ))}
        </ul>
      </motion.div>

      {/* Timeline and Fines */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.3, ease: "easeOut" }}
        className="grid gap-4 sm:grid-cols-2"
      >
        {/* Timeline */}
        <div className="rounded-2xl border border-atx-line bg-atx-panel/60 p-6">
          <h3 className="mb-2 flex items-center gap-2 text-[15px] font-semibold text-atx-ink">
            <svg
              className="h-4 w-4 text-atx-accent"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            Compliance timeline
          </h3>
          <p className="text-[15px] leading-[1.6] text-atx-ink-mid">
            {result.timeline}
          </p>
        </div>

        {/* Fines */}
        <div className="rounded-2xl border border-atx-line bg-atx-panel/60 p-6">
          <h3 className="mb-2 flex items-center gap-2 text-[15px] font-semibold text-atx-ink">
            <svg
              className="h-4 w-4 text-atx-accent"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
              />
            </svg>
            Potential fines
          </h3>
          <p className="text-[15px] leading-[1.6] text-atx-ink-mid">
            {result.fineRange}
          </p>
        </div>
      </motion.div>

      {/* CTA Section */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.4, ease: "easeOut" }}
        className="rounded-2xl border border-atx-accent/30 bg-atx-accent/[0.05] p-8 text-center"
      >
        <h3 className="mb-2 text-[19px] font-semibold tracking-[-0.48px] text-atx-ink">
          Automate your compliance with Attestix
        </h3>
        <p className="mx-auto mb-6 max-w-[520px] text-[15px] leading-[1.6] text-atx-ink-mid">
          Attestix provides 47 MCP tools for verifiable identity, W3C credentials, compliance
          declarations, audit trails, and more. Start automating your EU AI Act compliance today.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Link
            href="/docs/getting-started"
            className="inline-flex items-center justify-center rounded-full bg-atx-accent px-6 py-3 text-[15px] font-medium text-[oklch(0.14_0.01_180)] transition-colors duration-200 hover:bg-atx-accent-deep"
          >
            Get started
          </Link>
          <button
            type="button"
            onClick={onStartOver}
            className="inline-flex items-center justify-center rounded-full border border-atx-line px-6 py-3 text-[15px] font-medium text-atx-ink-mid transition-colors duration-200 hover:border-atx-ink-dim hover:text-atx-ink"
          >
            Start over
          </button>
        </div>
      </motion.div>

      {/* Disclaimer */}
      <p className="mx-auto max-w-[640px] text-center text-[13px] leading-[1.6] text-atx-ink-dim">
        This tool provides a general assessment based on the information you provided. It is not
        legal advice. For definitive classification of your AI system, consult with qualified legal
        counsel who specializes in EU AI Act compliance.
      </p>
    </div>
  );
}

function RiskIcon({
  level,
  className,
}: {
  level: string;
  className: string;
}) {
  if (level === "unacceptable") {
    return (
      <svg
        className={`h-12 w-12 ${className}`}
        fill="none"
        viewBox="0 0 24 24"
        strokeWidth={1.5}
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"
        />
      </svg>
    );
  }

  if (level === "high") {
    return (
      <svg
        className={`h-12 w-12 ${className}`}
        fill="none"
        viewBox="0 0 24 24"
        strokeWidth={1.5}
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
        />
      </svg>
    );
  }

  if (level === "limited") {
    return (
      <svg
        className={`h-12 w-12 ${className}`}
        fill="none"
        viewBox="0 0 24 24"
        strokeWidth={1.5}
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"
        />
      </svg>
    );
  }

  // minimal
  return (
    <svg
      className={`h-12 w-12 ${className}`}
      fill="none"
      viewBox="0 0 24 24"
      strokeWidth={1.5}
      stroke="currentColor"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
      />
    </svg>
  );
}
