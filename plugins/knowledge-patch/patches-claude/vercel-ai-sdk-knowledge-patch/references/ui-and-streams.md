# UI Messages, Chat, and Streams

## Persist `useChat` messages

Chat IDs can travel from the client to the server, while server-assigned response
message IDs return to the client. Use `appendResponseMessages` to combine prior and
returned messages before persistence. (since 4.1.0)

## Mix custom data with generation

`createDataStreamResponse` can emit custom data and message annotations before and
alongside a model response. Merge a `streamText` result with `mergeIntoDataStream`,
then read custom data and annotations through `useChat`. (since 4.1.0)

```ts
return createDataStreamResponse({
  execute: async dataStream => {
    dataStream.writeData({ type: 'source', url });
    const result = streamText({ model, messages });
    result.mergeIntoDataStream(dataStream);
  },
});
```

## Consume text streams and handle in-band errors

`streamText` starts immediately but honors consumer backpressure, so progress depends
on consuming the returned stream. Generation errors are delivered to `onError` or as
in-band `error` parts; tool execution failures are `tool-error` parts and also appear
in non-streaming `steps`. Schema failures and other `generateText` failures still
throw.

For v7 `StreamTextResult`, iterate `stream`; older APIs named this `fullStream`.

```ts
const result = streamText({
  model,
  prompt,
  onError: ({ error }) => log(error),
});

for await (const part of result.stream) handle(part);
```

## Apply stream transforms in order

`experimental_transform` accepts one transform or an ordered array. Its changes are
visible to callbacks and resolved result promises. A custom transform receives `tools`
and `stopStream`; after stopping early, it must emit synthetic `finish-step` and
`finish` events so downstream consumers complete.

```ts
const result = streamText({
  model,
  prompt,
  experimental_transform: [smoothStream(), redactTransform()],
});
```

## Treat experimental lifecycle hooks as observers

`experimental_onStart`, `experimental_onStepStart`,
`experimental_onToolCallStart`, and `experimental_onToolCallFinish` observe operation,
step, and tool boundaries. Exceptions inside these hooks are caught and do not
interrupt generation.

```ts
await generateText({
  model,
  prompt,
  tools,
  experimental_onToolCallFinish({ toolName, durationMs, error }) {
    recordToolRun({ toolName, durationMs, error });
  },
});
```

## Await response piping and configure first-content timeouts

Response-piping helpers return promises. Await them to catch stream read and write
failures. Streaming generation supports per-step `firstChunkMs` for the first content.
Both `firstChunkMs` and `chunkMs` are streaming-only and produce a warning when passed
to `generateText`. (since 2026-08)

```ts
const result = streamText({
  model,
  prompt,
  timeout: { firstChunkMs: 5_000 },
});

for await (const part of result.stream) consume(part);
```

## Connect chat directly to an agent

`DirectChatTransport` lets `useChat` call an `Agent` directly without a separate route
transport. UI flows can submit approval responses automatically, use asynchronous
`sendAutomaticallyWhen` conditions, and preserve provider metadata across streams and
turns. (since 2026-07)

```ts
const { messages, sendMessage } = useChat({
  transport: new DirectChatTransport({ agent }),
});
```

## Build browser realtime sessions

Experimental realtime support normalizes direct browser WebSocket sessions,
server-created ephemeral tokens, audio transcription, client-driven tools, and
`UIMessage[]` state across realtime providers and the gateway. (since 2026-07)

```ts
const realtime = experimental_useRealtime({
  model: realtimeModel,
  api: { token: '/api/realtime/setup' },
  onToolCall: async ({ toolCall }) => handleToolCall(toolCall),
});
```

## Completion and chat lifecycle details

Completion APIs accept typed custom request bodies. Errors thrown by a `Chat`
`onFinish` callback propagate to the initiating request. Chat status remains
`submitted` until response content starts streaming. (since 2026-08)
