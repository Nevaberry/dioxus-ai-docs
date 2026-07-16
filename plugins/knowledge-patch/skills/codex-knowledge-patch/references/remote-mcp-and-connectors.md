# Remote TUI, MCP, and connectors

## Remote TUI architecture

An app server can own a workspace and execute commands on one machine while a
TUI on another machine connects with `--remote`. Both the listener and client
require an explicit `ws://` or `wss://` URL.

For a local or SSH-forwarded loopback connection:

```bash
# Workspace host
codex app-server --listen ws://127.0.0.1:4500

# TUI host, through the forwarded loopback port
codex --remote ws://127.0.0.1:4500
```

Use unauthenticated plain WebSockets only for loopback or an SSH-forwarded
connection.

## Capability-token authentication

For a network listener, store the server's capability token in a protected file
and tell the client which environment variable contains the token. The client
refuses to send a token over non-loopback `ws://`, so authenticated network
access must reach the server through TLS at a `wss://` URL.

```bash
# Workspace host
codex app-server --listen ws://0.0.0.0:4500 \
  --ws-auth capability-token \
  --ws-token-file "$HOME/.codex/codex-app-server-token"

# TUI host; retrieve the same token through SSH
export CODEX_REMOTE_AUTH_TOKEN="$(ssh devbox 'cat ~/.codex/codex-app-server-token')"
codex --remote wss://devbox.example.com:4500 \
  --remote-auth-token-env CODEX_REMOTE_AUTH_TOKEN
```

## Signed bearer authentication

Select `--ws-auth signed-bearer-token` and provide
`--ws-shared-secret-file`. The server accepts HS256 JWTs with a required `exp`
claim and a shared secret of at least 32 bytes. It validates `nbf`, `iss`, and
`aud` when those claims are configured or present.

## Responses WebSockets behind proxies

Since `0.144.0`, Responses WebSockets retain their low-latency transport when
system proxies or custom certificate authorities are configured.

## MCP server administration

Register a local stdio server by placing its launcher after `--`. Pass launcher
environment values with repeatable `--env KEY=VALUE`:

```bash
codex mcp add local-tools --env MODE=dev -- ./tool-server
```

Alternatively, register a streamable-HTTP server with `--url` and optionally
name an environment variable that contains its bearer token:

```bash
codex mcp add hosted-tools --url https://tools.example/mcp \
  --bearer-token-env-var MCP_TOKEN
```

The stdio launcher and streamable-HTTP URL forms are mutually exclusive.
`codex mcp list` and `codex mcp get` support JSON output.

For an HTTP server that supports OAuth, use `login --scopes` and `logout`:

```bash
codex mcp login hosted-tools --scopes tools.read,tools.write
```

These OAuth commands do not apply to stdio servers. Use `codex mcp-server` to
expose the Codex CLI itself as an MCP server over stdio.

## Interactive and host-provided authentication

Since `0.144.0`, MCP tools may request interactive authentication without an
experimental opt-in. App-server hosts may provide Codex authentication at
runtime, and hosted login flows may redirect successful sign-ins to a hosted
page.

Long-running app sessions refresh expired authentication for the hosted
`codex_apps` connector.

For selecting a connector with `/apps`, see
[tui-and-session-controls.md](tui-and-session-controls.md).
