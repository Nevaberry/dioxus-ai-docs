# Streaming and Retry Links

## Contents

- [Stream query and mutation results](#stream-query-and-mutation-results)
- [Configure the batch stream](#configure-the-batch-stream)
- [Respect response-header timing](#respect-response-header-timing)
- [Handle streamed errors and final chunks](#handle-streamed-errors-and-final-chunks)
- [Keep JSONL responses alive](#keep-jsonl-responses-alive)
- [Meet runtime requirements](#meet-runtime-requirements)
- [Define explicit retry policy](#define-explicit-retry-policy)

## Stream query and mutation results

A query or mutation may return an async generator. With
`httpBatchStreamLink`, the client receives the resolved result as an
`AsyncIterable` and can process values before the procedure finishes.

```ts
import { createTRPCClient, httpBatchStreamLink } from '@trpc/client';

const appRouter = router({
  numbers: publicProcedure.query(async function* () {
    yield 1;
    yield 2;
  }),
});

const client = createTRPCClient<typeof appRouter>({
  links: [httpBatchStreamLink({ url: 'http://localhost:3000' })],
});

const numbers = await client.numbers.query();
for await (const number of numbers) console.log(number);
```

Use this for an incrementally delivered procedure result. It is not a
replacement for subscriptions, which have reconnection and ongoing event
semantics.

## Configure the batch stream

Set `streamHeader` on `httpBatchStreamLink` when the peer requires a custom
streaming header (since 11.13.2). Keep the option aligned with the server or
intermediary responsible for recognizing streamed responses.

## Respect response-header timing

The streaming batch response commits HTTP headers before procedure data is
available. Therefore:

- a procedure cannot change headers or set cookies after streaming starts;
- the object passed to `responseMeta` has no `data` key;
- response metadata cannot depend on the eventual procedure result.

Use `httpBatchLink` when authentication refresh, cookies, cache headers, or
other response headers must be calculated from returned data.

## Handle streamed errors and final chunks

Multi-call stream errors are attributed to the failing call's actual batch
index (since 11.14.0). Do not add client logic that assumes a streamed failure
belongs to the first or last operation.

Buffered chunks are preserved when the response stream closes (since
11.14.0). Consume the iterable to completion so already-buffered final results
can be delivered.

For streaming responses, the server unwraps an error stored in `cause` before
calling `onError` (since 11.17.0). Inspect the callback's error as the
originating error rather than expecting its transport wrapper.

## Keep JSONL responses alive

Configure `jsonl.pingMs` in the root server configuration to emit keepalive
pings on long-lived JSONL responses.

```ts
import { initTRPC } from '@trpc/server';

const t = initTRPC.create({
  jsonl: {
    pingMs: 1_000,
  },
});
```

Use a duration shorter than any relevant idle timeout in proxies or hosting
infrastructure.

## Meet runtime requirements

Outside browsers, the `fetch` supplied to `httpBatchStreamLink` must return a
Web or Node readable response body. A fetch implementation that buffers the
entire body defeats incremental delivery.

React Native needs:

- `TextDecoder` and `TextDecoderStream` polyfills;
- `ReadableStream` and `WritableStream` when the decoder polyfill does not
  provide them;
- a streaming-capable fetch implementation.

For Expo fetch, enable text streaming on the request:

```ts
httpBatchStreamLink({
  url: 'http://localhost:3000',
  fetch: (url, options) =>
    fetch(url, {
      ...options,
      reactNative: { textStreaming: true },
    }),
});
```

Configure AWS Lambda for streaming responses; otherwise the link behaves like
`httpBatchLink`. For Cloudflare Workers, enable the
`streams_enable_constructors` compatibility flag.

## Define explicit retry policy

`retryLink` requires a `retry` callback. It receives the failed `op`, its
`error`, and `attempts`; the attempt count includes the original call.
`retryDelayMs` is optional and defaults to no delay.

```ts
import { retryLink } from '@trpc/client';

const retry = retryLink({
  retry: ({ op, error, attempts }) =>
    op.type === 'query' &&
    (!error.data || error.data.code === 'INTERNAL_SERVER_ERROR') &&
    attempts <= 3,
  retryDelayMs: (attempt) => Math.min(1_000 * 2 ** attempt, 30_000),
});
```

Keep retries bounded and operation-aware. Clients using `@trpc/react-query`
usually already retry through TanStack Query and generally do not need
`retryLink` in addition.
