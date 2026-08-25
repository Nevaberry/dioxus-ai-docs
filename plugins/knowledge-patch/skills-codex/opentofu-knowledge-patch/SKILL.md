---
name: opentofu-knowledge-patch
description: OpenTofu
version: 1.12.0
license: MIT
metadata:
  author: Nevaberry
---


# OpenTofu Knowledge Patch

Use this skill when changing OpenTofu configuration, state, backends,
automation, tests, module distribution, or provider installation. Check the
project's required OpenTofu version before applying version-dependent advice,
and prefer the project's configuration, lock file, tests, and observed behavior
when they disagree with general guidance.

## Reference index

| Reference | Topics |
|---|---|
| [cli-automation-and-libraries.md](references/cli-automation-and-libraries.md) | CLI output, automation flags, console behavior, tracing, XDG paths, and Go libraries |
| [encryption.md](references/encryption.md) | State and plan encryption, migration, key providers, metadata, and remote-state decryption |
| [language-modules-and-lifecycle.md](references/language-modules-and-lifecycle.md) | Expressions, early evaluation, modules, providers, imports, moves, lifecycle, and ephemeral data |
| [state-backends-and-installation.md](references/state-backends-and-installation.md) | State persistence, backend behavior, locking, registry distribution, caches, and lock hashes |
| [testing.md](references/testing.md) | Mocks, overrides, test variables, module-under-test behavior, and cleanup recovery |
| [upgrade-security-and-platforms.md](references/upgrade-security-and-platforms.md) | Security floors, breaking changes, deprecations, transports, platforms, and container boundaries |

## Upgrade and security blockers

### Use fixed releases for registry initialization

Use OpenTofu 1.12.6 or 1.11.14 before installing modules or providers from OCI
registries. Earlier releases can disclose registry credentials across an HTTP
redirect and can be forced into excessive CPU or memory use by crafted relative
URLs from an untrusted registry or remote-state backend. Version 1.11.14 is the
final planned patch in its series, so move installations on that branch to a
newer series.

### Remove obsolete S3 compatibility settings

The S3 backend no longer accepts `use_legacy_workflow` in 1.8 or later. Remove
it before upgrading. S3 module sources switched to AWS CLI/SDK credential
discovery in 1.11, which can select a different credential source and enables
workload schemes such as IAM roles for service accounts.

### Do not mix PostgreSQL locking generations

OpenTofu 1.10 changed PostgreSQL backend locking. Do not run 1.10-or-newer and
older processes against the same database: incompatible locks can permit
conflicting state writes and data loss.

### Reconfigure AzureRM authentication

OpenTofu 1.11 ignores AzureRM `endpoint`/`ARM_ENDPOINT` and
`msi_endpoint`/`ARM_MSI_ENDPOINT`. Replace the latter with `MSI_ENDPOINT`, do
not combine `environment` with `metadata_host`, and run
`tofu init -reconfigure`; this is not a state migration.

### Respect platform and provisioner boundaries

OpenTofu 1.10 requires Linux kernel 3.2+ or macOS 11+. OpenTofu 1.11 requires
macOS 12+. WinRM warns in 1.12 and is planned to fail in 1.13, so migrate
Windows provisioners to SSH. The 1.12 series is the last planned macOS 12
series. Official 32-bit `386` and `arm` packages continue through 1.13 but are
planned for later removal.

## Encryption safety

### Treat encryption changes as migrations

Reads can try a primary encryption method and then fallbacks, but writes always
use the primary. Use an
`unencrypted` fallback when encrypting existing plaintext, or make
`unencrypted` primary and retain the former encrypted method as a fallback when
deliberately decrypting. Apply successfully before removing fallbacks.

```hcl
method "unencrypted" "migration" {}

state {
  method = method.aes_gcm.main
  fallback {
    method = method.unencrypted.migration
  }
}
```

OpenTofu 1.9 automatically applies encryption-configuration migrations, but
stored metadata still binds artifacts to method and key-provider names. Roll
renames safely with fallbacks or a stable `encrypted_metadata_alias`.

### Configure remote-state decryption separately

Encryption of the current project's state does not configure
`terraform_remote_state`. Give remote-state data sources their own default or
named method; named targets can address a root data source, a module-qualified
data source, or an indexed instance.

### Keep initialization inputs resolvable

Encryption variables and locals must be available during initialization and
cannot depend on state or provider functions. OpenTofu 1.11 also accepts apply-
time inputs for encryption, but each non-ephemeral value must equal the value
captured during planning.

## Language and lifecycle quick reference

### Use early evaluation deliberately

Variables and locals can drive backend configuration and module `source` and
`version`. They must be available during initialization. Sensitive values are
not allowed in backend configuration or module source locations. In 1.12,
declare an initialization-time contract explicitly with `const = true`.

```hcl
variable "module_source" {
  type  = string
  const = true
}
```

An identically named `.tofu` file masks its `.tf` counterpart. This lets a
module pair OpenTofu-only configuration with a Terraform-compatible fallback.

### Prefer lifecycle-native conditional existence

Use `lifecycle.enabled` for a resource or module that should have zero or one
instances. From 1.11.4, modules containing local provider configurations reject
it, as they already reject `count`, `for_each`, and `depends_on`.

```hcl
module "servers" {
  source = "./servers"

  lifecycle {
    enabled = var.enable_servers
  }
}
```

In 1.12, `prevent_destroy` can refer to other symbols, and
`lifecycle.destroy = false` forgets a managed object without asking its
provider to destroy it. Use 1.12.4+ when saving a plan that may replace such a
resource.

### Keep secrets out of plans and state

OpenTofu 1.11 adds ephemeral variables, outputs, and provider-defined resources
whose values live only for one operation phase. Provider-defined write-only
managed-resource attributes accept values without persisting them. Both
features require provider support.

### Account for expression changes

`&&` and `||` short-circuit in 1.10, so an unselected operand cannot fail while
dereferencing an absent value. `element` accepts negative wrapping indices,
with `-1` selecting the final element. In 1.12, a null comparison involving a
complex value is sensitive only when the whole value is sensitive, rather than
when merely a nested attribute is sensitive.

## State, distribution, and installation quick reference

### Use native S3 locking and keep lock files valid

OpenTofu 1.10 can lock state directly in S3. Use 1.10.2+ with buckets requiring
server-side encryption so the lockfile request includes the required header.
Multiple processes may share the global provider cache only when the filesystem
supports locking; use 1.10.5+ with `TF_PLUGIN_CACHE_DIR` and retain a valid
`.terraform.lock.hcl` in every project.

### Choose the right artifact source

Modules support `oci:` source addresses, and OCI registries can mirror
providers. Lock entries for certain rebuilt providers from
`registry.terraform.io` may select the matching republished version on
`registry.opentofu.org`; this does not apply to arbitrary third-party
providers.

When installation is directly from OpenTofu Registry, `tofu init` records
cross-platform `zh:` and `h1:` hashes. Alternative sources still require
`tofu providers lock`. A `network_mirror` can explicitly trust all hashes that
the mirror reports.

## CLI and automation quick reference

### Select and split plans reproducibly

`-exclude=ADDRESS` removes an object and its dependents, while `-target=ADDRESS`
includes an object and its requirements. In 1.10, `-target-file` and
`-exclude-file` accept reusable address lists.

```text
tofu plan -target-file=targets.txt
tofu plan -exclude-file=deferred.txt
```

Use `tofu show -state` for current state and `tofu show -plan=PLANFILE` for a
saved plan. The older positional plan form remains supported.

### Keep human and machine output together

`-json-into=FILENAME` writes streaming JSON events while retaining normal
terminal output. The destination may be a file or an IPC object such as a named
pipe or `/dev/fd/N`.

```text
tofu plan -json-into=plan-events.json
```

Use `-show-sensitive` only when disclosure is intentional. It unmasks values
for commands that return configuration or state. Diagnostic volume can be
controlled with `-consolidate-warnings` and `-consolidate-errors`.

## Testing quick reference

`mock_provider` supplies generated resource and data values;
`override_resource`, `override_data`, and `override_module` replace specific
targets. Overrides may be scoped inside a mock provider. Invalid fields are
errors, and newer generated mocks follow provider schemas more closely, so fix
previously accepted invalid shapes.

In 1.10, an explicit module under test may have a remote source and test-file
provider blocks may use earlier run outputs. In 1.11, `mock_provider` supports
`for_each`, and test-file variable blocks may call functions. If cleanup fails,
`tofu test` writes state so the remaining resources can be recovered.
