# State, Imports, and Backends

## State deletion and protection

`pulumi state delete --all` removes every resource entry. The command also
accepts multiple URNs and orders deletion safely by dependencies (batch
`3.214.1-3.228.0`). `pulumi state protect <URN>` changes protection directly in
state. `pulumi state taint` marks a resource for replacement on the next update;
`untaint` clears it.

Unresolved references are validation errors unless the operation supplies
`--allow-dangling-references`. `pulumi state get` displays one resource.

## Checkpoints and journaling

The CLI reads and writes v4 checkpoints/deployments. Engine journaling is
enabled by default; `PULUMI_DISABLE_JOURNALING=true` explicitly disables it.
State can contain NaN and infinity, and `Stash` stores arbitrary values.

Strings with non-UTF-8 bytes can flow through providers, engine, and state when
the language opts in; Go and PCL are the initial language paths. Machine output
represents such strings as base64-tagged byte values.

## DIY backends

S3, Azure Blob, Google Cloud Storage, PostgreSQL, and local backends support
stack-tag CRUD, automatic system tags, and tag-filtered listings. Tags are
versioned JSON in `.pulumi-tags` files next to checkpoints. Existing untagged
stacks remain valid, and stack deletion removes the tag file. On DIY backends,
`pulumi stack rm --remove-backups` removes backups too.

DIY state may use zstd compression. Legacy non-project operating mode began
deprecation in `3.214.1-3.228.0`; its warning is now an error. The bypass is
`PULUMI_DIY_BACKEND_IGNORE_DEPRECATION_ERROR`, replacing the old
`PULUMI_DIY_BACKEND_IGNORE_DEPRECATION_WARNING`.

S3-compatible backends with a custom endpoint default checksum calculation to
`when_required`.

## Backend selection and recovery

Current-stack selection is scoped to the active backend, so switching backends
does not reuse a stale selection. The service backend automatically repairs
snapshot-integrity problems and reports an error event for diagnosis.

When imported state names a service-backed secrets manager, `pulumi stack
import` reconfigures it for the target stack if necessary. `pulumi login
--insecure` propagates to service secrets-manager state for self-signed
backends.

## Backend-to-backend migration

`pulumi stack migrate` copies a stack from another backend into the active one
and re-encrypts configuration secrets and state under the target secrets
provider (batch `3.249.0-3.254.0`).

## Import files and direct state

Import files may define provider resources and associate ordinary resources with
them. They preserve assets, archives, and resource references nested in maps or
arrays. A resource may supply inputs and outputs; if outputs exist, import skips
the provider read and writes that state directly.

`ResourceImport` carries parent and properties for hierarchy and property
filtering. Imports from `--from` state files always generate resources. Imports
support parameterized and extension-parameterized providers. An import ID that
differs from the provider's canonical ID is preserved without causing later
deletion.

## State converter protocol

Converters can return explicit provider resources and link imported resources to
them. They can return inputs and outputs in `ConvertState`, receive
`schema_loader_target` and `resolver_target`, and request mappings for a named
ecosystem. Generated import files include explicit providers.

`pulumi preview --import-file` no longer writes unknown values, and `pulumi
import` rejects files that contain unknowns. These additions are included in
batch `3.255.0-3.258.0`.
