---
name: terraform-knowledge-patch
description: Terraform / OpenTofu
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Terraform / OpenTofu Knowledge Patch

Load this skill before changing Terraform or OpenTofu configuration, state,
backends, tests, automation, Stacks, or Terraform Plugin Framework code. Check
the executable and provider-framework versions first: several behaviors are
product-specific, patch-release-sensitive, or experimental.

## Reference Index

| Reference | Topics |
| --- | --- |
| [Language, Values, Modules, and Providers](references/language-and-modules.md) | Expressions, functions, validation, sensitivity, ephemeral values, modules, provider configuration |
| [State, Import, and Refactoring](references/state-import-and-refactoring.md) | State compatibility, moves, removals, imports, lifecycle, locking, and failed applies |
| [Backends, Encryption, Installation, and Security](references/backends-encryption-and-security.md) | Backend migrations, authentication, encryption, installation, checksums, platforms, and security floors |
| [CLI, Automation, and Output](references/cli-automation-and-output.md) | Planning, console, JSON, output rendering, queries, actions, targeting, and automation flags |
| [Terraform and OpenTofu Testing](references/testing.md) | Variables, mocks, overrides, state sharing, parallelism, cleanup, and reports |
| [Terraform Stacks and HCP Terraform](references/stacks-and-hcp.md) | Components, deployments, governance, registries, agents, migration, encryption, and usage |
| [Terraform Plugin Framework](references/provider-plugin-framework.md) | Functions, schemas, moves, ephemeral and write-only APIs, identity, actions, lists, and Go floors |

## Breaking Changes and Required Migrations

### Migrate S3 backend configuration deliberately

- Terraform's S3 backend uses the standard AWS SDK and CLI credential-chain
  order. The deprecated `use_legacy_workflow` switch only provided a temporary
  escape hatch; OpenTofu removed that switch.
- Terraform removed flat assume-role attributes. Move them into an
  `assume_role` block.
- Prefer S3-native locking with `use_lockfile = true`. DynamoDB locking is
  deprecated; both locks may coexist during a staged migration.
- OpenTofu S3 module sources also follow the standard credential search order,
  so an upgrade can select a different identity.

### Keep shared state readers compatible

Terraform state containing input validations requires readers on the 1.3,
1.4, and 1.5 lines to be at least 1.3.10, 1.4.7, and 1.5.7 respectively.
This includes consumers using `terraform_remote_state`.

### Remove unsupported test and CLI configuration

- Put provider version constraints in the main `required_providers` block,
  not provider blocks in `.tftest.hcl` files.
- Replace the deprecated `-state` option on `plan`, `apply`, and `refresh`
  with `backend "local" { path = ... }`.
- Test-directory variable files are test-only in OpenTofu; normal commands do
  not load them.
- The old OpenTofu container base-image workflow was removed. Use the supported
  custom-image process for derived images.

### Respect platform and transport floors

- Terraform requires Linux kernel 3.2 or later. Building Terraform requires a
  sufficiently recent macOS toolchain as detailed in the backend and security
  reference.
- OpenTofu raises its macOS floor over time and is phasing out WinRM
  provisioner connections. Migrate Windows provisioners to SSH.
- Plugin Framework releases raise the minimum Go version at several points;
  upgrade the toolchain before the framework dependency.

### Treat OpenTofu PostgreSQL locking as an atomic migration

Do not run OpenTofu processes with the newer PostgreSQL locking behavior
against the same database as older processes. Their lock implementations are
incompatible and concurrent use can cause conflicting writes and data loss.

### Reconfigure changed AzureRM backends

OpenTofu ignores obsolete AzureRM `endpoint` and `msi_endpoint` inputs. Use
`MSI_ENDPOINT` where applicable, avoid combining `environment` with
`metadata_host`, and run `tofu init -reconfigure` rather than
`-migrate-state` for this authentication migration.

## Sensitive, Ephemeral, and Write-Only Data

### Use ephemeral values for phase-scoped secrets

Terraform and OpenTofu support ephemeral variables, outputs, and
provider-declared resources. Their values exist for one operation phase and
are omitted from plan and state artifacts.

```hcl
variable "session_token" {
  type      = string
  ephemeral = true
}
```

An unknown ephemeral resource input can defer opening the resource until
apply. Dependencies still order its prerequisites and consumers.

### Rotate write-only arguments with a stored trigger

Provider-declared write-only resource arguments are sent to the provider but
are not persisted or diffed. Pair a secret argument with the provider's stored
version, keeper, or trigger argument so rotation produces a visible change.

```hcl
resource "aws_db_instance" "main" {
  password_wo         = ephemeral.random_password.db.result
  password_wo_version = var.password_version
}
```

Use the patch floors in the references when values combine `sensitive` and
`ephemeral` marks, modules have zero instances, or outputs contain partially
ephemeral structures.

## State, Import, and Refactoring

### Prefer declarative moves and removals

Use `moved` blocks for address changes. Cross-resource-type moves work only
when the target provider implements the conversion. Reserved resource type
names require explicit `resource.` prefixes.

```hcl
moved {
  from = resource.data.old_name
  to   = resource.data.new_name
}
```

Use `removed` blocks when decommissioning belongs in reviewed configuration.
Destroy-time provisioners are supported, with a patch floor for targets in
nested modules. OpenTofu also supports lifecycle controls for forgetting an
object without destroying it.

### Import by identity only when the provider supports it

An import block may use provider-defined `identity` instead of `id`; never set
both. Identity support also changes provider implementation and dependency
requirements, so consult the framework reference before adopting it.

## Language and Module Contracts

### Distinguish the two dynamic-template contracts

`templatestring(template, variables)` renders template text already held in a
string. Terraform requires its first argument to be a direct reference to a
named string object in the current module. OpenTofu also permits recursive
`templatefile` calls and limits their default nesting depth.

### Make early inputs explicit

OpenTofu evaluates dynamic module and backend inputs before normal provider
configuration. Use `const = true` where a variable must be statically
available. Terraform supports variables and locals in module `source` and
`version`; use the documented patch floors for null, sensitive, or ephemeral
results.

### Use explicit module contracts

- Mark obsolete inputs and outputs with `deprecated = "..."`.
- Terraform outputs can declare `type`; use `convert(value, type)` when an
  explicit conversion is part of the contract.
- Cross-object validations can refer to other inputs, locals, and data
  sources, but unknown and sensitive values still need careful handling.

## Testing Essentials

### Share inputs and setup safely

Test provider blocks can use variables and earlier run outputs, and test inputs
can call functions. File-level variables can consume external variables and,
where supported, previous run outputs. Use `state_key` when multiple Terraform
test runs intentionally share one internal state.

### Scope mocks and execution mode

Mocks and overrides can be provider-scoped. Terraform supports
`override_during = plan`; OpenTofu supports iterated mock providers. Invalid
mock fields that once produced warnings may now fail validation, so honor the
patch floors for structural values and provider reads.

### Account for ordering and cleanup

Terraform initially cleaned up in reverse run order, later added eligible
parallel execution and parallel teardown, and ignores `prevent_destroy` during
test cleanup. Keep ordering dependencies explicit. Experimental retained-test
backends and cleanup commands are not available in stable binaries.

## Queries, Actions, and Stacks

Terraform query files declare list resources for discovery and generated
imports. Provider-defined actions can run from lifecycle hooks or through
`-invoke`; use the patch floors for correct post-apply ordering and modules
with no instances.

Stacks separate reusable component configuration from deployment inputs and
state. Treat partial plans, linked Stack limits, deployment-group policy,
private execution, and plan entitlements as platform concerns; see the Stacks
reference before changing production orchestration.

## Provider Implementation

Before adding provider functions, ephemeral resources, write-only attributes,
resource identity, actions, list resources, or state stores, pin compatible
Plugin Framework and supporting-library versions. Several APIs changed before
compatibility protection began, and deferred operations and state stores remain
experimental.
