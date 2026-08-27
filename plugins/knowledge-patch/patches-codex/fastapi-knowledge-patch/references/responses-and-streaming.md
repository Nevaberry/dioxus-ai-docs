# Responses and streaming

## Ordinary response contracts

### Bodiless operations can return `None`

FastAPI 0.117.0 (`2025-09`) accepts `-> None` for a status code that forbids a
response body. The annotation can match the handler's real contract without
triggering response-model errors.

```python
@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int) -> None:
    return None
```

### Direct Pydantic JSON serialization

FastAPI 0.130 (`2026-02`) directly serializes typed Pydantic returns and
`response_model` values to JSON bytes when no response class is declared.
`ORJSONResponse` and `UJSONResponse` are deprecated from 0.131.

Declaring a JSON response class still applies Pydantic filtering, but the value
then passes through `jsonable_encoder` and the response class performs byte
serialization (`streaming-and-responses`). Omit the response class for the
direct path; specify it only when its distinct encoding behavior is wanted.

### Iterable return values honor model options

FastAPI 0.140.11 (`2026-08`) applies `response_model_*` settings to a
non-generator endpoint annotated with `Iterable[...]`, including options such
as `response_model_exclude_none`.

```python
from collections.abc import Iterable

@app.get("/items", response_model_exclude_none=True)
def read_items() -> Iterable[Item]:
    return [Item(name="one", note=None)]
```

FastAPI 0.140.9 recursively propagates `exclude_defaults=True` through mapping
keys and values in `jsonable_encoder()`, so defaults on nested models remain
excluded (`2026-08`).

## JSON Lines generators

FastAPI 0.134 (`2026-02`) lets a path operation stream by yielding. Without a
custom response class, `Iterable[Item]` or `AsyncIterable[Item]` selects JSON
Lines: each item is Pydantic-validated, filtered, documented, and serialized as
`application/jsonl`. An unannotated generator sends each item through
`jsonable_encoder` (`streaming-and-responses`).

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

FastAPI 0.140.8 preserves the streaming item type when a router is attached
with `include_router()`, retaining item validation, serialization, and OpenAPI
generation (`2026-08`). FastAPI 0.140.13 also honors the decorator's configured
`status_code` for JSON Lines and SSE endpoints.

## Raw streaming

Set `response_class=StreamingResponse` to send raw strings or bytes. Pydantic
does not process them, and the generator annotation is used only by type
checkers (`streaming-and-responses`). Give the response class an explicit media
type.

Prefer a yielding path operation with `response_class=StreamingResponse` over
directly returning a response backed by an async generator: the path-operation
form handles cancellation, whereas a directly returned response depends on the
generator reaching an `await` cancellation point. For blocking file-like
sources, use a regular `def` returning `Iterable[bytes]` so the work does not
block the event loop.

```python
from collections.abc import Iterable
from fastapi.responses import StreamingResponse

class BinaryStream(StreamingResponse):
    media_type = "application/octet-stream"

@app.get("/download", response_class=BinaryStream)
def stream_bytes() -> Iterable[bytes]:
    yield b"first chunk\n"
    yield b"second chunk\n"
```

Starlette `StreamingResponse` raises `ClientDisconnect` when a client drops;
wrapping middleware can handle it explicitly (see
[starlette.md](starlette.md)).

## Server-Sent Events

FastAPI 0.135.0 adds native SSE support (`2026-03`). Use
`response_class=EventSourceResponse`. Plain yielded values are JSON-encoded in
the event's `data:` field. As with JSON Lines, an iterable item annotation
enables validation, documentation, and Pydantic serialization; an unannotated
generator uses `jsonable_encoder` (`streaming-and-responses`).

```python
from collections.abc import AsyncIterable
from fastapi.sse import EventSourceResponse, ServerSentEvent

@app.get("/status", response_class=EventSourceResponse)
async def status() -> AsyncIterable[ServerSentEvent]:
    yield ServerSentEvent(data={"ready": True}, event="status", id="1")
    yield ServerSentEvent(raw_data="[DONE]", event="done")
```

`ServerSentEvent` can set `event`, `id`, `retry`, or `comment`. Its `data`
argument is always JSON-encoded. Use the mutually exclusive `raw_data` argument
for preformatted text or sentinels. `EventSourceResponse` defaults to a
15-second idle keepalive comment, `Cache-Control: no-cache`, and
`X-Accel-Buffering: no` (`streaming-and-responses`).

FastAPI 0.140.12 fixes `format_sse_event()` so multiline values are split
according to the SSE protocol (`2026-08`). Upgrade before relying on multiline
content rather than compensating in clients.

## Annotation and schema edge cases

FastAPI 0.140.10 correctly handles sequence annotations containing nested
`Annotated` metadata (`2026-08`). Remove workarounds that flatten those
annotations after upgrading.

JSON Schema for `bytes` uses
`contentMediaType: application/octet-stream`, replacing `format: binary`, from
FastAPI 0.129.1 (`2026-02`). Update response-schema snapshots and generators.
