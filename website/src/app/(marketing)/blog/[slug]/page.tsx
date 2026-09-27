import { ArticleAside } from "@/components/article-aside";
import { getBlogPosts, getPost } from "@/lib/blog";
import { siteConfig } from "@/lib/config";
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

export async function generateStaticParams() {
  const posts = await getBlogPosts();
  return posts.map((post) => ({ slug: post.slug }));
}

export async function generateMetadata(props: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata | undefined> {
  const params = await props.params;
  let post = await getPost(params.slug);
  let {
    title,
    publishedAt: publishedTime,
    summary: description,
    image,
  } = post.metadata;

  return {
    title,
    description,
    openGraph: {
      title,
      description,
      type: "article",
      publishedTime,
      url: `${siteConfig.url}/blog/${post.slug}`,
      images: [
        {
          url: image,
        },
      ],
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      images: [image],
    },
  };
}

// Absolute dates: relative ones ("3mo ago") go stale on a static site.
const formatDate = (d: string) =>
  new Date(d).toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" });

export default async function Page(props: {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  const params = await props.params;
  const post = await getPost(params.slug);
  if (!post) {
    notFound();
  }
  const more = (await getBlogPosts())
    .filter((p) => p.slug !== post.slug)
    .sort((a, b) => new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime())
    .slice(0, 3);
  const url = `${siteConfig.url}/blog/${post.slug}`;
  return (
    <section id="blog">
      <script
        type="application/ld+json"
        suppressHydrationWarning
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            headline: post.metadata.title,
            datePublished: post.metadata.publishedAt,
            dateModified: post.metadata.publishedAt,
            description: post.metadata.summary,
            image: post.metadata.image
              ? `${siteConfig.url}${post.metadata.image}`
              : `${siteConfig.url}/blog/${post.slug}/opengraph-image`,
            url: `${siteConfig.url}/blog/${post.slug}`,
            author: {
              "@type": "Person",
              name: post.metadata.author,
            },
          }),
        }}
      />
      <div className="mx-auto grid w-full max-w-[1200px] gap-10 px-6 pb-20 pt-12 lg:grid-cols-[250px_minmax(0,1fr)] lg:gap-16">
        <aside>
          <ArticleAside headings={post.headings} markdown={post.markdown} title={post.metadata.title} url={url} />
        </aside>

        <div className="max-w-[760px]">
          <header>
            <div className="flex flex-wrap items-center gap-3 text-[13px] text-atx-ink-dim">
              {post.metadata.category && (
                <span className="rounded-full bg-atx-accent/15 px-2.5 py-0.5 font-medium text-atx-accent">
                  {post.metadata.category}
                </span>
              )}
              <span>{post.minutes} min read</span>
            </div>
            <h1 className="mt-4 text-[clamp(32px,4.4vw,46px)] font-normal leading-[1.1] tracking-[-0.03em] text-atx-ink [text-wrap:balance]">
              {post.metadata.title}
            </h1>
            <div className="mt-6 flex flex-wrap gap-x-10 gap-y-3 border-b border-atx-line-soft pb-6 text-[13px]">
              <div>
                <p className="text-atx-ink-dim">Published on</p>
                <time dateTime={post.metadata.publishedAt} className="mt-0.5 block text-atx-ink">
                  {formatDate(post.metadata.publishedAt)}
                </time>
              </div>
              <div>
                <p className="text-atx-ink-dim">Written by</p>
                <p className="mt-0.5 text-atx-ink">{post.metadata.author}</p>
              </div>
            </div>
          </header>

          <article
            className="prose dark:prose-invert mt-8 max-w-none prose-headings:scroll-mt-24 prose-headings:text-atx-ink prose-h2:mt-12 prose-h2:border-l-2 prose-h2:border-atx-accent prose-h2:pl-4 prose-h2:text-[26px] prose-h2:font-normal prose-h2:tracking-[-0.6px] prose-h3:text-[19px] prose-h3:font-semibold prose-h3:tracking-[-0.48px] prose-p:leading-[1.7] prose-p:text-atx-ink-mid prose-li:text-atx-ink-mid prose-strong:text-atx-ink prose-a:text-atx-accent prose-a:decoration-atx-line prose-a:underline-offset-4 hover:prose-a:decoration-atx-accent prose-code:font-mono-atx prose-code:text-atx-accent prose-pre:rounded-xl prose-pre:border prose-pre:border-atx-line-soft prose-pre:bg-atx-bg-sunken prose-blockquote:border-atx-accent/50 prose-blockquote:text-atx-ink-mid prose-hr:border-atx-line-soft prose-img:rounded-xl prose-img:border prose-img:border-atx-line"
            dangerouslySetInnerHTML={{ __html: post.source }}
          ></article>
        </div>
      </div>

      {more.length > 0 && (
        <div className="border-t border-atx-line-soft bg-atx-bg-elev py-16">
          <div className="mx-auto max-w-[1200px] px-6">
            <p className="text-[14px] font-medium text-atx-accent">Keep reading</p>
            <h2 className="mt-2 text-[32px] font-medium tracking-[-0.8px] text-atx-ink">More from Attestix</h2>
            <div className="mt-8 grid gap-4 md:grid-cols-3">
              {more.map((p) => (
                <Link
                  key={p.slug}
                  href={`/blog/${p.slug}`}
                  className="group flex flex-col rounded-2xl border border-atx-accent/25 bg-atx-accent/[0.04] p-6 transition-colors duration-200 hover:border-atx-accent/60"
                >
                  <span className="text-[13px] text-atx-accent">{formatDate(p.publishedAt)}</span>
                  <span className="mt-2 text-[19px] font-medium leading-[1.3] tracking-[-0.4px] text-atx-ink">{p.title}</span>
                  <span className="mt-2 line-clamp-3 text-[14px] leading-[1.55] text-atx-ink-mid">{p.summary}</span>
                  <span className="mt-auto pt-5 text-[14px] font-medium text-atx-ink-mid group-hover:text-atx-ink">Read more &rarr;</span>
                </Link>
              ))}
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
