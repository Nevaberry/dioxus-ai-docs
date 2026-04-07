# Resource Identity for Import

Introduced in Terraform 1.12.

## What Changed

Resources can now define an `identity` schema — a set of attributes that uniquely identify the resource, separate from the full state schema. This enables importing by structured identity attributes instead of opaque provider-specific ID strings.

## Syntax

```hcl
import {
  to = aws_instance.example
  identity = {
    id = "i-1234567890abcdef0"
  }
}
```

The identity attributes vary by resource type — they are defined by the provider, not by Terraform itself.

## Bulk Search and Import (HCP Terraform)

Resource identity also powers a new bulk import workflow in HCP Terraform. You can search for existing resources by identity attributes and import them in batches, rather than manually specifying each resource's ID string.

## Key Points

- The `identity` block is optional — traditional `id = "string"` import syntax still works
- Identity attributes are defined per-resource-type by the provider
- Not all providers/resources support identity-based import yet — it requires provider updates
- This is primarily a DX improvement; the underlying import mechanism is unchanged
