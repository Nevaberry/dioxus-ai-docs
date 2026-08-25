# OpenTofu Test Behavior

## Cleanup failure recovery (`1.7.0`)

When `tofu test` cannot clean up resources, it dumps the state file. Preserve
that file and use it to recover, inspect, and manage the resources that remain.

## Provider mocks and targeted overrides (`1.8.0`)

`mock_provider` supports `mock_resource` and `mock_data`. Use
`override_resource`, `override_data`, and `override_module` to replace the
results of specific targets.

```hcl
mock_provider "aws" {
  mock_resource "aws_instance" {
    defaults = {
      id = "i-test"
    }
  }
}

override_resource {
  target = aws_instance.web
  values = {
    public_ip = "192.0.2.10"
  }
}
```

Test-file `variables` blocks may reference variables. Test run names cannot
contain spaces.

Later 1.8 patches stop validating mock-provider definitions against the real
provider schema and relax type validation for mocks and overrides. Do not infer
that an accepted mock shape is valid production provider configuration.

## Mock-local override scope (`1.9.0`)

`override_resource` and `override_data` may be nested in a `mock_provider`,
scoping the override to that mock. Invalid mock and override fields are errors,
not warnings.

## Remote modules and run-output providers (`1.10.0`)

An explicit module under test in `.tftest.hcl` may use a remote source.
Test-file `provider` blocks may refer to output values from a `run` block,
allowing later scenarios to configure providers with earlier results.

## Iterated mocks and function-valued variables (`1.11.0`)

`mock_provider` supports `for_each`, and test-file `variable` blocks can call
functions.

Generated mocks follow provider schemas more closely. Correct mocks or
overrides that depended on formerly unchecked invalid shapes after upgrading;
do not preserve them merely because an older release accepted them.
