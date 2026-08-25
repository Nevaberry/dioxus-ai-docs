# Remote TUI, MCP, and connectors

## Remote TUI and app-server ownership

The machine that owns the workspace and executes commands can run an app
server while another machine provides the TUI.

```bash
codex app-server --listen ws://127.0.0.1:4500
codex --remote ws://127.0.0.1:4500
```

For non-local use, authenticated connections should be behind TLS.
Capability-token authentication uses `--ws-token-file` and
`--remote-auth-token-env`. Signed-bearer authentication uses an HS256 JWT with
`exp` and a shared secret of at least 32 bytes. The client sends bearer tokens
only over `wss://` or loopback `ws://` URLs.

## Interactive and runtime authentication

MCP tools can request authentication interactively without an experimental
opt-in since `0.144.0`.

App-server hosts can provide authentication at runtime, and successful logins
can redirect to a hosted page.

## MCP administration and serving

Configure STDIO or streaming HTTP MCP servers in `~/.codex/config.toml` or
manage them with `codex mcp`. The CLI can also run as an MCP server for another
agent.

## Hosted connector refresh

Long-running app sessions refresh expired authentication for the hosted
`codex_apps` connector.

## Proxy-aware Responses WebSockets

Responses WebSockets retain their low-latency transport while respecting
system proxies and custom certificate authorities.

## Code Mode approvals

Hosted mode is the default for Code Mode, and every approval request triggers
an elicitation pause.

## CLI plugins

The CLI can browse and add plugins from available marketplaces, extending
terminal work with team tools and data.

## Marketplace sources

`codex plugin marketplace add` accepts repository shorthand, Git or SSH URLs,
or a local marketplace root. Git sources may be pinned with `--ref` and
sparsely checked out with repeatable `--sparse`. `upgrade` refreshes one named
Git marketplace or all of them, and `remove` deletes a configured source.

```bash
codex plugin marketplace add owner/repo --ref release --sparse plugins/team
codex plugin marketplace upgrade
```

## Sign in with ChatGPT for plugins

The beta sign-in flow initially supports Airtable, GitLab, HubSpot, Notion,
Supabase, and Vercel integrations. It can create or link accounts from the
plugin directory or participating partner sites. A partner receives only the
available name, email address, and profile picture; each plugin's requested
permissions still require a separate approval. (`2026-07-10-2026-08-18`)

## App-server V2 test client

`codex debug app-server send-message-v2 USER_MESSAGE` initializes the
experimental V2 protocol, starts a thread, sends one turn, and streams server
notifications for local protocol debugging.
