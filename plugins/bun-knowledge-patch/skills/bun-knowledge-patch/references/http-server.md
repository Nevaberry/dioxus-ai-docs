# HTTP Server (`Bun.serve`)

## Routes with Parameters

```ts
Bun.serve({
  routes: {
    "/api/users/:id": async (req) => {
      const { id } = req.params;
      return Response.json({ id });
    },
    "/api/users": {
      GET: async () => Response.json(await sql`SELECT * FROM users`),
      POST: async (req) => {
        const { name } = await req.json();
        const [user] = await sql`INSERT INTO users (name) VALUES (${name}) RETURNING *`;
        return Response.json(user);
      },
    },
    "/*": homepage,  // Catch-all for SPA
  },
});
```

The `fetch` handler is optional when `routes` is specified.

## Static Routes

Pre-cached responses (40% faster than dynamic fetch handler):

```ts
Bun.serve({
  static: {
    "/health": new Response("OK"),
    "/redirect": Response.redirect("/new-url", 301),
    "/api/version": Response.json({ version: "1.0" }),
  },
  fetch(req) { /* dynamic routes */ },
});

// Reload static routes dynamically
server.reload({ static: { "/": new Response("Updated!") } });
```

Static routes auto-generate `ETag` headers and respond with `304 Not Modified`.

## HTML Imports

Import HTML files to auto-bundle scripts and styles:

```ts
import homepage from "./index.html";

Bun.serve({
  static: { "/": homepage },
  // or with routes:
  routes: { "/": homepage },
});
```

Scripts (`<script src="...">`) and stylesheets (`<link rel="stylesheet">`) are bundled automatically.

## Cookies

`req.cookies` is a `CookieMap` - parsed lazily for performance:

```ts
Bun.serve({
  routes: {
    "/sign-in": (req) => {
      req.cookies.set("sessionId", Bun.randomUUIDv7(), {
        httpOnly: true,
        sameSite: "strict",
      });
      return new Response("Signed in");
    },
    "/sign-out": (req) => {
      req.cookies.delete("sessionId");
      return new Response("Signed out");
    },
  },
});
```

Standalone usage:

```ts
const cookie = new Bun.Cookie("name", "value");
cookie.serialize(); // "name=value; Path=/; SameSite=lax"

const cookieMap = new Bun.CookieMap();
cookieMap.set("a", "1");
cookieMap.toSetCookieHeaders(); // ["a=1; Path=/; SameSite=Lax", ...]
```

## CSRF Protection

```ts
const token = await Bun.CSRF.generate(sessionId);
const valid = await Bun.CSRF.verify(sessionId, token); // true/false
```

## Frontend Dev Server

Run HTML files directly with hot reloading:

```sh
bun ./index.html           # Single-page app
bun './**/*.html'          # Multi-page app (glob pattern)
```

## Browser Console Streaming

Stream browser `console.log` to terminal:

```sh
bun ./index.html --console
```

```ts
Bun.serve({
  development: {
    console: true,
    hmr: true,
  },
  routes: { "/": homepage },
});
```

Logs appear prefixed with `[browser]`.

## WebSocket Custom Headers

```ts
new WebSocket("ws://localhost:8080", {
  headers: { "Host": "custom.example.com", "X-Custom": "value" },
});
```

## WebSocket Proxy

```ts
new WebSocket("wss://example.com", {
  proxy: "http://proxy:8080",
});

// With authentication
new WebSocket("wss://example.com", {
  proxy: {
    url: "http://proxy:8080",
    headers: { "Proxy-Authorization": "Bearer token" },
  },
});
```

## ServerWebSocket Subscriptions

```ts
websocket: {
  open(ws) {
    ws.subscribe("chat");
    console.log(ws.subscriptions); // ["chat"]
  },
}
```
