# Integration Guide

How to use Attestix in your Python code, AI frameworks, and multi-agent systems.

## As a Python Library

You can import Attestix services directly without running the MCP server.

```python
import sys
sys.path.insert(0, "/path/to/attestix")

from services.identity_service import IdentityService
from services.credential_service import CredentialService
from services.compliance_service import ComplianceService
from services.provenance_service import ProvenanceService

# Services are instantiated once and reuse the same signing key
identity_svc = IdentityService()
credential_svc = CredentialService()
compliance_svc = ComplianceService()
provenance_svc = ProvenanceService()
```

All services share the same Ed25519 signing key (auto-generated on first use) and the same JSON storage files.

## With LangChain

### LangChain Tool Wrapper

Wrap Attestix services as LangChain tools:

```python
from langchain_core.tools import tool

sys.path.insert(0, "/path/to/attestix")
from services.identity_service import IdentityService
from services.compliance_service import ComplianceService

identity_svc = IdentityService()
compliance_svc = ComplianceService()

@tool
def create_agent_identity(name: str, capabilities: str, description: str) -> dict:
    """Create a verified identity for an AI agent."""
    return identity_svc.create_identity(
        display_name=name,
        source_protocol="manual",
        capabilities=capabilities.split(","),
        description=description,
        issuer_name="My Organization",
    )

@tool
def check_compliance(agent_id: str) -> dict:
    """Check EU AI Act compliance status for an agent."""
    return compliance_svc.get_compliance_status(agent_id)
```

### In a LangChain Agent

```python
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-4o")
tools = [create_agent_identity, check_compliance]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a compliance officer. Use tools to manage agent identities."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)

result = executor.invoke({"input": "Create an identity for our customer service bot"})
```

## With CrewAI

```python
from crewai import Agent, Task, Crew
from crewai_tools import tool

sys.path.insert(0, "/path/to/attestix")
from services.identity_service import IdentityService
from services.compliance_service import ComplianceService

identity_svc = IdentityService()
compliance_svc = ComplianceService()

@tool("Create Agent Identity")
def create_identity(name: str, capabilities: str) -> str:
    """Create a verified identity for an AI agent with the given name and capabilities."""
    result = identity_svc.create_identity(
        display_name=name,
        source_protocol="manual",
        capabilities=capabilities.split(","),
    )
    return f"Created agent {result['agent_id']}"

@tool("Check Compliance Status")
def check_compliance(agent_id: str) -> str:
    """Check EU AI Act compliance status for the given agent_id."""
    result = compliance_svc.get_compliance_status(agent_id)
    return f"Compliance: {result['completion_pct']}% complete. Missing: {result.get('missing', [])}"

compliance_officer = Agent(
    role="AI Compliance Officer",
    goal="Ensure all AI agents are EU AI Act compliant",
    tools=[create_identity, check_compliance],
    verbose=True,
)

audit_task = Task(
    description="Create an identity for our HR screening bot and check its compliance status",
    agent=compliance_officer,
    expected_output="Agent ID and compliance status report",
)

crew = Crew(agents=[compliance_officer], tasks=[audit_task])
result = crew.kickoff()
```

## With AutoGen

```python
import autogen
import sys

sys.path.insert(0, "/path/to/attestix")
from services.identity_service import IdentityService

identity_svc = IdentityService()

def create_agent_identity(name: str, capabilities: str) -> dict:
    return identity_svc.create_identity(
        display_name=name,
        source_protocol="manual",
        capabilities=capabilities.split(","),
    )

assistant = autogen.AssistantAgent(
    name="compliance_assistant",
    llm_config={"model": "gpt-4o"},
)

user_proxy = autogen.UserProxyAgent(
    name="user",
    human_input_mode="NEVER",
    function_map={"create_agent_identity": create_agent_identity},
)

user_proxy.initiate_chat(
    assistant,
    message="Create an identity for our data analysis agent with capabilities: data_analysis, reporting",
)
```

## Multi-Agent Identity Pattern

When multiple agents need to identify each other and delegate capabilities:

```python
from services.identity_service import IdentityService
from services.delegation_service import DelegationService

identity_svc = IdentityService()
delegation_svc = DelegationService()

# Create identities for each agent in your system
orchestrator = identity_svc.create_identity(
    display_name="Orchestrator",
    capabilities=["task_routing", "delegation"],
    description="Routes tasks to specialist agents",
    issuer_name="My Org",
)

analyst = identity_svc.create_identity(
    display_name="DataAnalyst",
    capabilities=["data_analysis", "chart_generation"],
    description="Analyzes datasets and produces reports",
    issuer_name="My Org",
)

# Orchestrator delegates specific capabilities to analyst
delegation = delegation_svc.create_delegation(
    issuer_agent_id=orchestrator["agent_id"],
    audience_agent_id=analyst["agent_id"],
    capabilities=["data_analysis"],
    expiry_hours=8,  # 8-hour work day
)

# Later, verify the delegation is still valid
verification = delegation_svc.verify_delegation(delegation["token"])
print(f"Valid: {verification['valid']}")
print(f"Capabilities: {verification['payload']['att']}")
```

## Compliance-as-Middleware

Add compliance checks to your agent pipeline:

```python
from services.identity_service import IdentityService
from services.compliance_service import ComplianceService
from services.provenance_service import ProvenanceService

identity_svc = IdentityService()
compliance_svc = ComplianceService()
provenance_svc = ProvenanceService()


class ComplianceMiddleware:
    """Wraps an agent to enforce compliance and log actions."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id

    def check_before_run(self):
        """Call before your agent processes a request."""
        status = compliance_svc.get_compliance_status(self.agent_id)
        if not status.get("compliant"):
            missing = status.get("missing", [])
            raise RuntimeError(
                f"Agent {self.agent_id} is not compliant. "
                f"Missing: {missing}"
            )

    def log_action(self, action_type: str, input_summary: str, output_summary: str,
                   rationale: str = "", human_override: bool = False):
        """Call after your agent processes a request."""
        provenance_svc.log_action(
            agent_id=self.agent_id,
            action_type=action_type,
            input_summary=input_summary,
            output_summary=output_summary,
            decision_rationale=rationale,
            human_override=human_override,
        )


# Usage
middleware = ComplianceMiddleware("attestix:your_agent_id")

# Before processing
middleware.check_before_run()

# Your agent does its work here...
result = "some output"

# After processing
middleware.log_action(
    action_type="inference",
    input_summary="User asked for diagnosis",
    output_summary="Suggested follow-up tests",
    rationale="Symptoms match 3 conditions requiring differential diagnosis",
)
```

## MCP Client Integration

If you're building an MCP client that connects to Attestix:

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["/path/to/attestix/main.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {len(tools.tools)}")

            # Call a tool
            result = await session.call_tool(
                "create_agent_identity",
                arguments={
                    "display_name": "MyAgent",
                    "capabilities": "data_analysis",
                },
            )
            print(result.content)

asyncio.run(main())
```

## Storage Location

All Attestix data is stored in JSON files in the same directory as `main.py`:

| File | Contents |
|------|----------|
| `identities.json` | All UAITs |
| `credentials.json` | Verifiable Credentials |
| `compliance.json` | Compliance profiles, assessments, declarations |
| `provenance.json` | Training data, model lineage, audit log |
| `reputation.json` | Interaction history and scores |
| `delegations.json` | Delegation tokens |
| `.signing_key.json` | Ed25519 server signing key (do not share) |
| `.keypairs.json` | Generated DID keypairs (do not share) |

To use a shared data directory across multiple applications, set the `ATTESTIX_DATA_DIR` environment variable or symlink the JSON files.

## Error Handling

All Attestix service methods return dictionaries. Errors are returned as:

```python
{
    "error": "Human-readable error message",
    "error_code": "CATEGORY_SPECIFIC_CODE",
    "category": "identity|compliance|credential|provenance"
}
```

Check for the `error` key in the response:

```python
result = identity_svc.create_identity(display_name="Test")
if "error" in result:
    print(f"Failed: {result['error']}")
else:
    print(f"Agent ID: {result['agent_id']}")
```
