# CLI, API, and Extensions

## Diff and resource commands

Server-side diff is stable for CLI workflows as of 3.2.0. Use it when the
server's admission and defaulting behavior must participate in the preview.

The CLI also adds `get-resource` in 3.2.0 to retrieve one resource belonging to
an Application. Prefer it over fetching an entire Application resource set
when scripts need a single object.

## Password and log input

The `bcrypt` command prompts when `--password` is omitted, and the Argo CD
password can be read from standard input (3.2.0). Prefer either route over argv
or shell history. Pod-log search supports case matching since 3.0.0; set the
matching behavior explicitly in scripts where case changes the result set.

## CLI plugins

The CLI supports plugins that add commands as of 3.1.0. Treat plugin binaries
as part of the CLI trust boundary, pin their provenance, and avoid command-name
collisions with built-in operations.

## Namespace-aware commands

ApplicationSet-in-any-namespace is stable in 3.5.0. `argocd appset` commands
can target an ApplicationSet namespace, and previously missing `argocd app`
subcommands accept `--app-namespace`. Make the namespace explicit in
multi-tenant automation rather than relying on a default.

## Typed event responses

Event-listing APIs return Argo CD's typed `EventList` in 3.5.0. Clients that
assumed an untyped Kubernetes list must decode the typed response and preserve
its Argo CD schema.

## Core mode

The CLI honors `--kube-context` when it constructs core-mode REST configuration
as of 3.5.0. Verify context selection in scripts that access more than one
cluster; do not assume the current kubeconfig context overrides the flag.

## Application user interface

In 3.5.0, New-App creation supports multi-source Applications, the network
view understands Gateway API resources, and Application lists can filter by
repository URL or target revision. Use the richer views for investigation and
authoring, but preserve exact source and revision values in API-driven
automation.

## Extensions and caller identity

### Trust only server-supplied identity

Since 3.2.0, the server forwards the authenticated user ID to extensions in a
request header. Consume that identity only behind the authenticated Argo CD
server. A direct client must not be able to spoof the same header and gain the
server's trust.

### Upgrade UI extensions to React 19

The UI uses React 19 in 3.5.0. Custom UI extensions must follow the React 19
extension upgrade guidance; `ReactJSXRuntime` is available as a global for
extension integration. Test mounting, shared runtime assumptions, and build
output before deploying an older extension bundle.
