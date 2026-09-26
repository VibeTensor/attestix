/**
 * Build-time LLM-first docs (llmstxt.org). Regenerated on every build, so it
 * cannot drift from the docs the way a hand-written llms.txt did:
 *   - public/llms.txt: index of site pages + every docs page, one line each,
 *     taken from each MDX file's own frontmatter title/description
 *   - public/docs/<slug>.md: raw markdown of each docs page (URL + ".md")
 * Page order follows the sidebar (content/docs/**\/meta.json).
 */
import { mkdirSync, readFileSync, rmSync, writeFileSync, existsSync } from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const DOCS = join(root, "content", "docs");
const OUT_MD = join(root, "public", "docs");
const SITE = "https://attestix.io";

// Marketing pages worth an agent's attention; docs are discovered from disk.
const SITE_PAGES = [
  ["Home", "/", "What Attestix is, how it works, install in three commands"],
  ["Research", "/research", "Product vision, the research paper, and technical notes"],
  ["Platform", "/platform", "The nine modules, seven-step compliance workflow, integrations, compliance matrix"],
  ["Console demo", "/console", "Interactive preview of the Attestix workspace; data is simulated"],
  ["Verify a credential", "/verify", "In-browser W3C VC verifier; nothing uploaded"],
  ["Bundle wire format v1", "/spec/bundle/v1", "Frozen spec of the portability bundle format"],
  ["EU AI Act fine calculator", "/demo/fine-calculator", "Article 99 maximum-fine estimator, incl. the SME lower-of rule"],
  ["Pricing", "/pricing", "Open source, Cloud, and Enterprise"],
  ["Changelog", "/changelog", "Release history"],
  ["Security", "/security", "Responsible disclosure"],
];

function frontmatter(raw) {
  const src = raw.replace(/\r\n/g, "\n"); // files may use Windows line endings
  const m = src.match(/^---\n([\s\S]*?)\n---\n?/);
  const get = (k) => (m?.[1].match(new RegExp(`^${k}:\\s*["']?(.+?)["']?\\s*$`, "m")) || [])[1];
  return { title: get("title"), description: get("description"), body: m ? src.slice(m[0].length) : src };
}

// Walk the sidebar order from meta.json, falling back to nothing (explicit is better).
function ordered(dir, slug = []) {
  const metaPath = join(dir, "meta.json");
  const pages = existsSync(metaPath) ? JSON.parse(readFileSync(metaPath, "utf8")).pages : [];
  const out = [];
  for (const p of pages) {
    if (p.startsWith("---")) continue; // sidebar separator
    const file = join(dir, `${p}.mdx`);
    if (existsSync(file)) out.push({ file, slug: p === "index" ? slug : [...slug, p] });
    else if (existsSync(join(dir, p))) out.push(...ordered(join(dir, p), [...slug, p]));
  }
  return out;
}

rmSync(OUT_MD, { recursive: true, force: true });
const lines = [
  "# Attestix",
  "",
  "> Open-source attestation infrastructure for AI agents: verifiable identity (W3C DIDs and Verifiable Credentials), delegation, hash-chained audit trails, EU AI Act compliance records, and optional on-chain anchoring. 47 MCP tools across 9 modules. Apache 2.0.",
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
  writeFileSync(mdFile, `# ${title}\n\n${description ? `> ${description}\n\n` : ""}${body.trim()}\n`);
  lines.push(`- [${title}](${SITE}/${urlPath}.md)${description ? `: ${description}` : ""}`);
  count++;
}

writeFileSync(join(root, "public", "llms.txt"), lines.join("\n") + "\n");
console.log(`llms.txt: ${count} docs pages + ${SITE_PAGES.length} site pages`);
