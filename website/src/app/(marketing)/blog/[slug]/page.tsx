import Author from "@/components/blog-author";
import { CtaV2 } from "@/components/sections/v2/cta-v2";
import { getBlogPosts, getPost } from "@/lib/blog";
import { siteConfig } from "@/lib/config";
import { formatDate } from "@/lib/utils";
import type { Metadata } from "next";
import Image from "next/image";
import { notFound } from "next/navigation";
import { Suspense } from "react";

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

export default async function Page(props: {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  const params = await props.params;
  const post = await getPost(params.slug);
  if (!post) {
    notFound();
  }
  // Reading time at 220 words per minute, counted from the rendered HTML.
  const wordCount = post.source
    .replace(/<[^>]+>/g, " ")
    .split(/\s+/)
    .filter(Boolean).length;
  const readingMinutes = Math.max(1, Math.ceil(wordCount / 220));
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
      <div className="mx-auto w-full max-w-[720px] px-6 pb-20 pt-16 md:pt-20">
        <header>
          <div className="flex flex-wrap items-center gap-x-2 text-[14px] text-atx-ink-dim">
            <time dateTime={post.metadata.publishedAt}>
              {formatDate(post.metadata.publishedAt)}
            </time>
            <span aria-hidden>&middot;</span>
            <span>{readingMinutes} min read</span>
          </div>
          <h1 className="mt-3 text-[clamp(34px,5vw,52px)] font-normal leading-[1.09] tracking-[-0.03em] text-atx-ink [text-wrap:balance]">
            {post.metadata.title}
          </h1>
          <div className="mt-6">
            <Author
              twitterUsername="vibetensor"
              name={post.metadata.author}
              image="https://avatars.githubusercontent.com/u/52927921?v=4"
            />
          </div>
        </header>
        <Suspense
          fallback={
            <div className="mt-10 h-64 w-full animate-pulse rounded-2xl bg-atx-panel"></div>
          }
        >
          {post.metadata.image && (
            <div className="mt-10">
              <Image
                width={1920}
                height={1080}
                src={post.metadata.image}
                alt={post.metadata.title}
                className="h-auto w-full rounded-2xl border border-atx-line"
              />
            </div>
          )}
        </Suspense>
        <article
          className="prose dark:prose-invert mt-10 max-w-none border-t border-atx-line-soft pt-10 prose-headings:text-atx-ink prose-h2:text-[24px] prose-h2:font-medium prose-h2:tracking-[-0.5px] prose-h3:text-[19px] prose-h3:font-semibold prose-h3:tracking-[-0.48px] prose-p:leading-[1.7] prose-p:text-atx-ink-mid prose-li:text-atx-ink-mid prose-strong:text-atx-ink prose-a:text-atx-accent prose-a:decoration-atx-line prose-a:underline-offset-4 hover:prose-a:decoration-atx-accent prose-code:font-mono-atx prose-code:text-atx-accent prose-pre:rounded-xl prose-pre:border prose-pre:border-atx-line-soft prose-pre:bg-atx-bg-sunken prose-blockquote:border-atx-accent/50 prose-blockquote:text-atx-ink-mid prose-hr:border-atx-line-soft prose-img:rounded-xl"
          dangerouslySetInnerHTML={{ __html: post.source }}
        ></article>
      </div>
      <CtaV2 />
    </section>
  );
}
