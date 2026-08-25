# CLI and Flux Operator

## Inspect merged reconciliation inputs

Since 2.5.0, the debug commands show effective values after inline data is
merged with referenced ConfigMaps and Secrets:

```shell
flux debug kustomization --show-vars
flux debug helmrelease --show-values
```

Referenced Secret values are printed in clear text. Do not paste this output
into tickets or persistent logs without redaction.

## Work with OCI artifacts

The following artifact commands and media types are stable as of 2.6.0:

```shell
flux build artifact
flux push artifact
flux pull artifact
flux tag artifact
flux diff artifact
flux list artifacts
```

- Config media type: `application/vnd.cncf.flux.config.v1+json`
- Content media type: `application/vnd.cncf.flux.content.v1.tar+gzip`

Use the stable media types when producing or consuming Flux-compatible OCI
artifacts outside the CLI.

## Manage CLI plugins

The 2.9.0 CLI discovers independently versioned plugins under
`~/fluxcd/plugins` and exposes each plugin as `flux <plugin>`. The initial
catalog includes Mirror for declarative registry mirroring and Schema for JSON
Schema and CEL validation.

```shell
flux plugin search
flux plugin install schema@0.5.0
flux plugin list
flux plugin update schema
flux plugin uninstall schema
```

Pin plugin versions or immutable digests in automation; an unpinned update can
change behavior independently of the core Flux CLI.

## Trigger a Receiver

Since 2.9.0, invoke a configured Receiver without hand-building its webhook
request:

```shell
flux trigger receiver
```

The Receiver still enforces its configured HMAC or OIDC authentication and
resource filtering.

## Use the Flux Operator Web UI

The Flux Operator Web UI added in 2.8.0 provides cluster and GitOps-resource
monitoring, rollout inspection, delivery graphs, and RBAC-guarded actions. It
supports OIDC single sign-on and Kubernetes RBAC for multi-tenant clusters.

In 2.9.0-era Operator releases, the UI also provides:

- a workload dashboard for Deployments, StatefulSets, DaemonSets, and CronJobs;
- a log viewer spanning multiple pods and containers;
- workload actions and log access authorized through Kubernetes RBAC with user
  impersonation.

Treat UI access as cluster access: configure OIDC identity mapping and RBAC
rules for the intended tenant boundaries.
