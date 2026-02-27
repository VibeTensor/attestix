import BlogCard from "@/components/blog-card";
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

  const articles = await Promise.all(
    allPosts.sort((a, b) => b.publishedAt.localeCompare(a.publishedAt))
  );

  return (
    <>
      <div className="mx-auto w-full max-w-screen-xl px-2.5 lg:px-20 mt-24">
        <div className="text-center py-16">
          <h1 className="text-3xl font-bold text-foreground sm:text-4xl">
            Articles
          </h1>
          <p className="mt-4 text-xl text-muted-foreground">
            Latest news and updates from {siteConfig.name}
          </p>
          <div className="mt-4 flex justify-center gap-3">
            <a
              href="/feed.xml"
              className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
              title="RSS Feed"
            >
              <RssIcon className="h-4 w-4" />
              RSS
            </a>
            <span className="text-muted-foreground/40">|</span>
            <a
              href="/feed.json"
              className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
              title="JSON Feed"
            >
              JSON Feed
            </a>
          </div>
        </div>
      </div>
      <div className="min-h-[50vh] bg-secondary/30 backdrop-blur-lg">
        <div className="mx-auto grid w-full max-w-screen-xl grid-cols-1 gap-8 px-2.5 py-10 lg:px-20 lg:grid-cols-3">
          {articles.map((data, idx) => (
            <BlogCard key={data.slug} data={data} priority={idx <= 1} />
          ))}
        </div>
      </div>
    </>
  );
}
