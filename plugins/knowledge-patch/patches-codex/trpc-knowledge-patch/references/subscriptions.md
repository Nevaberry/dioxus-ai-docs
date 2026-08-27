# Subscriptions

## Contents

- [Choose SSE and generator handlers](#choose-sse-and-generator-handlers)
- [Use public subscription types](#use-public-subscription-types)
- [Resume tracked events safely](#resume-tracked-events-safely)
- [Configure EventSource credentials](#configure-eventsource-credentials)
- [Refresh active connection configuration](#refresh-active-connection-configuration)
- [Configure liveness and duration](#configure-liveness-and-duration)
- [Control React subscriptions](#control-react-subscriptions)
- [Support React Native](#support-react-native)

## Choose SSE and generator handlers

Prefer Server-Sent Events as the first-choice subscription transport. Use
WebSockets when the application specifically needs their connection behavior.

Subscription handlers may be JavaScript generators. Use generator cleanup to
release listeners when the subscription ends or its abort signal fires, and
apply an output validator when emitted values need runtime validation.

```ts
const onMessage = publicProcedure
  .output(messageSchema)
  .subscription(async function* ({ signal }) {
    const messages = on(events, 'message', { signal });
    for await (const [message] of messages) yield message;
  });
```

## Use public subscription types

Import client resolver contracts from the public package rather than an
internal module (since 11.11.0).

```ts
import type { ResolverDef, SubscriptionResolver } from '@trpc/client';
```

Use the subscription inference helpers added in 11.17.0 to derive integration
types from router definitions instead of duplicating input and event types.

## Resume tracked events safely

Yield `tracked(id, data)` to make both `httpSubscriptionLink` and `wsLink`
resume with the most recently received event ID. Define `lastEventId` in the
procedure input; the reconnecting link supplies it there.

```ts
import { on } from 'node:events';
import { tracked } from '@trpc/server';
import { z } from 'zod';

const onPostAdd = publicProcedure
  .input(z.object({ lastEventId: z.string().nullish() }).optional())
  .subscription(async function* (opts) {
    // Attach first so events cannot fall between replay and live listening.
    const live = on(events, 'add', { signal: opts.signal });

    for await (const post of rowsAfter(opts.input?.lastEventId)) {
      yield tracked(post.id, post);
    }
    for await (const [post] of live) {
      yield tracked(post.id, post);
    }
  });
```

Attach the live listener before querying missed rows. Reversing those steps
creates a replay/listen race.

Thrown errors in the 5xx class cause reconnection and resume. Other errors stop
the subscription and reach the client's `onError` callback.

## Configure EventSource credentials

Native `EventSource` sends cookies on same-origin requests. For cross-origin
cookies, set `withCredentials`:

```ts
httpSubscriptionLink({
  url: 'https://api.example.com/trpc',
  eventSourceOptions: () => ({ withCredentials: true }),
});
```

Native `EventSource` cannot attach arbitrary headers. Supply a compatible
ponyfill when bearer tokens or other headers are required.

```ts
httpSubscriptionLink({
  url: 'https://api.example.com/trpc',
  EventSource: EventSourcePolyfill,
  eventSourceOptions: async ({ op }) => ({
    headers: { authorization: `Bearer ${await tokenFor(op)}` },
  }),
});
```

As a fallback, `connectionParams` are serialized into the URL and exposed as
`opts.info.connectionParams` while creating server context. Prefer headers or
cookies for authentication because URL values have different exposure and
size characteristics.

## Refresh active connection configuration

An `EventSource` instance's built-in retry does not rerun the link's `url()` or
`eventSourceOptions()` callbacks. Place `retryLink` before
`httpSubscriptionLink` in the subscription branch when expired credentials
must create a fresh connection.

```ts
splitLink({
  condition: (op) => op.type === 'subscription',
  true: [
    retryLink({
      retry: ({ error }) =>
        error.data?.code === 'UNAUTHORIZED' ||
        error.data?.code === 'FORBIDDEN',
    }),
    httpSubscriptionLink({
      url: () => getAuthenticatedUrl(),
      EventSource: EventSourcePolyfill,
      eventSourceOptions: () => getAuthenticatedOptions(),
    }),
  ],
  false: httpBatchLink({ url }),
});
```

Recreation reads fresh callback values but discards the tracked-event state
held by the old `EventSource` instance. Account for that distinction when
combining authentication refresh with resumable streams.

## Configure liveness and duration

Advertise an inactivity threshold from the server with
`sse.client.reconnectAfterInactivityMs`. When neither event data nor a ping
arrives before that interval, the client enters `connecting` and reconnects.

```ts
const t = initTRPC.create({
  sse: {
    ping: { enabled: true, intervalMs: 2_000 },
    client: { reconnectAfterInactivityMs: 3_000 },
  },
});
```

Server pings are opt-in through `sse.ping`. Choose
`sse.emitAndEndImmediately` for a one-event mode on runtimes that cannot keep a
streaming response open.

SSE subscriptions reconnect after reaching `maxDurationMs` (since 11.12.0).
A server-enforced connection duration therefore rotates the connection rather
than leaving the subscription disconnected.

## Control React subscriptions

Pause `useSubscription` by passing TanStack Query's `skipToken`. The `enabled`
option is deprecated and scheduled for removal in v12.

```tsx
import { skipToken } from '@tanstack/react-query';

const subscription = trpc.onPostAdd.useSubscription(
  paused ? skipToken : undefined,
  { onData: (post) => console.log(post) },
);

if (subscription.status === 'error') {
  return <button onClick={subscription.reset}>Reconnect</button>;
}
```

Treat the result as a discriminated state with `idle`, `connecting`, `pending`,
or `error`. Call `reset()` to restart manually. After the server completes the
subscription, the result returns to `idle` with `data: undefined`.

## Support React Native

`httpSubscriptionLink` needs ponyfills for EventSource, Streams, and
AsyncIterator APIs in React Native:

- `rn-eventsource-reborn` for EventSource;
- `web-streams-polyfill` for `ReadableStream` and `TransformStream`;
- `@azure/core-asynciterator-polyfill` for AsyncIterator support.

```ts
import '@azure/core-asynciterator-polyfill';
import { RNEventSource } from 'rn-eventsource-reborn';
import { ReadableStream, TransformStream } from 'web-streams-polyfill';

globalThis.ReadableStream ||= ReadableStream;
globalThis.TransformStream ||= TransformStream;

httpSubscriptionLink({ url, EventSource: RNEventSource });
```

Prefer the React-Native-networking-backed EventSource. XMLHttpRequest-based
ponyfills can fail to reconnect after the application returns from the
background.
