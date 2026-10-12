import fs from "fs";
import path from "path";
import rehypePrettyCode from "rehype-pretty-code";
import rehypeStringify from "rehype-stringify";
import remarkGfm from "remark-gfm";
import remarkParse from "remark-parse";
import remarkRehype from "remark-rehype";
import { unified, type Plugin } from "unified";
import type { Root, RootContent } from "hast";

export type Post = {
  title: string;
  publishedAt: string;
  summary: string;
  author: string;
  slug: string;
  image?: string;
  /** Product | Research | Release | Guide | Regulation */
  category?: string;
};

export type Heading = { id: string; text: string };

function headingText(node: Root | RootContent): string {
  if (node.type === "text") return node.value;
  return "children" in node ? node.children.map(headingText).join("") : "";
}

function headingIds(headings: Heading[]): Plugin<[], Root> {
  return () => (tree) => {
    const visit = (node: Root | RootContent) => {
      if (node.type === "element" && node.tagName === "h2") {
        const text = headingText(node).trim();
        const base = text.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "") || "section";
        let id = base;
        let suffix = 2;
        while (headings.some((heading) => heading.id === id)) id = `${base}-${suffix++}`;
        node.properties.id = id;
        headings.push({ id, text });
      }
      if ("children" in node) node.children.forEach(visit);
    };
    visit(tree);
  };
}

const readingMinutes = (md: string) =>
  Math.max(1, Math.ceil(md.split(/\s+/).filter(Boolean).length / 220));

function parseFrontmatter(fileContent: string) {
  const frontmatterRegex = /^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/;
  const match = frontmatterRegex.exec(fileContent);
  if (!match) {
    throw new Error("Missing frontmatter delimiters at start of MDX file");
  }
  const frontMatterBlock = match[1];
  let content = fileContent.replace(frontmatterRegex, "").trim();
  let frontMatterLines = frontMatterBlock.trim().split("\n");
  let metadata: Partial<Post> = {};

  frontMatterLines.forEach((line) => {
    let [key, ...valueArr] = line.split(": ");
    let value = valueArr.join(": ").trim();
    value = value.replace(/^['"](.*)['"]$/, "$1"); // Remove quotes
    metadata[key.trim() as keyof Post] = value;
  });

  return { data: metadata as Post, content };
}

function getMDXFiles(dir: string) {
  return fs.readdirSync(dir).filter((file) => path.extname(file) === ".mdx");
}

async function renderMarkdown(markdown: string) {
  const headings: Heading[] = [];
  const p = await unified()
    .use(remarkParse)
    .use(remarkGfm)
    .use(remarkRehype)
    .use(rehypePrettyCode, {
      // https://rehype-pretty.pages.dev/#usage
      theme: {
        light: "min-light",
        dark: "min-dark",
      },
      keepBackground: false,
    })
    .use(headingIds(headings))
    .use(rehypeStringify)
    .process(markdown);

  return { html: p.toString(), headings };
}

export async function markdownToHTML(markdown: string) {
  return (await renderMarkdown(markdown)).html;
}

export async function getPost(slug: string) {
  if (!/^[a-z0-9-]+$/.test(slug)) {
    throw new Error(`Invalid blog slug: ${slug}`);
  }
  const filePath = path.join(process.cwd(), "content", `${slug}.mdx`);
  const source = fs.readFileSync(filePath, "utf-8");
  const { content: rawContent, data: metadata } = parseFrontmatter(source);
  const { html: content, headings } = await renderMarkdown(rawContent);
  const defaultImage = `/og-image.png`;
  return {
    source: content,
    markdown: rawContent,
    headings,
    minutes: readingMinutes(rawContent),
    metadata: {
      ...metadata,
      image: metadata.image || defaultImage,
    },
    slug,
  };
}

async function getAllPosts(dir: string) {
  const mdxFiles = getMDXFiles(dir);
  return Promise.all(
    mdxFiles.map(async (file) => {
      const slug = path.basename(file, path.extname(file));
      const { metadata, source, minutes } = await getPost(slug);
      return {
        ...metadata,
        slug,
        source,
        minutes,
      };
    })
  );
}

export async function getBlogPosts() {
  return getAllPosts(path.join(process.cwd(), "content"));
}
