# Terraform and OpenTofu Testing

Mocks and overrides, test inputs, execution ordering, concurrency, diagnostics, reports, and cleanup.

## Mocks and overrides

### Formatting mock data files

*Terraform 1.7.0 — batch `terraform-1.7.0`.*

Starting in 1.7.2, `terraform fmt` includes Terraform mock data files with the `.tfmock.hcl` suffix.

### Functions in Terraform Test mocks

*Terraform 1.15.0 — batch `terraform-1.15.0`.*

Terraform Test mock blocks can now call functions when constructing mock values, allowing generated or transformed fixture values rather than literals only.

### Mock providers and targeted test overrides

*Terraform 1.7.0 — batch `terraform-1.7.0-guide`.*

Terraform tests can replace provider calls with `mock_provider`; unspecified computed attributes receive generated fake data, while `mock_resource` defaults supply stable values for every resource of that type. Aliases allow real and mocked providers in the same suite, and override blocks can replace individual resources, data sources, or module outputs either for the whole test file or inside one `run`, with real or mocked providers.

```hcl
mock_provider "aws" {
  mock_resource "aws_s3_bucket" {
    defaults = { arn = "arn:aws:s3:::test-bucket" }
  }
}

override_module {
  target  = module.database
  outputs = { endpoint = "db.example.test:3306" }
}
```

### Mock-provider-local overrides

*OpenTofu 1.9.0 — batch `opentofu-1.9.0`.*

`override_resource` and `override_data` blocks can be scoped inside one `mock_provider`, rather than affecting the whole test file. Invalid override and mock fields now fail `tofu test` as errors instead of warnings.

### Plan-time test mocks and overrides

*Terraform 1.11.0 — batch `terraform-1.11.0-guide`.*

Mocked and overridden values can now be used by unit-test runs whose `command` is `plan`. Set `override_during = plan` in the test configuration; the default remains `override_during = apply`.

### Provider-mocking patch compatibility

*OpenTofu 1.8.0 — batch `opentofu-1.8.0`.*

The new provider mocks and test overrides received significant follow-up fixes: 1.8.6 relaxes provider-schema and type validation, 1.8.7 corrects dynamic nulls and variable type defaults, 1.8.10 handles structural attributes, and 1.8.11 corrects mocked `ReadResource` calls. Use 1.8.11 or later when relying heavily on mocks; 1.8.8 also prevents outputs from destroyed modules leaking between test runs.

### Test and provider-lock behavior

*Terraform 1.14.0 — batch `terraform-1.14.0`.*

Verbose `terraform test` output now includes expected diagnostics, and test cleanup ignores `prevent_destroy`. Terraform 1.14.1 permits ephemeral outputs in tested root modules and makes `terraform providers lock` include providers required by tests; 1.14.6 reports an invalid test provider configuration as an error.

## Variables and evaluation

### Dynamically sensitive test inputs

*Terraform 1.9.0 — batch `terraform-1.9.0`.*

Test runs now preserve the dynamic sensitivity of values passed to input variables; the destination variable no longer needs a static `sensitive = true` declaration for the value to remain sensitive.

### More flexible Terraform test inputs

*Terraform 1.7.0 — batch `terraform-1.7.0-guide`.*

Provider blocks in tests can reference variables and prior run outputs, HCL functions are accepted in variable and provider blocks, and test variables can be loaded from `*.tfvars` files.

### Richer variables in Terraform tests

*Terraform 1.13.0 — batch `terraform-1.13.0`.*

A `.tftest.hcl` file can declare `variable` blocks for external values it references; declarations are optional, but complex values can produce diagnostics without their type definitions. File-level `variables` blocks can also refer to run outputs and other variables, allowing shared inputs to be derived inside the test file.

```hcl
variable "fixture" {
  type = object({ region = string })
}
```

### Test environment variables restored in 1.8.2

*Terraform 1.8.0 — batch `terraform-1.8.0`.*

Terraform 1.8.2 restores propagation of `TF_ENV_*` variables into testing modules, so test suites relying on them should not remain on 1.8.0 or 1.8.1.

### Test file variables can use global variables

*Terraform 1.8.0 — batch `terraform-1.8.0`.*

File-level `variables` blocks in Terraform test files can now refer to global variables, allowing shared inputs to feed file-specific values without duplication.

### Windows test variable-file loading

*Terraform 1.7.0 — batch `terraform-1.7.0`.*

Terraform 1.7.4 fixes automatic loading of variable files from the test directory on Windows, so Windows users relying on this 1.7 test feature should use 1.7.4 or later.

## Execution, reporting, and cleanup

### Alpha-only retained test state and cleanup

*Terraform 1.15.0 — batch `terraform-1.15.0`.*

In alpha builds, a test `run` block can select a `backend`, and `skip_cleanup` at file or run scope retains affected state under `.terraform`. The experimental `terraform test cleanup` command can retry cleanup from the saved manifests and state files after failed or deliberately skipped cleanup.

### Initialization in test-only directories

*Terraform 1.12.0 — batch `terraform-1.12.0`.*

`terraform init` now succeeds when tests are present even if the current directory contains no Terraform configuration files directly.

### JUnit test reports

*Terraform 1.11.0 — batch `terraform-1.11.0-guide`.*

The `terraform test` command's `-junit-xml` flag is now generally available for writing JUnit XML reports for CI systems.

### More capable test configuration

*OpenTofu 1.11.0 — batch `opentofu-1.11.0`.*

Test-file `mock_provider` blocks now accept `for_each`, and test-file `variable` blocks can call functions. Generated mocks follow provider schemas more strictly, so formerly accepted invalid mocks or overrides must be corrected; the still-unreleased 1.11.6 fixes cleanup for mocked resources that have write-only attributes.

### More capable test configurations

*OpenTofu 1.10.0 — batch `opentofu-1.10.0`.*

An explicit module under test in `.tftest.hcl` can now use a remote module source. Test-file provider configurations can also refer to output values from an earlier `run` block.

### Parallel test controls

*Terraform 1.12.0 — batch `terraform-1.12.0`.*

Individual `run` blocks can be marked as eligible for parallel execution. Separately, `terraform test -parallelism=n` controls the number of parallel operations within each run's plan or apply.

```hcl
run "unit" {
  command  = plan
  parallel = true
}
```

### Parallel test teardown and patch compatibility

*Terraform 1.13.0 — batch `terraform-1.13.0`.*

Teardown operations for parallel tests can now run concurrently. Terraform 1.13.1 restores a successful exit for suites containing zero tests, and 1.13.2 corrects cleanup-node ordering, so use at least 1.13.2 when cleanup dependencies matter.

### Provider constraints must leave test files

*Terraform 1.9.0 — batch `terraform-1.9.0`.*

Terraform 1.9 rejects version constraints in provider blocks inside `.tftest.hcl` files. Move those constraints into the main configuration's provider requirements before upgrading.

### Shared state between test runs

*Terraform 1.11.0 — batch `terraform-1.11.0-guide`.*

The new `state_key` attribute on a `run` block selects the internal test state file. Assigning the same key to setup and verification runs lets them deliberately target the same infrastructure.

### Test cleanup follows reverse run order

*Terraform 1.7.0 — batch `terraform-1.7.0`.*

`terraform test` now destroys test infrastructure in simple reverse order of the `run` blocks, making cleanup order explicit for tests with dependencies between runs.

### Test failure continuation and diagnostics

*Terraform 1.12.0 — batch `terraform-1.12.0`.*

A missing expected failure no longer prevents subsequent tests from executing. Failed run assertions also produce detailed diagnostic objects.

### Test isolation and cleanup diagnostics

*OpenTofu 1.7.0 — batch `opentofu-1.7.0`.*

When `tofu test` cannot clean up resources, it now dumps the state file for recovery. Starting in 1.7.4, automatically loaded test-directory tfvars files no longer leak into non-test commands.

