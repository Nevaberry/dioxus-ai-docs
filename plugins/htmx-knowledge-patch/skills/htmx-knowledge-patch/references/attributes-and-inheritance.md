# htmx 4.0: Attributes & Inheritance

## Explicit Inheritance (Breaking)

Attributes no longer inherit down the DOM implicitly. Use `:inherited` suffix:

```html
<!-- htmx 4: explicit inheritance -->
<div hx-confirm:inherited="Are you sure?">
  <button hx-delete="/item/1">Delete</button>
</div>
```

Use `:append` to add to an inherited value:

```html
<div hx-include:inherited="#global-fields">
    <form hx-include:inherited:append=".extra">...</form>
</div>
```

Revert to implicit behavior: `htmx.config.implicitInheritance = true`

## Per-Status-Code Behavior with `hx-status`

```html
<form
  hx-post="/save"
  hx-status:422="swap:innerHTML target:#errors select:#validation-errors"
  hx-status:5xx="swap:none push:false"
></form>
```

Keys: `swap:`, `target:`, `select:`, `push:`, `replace:`, `transition:`. Supports wildcards (`5xx`, `50x`).

## New Attributes

| Attribute | Purpose |
|-----------|---------|
| `hx-action` | Specify URL (use with `hx-method`) |
| `hx-method` | Specify HTTP method |
| `hx-config` | Per-element request config (JSON or `key:value`) |
| `hx-ignore` | Disable htmx processing (replaces old `hx-disable`) |
| `hx-validate` | Control form validation behavior |

## Attribute Renames (Breaking — do BEFORE upgrading)

1. `hx-disable` → `hx-ignore` (skip htmx processing)
2. `hx-disabled-elt` → `hx-disable` (disable form elements during requests)

**Important**: These swap meanings. Rename `hx-disable` to `hx-ignore` first, then rename `hx-disabled-elt` to `hx-disable`.

## Removed Attributes

| Removed | Replacement |
|---------|-------------|
| `hx-vars` | `hx-vals` with `js:` prefix |
| `hx-params` | `htmx:config:request` event |
| `hx-prompt` | `hx-confirm` with `js:` prefix |
| `hx-ext` | Include extension script directly |
| `hx-disinherit` / `hx-inherit` | Not needed (inheritance is now explicit) |
| `hx-request` | `hx-config` |
| `hx-history` / `hx-history-elt` | Removed entirely |
