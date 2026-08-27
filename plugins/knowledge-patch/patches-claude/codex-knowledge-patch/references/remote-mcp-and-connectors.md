# Remote TUI, MCP, and connectors

## Remote TUI ownership

The workspace-owning machine runs the app server and executes commands; a
second machine may provide the TUI.

```bash
# Workspace host
codex app-server --listen ws://127.0.0.1:4500

# TUI through a forwarded loopback port
codex --remote ws://127.0.0.1:4500
```

Pass an explicit `ws://` or `wss://` URL. For non-local use, put authenticated
connections behind TLS.

## Capability-token authentication

For a network listener, configure a capability token. The app server reads the
token from `--ws-token-file`; the client reads it from the environment variable
named by `--remote-auth-token-env`.

The client refuses to send a bearer token over non-loopback `ws://`.

## Signed bearer authentication

Signed bearer authentication uses HS256 JWTs with a required `exp` claim. The
shared secret must contain at least 32 bytes, and the client sends the token
only over `wss://` or loopback `ws://`.

## Interactive MCP authentication

Since `0.144.0`, MCP tools may request interactive authentication by default;
an experimental opt-in is no longer needed.

App-server hosts may supply authentication at runtime. A successful hosted
login may redirect to a hosted page. Long-running app sessions refresh expired
authentication for the hosted `codex_apps` connector.

## MCP administration and serving

Configure STDIO or streaming HTTP MCP servers in `~/.codex/config.toml`, or
manage them with `codex mcp`. The CLI can also run as an MCP server for another
agent.

## Proxy-aware Responses WebSockets

Since `0.144.0`, Responses WebSockets keep the low-latency transport while
respecting system proxy settings and custom certificate authorities.

## App-server V2 test client

`codex debug app-server send-message-v2 USER_MESSAGE` initializes the
experimental V2 protocol, starts a thread, sends one turn, and streams server
notifications. Use it for local protocol debugging.

## Sign in with ChatGPT for plugins

The beta sign-in flow initially supports Airtable, GitLab, HubSpot, Notion,
Supabase, and Vercel integrations. It can create or link an account from the
plugin directory or a participating partner site.

A partner receives only the available name, email address, and profile
picture. The requested permissions for each plugin still require a separate
approval.
