# APIs and integrations

## Store API request and response contracts

### Requests stay stateless (since 6.7.13.0)

Store API requests no longer start sessions implicitly. They remain stateless
unless application or extension code explicitly starts a Symfony session.
Storefront session handling, including customer imitation, is unchanged. The
change also avoids PHP session locks and storage growth caused by sales-channel
or Storefront subscribers.

### Orders hide purchase prices (since 6.7.13.0)

JSON serialization removes
`orders.elements[].lineItems[].payload.purchasePrices` for existing and new
orders, with no Store API replacement. The raw payload remains available from
PHP line-item APIs; headless clients and integrations must stop consuming it.

### Search limits are per-request

`/store-api/product-listing/{categoryId}`, `/store-api/search`, and
`/store-api/search-suggest` accept a `limit` request or query parameter capped
by `shopware.api.store.max_limit`, whose default is 100.

### Registration event customers are lean

Customer entities on registration, login, guest double-opt-in, and
registration double-opt-in events no longer preload associations. Subscribers
must explicitly query required related data.

### Cookie groups

`/store-api/cookie-groups` returns groups registered through `CookieRoute`.
Plugins must replace `CookieProviderInterface` decorators with a
`CookieGroupCollectEvent` listener that adds `CookieGroup` / `CookieEntry`
structs. Twig cookie fields use `name` and `description`, not `snippet_name`
and `snippet_description`.

### Measurement conversion

Store API context and product responses convert database kg/mm values to the
sales-channel domain's configured measurement system.

### Explicit JSON schemas (since 6.7.13.0)

When `Resources/Schema/StoreApi/components/schemas/` defines an entity
component, `StoreApiGenerator` uses that JSON schema as the sole source of
truth. It does not merge properties or required fields from the PHP
`EntityDefinition`, so bundles providing both must keep the JSON component
complete.

## Admin API operations

### Translation management (since 6.7.13.0)

The synchronous routes and privileges are:

- `GET /api/_action/translation/list` — `read` on `system:translation`
- `POST /api/_action/translation/install` — `create` on `system:translation`
- `POST /api/_action/translation/update` — `update` on `system:translation`
- `DELETE /api/_action/translation/{locale}` — `delete` on
  `system:translation`

Installation accepts `locales` or `all: true`, with optional
`activate: false`. Removal leaves language, locale, and snippet-set entities
intact. `Shopware\Core\System\Snippet\Event\TranslationLoadedEvent` and
`TranslationRemovedEvent` fire for API and CLI operations. Multi-locale
operations are synchronous and non-atomic.

### Media downloads (since 6.7.13.0)

`GET /api/_action/media/{mediaId}/download` streams the media file or redirects
to its resolved storage URL. A `media:read` client can first request
`GET /api/_action/media/{mediaId}/download/prepare` to determine whether to use
an external URL or an authenticated blob request.

### Measurement headers

Admin API clients can choose units using `sw-measurement-weight-unit` and
`sw-measurement-length-unit`.

## Integration ACL and OAuth

### Scope a standard integration to an app user (since 6.7.13.0)

For a standard integration, a valid `sw-app-user-id` request header limits
effective permissions to the intersection of the integration ACL and that
user's ACL, matching app integrations. Empty or invalid IDs are ignored.

### OAuth token requests

Send scopes in the singular `scope` field as a space-delimited string.
Array-valued `scopes` is no longer accepted by `/api/oauth/token`.
`/api/oauth/authorize` and `AuthController::authorize()` were removed without
replacement.

## MCP

### Endpoints have no feature flag

Remove `MCP_SERVER` from the environment. `/api/_mcp` and `/store-api/_mcp` are
reachable whenever `symfony/mcp-bundle` is installed, with no supported flag
for disabling them. Their PHP API remains experimental until 6.8.

### Toolsets and list-change notifications

The Shopware MCP server supports toolsets and tool-list-change notifications,
so clients can refresh advertised tools when availability changes rather than
treating the initial list as static.

## OpenAPI generation

swagger-php 6.4 replaces the static scan and finder APIs. Extensions that use
swagger-php programmatically should declare their own Composer dependency
instead of relying on Shopware's transitive package.

```php
$openApi = (new OpenApi\Generator($logger))->generate([$sourceDirectory]);
```

For cross-version processors, use `getProcessorPipeline()` /
`setProcessorPipeline()` when present and fall back to the v4 `getProcessors()`
/ `setProcessors()` methods. Use `Generator::isDefault()` instead of comparing
directly with `Generator::UNDEFINED`.

## DAL write permissions through APIs

Post-write events triggered by Admin API and Sync API writes preserve the
original context source but run plugin-side DAL writes in system scope. Callers
need privileges only for their submitted payload. Listeners that intentionally
depend on the initiating identity must inspect `getContext()->getSource()`.
Private-media reads still require an explicit
`$context->scope(Context::SYSTEM_SCOPE, ...)` block (since 6.7.13.0).
