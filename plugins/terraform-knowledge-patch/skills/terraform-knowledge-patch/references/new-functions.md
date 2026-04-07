# New Functions

## templatestring (TF 1.9)

Renders a template from a string value rather than a file. Works like `templatefile()` but takes a string as the first argument instead of a file path.

```hcl
locals {
  rendered = templatestring(data.http.template.response_body, {
    APP_NAME = var.app_name
    PORT     = var.port
  })
}
```

### Use cases

- Rendering templates fetched from HTTP data sources
- Processing templates stored in variables or locals
- Dynamic template content that isn't stored as a file

### Comparison

| Function | First argument | Source |
|---|---|---|
| `templatefile()` | File path | Static file on disk |
| `templatestring()` | String value | Any string expression |

Both support the same template syntax (string interpolation, directives, etc.).

## ephemeralasnull (TF 1.10+)

Converts an ephemeral value to a non-ephemeral `null`. Useful in conditionals where you need to branch on whether an ephemeral value exists but don't need the value itself in a non-ephemeral context.

```hcl
locals {
  # Use in a conditional without leaking the ephemeral value
  has_secret = ephemeralasnull(var.secret_token) != null ? true : false
}
```

## terraform.applying (TF 1.10+)

A named value (not a function) that returns `true` during the apply phase and `false` during plan. Useful for conditional logic that should only execute during apply.

```hcl
locals {
  phase = terraform.applying ? "apply" : "plan"
}
```
