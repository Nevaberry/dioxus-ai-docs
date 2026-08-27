# Terraform and OpenTofu Testing

## Inputs and variable scope

Terraform test provider blocks can reference input variables and earlier run
outputs, and functions are allowed in variable and provider blocks. Tests can
also load values from `*.tfvars` files (`terraform-1.7.0-guide`). On Windows,
use Terraform 1.7.4 or later for reliable automatic variable-file loading from
the test directory (`terraform-1.7.0`).

Terraform file-level `variables` can reference global inputs
(`terraform-1.8.0`). Terraform test inputs preserve sensitivity marks carried
dynamically by their values (`terraform-1.9.0`).

Terraform test files can declare their external variables; declarations are
optional, but they improve diagnostics for complex values. File-level
variables can also refer to other variables and run outputs
(`terraform-1.13.0`).

```hcl
variable "region" {
  type = string
}

variables {
  region      = var.region
  resource_id = run.setup.resource_id
}
```

OpenTofu test-directory variable files are isolated from non-test commands;
move ordinary planning and apply inputs elsewhere or pass them explicitly
(`opentofu-1.9.0`). OpenTofu test-scenario variable blocks can call functions
(`opentofu-1.11.0`).

## Provider requirements

Terraform provider blocks in `.tftest.hcl` cannot declare version constraints.
Put them in the main configuration's `required_providers` block
(`terraform-1.9.0`).

```hcl
terraform {
  required_providers {
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }
  }
}
```

Starting in Terraform 1.14.1, `terraform providers lock` includes providers
used only by test files (`terraform-1.14.0`).

## Mocks and overrides

### OpenTofu mocks

OpenTofu supports `mock_provider`, `mock_resource`, `mock_data`,
`override_resource`, `override_data`, and `override_module`
(`opentofu-1.8.0`). Use at least 1.8.11 on that line for structural typed
attributes and provider `ReadResource` handling.

Overrides may be scoped inside a particular mock provider. Invalid mock or
override fields produce errors instead of warnings (`opentofu-1.9.0`). On the
1.9 line, use 1.9.2 for structural typed attributes and 1.9.3 for correct
mocked provider reads.

OpenTofu mock providers accept `for_each`. Generated mocks more strictly
follow provider schemas, so configurations previously tolerated can fail
validation (`opentofu-1.11.0`).

### Terraform mocks

Terraform mocks and overrides can affect `command = plan` runs with
`override_during = plan`; the default is `apply`
(`terraform-1.11.0-guide`). Terraform test mock values can call functions
(`terraform-1.15.0`).

Terraform formats `*.tfmock.hcl` with `terraform fmt` starting in 1.7.2
(`terraform-1.7.0`).

## Shared state and remote modules

Terraform run blocks accept `state_key`. Runs with the same key share an
internal state, allowing setup and verification to use the same infrastructure
(`terraform-1.11.0-guide`).

```hcl
run "setup" {
  state_key = "shared"
}

run "verify" {
  state_key = "shared"
}
```

An explicit module selected in an OpenTofu test file can use a remote source
(`opentofu-1.10.0`).

## Ordering, parallelism, and cleanup

Terraform originally destroys test infrastructure in reverse run-block order,
so tests with cleanup dependencies must order their runs deliberately
(`terraform-1.7.0`).

Terraform later lets runs declare eligibility for parallel execution.
`terraform test -parallelism=n` separately controls concurrent operations
inside each run's plan or apply (`terraform-1.12.0`). Terraform can also
perform eligible teardown in parallel; use 1.13.2 or later for correct cleanup
node ordering (`terraform-1.13.0`).

If a declared expected failure does not occur, later Terraform tests continue
rather than stopping the suite (`terraform-1.12.0`). `terraform init` also
succeeds in a directory containing only test files and no root configuration.

Terraform test cleanup ignores `prevent_destroy`, and verbose output includes
expected diagnostics. Use 1.14.1 or later for ephemeral outputs in tested root
modules and 1.14.6 or later so invalid test provider configuration reliably
returns an error (`terraform-1.14.0`).

## Reports and machine-readable diagnostics

`terraform test -junit-xml=report.xml` is generally available and emits JUnit
XML for CI (`terraform-1.11.0-guide`). File-level diagnostics appear in JUnit
skipped-test elements (`terraform-1.15.0`).

## Experimental retained infrastructure

Terraform alpha builds can place a `backend` block in a test run, set
`skip_cleanup`, retain test state under `.terraform`, and retry cleanup with
`terraform test cleanup`. These features are not present in stable Terraform
1.15 releases (`terraform-1.15.0`).
