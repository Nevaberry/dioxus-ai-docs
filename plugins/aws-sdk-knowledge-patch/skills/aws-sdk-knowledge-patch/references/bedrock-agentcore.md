# Bedrock AgentCore (GA Oct 2025)

Enterprise services for deploying AI agents at scale. Framework-agnostic (Strands, LangGraph, etc.).

## Runtime: Serverless Agent Deployment

```python
from bedrock_agentcore.runtime import BedrockAgentCoreApp
app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    return agent(payload.get("prompt"))
```

## Memory: Session + Long-Term

```python
from bedrock_agentcore.memory import MemoryClient
memory_client = MemoryClient(region_name="us-east-1")
memory = memory_client.create_memory_and_wait(
    name="MyMemory", description="...",
    strategies=[{"semanticMemoryStrategy": {
        "name": "facts", "namespaces": ["/facts/{actorId}"]
    }}]
)
memory_client.create_event(memory_id=mid, actor_id="u1", session_id="s1", messages=[...])
memories = memory_client.retrieve_memories(memory_id=mid, namespace="/facts/u1", query="topic")
```

## Identity: OAuth2 and API Key Credentials

```python
from bedrock_agentcore.services.identity import IdentityClient
identity_client = IdentityClient("us-east-1")
```

## CLI

Install: `pip install bedrock-agentcore bedrock-agentcore-starter-toolkit`

Commands:
- `agentcore configure` — set up configuration
- `agentcore launch [--local]` — deploy agent (or run locally)
- `agentcore invoke` — invoke a deployed agent
