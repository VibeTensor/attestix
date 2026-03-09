"use client";

import Link from "next/link";
import { motion } from "motion/react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import type { RiskAssessment } from "./risk-engine";

interface StepResultProps {
  result: RiskAssessment;
  onStartOver: () => void;
}

export function StepResult({ result, onStartOver }: StepResultProps) {
  return (
    <div className="space-y-6">
      {/* Risk Level Card */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
        className={`rounded-xl border-2 p-6 sm:p-8 ${result.borderColor} ${result.bgColor}`}
      >
        <div className="flex flex-col sm:flex-row sm:items-center gap-4 mb-4">
          <RiskIcon level={result.level} className={result.iconColor} />
          <div>
            <Badge
              className={`mb-2 ${result.bgColor} ${result.color} border ${result.borderColor}`}
            >
              {result.level.toUpperCase()} RISK
            </Badge>
            <h2 className={`text-2xl font-bold ${result.color}`}>
              {result.title}
            </h2>
          </div>
        </div>
        <p className="text-sm text-muted-foreground leading-relaxed">
          {result.description}
        </p>
      </motion.div>

      {/* Applicable Articles */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.1, ease: "easeOut" }}
        className="rounded-lg border border-border bg-card p-6"
      >
        <h3 className="text-lg font-semibold text-foreground mb-3 flex items-center gap-2">
          <svg
            className="h-5 w-5 text-primary"
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
          Applicable EU AI Act Articles
        </h3>
        <ul className="space-y-2">
          {result.articles.map((article) => (
            <li
              key={article}
              className="flex items-start gap-2 text-sm text-muted-foreground"
            >
              <span className="mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-primary/60" />
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
        className="rounded-lg border border-border bg-card p-6"
      >
        <h3 className="text-lg font-semibold text-foreground mb-3 flex items-center gap-2">
          <svg
            className="h-5 w-5 text-primary"
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
          Key Obligations
        </h3>
        <ul className="space-y-2">
          {result.obligations.map((obligation) => (
            <li
              key={obligation}
              className="flex items-start gap-2 text-sm text-muted-foreground"
            >
              <span className="mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-primary/60" />
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
        <div className="rounded-lg border border-border bg-card p-6">
          <h3 className="text-sm font-semibold text-foreground mb-2 flex items-center gap-2">
            <svg
              className="h-4 w-4 text-primary"
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
            Compliance Timeline
          </h3>
          <p className="text-sm text-muted-foreground leading-relaxed">
            {result.timeline}
          </p>
        </div>

        {/* Fines */}
        <div className="rounded-lg border border-border bg-card p-6">
          <h3 className="text-sm font-semibold text-foreground mb-2 flex items-center gap-2">
            <svg
              className="h-4 w-4 text-primary"
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
            Potential Fines
          </h3>
          <p className="text-sm text-muted-foreground leading-relaxed">
            {result.fineRange}
          </p>
        </div>
      </motion.div>

      {/* CTA Section */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.4, ease: "easeOut" }}
        className="rounded-lg border border-primary/20 bg-primary/5 p-6 text-center"
      >
        <h3 className="text-lg font-semibold text-foreground mb-2">
          Automate your compliance with Attestix
        </h3>
        <p className="text-sm text-muted-foreground mb-4 max-w-lg mx-auto">
          Attestix provides 47 MCP tools for verifiable identity, W3C credentials, compliance
          declarations, audit trails, and more. Start automating your EU AI Act compliance today.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Button asChild>
            <Link href="/docs/getting-started">Get Started</Link>
          </Button>
          <Button variant="outline" onClick={onStartOver}>
            Start Over
          </Button>
        </div>
      </motion.div>

      {/* Disclaimer */}
      <p className="text-xs text-muted-foreground/60 text-center leading-relaxed max-w-xl mx-auto">
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
