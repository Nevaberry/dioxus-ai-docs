# Responses and streaming

## Bodiless responses can return `None`

FastAPI 0.117.0 accepts `-> None` on operations whose status code forbids a
body (`2025-09`):

```python
from fastapi import FastAPI

app = FastAPI()

@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int) -> None:
    return None
```

This expresses the actual handler contract without producing a response-model
error.

## Prefer direct Pydantic JSON serialization

From FastAPI 0.130, a Pydantic return annotation or `response_model` makes
Pydantic serialize a standard JSON response directly to bytes (`2026-02`).

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str

@app.get("/items/{item_id}")
def read_item(item_id: int) -> Item:
    return Item(name=f"item-{item_id}")
```

Declaring a JSON response class still applies Pydantic validation and
filtering, but then passes the result through `jsonable_encoder` and lets the
response class serialize bytes. Omit the response class for the direct path.
`ORJSONResponse` and `UJSONResponse` are deprecated from FastAPI 0.131.

FastAPI 0.140.9 propagates `exclude_defaults=True` recursively through mapping
keys and values (`2026-08`):

```python
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

class Item(BaseModel):
    count: int = 0

assert jsonable_encoder(
    {"item": Item(count=0)}, exclude_defaults=True
) == {"item": {}}
```

## Stream typed JSON Lines

FastAPI 0.134 supports generator path operations. Without a custom response
class, annotate the generator as `Iterable[Item]` or `AsyncIterable[Item]` to
validate, filter, document, and serialize every yielded item with Pydantic as
`application/jsonl`. Without a return annotation, each item goes through
`jsonable_encoder`.

```python
from collections.abc import AsyncIterable
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    value: int

@app.get("/items/stream")
async def stream_items() -> AsyncIterable[Item]:
    yield Item(value=1)
```

FastAPI 0.140.8 preserves the streaming item type when the endpoint's router
is attached with `include_router()`, keeping validation, serialization, and
OpenAPI generation intact. FastAPI 0.140.13 honors a non-default `status_code`
declared on JSON Lines and SSE generator endpoints (`2026-08`).

For non-generator endpoints annotated with `Iterable[...]`, FastAPI 0.140.11
applies `response_model_*` settings, including filtering such as
`response_model_exclude_none`:

```python
from collections.abc import Iterable
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    note: str | None = None

@app.get("/items", response_model_exclude_none=True)
def read_items() -> Iterable[Item]:
    return [Item(name="one")]
```

## Stream raw strings and bytes

Set `response_class=StreamingResponse` for raw output. Yielded strings and
bytes bypass Pydantic and structured serialization; the generator annotation
is only for type checking. Provide an explicit media type, normally through a
subclass:

```python
from collections.abc import Iterable
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

class BinaryStream(StreamingResponse):
    media_type = "application/octet-stream"

app = FastAPI()

@app.get("/download", response_class=BinaryStream)
def stream_bytes() -> Iterable[bytes]:
    yield b"first chunk\n"
    yield b"second chunk\n"
```

Prefer the decorator-and-`yield` form. A directly returned
`StreamingResponse` relies on its async generator reaching an `await`
cancellation point, while the path-operation form handles cancellation. For a
blocking file-like source, use regular `def` and `Iterable[bytes]` so FastAPI
runs the work without blocking the event loop.

Starlette 0.42 and newer raises `ClientDisconnect` when the client drops a
`StreamingResponse`. Middleware or code around response transmission should
handle that outcome deliberately.

## Send Server-Sent Events

FastAPI 0.135.0 adds native SSE support (`2026-03`). Set
`response_class=EventSourceResponse` and yield ordinary values; each becomes
JSON in the event's `data:` field. An iterable item annotation enables
Pydantic validation, documentation, and serialization, while an unannotated
generator uses `jsonable_encoder`.

```python
from collections.abc import AsyncIterable
from fastapi import FastAPI
from fastapi.sse import EventSourceResponse

app = FastAPI()

@app.get("/events", response_class=EventSourceResponse)
async def events() -> AsyncIterable[dict[str, str]]:
    yield {"status": "ready"}
```

Yield `ServerSentEvent` to set `event`, `id`, `retry`, or `comment`. `data` is
always JSON-encoded; use the mutually exclusive `raw_data` for preformatted
text and sentinels.

```python
from collections.abc import AsyncIterable
from fastapi.sse import EventSourceResponse, ServerSentEvent

@app.get("/status", response_class=EventSourceResponse)
async def status() -> AsyncIterable[ServerSentEvent]:
    yield ServerSentEvent(data={"ready": True}, event="status", id="1")
    yield ServerSentEvent(raw_data="[DONE]", event="done")
```

`EventSourceResponse` sends an idle keepalive comment every 15 seconds and
defaults to `Cache-Control: no-cache` and `X-Accel-Buffering: no`.

FastAPI 0.140.12 fixes `format_sse_event()` line splitting to follow the SSE
wire format. Upgrade before relying on multiline event content instead of
compensating in clients. FastAPI 0.140.13 also fixes SSE decorator status
codes (`2026-08`).

## Byte schema metadata

From FastAPI 0.129.1, JSON Schema for `bytes` uses
`contentMediaType: application/octet-stream`, not `format: binary`. Update
schema snapshots, generators, and consumers that match the older form.
