import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { getBlogPosts } from "@/lib/blog";
import { constructMetadata } from "@/lib/utils";

export const metadata = constructMetadata({
  title: "Research",
  description:
    "Why Attestix exists, where it is going, and the research behind it: the product vision, the paper, and technical notes.",
});

const minutes = (html: string) =>
  Math.max(1, Math.ceil(html.replace(/<[^>]+>/g, " ").split(/\s+/).filter(Boolean).length / 220));

const fmt = (d: string) =>
  new Date(d).toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" });

function Tag({ children }: { children: React.ReactNode }) {
  return (
    <span className="rounded-full border border-atx-line px-2.5 py-0.5 text-[12px] text-atx-ink-mid">
      {children}
    </span>
  );
}

export default async function ResearchPage() {
  const posts = (await getBlogPosts()).sort(
    (a, b) => new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime(),
  );
  const vision = posts.find((p) => p.slug === "product-vision");
  const notes = posts.filter((p) => p.slug !== "product-vision");

  return (
    <section className="mx-auto max-w-[1200px] px-6 pb-20 pt-16">
      <div className="text-center">
        <p className="text-[14px] font-medium text-atx-accent">Research</p>
        <h1 className="mt-3 text-[clamp(34px,5vw,52px)] font-normal leading-[1.09] tracking-[-0.03em] text-atx-ink [text-wrap:balance]">
          Why Attestix exists, and where it is going
        </h1>
        <p className="mx-auto mt-5 max-w-[640px] text-[17.5px] leading-[1.6] text-atx-ink-mid [text-wrap:balance]">
          The product vision, the research paper, and the technical notes behind
          verifiable evidence for AI agents.
        </p>
      </div>

      <div className="mt-14 grid gap-4 lg:grid-cols-2">
        {vision && (
          <Link
            href={`/blog/${vision.slug}`}
            className="group rounded-2xl border border-atx-accent/30 bg-atx-accent/[0.05] p-7 transition-colors duration-200 hover:border-atx-accent/60"
          >
            <div className="flex items-center gap-3 text-[13px] text-atx-ink-dim">
              <Tag>Product</Tag> {fmt(vision.publishedAt)} &middot; {minutes(vision.source)} min read
            </div>
            <h2 className="mt-4 text-[26px] font-medium tracking-[-0.6px] text-atx-ink">{vision.title}</h2>
            <p className="mt-3 text-[15px] leading-[1.6] text-atx-ink-mid">{vision.summary}</p>
            <span className="mt-5 inline-flex items-center gap-1.5 text-[14px] font-medium text-atx-accent">
              Read <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" />
            </span>
          </Link>
        )}
        <Link
          href="/research/paper"
          className="group rounded-2xl border border-atx-info/30 bg-atx-info/[0.05] p-7 transition-colors duration-200 hover:border-atx-info/60"
        >
          <div className="flex items-center gap-3 text-[13px] text-atx-ink-dim">
            <Tag>Research</Tag> IEEE format &middot; peer review in progress
          </div>
          <h2 className="mt-4 text-[26px] font-medium tracking-[-0.6px] text-atx-ink">
            Attestation infrastructure for AI agents
          </h2>
          <p className="mt-3 text-[15px] leading-[1.6] text-atx-ink-mid">
            The paper behind Attestix: agent identity tokens, W3C Verifiable
            Credentials, and a hash-chained audit trail, evaluated against five
            open standards and ten EU AI Act articles.
          </p>
          <span className="mt-5 inline-flex items-center gap-1.5 text-[14px] font-medium text-atx-info">
            Read <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" />
          </span>
        </Link>
      </div>

      <h2 className="mt-16 text-[14px] font-medium text-atx-ink-mid">Notes and releases</h2>
      <div className="mt-4 divide-y divide-atx-line-soft border-y border-atx-line-soft">
        {notes.map((p) => (
          <Link
            key={p.slug}
            href={`/blog/${p.slug}`}
            className="group grid gap-2 py-5 transition-colors duration-200 md:grid-cols-[180px_1fr_auto] md:items-baseline md:gap-6"
          >
            <span className="text-[13px] text-atx-ink-dim">{fmt(p.publishedAt)}</span>
            <span>
              <span className="block text-[17px] text-atx-ink transition-colors group-hover:text-atx-accent">
                {p.title}
              </span>
              <span className="mt-1 block text-[14px] leading-[1.55] text-atx-ink-mid">{p.summary}</span>
            </span>
            <span className="text-[13px] text-atx-ink-dim">{minutes(p.source)} min read</span>
          </Link>
        ))}
      </div>
    </section>
  );
}
