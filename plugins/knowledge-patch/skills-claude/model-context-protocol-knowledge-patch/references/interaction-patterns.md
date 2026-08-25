# Elicitation, Sampling, Tools, and Tasks

## Tool behavior annotations (`2025-03-26`)

Tool definitions may carry annotations describing behavior such as read-only
or destructive effects. Clients can use those annotations to present intended
effects more accurately.

## Progress and content (`2025-03-26`)

`ProgressNotification` supports a `message` field in addition to progress
values, allowing descriptive updates:

```json
{"jsonrpc":"2.0","method":"notifications/progress","params":{"progressToken":"job-7","progress":42,"message":"Indexing files"}}
```

MCP content may also contain audio alongside text and image content.

## Completion negotiation and context

The `completions` capability (`2025-03-26`) lets a server advertise argument
autocompletion. Clients should check it before relying on completion requests.

`CompletionRequest` gains `context` (`2025-06-18`) for previously resolved
variables, so later suggestions can account for earlier selections.

## Form elicitation (`2025-06-18-compat`)

A client advertises `capabilities.elicitation`; a server can then nest an
`elicitation/create` request inside another operation to ask for non-sensitive
structured input. `requestedSchema` is a flat object limited to primitive
string, number/integer, boolean, or string-enum properties. Complex nesting
and arrays of objects are unsupported.

```json
{"jsonrpc":"2.0","id":7,"method":"elicitation/create","params":{"message":"Choose a region","requestedSchema":{"type":"object","properties":{"region":{"type":"string","enum":["eu","us"],"enumNames":["Europe","United States"]}},"required":["region"]}}}
```

The response action is `accept`, `decline`, or `cancel`. Acceptance carries
schema-conforming `content`; decline is an explicit refusal and cancel is a
dismissal without a choice. Decline and cancel typically omit `content`.

```json
{"jsonrpc":"2.0","id":7,"result":{"action":"accept","content":{"region":"eu"}}}
```

## Elicitation modes and URL completion (`2025-11-25-compat`)

Negotiate modes with `elicitation: {form: {}, url: {}}`. The legacy empty
object means form-only, and an omitted request `mode` defaults to `form`. URL
mode is still subject to change and is for sensitive or third-party
interactions outside the client. Do not use it to authorize the client to the
MCP server.

```json
{
  "method": "elicitation/create",
  "params": {
    "mode": "url",
    "elicitationId": "setup-7",
    "url": "https://mcp.example.com/connect",
    "message": "Connect the external service."
  }
}
```

An `accept` response means only that the user agreed to open the URL, not that
the out-of-band interaction finished. The server may later send
`notifications/elicitation/complete` with the same ID. Alternatively, error
`-32042` carries one or more required URL elicitations; the client can complete
them before retrying the original request.

## Form choice schemas (`2025-11-25-compat`)

Form schemas remain flat but now support multi-select string arrays. Use
`oneOf` entries containing `const` and `title` for titled single-select
choices. For titled multi-select choices, use array `items.anyOf`. Defaults are
supported, and clients should pre-populate them.

```json
{
  "type": "array",
  "items": {
    "anyOf": [
      {"const": "eu", "title": "Europe"},
      {"const": "us", "title": "United States"}
    ]
  }
}
```

## Structured and linked tool results (`2025-06-18-compat`)

A tool may declare `outputSchema` and return its JSON object in
`structuredContent`. Servers must conform to the declared schema, and clients
should validate it. For older clients, also serialize the same JSON into a
text item in `content`.

```json
{"content":[{"type":"text","text":"{\"temperature\":22.5}"}],"structuredContent":{"temperature":22.5}}
```

Tool results may contain a `resource_link` with a fetchable or subscribable
URI and resource annotations. The linked resource is not guaranteed to appear
in `resources/list`.

```json
{"type":"resource_link","uri":"file:///project/src/main.rs","name":"main.rs","mimeType":"text/x-rust"}
```

## Tool-enabled sampling (`2025-11-25-compat`)

Clients advertise `sampling: {tools: {}}` before servers include `tools` and
optional `toolChoice` (`auto`, `required`, or `none`) in
`sampling/createMessage`. A tool-using result contains assistant `tool_use`
content with `id`, `name`, and `input`. The server executes it and sends a new
sampling request whose next user message contains the matching `tool_result`.

```json
{"role":"assistant","content":[{"type":"tool_use","id":"call-1","name":"weather","input":{"city":"Paris"}}]}
{"role":"user","content":[{"type":"tool_result","toolUseId":"call-1","content":[{"type":"text","text":"18 C"}]}]}
```

Every tool use must be followed before any other message by exactly one
matching result. A tool-result message must contain only tool results.
Violations use `-32602`.

## Sampling context soft-deprecation (`2025-11-25-compat`)

`includeContext: "thisServer"` and `"allServers"` are soft-deprecated. Omit
the field to use the `"none"` default. A server should send either old value
only when the client explicitly advertises `sampling: {context: {}}`.

## Experimental task creation (`2025-11-25-compat`)

Tasks are experimental and negotiated by request category. Servers can
advertise `tasks.requests.tools.call`; clients can advertise
`tasks.requests.sampling.createMessage` and
`tasks.requests.elicitation.create`. `tasks.list` and `tasks.cancel` are
separate capabilities.

A tool sets `execution.taskSupport` to `required`, `optional`, or `forbidden`;
absence means forbidden. Violating required or forbidden task use should
produce `-32601`.

```json
{
  "method": "tools/call",
  "params": {
    "name": "long_job",
    "arguments": {},
    "task": {"ttl": 60000}
  }
}
```

An accepted augmented request immediately returns `result.task` instead of
the underlying operation result. The receiver creates the unique task ID,
starts it in `working`, and may override the requested millisecond TTL.

## Task polling, results, and related messages (`2025-11-25-compat`)

Poll with `tasks/get` while respecting `pollInterval`.
`notifications/tasks/status` is optional and cannot replace polling.
`tasks/result` blocks until `completed`, `failed`, or `cancelled`, then returns
exactly the underlying request's result or JSON-RPC error.

`input_required` instructs the requestor to call `tasks/result` so the receiver
can deliver needed requests before returning to `working`.

```json
{"method":"tasks/get","params":{"taskId":"task-7"}}
{"method":"tasks/result","params":{"taskId":"task-7"}}
```

Task-associated messages carry
`_meta["io.modelcontextprotocol/related-task"].taskId`. The `tasks/get`,
`tasks/list`, and `tasks/cancel` control messages omit it. A `tasks/result`
request also omits it because its `taskId` parameter is authoritative; a
`tasks/result` response must carry it because the underlying result lacks a
task ID.

Terminal states never transition. Expired tasks may disappear. Cancelling an
already-terminal task returns `-32602`.

## Presentation metadata (`2025-06-18`, `2025-11-25`)

Schema types can use `title` as a human-friendly display label while keeping
`name` as the programmatic identifier used in protocol calls. Tools,
resources, resource templates, and prompts can expose icons for clients to
present.

## Tool input validation failures (`2025-11-25`)

Return tool-call input validation failures as Tool Execution Errors rather
than Protocol Errors. This lets the caller inspect the failure and correct the
tool input.
