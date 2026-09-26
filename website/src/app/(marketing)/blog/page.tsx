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
    <>
      <section className="px-6 pb-12 pt-16 text-center md:pt-20">
        <div className="mx-auto max-w-[860px]">
          <AtxEyebrow>Writing</AtxEyebrow>
          <h1 className="mt-3 text-[clamp(34px,5vw,52px)] font-normal leading-[1.09] tracking-[-0.03em] text-atx-ink [text-wrap:balance]">
            Notes, releases, <span className="text-atx-accent">field reports.</span>
          </h1>
          <p className="mx-auto mt-5 max-w-[640px] text-[17.5px] leading-[1.6] text-atx-ink-mid [text-wrap:balance]">
            Release notes, research summaries, and updates from building
            attestation infrastructure for AI agents. Subscribe via RSS or JSON
            Feed.
          </p>
          <div className="mt-6 flex flex-wrap items-center justify-center gap-4 text-[14px] font-medium text-atx-ink-mid">
            <a
              href="/feed.xml"
              className="inline-flex items-center gap-1.5 underline decoration-atx-line underline-offset-4 transition-colors duration-200 hover:text-atx-ink hover:decoration-atx-ink-dim"
              title="RSS Feed"
            >
              <RssIcon className="h-3.5 w-3.5" />
              RSS
            </a>
            <span aria-hidden className="text-atx-ink-faint">/</span>
            <a
              href="/feed.json"
              className="inline-flex items-center gap-1.5 underline decoration-atx-line underline-offset-4 transition-colors duration-200 hover:text-atx-ink hover:decoration-atx-ink-dim"
              title="JSON Feed"
            >
              JSON feed
            </a>
          </div>
        </div>
      </section>

      <section className="bg-atx-bg pb-20">
        <div className="mx-auto w-full max-w-[1200px] px-6">
          <div className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3">
            {articles.map((data, idx) => (
              <BlogCard key={data.slug} data={data} priority={idx <= 1} />
            ))}
          </div>

          <div className="mt-16">
            <AtxSubstackSubscribe />
          </div>
        </div>
      </section>
    </>
  );
}
