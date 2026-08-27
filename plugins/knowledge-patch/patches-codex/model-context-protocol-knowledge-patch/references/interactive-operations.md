# Interactive Operations

## Tool definitions and results

### Behavior annotations

Tool definitions can carry annotations describing behavior such as whether a
tool is read-only or destructive, allowing clients to present its intended
effects more accurately. (`2025-03-26`)

### Structured content and resource links

A tool may declare an `outputSchema` and return the corresponding JSON object
in `structuredContent`. Servers must conform to the declared schema and clients
should validate it. For older clients, the server should also serialize the
same JSON into a text item in `content`. (`2025-06-18-compat`)

```json
{"content":[{"type":"text","text":"{\"temperature\":22.5}"}],"structuredContent":{"temperature":22.5}}
```

Tool results may contain a `resource_link` with a fetchable or subscribable URI
and resource annotations. The link is not guaranteed to appear in
`resources/list`.

```json
{"type":"resource_link","uri":"file:///project/src/main.rs","name":"main.rs","mimeType":"text/x-rust"}
```

### Input validation failures

For `2025-11-25`, tool-call input validation failures should be returned as
Tool Execution Errors rather than Protocol Errors. This lets the failure be
inspected and the tool input corrected.

## Content, progress, and completion

MCP content can contain audio data alongside text and image content types.
(`2025-03-26`)

`ProgressNotification` has a `message` field for descriptive status updates in
addition to its progress values. (`2025-03-26`)

```json
{"jsonrpc":"2.0","method":"notifications/progress","params":{"progressToken":"job-7","progress":42,"message":"Indexing files"}}
```

The `completions` capability lets servers explicitly advertise argument
autocompletion support; clients should check it before relying on completion
requests. (`2025-03-26`)

`CompletionRequest` has a `context` field for previously resolved variables,
allowing later completion requests to account for values already selected.
(`2025-06-18`)

## Elicitation

### Form requests and response actions

A client advertises `capabilities.elicitation`, after which a server can nest
an `elicitation/create` request inside another operation to ask the user for
non-sensitive structured input. (`2025-06-18-compat`)

`requestedSchema` is restricted to a flat object of primitive string,
number/integer, boolean, or string-enum properties. Complex nesting and arrays
of objects are not supported.

```json
{"jsonrpc":"2.0","id":7,"method":"elicitation/create","params":{"message":"Choose a region","requestedSchema":{"type":"object","properties":{"region":{"type":"string","enum":["eu","us"],"enumNames":["Europe","United States"]}},"required":["region"]}}}
```

The response action is `accept`, `decline`, or `cancel`. Acceptance carries
schema-conforming `content`; decline is an explicit refusal; cancel is a
dismissal without a choice. Decline and cancel typically omit `content`.

```json
{"jsonrpc":"2.0","id":7,"result":{"action":"accept","content":{"region":"eu"}}}
```

### Mode negotiation and URL mode

For `2025-11-25-compat`, elicitation capabilities negotiate modes explicitly
with `elicitation: {form: {}, url: {}}`. The legacy empty object means
form-only, and an omitted request `mode` defaults to `"form"`.

URL mode is still subject to change. It is for sensitive or third-party
interactions outside the client, not for authorizing the client to the MCP
server.

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
`-32042` carries one or more required URL elicitations that the client can
complete before retrying the original request.

### Choice fields

Form schemas remain flat, but choice fields include multi-select string arrays
in `2025-11-25-compat`. Use `oneOf` entries with `const` and `title` for titled
single-select choices, and array `items.anyOf` for titled multi-select choices.
Defaults are supported, and clients should pre-populate them.

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

## Sampling with tools

Clients advertise `sampling: {tools: {}}` before servers send `tools` and
optional `toolChoice` with `auto`, `required`, or `none` in
`sampling/createMessage`. (`2025-11-25-compat`)

A tool-using result has assistant `tool_use` content with `id`, `name`, and
`input`. The server executes it and sends another sampling request whose next
user message contains the matching `tool_result`.

```json
{"role":"assistant","content":[{"type":"tool_use","id":"call-1","name":"weather","input":{"city":"Paris"}}]}
{"role":"user","content":[{"type":"tool_result","toolUseId":"call-1","content":[{"type":"text","text":"18 C"}]}]}
```

Every tool use must be followed before any other message by exactly one
matching result. A tool-result message must contain only tool results.
Violations use `-32602`.

`includeContext: "thisServer"` and `"allServers"` are soft-deprecated. Omit
the field to use its `"none"` default. A server should send either old value
only when the client explicitly advertises `sampling: {context: {}}`.
(`2025-11-25-compat`)

## Experimental tasks

### Capabilities and creation

Tasks are experimental in `2025-11-25-compat` and must be negotiated by
request category. Servers can advertise `tasks.requests.tools.call`; clients
can advertise `tasks.requests.sampling.createMessage` and
`tasks.requests.elicitation.create`. `tasks.list` and `tasks.cancel` are
separate capabilities.

A tool sets `execution.taskSupport` to `required`, `optional`, or `forbidden`;
absence means the default `forbidden` case. Violating required or forbidden
task use should produce `-32601`.

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

An accepted augmented request immediately returns `result.task` rather than
the underlying operation result. The receiver creates the unique task ID,
starts it in `working`, and may override the requested millisecond TTL.

### Polling, results, and state

Poll with `tasks/get` while respecting `pollInterval`.
`notifications/tasks/status` is optional and cannot replace polling.
`tasks/result` blocks until `completed`, `failed`, or `cancelled`, then returns
exactly the underlying request's result or JSON-RPC error.

```json
{"method":"tasks/get","params":{"taskId":"task-7"}}
{"method":"tasks/result","params":{"taskId":"task-7"}}
```

`input_required` tells the requestor to call `tasks/result` so the receiver can
deliver needed requests before returning to `working`. Terminal states never
transition. Expired tasks may disappear. Cancelling an already-terminal task
returns `-32602`.

### Related-task metadata

Task-associated messages carry
`_meta["io.modelcontextprotocol/related-task"].taskId`. The `tasks/get`,
`tasks/list`, and `tasks/cancel` control messages omit it. A `tasks/result`
request also omits it because its `taskId` parameter is authoritative, while a
`tasks/result` response must carry it because the underlying result has no task
ID.

## Presentation metadata

Schema types can provide `title` as a human-friendly display name while
reserving `name` for the programmatic identifier. Protocol calls should use
`name`; interfaces can present `title`. (`2025-06-18`)

Servers can expose icons on tools, resources, resource templates, and prompts;
clients can use them when presenting those objects. (`2025-11-25`)

The `Implementation` interface has an optional `description` field for
human-readable client or server context during initialization. (`2025-11-25`)
