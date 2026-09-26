import Link from "next/link";

// Only integrations that ship in the package (attestix/integrations/*) or are
// independently verifiable (the MCP Registry listing). Add a name here only
// with a guide to link to.
const WORKS_WITH = [
  { name: "LangChain", href: "/docs/guides/langchain" },
  { name: "CrewAI", href: "/docs/guides/crewai" },
  { name: "OpenAI Agents SDK", href: "/docs/guides/openai-agents-sdk" },
  { name: "Claude Code (MCP)", href: "/docs/getting-started" },
  {
    name: "MCP Registry",
    href: "https://registry.modelcontextprotocol.io/v0/servers?search=attestix",
  },
];

export function TrustStrip() {
  return (
    <section className="border-y border-atx-line-soft">
      <div className="mx-auto flex max-w-[1320px] flex-wrap items-center justify-center gap-x-8 gap-y-3 px-7 py-6">
        <span className="text-[13px] text-atx-ink-dim">Works with</span>
        {WORKS_WITH.map((w) => (
          <Link
            key={w.name}
            href={w.href}
            className="text-[15px] font-medium text-atx-ink-mid transition-colors hover:text-atx-accent"
          >
            {w.name}
          </Link>
        ))}
      </div>
    </section>
  );
}
