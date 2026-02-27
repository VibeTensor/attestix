import { siteConfig } from "@/lib/config";
import { constructMetadata } from "@/lib/utils";
import { Header } from "@/components/sections/header";
import { Footer } from "@/components/sections/footer";
import Link from "next/link";

export const metadata = constructMetadata({
  title: "Cross-Post Guide",
  description:
    "How to syndicate Attestix blog posts to Dev.to, Hashnode, and other platforms with proper canonical URLs.",
});

export default function CrossPostGuide() {
  const baseUrl = siteConfig.url;

  return (
    <>
      <Header />
      <main className="container max-w-3xl mx-auto px-4 py-24">
        <article className="prose dark:prose-invert prose-headings:text-foreground prose-p:text-muted-foreground prose-strong:text-foreground prose-a:text-primary prose-code:text-primary max-w-none">
          <h1>Cross-Posting Guide</h1>
          <p>
            This guide covers how to syndicate Attestix blog posts to external
            platforms while preserving SEO value on our primary domain. The
            golden rule: always publish on {baseUrl} first, wait for Google to
            index it, then cross-post with canonical URLs pointing back.
          </p>

          <h2>Syndication Workflow</h2>
          <ol>
            <li>
              <strong>Publish on attestix.vibetensor.com</strong> - Create the
              MDX file in <code>content/</code>, deploy, and verify the post is
              live
            </li>
            <li>
              <strong>Wait 5-7 days</strong> - Allow Google to crawl and index
              the original post. Verify indexing via{" "}
              <code>site:attestix.vibetensor.com/blog/your-slug</code> in Google
              Search
            </li>
            <li>
              <strong>Cross-post with canonical URL</strong> - Publish on Dev.to
              and/or Hashnode with the canonical URL set to the original post
            </li>
          </ol>

          <h2>Dev.to</h2>
          <p>
            Dev.to supports canonical URLs natively in their editor frontmatter.
          </p>
          <h3>Manual Process</h3>
          <ol>
            <li>
              Go to{" "}
              <a
                href="https://dev.to/new"
                target="_blank"
                rel="noopener noreferrer"
              >
                dev.to/new
              </a>
            </li>
            <li>
              Add canonical URL in the frontmatter at the top of the editor:
            </li>
          </ol>
          <pre>
            <code>{`---
title: Your Post Title
published: true
tags: ai, agents, compliance, opensource
canonical_url: ${baseUrl}/blog/your-slug
---

Your content here (paste the markdown from the MDX file)`}</code>
          </pre>
          <h3>Via API</h3>
          <p>
            Dev.to provides an API for automated publishing. Generate an API key
            at{" "}
            <a
              href="https://dev.to/settings/extensions"
              target="_blank"
              rel="noopener noreferrer"
            >
              dev.to/settings/extensions
            </a>
            , then use:
          </p>
          <pre>
            <code>{`curl -X POST https://dev.to/api/articles \\
  -H "Content-Type: application/json" \\
  -H "api-key: YOUR_DEV_TO_API_KEY" \\
  -d '{
    "article": {
      "title": "Your Post Title",
      "body_markdown": "Your markdown content",
      "published": true,
      "tags": ["ai", "agents", "compliance", "opensource"],
      "canonical_url": "${baseUrl}/blog/your-slug"
    }
  }'`}</code>
          </pre>

          <h2>Hashnode</h2>
          <p>
            Hashnode supports canonical URLs via their editor and API.
          </p>
          <h3>Manual Process</h3>
          <ol>
            <li>Create a new article on your Hashnode blog</li>
            <li>
              In the article settings (gear icon), find{" "}
              <strong>Are you republishing?</strong>
            </li>
            <li>
              Paste the canonical URL:{" "}
              <code>{baseUrl}/blog/your-slug</code>
            </li>
            <li>Publish</li>
          </ol>
          <h3>Via API (GraphQL)</h3>
          <pre>
            <code>{`mutation {
  publishPost(input: {
    title: "Your Post Title"
    contentMarkdown: "Your markdown content"
    tags: [{ slug: "ai" }, { slug: "open-source" }]
    isRepublished: { originalArticleURL: "${baseUrl}/blog/your-slug" }
    publicationId: "YOUR_PUBLICATION_ID"
  }) {
    post { url }
  }
}`}</code>
          </pre>

          <h2>Medium</h2>
          <p>
            Medium supports canonical URLs via their API but not through the
            standard editor UI. Use the Import feature instead:
          </p>
          <ol>
            <li>
              Go to <strong>medium.com/p/import</strong>
            </li>
            <li>
              Paste the URL of your original post:{" "}
              <code>{baseUrl}/blog/your-slug</code>
            </li>
            <li>
              Medium will import the content and automatically set the canonical
              URL to your original
            </li>
          </ol>
          <p>
            <strong>Note:</strong> Medium is lower priority for developer
            tooling content. Dev.to and Hashnode have stronger developer
            audiences.
          </p>

          <h2>Recommended Tags</h2>
          <p>
            Use consistent tags across platforms for discoverability:
          </p>
          <ul>
            <li>
              <code>ai</code>, <code>ai-agents</code>,{" "}
              <code>open-source</code>, <code>security</code>,{" "}
              <code>compliance</code>
            </li>
            <li>
              Platform-specific: <code>python</code>, <code>mcp</code>,{" "}
              <code>w3c</code>, <code>blockchain</code>,{" "}
              <code>verifiable-credentials</code>
            </li>
          </ul>

          <h2>Feeds</h2>
          <p>
            Subscribe to the Attestix blog via RSS or JSON Feed to stay updated:
          </p>
          <ul>
            <li>
              <strong>RSS:</strong>{" "}
              <a href="/feed.xml">
                {baseUrl}/feed.xml
              </a>
            </li>
            <li>
              <strong>JSON Feed:</strong>{" "}
              <a href="/feed.json">
                {baseUrl}/feed.json
              </a>
            </li>
          </ul>

          <h2>Content Checklist</h2>
          <p>Before cross-posting, verify:</p>
          <ul>
            <li>Original post is live and indexed by Google</li>
            <li>Canonical URL is set correctly (exact URL match)</li>
            <li>
              Code blocks render properly on the target platform (test syntax
              highlighting)
            </li>
            <li>
              Links in the content use absolute URLs (
              <code>{baseUrl}/...</code>) not relative paths
            </li>
            <li>
              Author bio links back to the Attestix website or GitHub
            </li>
            <li>
              The post ends with a CTA:{" "}
              <code>pip install attestix</code> and a link to the GitHub repo
            </li>
          </ul>

          <div className="mt-12 p-6 border border-border rounded-lg bg-secondary/20">
            <h3 className="mt-0">Quick Links</h3>
            <ul className="mb-0">
              <li>
                <Link href="/blog">Blog</Link>
              </li>
              <li>
                <a href="/feed.xml">RSS Feed</a>
              </li>
              <li>
                <a
                  href={siteConfig.links.github}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  GitHub Repository
                </a>
              </li>
              <li>
                <a
                  href={siteConfig.links.docs}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Documentation
                </a>
              </li>
            </ul>
          </div>
        </article>
      </main>
      <Footer />
    </>
  );
}
