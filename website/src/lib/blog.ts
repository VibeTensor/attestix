import fs from "fs";
import path from "path";
import rehypePrettyCode from "rehype-pretty-code";
import rehypeStringify from "rehype-stringify";
import remarkGfm from "remark-gfm";
import remarkParse from "remark-parse";
import remarkRehype from "remark-rehype";
import { unified } from "unified";

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

const slugify = (t: string) =>
  t.toLowerCase().replace(/<[^>]+>/g, "").replace(/&[a-z#0-9]+;/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

// Give every h2 an id (for the table of contents) and collect them.
function withHeadingIds(html: string): { html: string; headings: Heading[] } {
  const headings: Heading[] = [];
  const out = html.replace(/<h2>([\s\S]*?)<\/h2>/g, (_, inner: string) => {
    const text = inner.replace(/<[^>]+>/g, "").trim();
    let id = slugify(text) || `section-${headings.length + 1}`;
    if (headings.some((h) => h.id === id)) id = `${id}-${headings.length + 1}`;
    headings.push({ id, text });
    return `<h2 id="${id}">${inner}</h2>`;
  });
  return { html: out, headings };
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

export async function markdownToHTML(markdown: string) {
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
    .use(rehypeStringify)
    .process(markdown);

  return p.toString();
}

export async function getPost(slug: string) {
  if (!/^[a-z0-9-]+$/.test(slug)) {
    throw new Error(`Invalid blog slug: ${slug}`);
  }
  const filePath = path.join(process.cwd(), "content", `${slug}.mdx`);
  const source = fs.readFileSync(filePath, "utf-8");
  const { content: rawContent, data: metadata } = parseFrontmatter(source);
  const { html: content, headings } = withHeadingIds(await markdownToHTML(rawContent));
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
