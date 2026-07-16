# Responses and streaming

Use this reference to choose between ordinary model responses, JSON Lines, raw chunk streaming, and Server-Sent Events.

## Contents

- [Ordinary responses](#ordinary-responses)
- [Yield directly from a path operation](#yield-directly-from-a-path-operation)
- [JSON Lines](#json-lines)
- [Raw `StreamingResponse` chunks](#raw-streamingresponse-chunks)
- [Server-Sent Events](#server-sent-events)
- [Resource lifetime and disconnects](#resource-lifetime-and-disconnects)

## Ordinary responses

### Bodiless status codes

FastAPI 0.117 accepts `-> None` for a response status that cannot carry a body, such as `204 No Content` (`2025-09`). Use the accurate annotation rather than inventing a response model to satisfy route construction.

### Model-backed JSON serialization

FastAPI 0.130 serializes through Pydantic when a handler has a Pydantic return annotation or a `response_model`. FastAPI 0.131 deprecates `ORJSONResponse` and `UJSONResponse` (`2026-02`):

```python
from fastapi import FastAPI
from pydantic import BaseModel

class Item(BaseModel):
    name: str

app = FastAPI()

@app.get("/items/{name}", response_model=Item)
def read_item(name: str):
    return {"name": name}
```

Use specialized response classes only when response semantics—not routine JSON speed—require them.

### Byte schemas

FastAPI 0.129.1 documents `bytes` with JSON Schema `contentMediaType: application/octet-stream` instead of `format: binary`. Update schema snapshots and generators that used the old marker.

## Yield directly from a path operation

FastAPI 0.134 can stream JSON Lines or binary data directly when the path operation uses `yield`; wrapping every generator in `StreamingResponse` is no longer necessary (`2026-02`). The declaration and response class determine the mode.

## JSON Lines

A normally yielded endpoint responds with `application/jsonl` (`streaming-and-responses`). Annotate the generator to define item handling:

- Use `AsyncIterable[Item]` for an asynchronous generator.
- Use `Iterable[Item]` for a synchronous generator.
- With one of these annotations, FastAPI validates, filters, documents, and serializes every item through Pydantic.
- Without a return annotation, FastAPI serializes yielded values through `jsonable_encoder` instead.

```python
from collections.abc import AsyncIterable

@app.get("/items/stream")
async def stream_items() -> AsyncIterable[Item]:
    for item in items:
        yield item
```

Use this mode for structured sequences whose individual records must obey the documented model.

## Raw `StreamingResponse` chunks

Set `response_class=StreamingResponse` to yield unmodified strings or bytes. In this mode:

- FastAPI bypasses JSON conversion and Pydantic serialization.
- The generator's return annotation does not control runtime serialization.
- A bare `StreamingResponse` has no content type.

Define a response subclass when clients require a media type:

```python
from collections.abc import AsyncIterable
from fastapi.responses import StreamingResponse

class PNGStreamingResponse(StreamingResponse):
    media_type = "image/png"

@app.get("/image/stream", response_class=PNGStreamingResponse)
async def stream_image() -> AsyncIterable[bytes]:
    for chunk in chunks:
        yield chunk
```

Use this mode for already encoded media, protocol frames, or other byte streams that must not be structurally transformed.

## Server-Sent Events

FastAPI 0.135 introduces SSE support (`2026-03`). Import its response and event types from `fastapi.sse`.

### Plain yielded values

Set `response_class=EventSourceResponse`. Each plain yielded value is JSON-encoded into the event's `data:` field. As with JSON Lines, `AsyncIterable[Item]` enables per-item Pydantic validation, documentation, and serialization; no annotation falls back to `jsonable_encoder`.

```python
from collections.abc import AsyncIterable
from fastapi.sse import EventSourceResponse

@app.get("/items/events", response_class=EventSourceResponse)
async def stream_items() -> AsyncIterable[Item]:
    for item in items:
        yield item
```

### Structured event metadata

Yield `ServerSentEvent` when an event needs `event`, `id`, `retry`, or `comment` fields. Its `data` argument is always JSON-encoded. Use the mutually exclusive `raw_data` argument for preformatted text or sentinel values:

```python
from collections.abc import AsyncIterable
from fastapi.sse import EventSourceResponse, ServerSentEvent

@app.get("/events", response_class=EventSourceResponse)
async def events() -> AsyncIterable[ServerSentEvent]:
    yield ServerSentEvent(
        data={"status": "ready"}, event="status", id="1", retry=5000
    )
    yield ServerSentEvent(raw_data="[DONE]", event="done")
```

### Connection defaults

FastAPI's SSE response sends a keepalive comment after 15 idle seconds. It also sets:

- `Cache-Control: no-cache`
- `X-Accel-Buffering: no`

These defaults discourage intermediary caching and buffering and help keep idle connections alive.

## Resource lifetime and disconnects

A request-scoped `yield` dependency remains active until streaming finishes; a function-scoped one exits before sending the response. Select the dependency scope based on whether the generator still needs the resource. See [dependency-injection.md](dependency-injection.md).

With Starlette 0.42 or newer, a client disconnect while a `StreamingResponse` is sending raises `ClientDisconnect`. Allow intentional cleanup to run, and update middleware, tests, and error reporting that assumed a dropped stream ended silently.
