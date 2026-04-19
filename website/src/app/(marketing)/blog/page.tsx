import BlogCard from "@/components/blog-card";
import { AtxEyebrow } from "@/components/atx/atx-eyebrow";
import { AtxSubstackSubscribe } from "@/components/atx/atx-substack-subscribe";
import { getBlogPosts } from "@/lib/blog";
import { siteConfig } from "@/lib/config";
import { constructMetadata } from "@/lib/utils";
import { RssIcon } from "lucide-react";

export const metadata = constructMetadata({
  title: "Blog",
  description: `Latest news and updates from ${siteConfig.name}.`,
});

export default async function Blog() {
  const allPosts = await getBlogPosts();
  const articles = allPosts.sort((a, b) =>
    b.publishedAt.localeCompare(a.publishedAt)
  );

  return (
    <section className="mx-auto max-w-[1320px] px-7 py-24">
      <div className="grid items-start gap-10 lg:grid-cols-[1fr_1.2fr]">
        <div>
          <AtxEyebrow>Writing</AtxEyebrow>
          <h1 className="mt-3 font-serif text-[clamp(36px,4.8vw,60px)] leading-[1.05] tracking-[-0.012em] text-atx-ink">
            Notes, releases,
            <br />
            <em className="italic text-atx-accent">field reports.</em>
          </h1>
        </div>
        <p className="text-[15px] leading-[1.65] text-atx-ink-mid">
          Release notes, research summaries, and updates from building
          attestation infrastructure for AI agents. Subscribe via RSS or JSON
          Feed.
        </p>
      </div>

      <div className="mt-6 flex flex-wrap items-center gap-4 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        <a
          href="/feed.xml"
          className="inline-flex items-center gap-1.5 transition-colors hover:text-atx-accent"
          title="RSS Feed"
        >
          <RssIcon className="h-3.5 w-3.5" />
          RSS
        </a>
        <span className="text-atx-ink-faint">/</span>
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

      <div className="mt-16">
        <AtxSubstackSubscribe />
      </div>
    </section>
  );
}
