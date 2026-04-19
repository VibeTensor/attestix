"use client";

import { useEffect, useState } from "react";

const TARGET_UTC = Date.UTC(2026, 7, 2, 0, 0, 0);

function compute() {
  const now = Date.now();
  const diff = Math.max(0, TARGET_UTC - now);
  const days = Math.floor(diff / (24 * 60 * 60 * 1000));
  const hours = Math.floor((diff / (60 * 60 * 1000)) % 24);
  const minutes = Math.floor((diff / (60 * 1000)) % 60);
  return { days, hours, minutes };
}

export function AtxCountdown() {
  const [t, setT] = useState<{ days: number; hours: number; minutes: number } | null>(null);

  useEffect(() => {
    setT(compute());
    const id = window.setInterval(() => setT(compute()), 60_000);
    return () => window.clearInterval(id);
  }, []);

  if (!t) {
    return <span className="font-mono-atx text-atx-ink">Aug 2, 2026</span>;
  }

  if (t.days === 0 && t.hours === 0 && t.minutes === 0) {
    return (
      <strong className="font-mono-atx text-atx-err">
        Enforcement active
      </strong>
    );
  }

  return (
    <span className="font-mono-atx text-atx-ink">
      {t.days}d {t.hours}h {t.minutes}m
    </span>
  );
}
