import { getBlogPosts } from "@/lib/blog";
import { siteConfig } from "@/lib/config";
import { source } from "@/lib/source";
import { MetadataRoute } from "next";

export const dynamic = "force-static";

// Per-section priority weighting for generated docs routes.
const docsPriority: Record<string, number> = {
  "getting-started": 0.9,
  examples: 0.75,
  guides: 0.8,
  reference: 0.8,
  project: 0.6,
};

function docsPriorityFor(slug: readonly string[]): number {
  if (slug.length === 0) {
    return 0.9;
  }
  return docsPriority[slug[0]] ?? 0.7;
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const posts = await getBlogPosts();

  const blogRoutes = posts.map((post) => ({
    url: `${siteConfig.url}/blog/${post.slug}`,
    lastModified: new Date(post.publishedAt),
    changeFrequency: "monthly" as const,
    priority: 0.6,
  }));

  // Auto-generate routes for every docs MDX page so the sitemap stays in sync
  // with `content/docs/**` instead of being manually hand-maintained (which
  // previously surfaced only 4 of 17+ pages to crawlers). The `/docs` index is
  // listed above as a hardcoded high-priority entry, so skip any empty-slug
  // page here to avoid emitting a duplicate <url> for the same loc.
  const docsRoutes = source
    .getPages()
    .filter((page) => page.slugs.length > 0)
    .map((page) => ({
      url: `${siteConfig.url}${page.url}`,
      lastModified: new Date(),
      changeFrequency: "monthly" as const,
      priority: docsPriorityFor(page.slugs),
    }));

  return [
    {
      url: siteConfig.url,
      lastModified: new Date(),
      changeFrequency: "weekly",
      priority: 1.0,
    },
    {
      url: `${siteConfig.url}/blog`,
      lastModified: new Date(),
      changeFrequency: "weekly",
      priority: 0.8,
    },
    {
      url: `${siteConfig.url}/legal/privacy`,
      lastModified: new Date(),
      changeFrequency: "yearly",
      priority: 0.3,
    },
    {
      url: `${siteConfig.url}/legal/terms`,
      lastModified: new Date(),
      changeFrequency: "yearly",
      priority: 0.3,
    },
    {
      url: `${siteConfig.url}/legal/cookies`,
      lastModified: new Date(),
      changeFrequency: "yearly",
      priority: 0.3,
    },
    {
      url: `${siteConfig.url}/pricing`,
      lastModified: new Date(),
      changeFrequency: "monthly",
      priority: 0.7,
    },
    {
      url: `${siteConfig.url}/faq`,
      lastModified: new Date(),
      changeFrequency: "monthly",
      priority: 0.6,
    },
    {
      url: `${siteConfig.url}/community`,
      lastModified: new Date(),
      changeFrequency: "monthly",
      priority: 0.6,
    },
    {
      url: `${siteConfig.url}/docs`,
      lastModified: new Date(),
      changeFrequency: "weekly",
      priority: 0.9,
    },
    ...docsRoutes,
    {
      url: `${siteConfig.url}/cross-post`,
      lastModified: new Date(),
      changeFrequency: "monthly",
      priority: 0.4,
    },
    ...blogRoutes,
  ];
}
