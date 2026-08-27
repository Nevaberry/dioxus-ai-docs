# WebSocket hibernation

## Use Durable Object WebSocket handlers

Accept the server side with `ctx.acceptWebSocket()` and handle wake-up events
through class methods such as `webSocketMessage()` and `webSocketClose()`.
Standard `ws.accept()` does not enable hibernation. Only inbound WebSockets
served by the Durable Object can hibernate; outbound WebSocket connections
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

## Preserve per-connection state with attachments

`serializeAttachment(value)` stores a structured-clone snapshot with the
socket across hibernation, up to 16,384 bytes. Later mutations are not saved
unless the method is called again. `deserializeAttachment()` returns the
latest snapshot or `null`.

```ts
server.serializeAttachment({ userId });

webSocketMessage(ws: WebSocket, message: string | ArrayBuffer) {
  const state = ws.deserializeAttachment() as { userId: string };
  ws.send(`${state.userId}: ${message}`);
}
```

The attachment is lost when either side closes. Put larger or longer-lived
state in Durable Object storage.

## Group accepted sockets with bounded tags

`acceptWebSocket()` accepts at most 10 tags per socket, each at most 256
characters. `getWebSockets(tag)` filters attached sockets, and `getTags(ws)`
returns a socket's tags. `getTags()` throws if that Durable Object did not
accept the socket.

```ts
this.ctx.acceptWebSocket(server, ["room:42"]);
const roomSockets = this.ctx.getWebSockets("room:42");
const tags = this.ctx.getTags(server);
```

## Configure auto-responses

`setWebSocketAutoResponse()` installs one request/response pair that the
runtime handles without waking the object. Each string is limited to 2,048
characters. Omitting the pair clears it, while
`getWebSocketAutoResponseTimestamp(ws)` continues to report the last
auto-response time for the socket.

```ts
this.ctx.setWebSocketAutoResponse(
  new WebSocketRequestResponsePair("ping", "pong"),
);
```

## Limit hibernatable event runtime

`setHibernatableWebSocketEventTimeout(milliseconds)` caps a hibernatable event
at no more than 604,800,000 ms (seven days). Passing `0` or omitting the value
clears the limit. The getter returns the current millisecond value or `null`.

## Account for closing sockets

A server-closed socket can remain in `CLOSING` and continue to appear in
`getWebSockets()` until the peer completes the close handshake. With
compatibility date `2026-04-07` or later, the default
`web_socket_auto_reply_to_close` flag automatically completes the handshake so
sockets reach `CLOSED` sooner.
