# CLI, API, and Extensions

## Diff and resource retrieval

Server-side diff is stable and supported in CLI workflows (3.2.0). The CLI
also has `get-resource` for retrieving an individual resource belonging to an
Application (3.2.0). Use the single-resource path when automation does not need
the entire Application resource set.

Server-side diff masks Secret data in the last-applied-configuration annotation
and prevents CLI Secret-mask spoofing (3.3.13). Keep clients current and do not
trust client-generated masking as proof that server output is safe.

## Password input

`bcrypt` prompts when `--password` is omitted, and the Argo CD password can be
read from standard input (3.2.0). Helm registry passwords are likewise passed
through standard input (3.3.13). Prefer prompt or stdin flows over argv, which
can expose credentials through process inspection or shell history.

## CLI plugins

The CLI supports plugins that add commands (3.1.0). Treat plugins as part of
the CLI deployment: version, distribute, and test them alongside the CLI they
extend.

## Logs, exec, and port forwarding

Pod-log search can perform case matching (3.0.0). Log access itself is subject
to RBAC by default, so search capability does not imply permission.

Pod exec and port forwarding use WebSockets instead of SPDY (3.0.0). Ensure
every intermediary preserves the HTTP upgrade and WebSocket connection before
diagnosing these operations as an Argo CD authorization failure.

## Namespace-aware commands

ApplicationSet-in-any-namespace support is stable in 3.5.0. `argocd appset`
commands can identify the ApplicationSet namespace, and previously missing
`argocd app` subcommands accept `--app-namespace`. Always provide namespace
context in automation that can encounter duplicate names.

## Core-mode context

The CLI honors `--kube-context` when creating its core-mode REST configuration
(3.5.0). The application controller can also sync in core mode when
`server.secretkey` is absent. Test both context selection and secretless core
mode rather than applying server-mode assumptions.

## Typed event-list responses

Event-listing APIs return Argo CD's typed `EventList` in 3.5.0. API consumers
that assumed an untyped Kubernetes list must decode and validate the typed
response.

## Authenticated extension identity

The server forwards the authenticated user's ID to extensions in a request
header (3.2.0). Use the forwarded identity only inside the authenticated Argo
CD server's trust boundary; an extension directly reachable by clients must
not treat a spoofable copy of the header as equivalent authentication.

## UI extensions

The UI uses React 19 in 3.5.0, and `ReactJSXRuntime` is exposed as a global for
extension integration. Upgrade custom UI extensions using their React 19
guidance and test runtime/global assumptions before deploying them with the
new UI.
