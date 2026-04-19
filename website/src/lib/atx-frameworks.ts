export type FrameworkStatus = "production" | "example";

export interface Framework {
  slug: string;
  name: string;
  status: FrameworkStatus;
  tagline: string;
  install: string;
  wires: string[];
  code: string;
}

export const ATX_FRAMEWORKS: Framework[] = [
  {
    slug: "langchain",
    name: "LangChain",
    status: "production",
    tagline:
      "Native BaseCallbackHandler. Every tool call, LLM call, and chain step is attested.",
    install: "pip install attestix[langchain]",
    wires: [
      "BaseCallbackHandler implementation",
      "Hash-chained audit trail per chain run",
      "Auto VC issuance on chain completion",
    ],
    code: `<span class="c">from</span> attestix.integrations.langchain <span class="c">import</span> AttestixCallback
<span class="c">from</span> langchain.agents <span class="c">import</span> AgentExecutor

attestix_cb = <span class="k">AttestixCallback</span>(
  agent_id=<span class="s">"attestix:f9bdb7a94ccb40f1"</span>,
)

agent = <span class="k">AgentExecutor</span>(
  agent=my_agent,
  tools=tools,
  callbacks=[attestix_cb],
)
<span class="c"># every tool call is now signed and hash-chained</span>`,
  },
  {
    slug: "openai-agents-sdk",
    name: "OpenAI Agents SDK",
    status: "production",
    tagline:
      "Attestix exposes all 47 MCP tools natively to the OpenAI Agents SDK via MCPServerStdio.",
    install: "pip install attestix[openai-agents]",
    wires: [
      "MCPServerStdio integration",
      "47 Attestix tools available to any OpenAI agent",
      "Actions logged through the Attestix audit service",
    ],
    code: `<span class="c">from</span> agents <span class="c">import</span> Agent
<span class="c">from</span> agents.mcp <span class="c">import</span> MCPServerStdio

attestix_mcp = <span class="k">MCPServerStdio</span>(
  params={<span class="s">"command"</span>: <span class="s">"attestix"</span>, <span class="s">"args"</span>: [<span class="s">"mcp"</span>]},
)

agent = <span class="k">Agent</span>(
  name=<span class="s">"quarterly-analyst"</span>,
  mcp_servers=[attestix_mcp],
)
<span class="c"># all 47 Attestix tools discovered automatically</span>`,
  },
  {
    slug: "crewai",
    name: "CrewAI",
    status: "production",
    tagline:
      "Attach Attestix to every crew agent through the mcps field. Crews become attestable by default.",
    install: "pip install attestix[crewai]",
    wires: [
      "MCPServerAdapter per crew agent",
      "Crew-wide compliance profile",
      "Role delegation recorded as UCAN",
    ],
    code: `<span class="c">from</span> crewai <span class="c">import</span> Agent, Crew
<span class="c">from</span> crewai_tools <span class="c">import</span> MCPServerAdapter

attestix = <span class="k">MCPServerAdapter</span>({<span class="s">"command"</span>: <span class="s">"attestix"</span>, <span class="s">"args"</span>: [<span class="s">"mcp"</span>]})

analyst = <span class="k">Agent</span>(
  role=<span class="s">"Financial analyst"</span>,
  goal=<span class="s">"Analyse quarterly data"</span>,
  mcps=[attestix],
)
crew = <span class="k">Crew</span>(agents=[analyst])`,
  },
  {
    slug: "dify",
    name: "Dify",
    status: "example",
    tagline:
      "Example integration. Dify supports MCP servers, so Attestix attaches as a tool provider.",
    install: "See docs / integrations / dify",
    wires: [
      "Register Attestix MCP endpoint",
      "Invoke tools from Dify workflows",
      "Audit trail synced to Attestix",
    ],
    code: `<span class="c"># dify.yaml</span>
<span class="k">mcp_servers</span>:
  - <span class="k">name</span>: <span class="s">attestix</span>
    <span class="k">command</span>: <span class="s">attestix</span>
    <span class="k">args</span>: [<span class="s">mcp</span>]
    <span class="k">capabilities</span>:
      - <span class="s">identity</span>
      - <span class="s">credentials</span>
      - <span class="s">compliance</span>`,
  },
  {
    slug: "google-adk",
    name: "Google ADK",
    status: "example",
    tagline: "Example integration. Google Agent Development Kit wires in as an MCP client.",
    install: "See docs / integrations / google-adk",
    wires: [
      "MCP client registration",
      "Tool discovery from Attestix",
      "Session-bound audit trail",
    ],
    code: `<span class="c">from</span> google.adk <span class="c">import</span> Agent
<span class="c">from</span> google.adk.tools.mcp <span class="c">import</span> McpClient

mcp = <span class="k">McpClient</span>(command=<span class="s">"attestix"</span>, args=[<span class="s">"mcp"</span>])
agent = <span class="k">Agent</span>(
  name=<span class="s">"analyst"</span>,
  tools=mcp.tools(),
)`,
  },
  {
    slug: "semantic-kernel",
    name: "Semantic Kernel",
    status: "example",
    tagline:
      "Example integration. Microsoft Semantic Kernel consumes Attestix via its MCP plugin layer.",
    install: "See docs / integrations / semantic-kernel",
    wires: [
      "Kernel plugin registration",
      "Function-call attestation",
      "VP exchange with other SK agents",
    ],
    code: `<span class="c">// C# / Semantic Kernel</span>
<span class="k">var</span> kernel = <span class="k">Kernel</span>.CreateBuilder()
  .AddMcpPlugin(<span class="s">"attestix"</span>, <span class="s">"attestix mcp"</span>)
  .Build();`,
  },
  {
    slug: "strands",
    name: "Strands",
    status: "example",
    tagline: "Example integration. Strands agents call Attestix tools through the MCP runtime.",
    install: "See docs / integrations / strands",
    wires: [
      "MCP runtime binding",
      "Strand-level compliance profile",
      "Agent identity attestation",
    ],
    code: `<span class="c">from</span> strands <span class="c">import</span> Agent, MCPClient

attestix = <span class="k">MCPClient</span>(<span class="s">"attestix"</span>, [<span class="s">"mcp"</span>])
agent = <span class="k">Agent</span>(mcp_clients=[attestix])`,
  },
];
