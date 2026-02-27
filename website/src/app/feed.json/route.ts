import { getBlogPosts } from "@/lib/blog";
import { siteConfig } from "@/lib/config";

export const dynamic = "force-static";

export async function GET() {
  const posts = await getBlogPosts();
  const sorted = posts.sort(
    (a, b) =>
      new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime()
  );

  const baseUrl = siteConfig.url;

  const feed = {
    version: "https://jsonfeed.org/version/1.1",
    title: siteConfig.name,
    home_page_url: baseUrl,
    feed_url: `${baseUrl}/feed.json`,
    description: siteConfig.description,
    language: "en-US",
    icon: `${baseUrl}/atx_gold.svg`,
    authors: [
      {
        name: "VibeTensor",
        url: "https://vibetensor.com",
      },
    ],
    items: sorted.map((post) => ({
      id: `${baseUrl}/blog/${post.slug}`,
      url: `${baseUrl}/blog/${post.slug}`,
      title: post.title,
      summary: post.summary,
      date_published: new Date(post.publishedAt).toISOString(),
      authors: [{ name: post.author }],
    })),
  };

  return new Response(JSON.stringify(feed, null, 2), {
    headers: {
      "Content-Type": "application/feed+json; charset=utf-8",
      "Cache-Control": "public, max-age=3600, s-maxage=3600",
    },
  });
}
