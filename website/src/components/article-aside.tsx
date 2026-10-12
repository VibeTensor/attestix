"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import type { Heading } from "@/lib/blog";

// Sticky article sidebar: back link, table of contents that tracks the
// section in view, share links, and "Copy as Markdown".
export function ArticleAside({
  headings,
  markdown,
  title,
  url,
}: {
  headings: Heading[];
  markdown: string;
  title: string;
  url: string;
}) {
  const [active, setActive] = useState(headings[0]?.id);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const els = headings.map((h) => document.getElementById(h.id)).filter(Boolean) as HTMLElement[];
    const io = new IntersectionObserver(
      (entries) => {
        const top = entries.filter((e) => e.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
        if (top) setActive(top.target.id);
      },
      { rootMargin: "-80px 0px -65% 0px" },
    );
    els.forEach((el) => io.observe(el));
    return () => io.disconnect();
  }, [headings]);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(`# ${title}\n\n${markdown}`);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch {
      // clipboard blocked; nothing to do
    }
  };

  const share = encodeURIComponent(url);
  return (
    <div className="lg:sticky lg:top-24">
      <Link href="/blog" className="text-[14px] text-atx-ink-dim transition-colors duration-200 hover:text-atx-ink">
        &larr; All posts
      </Link>

      {headings.length > 1 && (
        <nav aria-label="Table of contents" className="mt-8 hidden lg:block">
          <p className="text-[14px] font-medium text-atx-ink">Table of contents</p>
          <ul className="mt-3 space-y-2 border-l border-atx-line-soft">
            {headings.map((h) => (
              <li key={h.id}>
                <a
                  href={`#${h.id}`}
                  className={`-ml-px block border-l-2 pl-3 text-[13.5px] leading-[1.45] transition-colors duration-200 ${
                    active === h.id
                      ? "border-atx-accent text-atx-ink"
                      : "border-transparent text-atx-ink-dim hover:text-atx-ink-mid"
                  }`}
                >
                  {h.text}
                </a>
              </li>
            ))}
          </ul>
        </nav>
      )}

      <div className="mt-8 hidden lg:block">
        <p className="text-[14px] font-medium text-atx-ink">Share this article</p>
        <div className="mt-3 flex gap-4 text-[13px] text-atx-ink-mid">
          <a href={`https://x.com/intent/post?url=${share}&text=${encodeURIComponent(title)}`} target="_blank" rel="noopener noreferrer" className="hover:text-atx-ink">
            X
          </a>
          <a href={`https://www.linkedin.com/sharing/share-offsite/?url=${share}`} target="_blank" rel="noopener noreferrer" className="hover:text-atx-ink">
            LinkedIn
          </a>
        </div>
      </div>

      <button
        type="button"
        onClick={copy}
        className="mt-8 hidden w-full rounded-full bg-white px-5 py-3 text-[14px] font-medium text-[#111315] transition-shadow duration-200 hover:shadow-[0_8px_30px_rgba(230,172,61,0.3)] lg:block"
      >
        {copied ? "Copied" : "Copy as Markdown"}
      </button>
    </div>
  );
}
