# Testing and Go tooling

## Provider mocks and targeted overrides (`1.8.0`)

`tofu test` supports `mock_provider` with `mock_resource` and `mock_data`. Use `override_resource`, `override_data`, and `override_module` when only specific results should be replaced.

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

Test-file `variables` blocks can reference variables. Test run names cannot contain spaces.

Later 1.8 patches stop validating mock-provider definitions against the real provider schema and relax type validation for mocks and overrides. Do not treat that permissiveness as a durable contract: later releases tighten shapes again.

## Override scoping (`1.9.0`)

Place `override_resource` or `override_data` inside a `mock_provider` to scope the override to that mock. Invalid mock and override fields are errors rather than warnings, so upgrade stale fixtures before relying on the new validation.

## Remote modules and run-output providers (`1.10.0`)

An explicit module under test in `.tftest.hcl` may use a remote source.

A test-file `provider` block may refer to output values from an earlier `run` block. This lets setup runs produce provider configuration for later scenarios; preserve dependency order when restructuring tests.

## Iterated mocks and function inputs (`1.11.0`)

`mock_provider` supports `for_each`. Test-file `variable` blocks may call functions.

Generated mocks follow provider schemas more closely. Correct mocks and overrides that relied on previously unchecked or invalid shapes; do not assume generated placeholders will preserve older permissive behavior.

## Failed cleanup recovery (`1.7.0`)

When `tofu test` cannot clean up resources, it dumps the state file. Preserve that file and use it to recover and manage the remaining resources rather than manually reconstructing their addresses.

## Go release and registry tooling (`1.8.0`)

TofuDL is a Go library for:

- locating the latest OpenTofu release
- verifying its signature
- downloading and extracting the binary
- mirroring releases for air-gapped environments

The experimental `libregistry` library offers structured access to registry metadata and building blocks for independent registry tools. Its experimental status means consumers should isolate it behind a small adapter and expect API changes.
