import Link from "next/link";
import { RssIcon } from "lucide-react";
import { AtxSubstackSubscribe } from "@/components/atx/atx-substack-subscribe";
import { PostList } from "@/components/post-list";
import { getBlogPosts } from "@/lib/blog";
import { siteConfig } from "@/lib/config";
import { constructMetadata } from "@/lib/utils";

export const metadata = constructMetadata({
  title: "Blog",
  description: `Product notes, research, releases, and guides from ${siteConfig.name}.`,
});

const fmt = (d: string) =>
  new Date(d).toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" });

export default async function Blog() {
  const posts = (await getBlogPosts()).sort((a, b) => b.publishedAt.localeCompare(a.publishedAt));
  const latest = posts.slice(0, 4);

  return (
    <>
      <section className="px-6 pb-14 pt-16 text-center">
        <div className="mx-auto max-w-[860px]">
          <p className="text-[14px] font-medium text-atx-accent">From research to product</p>
          <h1 className="mt-3 text-[clamp(34px,5vw,52px)] font-normal leading-[1.09] tracking-[-0.03em] text-atx-ink [text-wrap:balance]">
            Attestix <span className="text-atx-accent">writing</span>
          </h1>
          <p className="mx-auto mt-5 max-w-[640px] text-[17.5px] leading-[1.6] text-atx-ink-mid [text-wrap:balance]">
            Product notes, research, release announcements, and guides from
            building verifiable evidence for AI agents.
          </p>
          <div className="mt-7 flex flex-wrap items-center justify-center gap-3">
            <Link
              href="/research"
              className="rounded-full bg-atx-accent px-6 py-3 text-[15px] font-medium text-[oklch(0.14_0.01_180)] transition-colors duration-200 hover:bg-atx-accent-deep"
            >
              Research and vision
            </Link>
            <a
              href="/feed.xml"
              className="inline-flex items-center gap-2 rounded-full border border-atx-line px-6 py-3 text-[15px] font-medium text-atx-ink-mid transition-colors duration-200 hover:border-atx-ink-dim hover:text-atx-ink"
            >
              <RssIcon className="h-4 w-4" /> RSS feed
            </a>
          </div>
        </div>
      </section>

      <section className="px-6 pb-16">
        <div className="mx-auto max-w-[1200px]">
          <p className="text-[14px] font-medium text-atx-accent">Highlights</p>
          <h2 className="mt-2 text-[32px] font-medium tracking-[-0.8px] text-atx-ink">Latest updates</h2>
          <div className="mt-6 grid gap-3 md:grid-cols-2 lg:grid-cols-4">
            {latest.map((p) => (
              <Link
                key={p.slug}
                href={`/blog/${p.slug}`}
                className="group flex min-h-[230px] flex-col rounded-2xl border border-atx-accent/25 bg-atx-accent/[0.05] p-5 transition-colors duration-200 hover:border-atx-accent/60"
              >
                <span className="text-[13px] text-atx-accent">{fmt(p.publishedAt)}</span>
                <span className="mt-2 text-[18px] font-medium leading-[1.3] tracking-[-0.4px] text-atx-ink">{p.title}</span>
                <span className="mt-2 line-clamp-2 text-[14px] leading-[1.5] text-atx-ink-mid">{p.summary}</span>
                <span className="mt-auto pt-4 text-[14px] font-medium text-atx-ink-mid group-hover:text-atx-ink">Read more &rarr;</span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="px-6 pb-20">
        <div className="mx-auto max-w-[1200px]">
          <PostList
            rows={posts.map((p) => ({ slug: p.slug, title: p.title, category: p.category, date: fmt(p.publishedAt) }))}
          />
          <div className="mt-16">
            <AtxSubstackSubscribe />
          </div>
        </div>
      </section>
    </>
  );
}
