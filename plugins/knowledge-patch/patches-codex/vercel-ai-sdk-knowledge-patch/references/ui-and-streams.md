# UI Messages, Chat, and Streams

## Chat persistence

Since 4.1.0, chat IDs can travel from the client to the server and server-assigned
response message IDs can travel back to the client. Use `appendResponseMessages` to
combine stored prior messages with returned response messages before persistence.
Preserve the server's IDs rather than regenerating them on the client.

## Custom data streams

`createDataStreamResponse` (4.1.0) can emit arbitrary data and message annotations
before and alongside model output. Merge a `streamText` result with
`mergeIntoDataStream`; `useChat` can then read both custom data and annotations.

```ts
return createDataStreamResponse({
  execute: async dataStream => {
    dataStream.writeData({ type: 'source', url });
    const result = streamText({ model, messages });
    result.mergeIntoDataStream(dataStream);
  },
});
```

## Consume every text stream

`streamText` starts immediately but honors consumer backpressure, so generation makes
progress only while a returned stream is consumed. Generation errors are delivered to
`onError` or as in-band `error` parts in the full event stream; they are not thrown by
the initial call. Tool execution failures are `tool-error` parts and also appear in
non-streaming `steps`. Schema failures and other `generateText` failures still throw.

```ts
const result = streamText({
  model,
  prompt,
  onError: ({ error }) => log(error),
});

// On v7 use result.stream; earlier API lines expose result.fullStream.
for await (const part of result.stream) handle(part);
```

Response-piping helpers return promises as of 2026-08. Await them to catch failures
while reading from the generation stream or writing to the response.

## Time to first content

Streaming generation supports per-step `firstChunkMs` (2026-08) for the first content
chunk. Both `firstChunkMs` and the idle `chunkMs` budget are streaming-only and emit a
warning when passed to `generateText`.

```ts
const result = streamText({
  model,
  prompt,
  timeout: { firstChunkMs: 5_000 },
});

for await (const part of result.stream) consume(part);
```

## Stream transforms

`experimental_transform` accepts one transform or an ordered array. Transformed
events are the values observed by later transforms, callbacks, and resolved result
promises. A custom transform receives `tools` and `stopStream`. If it stops early, it
must emit synthetic `finish-step` and `finish` events so downstream consumers settle.

```ts
const result = streamText({
  model,
  prompt,
  experimental_transform: [smoothStream(), redactTransform()],
});
```

## Direct agent chat

`DirectChatTransport` (2026-07) connects `useChat` directly to an `Agent`, avoiding a
separate route transport.

```ts
const { messages, sendMessage } = useChat({
  transport: new DirectChatTransport({ agent }),
});
```

UI flows can submit approval responses automatically, use asynchronous
`sendAutomaticallyWhen` conditions, and preserve provider metadata across streams and
turns.

## Realtime browser sessions

Experimental realtime hooks (2026-07) normalize direct browser WebSocket sessions,
server-created ephemeral tokens, audio transcription, client-driven tools, and
`UIMessage[]` state across realtime providers and the gateway.

```ts
const realtime = experimental_useRealtime({
  model: realtimeModel,
  api: { token: '/api/realtime/setup' },
  onToolCall: async ({ toolCall }) => handleToolCall(toolCall),
});
```

Keep privileged provider credentials on the server and issue browser sessions only
the ephemeral material required by the selected realtime transport.

## Completion and chat lifecycle

Completion APIs accept typed custom request bodies as of 2026-08. Errors thrown by a
`Chat` instance's `onFinish` callback propagate to the request that initiated the
response. Chat status remains `submitted` until response content actually begins
streaming, so do not interpret `submitted` as evidence that content has arrived.
