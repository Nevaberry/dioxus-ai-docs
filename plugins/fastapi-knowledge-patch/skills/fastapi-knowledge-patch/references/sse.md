# Server-Sent Events (FastAPI 0.135.0+)

Native SSE support via `fastapi.sse`. No third-party packages (like `sse-starlette`) needed.

## Basic Usage

Import `EventSourceResponse` and use `yield` in path operations:

```python
from collections.abc import AsyncIterable
from fastapi import FastAPI
from fastapi.sse import EventSourceResponse, ServerSentEvent
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.get("/items/stream", response_class=EventSourceResponse)
async def stream_items() -> AsyncIterable[Item]:
    for item in items:
        yield item  # auto-serialized as JSON in data: field
```

## ServerSentEvent Fields

For SSE fields (`event`, `id`, `retry`, `comment`), yield `ServerSentEvent` objects:

```python
yield ServerSentEvent(data=item, event="item_update", id=str(i), retry=5000)
yield ServerSentEvent(raw_data="[DONE]", event="done")  # raw_data skips JSON encoding
yield ServerSentEvent(comment="keep-alive")  # comment-only event
```

- `data` and `raw_data` are **mutually exclusive** -- setting both raises an error
- `data` accepts Pydantic models, dicts, lists -- auto-serialized to JSON
- `raw_data` sends the string as-is in the `data:` field

## Sync Support

Works with `def` (non-async) generators too -- use `Iterable[T]` return type:

```python
from collections.abc import Iterable

@app.get("/items/stream", response_class=EventSourceResponse)
def stream_items() -> Iterable[Item]:
    for item in items:
        yield item
```

## Last-Event-ID Resumption

Read `Last-Event-ID` from the request header to resume streams after client reconnection:

```python
from typing import Annotated
from fastapi import Header

@app.get("/items/stream", response_class=EventSourceResponse)
async def stream_items(
    last_event_id: Annotated[int | None, Header()] = None,
) -> AsyncIterable[ServerSentEvent]:
    start = last_event_id + 1 if last_event_id is not None else 0
    for i, item in enumerate(items):
        if i < start:
            continue
        yield ServerSentEvent(data=item, id=str(i))
```

## SSE over POST

SSE works with **any HTTP method**, not just GET. This is relevant for MCP-style POST-based SSE streaming:

```python
@app.post("/chat/stream", response_class=EventSourceResponse)
async def chat_stream(request: ChatRequest) -> AsyncIterable[ServerSentEvent]:
    async for chunk in generate_response(request.message):
        yield ServerSentEvent(data=chunk)
```

## Default Behavior

- Auto keep-alive ping every 15 seconds
- `Cache-Control: no-cache` header set automatically
- `X-Accel-Buffering: no` header set automatically (prevents nginx buffering)
