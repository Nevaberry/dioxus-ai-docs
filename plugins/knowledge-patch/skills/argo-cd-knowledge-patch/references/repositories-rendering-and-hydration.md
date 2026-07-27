# Repositories, Rendering, and Hydration

## Repository source and authentication

- Git and OCI repository authentication can use Azure workload identity since
  3.0.0. Prefer the workload identity flow over embedding long-lived repository
  credentials where the Azure environment supports it.
- OCI sources are supported as a beta capability since 3.1.0. Treat source
  compatibility and operational behavior as beta when deciding whether to use
  OCI in a production delivery path.

## Config-management plugin environment

Since 3.0.0, config-management plugins receive environment variables even when
their values are empty. Plugin logic must distinguish three cases when they
have different meanings: a variable that is absent, one that is present but
empty, and one with a non-empty value.

Manifest generation also receives the Application project name in
`ARGOCD_APP_PROJECT_NAME` since 3.0.0. Use it as a supplied build input rather
than reconstructing the project name from unrelated metadata.

## Kustomize integration

- Kustomize label processing supports `--include-templates` since 3.0.0. Set
  it when labels must also be applied to template content, and account for the
  resulting manifest diff.
- Kustomize integrations can ignore missing components since 3.0.0. Use this
  only where an optional component is intentional; otherwise a missing
  component should continue to fail early.

## Source Hydrator webhooks

Webhook handling recognizes `sourceHydrator` fields since 3.0.0. Include those
fields when routing or validating webhook events for hydrated sources; do not
strip them as unknown payload data.

## Source Hydrator commits and credentials

Since 3.2.0:

- Hydrator commit messages can be templated. Keep the template useful for
  provenance while excluding credentials and other secret inputs.
- Source Hydrator can use a credential template for its source repository.
  Match the template through repository configuration rather than duplicating
  static credentials in each hydration definition.

## Hydrated worktree preservation

Hydration behavior in 3.2.0 preserves files that the hydrator did not generate
and adds `.gitattributes` at the hydrated repository root. Cleanup or diff
automation must therefore distinguish generated outputs from retained
user-managed files. Do not remove `.gitattributes` as unexplained residue; it
is part of the hydrated repository behavior.
