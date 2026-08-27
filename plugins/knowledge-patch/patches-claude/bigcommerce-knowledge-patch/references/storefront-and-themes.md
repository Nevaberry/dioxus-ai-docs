# Storefront and Themes

## Catalyst checkout session sync

Checkout session sync can fail with `Invalid JWT token` or `404` when:

- checkout or login-token routes use the edge runtime
- `BIGCOMMERCE_STOREFRONT_TOKEN` contains an OAuth token
- the channel and custom domain do not match
- the domain is not primary
- the domain is not fully propagated and verified
- the redirect exceeds the JWT's 30-second lifetime

Inspect the JWT's `channel_id`, `redirect_to`, and `eat` claims when diagnosing
configuration mismatches.

## Stencil category custom-field visibility

The redundant `is_visible` property on custom-field overrides in Stencil's
`category_content` resource is deprecated and will stop being returned.

Remove theme references to `is_visible`. There is no replacement field.
