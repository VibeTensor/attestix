/**
 * Build-time LLM-first docs (llmstxt.org). Regenerated on every build, so it
 * cannot drift from the docs the way a hand-written llms.txt did:
 *   - public/llms.txt: index of site pages + every docs page, one line each,
 *     taken from each MDX file's own frontmatter title/description
 *   - public/docs/<slug>.md: raw markdown of each docs page (URL + ".md")
 * Page order follows the sidebar (content/docs/**\/meta.json).
 */
import { mkdirSync, readFileSync, copyFileSync, writeFileSync, renameSync, existsSync, readdirSync } from "fs";
import { dirname, join, relative } from "path";
import { randomUUID } from "node:crypto";
import { fileURLToPath } from "url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const DOCS = join(root, "content", "docs");
const backupRoot = join(root, ".source", "docs-export-backups", String(Date.now()));
const SITE = "https://attestix.io";

// Marketing pages worth an agent's attention; docs are discovered from disk.
const SITE_PAGES = [
  ["Home", "/", "What Attestix is, how it works, install in three commands"],
  ["Research", "/research", "Product vision, the research paper, and technical notes"],
  ["Platform", "/platform", "Agent identity, signed records, verification boundaries and integrations"],
  ["Console demo", "/console", "Interactive preview of the Attestix workspace; data is simulated"],
  ["Verify a credential", "/verify", "In-browser W3C VC verifier; nothing uploaded"],
  ["Bundle wire format v1", "/spec/bundle/v1", "Frozen spec of the portability bundle format"],
  ["EU AI Act fine calculator", "/demo/fine-calculator", "Illustrative Article 99 estimator; assess actual applicability separately"],
  ["Pricing", "/pricing", "Self-hosted source and proposed hosted-service availability"],
  ["Changelog", "/changelog", "Release history"],
  ["Security", "/security", "Responsible disclosure"],
];

function frontmatter(raw) {
  const src = raw.replace(/\r\n/g, "\n"); // files may use Windows line endings
  const m = src.match(/^---\n([\s\S]*?)\n---\n?/);
  const get = (k) => (m?.[1].match(new RegExp(`^${k}:\\s*["']?(.+?)["']?\\s*$`, "m")) || [])[1];
  return { title: get("title"), description: get("description"), body: m ? src.slice(m[0].length) : src };
}

// Preserve sidebar order, then include reachable pages omitted from the sidebar.
function ordered(dir, slug = []) {
  const metaPath = join(dir, "meta.json");
  const pages = existsSync(metaPath) ? JSON.parse(readFileSync(metaPath, "utf8")).pages : [];
  const out = [];
  const listed = new Set();
  for (const p of pages) {
    if (p.startsWith("---")) continue; // sidebar separator
    if (listed.has(p)) continue;
    listed.add(p);
    const file = join(dir, `${p}.mdx`);
    if (existsSync(file)) out.push({ file, slug: p === "index" ? slug : [...slug, p] });
    else if (existsSync(join(dir, p))) out.push(...ordered(join(dir, p), [...slug, p]));
  }
  for (const entry of readdirSync(dir, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
    const name = entry.name.replace(/\.mdx$/, "");
    if (listed.has(name)) continue;
    if (entry.isFile() && entry.name.endsWith(".mdx")) {
      out.push({ file: join(dir, entry.name), slug: name === "index" ? slug : [...slug, name] });
    } else if (entry.isDirectory()) {
      out.push(...ordered(join(dir, entry.name), [...slug, entry.name]));
    }
  }
  return out;
}

function writeGenerated(file, content) {
  if (existsSync(file)) {
    const backup = join(backupRoot, relative(root, file));
    mkdirSync(dirname(backup), { recursive: true });
    copyFileSync(file, backup);
    if (!readFileSync(file).equals(readFileSync(backup))) {
      throw new Error("Generated-file backup verification failed");
    }
  }
  mkdirSync(dirname(file), { recursive: true });
  const temporary = `${file}.${process.pid}.${randomUUID()}.tmp`;
  writeFileSync(temporary, content);
  renameSync(temporary, file);
}

const lines = [
  "# Attestix",
  "",
  "> Agent identity, signed credentials, delegated authority and portable governance evidence. Apache 2.0. Signatures do not establish legal conformity, trusted issuer authority, live revocation or complete capture.",
  "",
  "Every docs page below is also available as raw markdown at its URL plus `.md`. This file is generated at build time from the docs themselves.",
  "",
  "## Site",
  "",
  ...SITE_PAGES.map(([t, p, d]) => `- [${t}](${SITE}${p}): ${d}`),
  "",
  "## Docs",
  "",
];

let count = 0;
for (const { file, slug } of ordered(DOCS)) {
  const { title, description, body } = frontmatter(readFileSync(file, "utf8"));
  const urlPath = ["docs", ...slug].join("/");
  const mdFile = join(root, "public", `${urlPath}.md`);
  mkdirSync(dirname(mdFile), { recursive: true });
  writeGenerated(mdFile, `# ${title}\n\n${description ? `> ${description}\n\n` : ""}${body.trim()}\n`);
  lines.push(`- [${title}](${SITE}/${urlPath}.md)${description ? `: ${description}` : ""}`);
  count++;
}

writeGenerated(join(root, "public", "llms.txt"), lines.join("\n") + "\n");
console.log(`llms.txt: ${count} docs pages + ${SITE_PAGES.length} site pages`);
