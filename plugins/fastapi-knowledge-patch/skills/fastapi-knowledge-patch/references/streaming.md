# Streaming

FastAPI 0.134.0+ adds native streaming support via `yield` in path operations. FastAPI 0.135.0 adds first-class Server-Sent Events.

## JSON Lines Streaming (0.134.0)

Use `yield` in path operations to stream JSON Lines (`application/jsonl`). Declare return type as `AsyncIterable[Model]` for Pydantic validation and Rust-speed serialization.

### Async

```python
from collections.abc import AsyncIterable
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float


@app.get("/items/stream")
async def stream_items() -> AsyncIterable[Item]:
    for item in get_items():
        yield item
```

### Sync

Use `Iterable[Model]` for synchronous generators:

```python
from collections.abc import Iterable

@app.get("/items/stream")
def stream_items() -> Iterable[Item]:
    for item in get_items():
        yield item
```

No `StreamingResponse` wrapper needed — FastAPI handles the response automatically. Each yielded model is serialized as a JSON line.

## Server-Sent Events (0.135.0)

New `EventSourceResponse` and `ServerSentEvent` in `fastapi.sse`.

### Simple SSE — yield models directly

```python
from collections.abc import AsyncIterable
from fastapi import FastAPI
from fastapi.sse import EventSourceResponse, ServerSentEvent
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.get("/stream", response_class=EventSourceResponse)
async def sse_items() -> AsyncIterable[Item]:
    for item in get_items():
        yield item
```

### Advanced SSE — control event/id/retry fields

```python
@app.get("/events", response_class=EventSourceResponse)
async def sse_events() -> AsyncIterable[ServerSentEvent]:
    yield ServerSentEvent(data=item, event="update", id="1", retry=5000)
    yield ServerSentEvent(raw_data="[DONE]")  # raw_data skips JSON encoding
```

### Reconnection

Read `Last-Event-ID` header for reconnection resume. Works with POST too.

### Key details

- Declare `response_class=EventSourceResponse` on the endpoint
- Yield Pydantic models directly for automatic JSON serialization
- Use `ServerSentEvent` for control over `event`, `id`, `retry` fields
- `raw_data` sends the string as-is without JSON encoding
- Works with both `async def` and `def` endpoints
