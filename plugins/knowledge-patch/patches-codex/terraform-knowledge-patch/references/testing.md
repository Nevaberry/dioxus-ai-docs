# Terraform and OpenTofu Testing

## Terraform test inputs (`terraform-1.7.0-guide`)

Terraform 1.7 test provider blocks can reference variables and earlier run outputs. HCL functions are accepted in variable and provider blocks, and tests can load values from `*.tfvars` files.

```hcl
provider "aws" {
  region = var.test_region
}

run "verify" {
  variables {
    expected_id = run.setup.resource_id
  }
}
```

Terraform 1.8 file-level `variables` blocks can refer to global inputs (`terraform-1.8.0`).

```hcl
variables {
  region = var.test_region
}
```

Terraform 1.9 preserves sensitivity marks dynamically carried by values passed to test variables, not only marks arising from `sensitive = true` on the destination (`terraform-1.9.0`). Provider version constraints are no longer allowed in `.tftest.hcl`; declare them in the main configuration's `required_providers` block.

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

## Cleanup order and failure handling

Terraform 1.7 destroys test infrastructure in reverse run-block order; arrange dependent cleanup accordingly. On Windows, use Terraform 1.7.4 or later for reliable automatic variable-file loading from the test directory (`terraform-1.7.0`).

Terraform 1.12 continues later tests when a run fails to encounter a declared expected failure. Terraform 1.13 can tear down eligible test infrastructure in parallel; use 1.13.2 or later for corrected cleanup-node ordering.

Terraform 1.14 ignores `prevent_destroy` during test cleanup and includes expected diagnostics in verbose output. Use 1.14.1 or later for ephemeral root-module outputs and 1.14.6 or later so invalid test provider configuration reliably errors.

## Shared state and plan-time overrides (`terraform-1.11.0-guide`)

`run` blocks accept `state_key`; runs sharing a key operate on one internal state file.

```hcl
run "setup" {
  state_key = "shared"
}

run "verify" {
  state_key = "shared"
}
```

Mocks and overrides can affect `command = plan` runs with `override_during = plan`; the default is `override_during = apply`.

## Parallelism and initialization (`terraform-1.12.0`)

Terraform 1.12 lets test runs opt into parallel execution. Independently, `terraform test -parallelism=n` controls concurrent operations inside each run's plan or apply.

```shell
terraform test -parallelism=4
```

`terraform init` now succeeds in a directory containing tests but no root configuration files.

## External and derived test variables (`terraform-1.13.0`)

Test files can declare external variables. Declarations are optional, but omitting them for complex values can produce diagnostics.

```hcl
variable "region" {
  type = string
}
```

A top-level test `variables` block can refer to other variables and run outputs.

```hcl
variables {
  region      = var.region
  resource_id = run.setup.resource_id
}
```

## Mock data and reports

Terraform 1.7.2 `fmt` formats `*.tfmock.hcl` files. Terraform 1.11 makes `terraform test -junit-xml=report.xml` generally available (`terraform-1.11.0-guide`). Terraform 1.15 mock values can call functions (`terraform-1.15.0`).

Starting in Terraform 1.14.1, `terraform providers lock` includes providers used only by tests. Terraform 1.15 adds file-level diagnostics to JUnit XML skipped-test elements.

## OpenTofu mocks and overrides (`opentofu-1.8.0`)

OpenTofu Test supports `mock_provider`, `mock_resource`, `mock_data`, `override_resource`, `override_data`, and `override_module`. Use at least 1.8.11 for tests that rely on mocks; fixes through that patch cover structural typed attributes and provider `ReadResource` calls.

OpenTofu 1.9 permits `override_resource` and `override_data` inside a specific `mock_provider` (`opentofu-1.9.0`). Invalid mock or override fields become errors instead of warnings. Tests with structural typed attributes need at least 1.9.2, and 1.9.3 fixes mocked `ReadResource` behavior.

Variable files inside `tests` are isolated from non-test commands in OpenTofu 1.9. Move ordinary plan/apply inputs elsewhere or pass them explicitly.

OpenTofu 1.10 permits a `.tftest.hcl` selected module to use a remote source (`opentofu-1.10.0`). Use at least 1.10.7 when testing deprecated module outputs or complex deprecated values.

OpenTofu 1.11 test `mock_provider` blocks accept `for_each`, and scenario `variable` blocks can call functions (`opentofu-1.11.0`). Generated mocks follow provider schemas more strictly, so configurations tolerated by older versions can fail validation.

## Experimental retained infrastructure

Terraform 1.15 alpha builds allowed a test `run` backend, `skip_cleanup`, and `terraform test cleanup` for state retained under `.terraform`. These are not available in stable 1.15 releases; do not build stable workflows around them.
