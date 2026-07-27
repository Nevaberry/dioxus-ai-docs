# CLI, API, and Extensions

## Diff and resource inspection

- Server-side diff is stable and supported in CLI workflows since 3.2.0. Use
  it when the comparison needs server behavior rather than only local rendering.
- The CLI adds `get-resource` in 3.2.0 for retrieving one Application resource.
  Prefer it when automation needs a single resource rather than parsing a
  complete Application resource tree.

## Credential input

In 3.2.0, `bcrypt` prompts for a password when `--password` is omitted. An
Argo CD password can also be read from standard input. Prefer prompting or a
protected stdin pipeline over command-line arguments, which can leak through
shell history or process inspection.

## CLI extension and log behavior

- CLI plugin support was added in 3.1.0. Treat plugin binaries and their command
  namespaces as part of the workstation trust and compatibility surface.
- Pod-log search can match case since 3.0.0. Select case behavior explicitly
  when scripts depend on exact capitalization.

## Exec and port forwarding

Pod exec and port forwarding use WebSockets instead of SPDY since 3.0.0.
Reverse proxies, load balancers, and authentication intermediaries must allow
the HTTP connection upgrade and preserve the connection for the session.
Diagnose failures at the intermediary as well as at `argocd-server`.

## Authenticated extension requests

Since 3.2.0, the server passes the authenticated user ID to extensions in a
request header. Extensions can use this to associate work with the caller, but
they should trust it only when the request is received through the authenticated
Argo CD server. Strip or overwrite client-supplied identity headers at the
trusted boundary to prevent confusion with server-provided identity.
