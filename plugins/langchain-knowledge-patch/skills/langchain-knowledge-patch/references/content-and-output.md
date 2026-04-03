# Content Blocks & Structured Output (LangChain 1.0)

## Standard Content Blocks

Provider-agnostic typed content on messages via `content_blocks` property:

```python
response = model.invoke("Explain AI")
for block in response.content_blocks:
    if block["type"] == "text":
        print(block["text"])
    elif block["type"] == "reasoning":
        print(block["reasoning"])
```

### Multimodal Input

```python
from langchain.messages import HumanMessage

msg = HumanMessage(content_blocks=[
    {"type": "text", "text": "Describe this image."},
    {"type": "image", "url": "https://example.com/img.jpg"},
])
```

### Serialization

Opt-in serialization to `content` field:
- Environment variable: `LC_OUTPUT_VERSION=v1`
- Model init parameter: `output_version="v1"`

## Structured Output Strategies

```python
from langchain.agents.structured_output import ToolStrategy, ProviderStrategy
```

### ToolStrategy

Works with any model that supports tool calling:

```python
agent = create_agent(model="gpt-4.1", tools=tools, response_format=ToolStrategy(MySchema))
```

### ProviderStrategy

Uses native structured output (more reliable, fewer providers support it):

```python
agent = create_agent(model="gpt-4.1", response_format=ProviderStrategy(MySchema))
```

### Auto-Fallback

Passing a schema directly defaults to `ProviderStrategy` with `ToolStrategy` fallback:

```python
agent = create_agent(model="gpt-4.1", response_format=MySchema)
```

### Accessing Structured Output

```python
result["structured_response"]  # access the typed output
```

### Key Change

Prompted output is removed. Structured output now happens in the main agent loop (no extra LLM call).
