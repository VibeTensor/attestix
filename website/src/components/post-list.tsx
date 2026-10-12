"use client";

import Link from "next/link";
import { useState } from "react";

type Row = { slug: string; title: string; category?: string; date: string };

// "All posts" list with category filter pills.
export function PostList({ rows }: { rows: Row[] }) {
  const cats = ["All", ...Array.from(new Set(rows.map((r) => r.category).filter(Boolean) as string[]))];
  const [cat, setCat] = useState("All");
  const shown = cat === "All" ? rows : rows.filter((r) => r.category === cat);

  return (
    <div>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-[14px] font-medium text-atx-accent">Archive</p>
          <h2 className="mt-2 text-[32px] font-medium tracking-[-0.8px] text-atx-ink">All posts</h2>
        </div>
        <div className="flex flex-wrap gap-2">
          {cats.map((c) => (
            <button
              key={c}
              type="button"
              aria-pressed={cat === c}
              onClick={() => setCat(c)}
              className={`rounded-full border px-3.5 py-1 text-[13px] font-medium transition-colors duration-200 ${
                cat === c
                  ? "border-atx-accent bg-atx-accent/15 text-atx-accent"
                  : "border-atx-line text-atx-ink-mid hover:border-atx-ink-dim hover:text-atx-ink"
              }`}
            >
              {c}
            </button>
          ))}
        </div>
      </div>
      <div className="mt-6 divide-y divide-atx-line-soft border-y border-atx-line-soft">
        {shown.map((r) => (
          <Link
            key={r.slug}
            href={`/blog/${r.slug}`}
            className="group grid items-baseline gap-1 py-4 transition-colors duration-200 md:grid-cols-[1fr_auto_140px] md:gap-6"
          >
            <span className="text-[17px] text-atx-ink-mid transition-colors group-hover:text-atx-ink">{r.title}</span>
            <span className="text-[13px] text-atx-accent">{r.category}</span>
            <span className="text-[13px] text-atx-ink-dim md:text-right">{r.date}</span>
          </Link>
        ))}
      </div>
    </div>
  );
}
