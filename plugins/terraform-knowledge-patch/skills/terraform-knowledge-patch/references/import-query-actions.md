# Import, Query & Actions

## Import by Identity (1.12)

`import` blocks support structured `identity` instead of opaque `id` string (provider must implement identity schema):

```hcl
import {
  to       = aws_instance.example
  identity = { instance_id = "i-1234567890abcdef0" }
}
```

## List Resources and `terraform query` (1.14)

Query existing infrastructure via `.tfquery.hcl` files without managing state:

```hcl
# find_instances.tfquery.hcl
list "aws_instance" "all" {
  filter {
    tag    = "Environment"
    values = ["production"]
  }
}
```

Run with `terraform query`. Can generate import configuration from results.

## Actions Block (1.14)

Imperative operations outside CRUD lifecycle. Provider-defined actions like lambda invocations or cache invalidations:

```hcl
action "invalidate_cache" {
  type = "aws_cloudfront_create_invalidation"
  inputs = {
    distribution_id = aws_cloudfront_distribution.main.id
    paths           = ["/*"]
  }
}
```

Triggered via `-invoke` CLI flag or resource lifecycle hooks.
