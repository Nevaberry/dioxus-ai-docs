# WebSocket hibernation

## Accept sockets through the Durable Object state

For hibernation, accept the server endpoint with `ctx.acceptWebSocket()` and
handle wake-up events in Durable Object methods such as `webSocketMessage()` and
`webSocketClose()`. The standard `ws.accept()` path does not enable hibernation.
Only inbound WebSockets served by the object can hibernate; outbound WebSockets
cannot.

```ts
export class Room extends DurableObject {
  async fetch(): Promise<Response> {
    const [client, server] = Object.values(new WebSocketPair());
    this.ctx.acceptWebSocket(server);
    return new Response(null, { status: 101, webSocket: client });
  }

  webSocketMessage(ws: WebSocket, message: string | ArrayBuffer) {
    ws.send(message);
  }
}
```

## Serialized attachments

`serializeAttachment(value)` stores a structured-clone snapshot with a socket
across hibernation. The snapshot is limited to 16,384 bytes; subsequent changes
to the original value are not saved unless `serializeAttachment()` is called
again. `deserializeAttachment()` returns the latest snapshot or `null`.

```ts
server.serializeAttachment({ userId });

webSocketMessage(ws: WebSocket, message: string | ArrayBuffer) {
  const state = ws.deserializeAttachment() as { userId: string };
  ws.send(`${state.userId}: ${message}`);
}
```

The attachment disappears when either endpoint closes. Store larger or
longer-lived state in Durable Object storage.

## Tags

`acceptWebSocket()` can assign at most 10 tags, each no longer than 256
characters. `getWebSockets(tag)` filters attached sockets by one tag.
`getTags(ws)` returns a socket's tags and throws if that socket was not accepted
by this Durable Object.

```ts
this.ctx.acceptWebSocket(server, ["room:42"]);
const roomSockets = this.ctx.getWebSockets("room:42");
const tags = this.ctx.getTags(server);
```

## Wake-free auto-responses

`setWebSocketAutoResponse()` installs a single request/response pair that the
runtime handles without waking the object. Both strings are limited to 2,048
characters. Omitting the pair clears the configured response, while
`getWebSocketAutoResponseTimestamp(ws)` continues to report the time of that
socket's last automatic response.

```ts
this.ctx.setWebSocketAutoResponse(
  new WebSocketRequestResponsePair("ping", "pong"),
);
```

## Event runtime limit

`setHibernatableWebSocketEventTimeout(milliseconds)` limits a hibernatable
event to at most 604,800,000 ms, or seven days. Pass `0` or omit the value to
clear the limit. The getter returns the active number of milliseconds or
`null`.

```ts
this.ctx.setHibernatableWebSocketEventTimeout(30_000);
```

## Close-handshake visibility

A server-closed socket can remain in `CLOSING` and continue appearing in
`getWebSockets()` until its peer completes the closing handshake. With
compatibility date `2026-04-07` or later, the default
`web_socket_auto_reply_to_close` flag automatically completes the handshake so
the socket reaches `CLOSED` sooner.
