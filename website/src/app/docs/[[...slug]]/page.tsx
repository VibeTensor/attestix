import { source } from "@/lib/source";
import { DocsBody, DocsPage, DocsTitle, DocsDescription } from "fumadocs-ui/page";
import defaultMdxComponents from "fumadocs-ui/mdx";
import { notFound } from "next/navigation";
import { Mermaid } from "@/components/mermaid";

export default async function Page(props: {
  params: Promise<{ slug?: string[] }>;
}) {
  const params = await props.params;
  const page = source.getPage(params.slug);
  if (!page) notFound();

  const MDX = page.data.body;
  // Raw markdown twin written at build time by scripts/generate-llms.mjs
  const mdHref = `/${["docs", ...(params.slug ?? [])].join("/")}.md`;
  const issueHref = `https://github.com/VibeTensor/attestix/issues/new?title=${encodeURIComponent(
    `Docs feedback: ${page.data.title}`,
  )}&body=${encodeURIComponent(`Page: https://attestix.io${page.url}\n\n`)}`;

  return (
    <DocsPage
      toc={page.data.toc}
      full={page.data.full}
      editOnGithub={{
        repo: "attestix",
        owner: "VibeTensor",
        sha: "main",
        path: `website/content/docs/${page.file.path}`,
      }}
    >
      <DocsTitle>{page.data.title}</DocsTitle>
      <DocsDescription>{page.data.description}</DocsDescription>
      <DocsBody>
        <MDX components={{ ...defaultMdxComponents, Mermaid }} />
      </DocsBody>
      <div className="mt-10 flex flex-wrap gap-x-6 gap-y-2 border-t border-fd-border pt-5 text-[13px] text-fd-muted-foreground">
        <a href={mdHref} className="hover:text-fd-foreground">
          View as Markdown (for AI agents)
        </a>
        <a href="/llms.txt" className="hover:text-fd-foreground">
          llms.txt index
        </a>
        <a href={issueHref} target="_blank" rel="noopener noreferrer" className="hover:text-fd-foreground">
          Found an issue with this page? Report it &#8599;
        </a>
      </div>
    </DocsPage>
  );
}

export function generateStaticParams() {
  return source.generateParams();
}

export async function generateMetadata(props: {
  params: Promise<{ slug?: string[] }>;
}) {
  const params = await props.params;
  const page = source.getPage(params.slug);
  if (!page) notFound();

  return {
    title: `${page.data.title} - Attestix Docs`,
    description: page.data.description,
  };
}
