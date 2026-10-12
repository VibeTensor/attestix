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

      <div className="mt-6 flex flex-wrap items-center gap-4 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        {/* oxlint-disable-next-line nextjs/no-html-link-for-pages -- Feed document is not a Next page. */}
        <a
          href="/feed.xml"
          className="inline-flex items-center gap-1.5 transition-colors hover:text-atx-accent"
          title="RSS Feed"
        >
          <RssIcon className="h-3.5 w-3.5" />
          RSS
        </a>
        <span className="text-atx-ink-faint">/</span>
        {/* oxlint-disable-next-line nextjs/no-html-link-for-pages -- Feed document is not a Next page. */}
        <a
          href="/feed.json"
          className="inline-flex items-center gap-1.5 transition-colors hover:text-atx-accent"
          title="JSON Feed"
        >
          JSON feed
        </a>
      </div>

      <div className="mt-14 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {articles.map((data, idx) => (
          <BlogCard key={data.slug} data={data} priority={idx <= 1} />
        ))}
      </div>

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
