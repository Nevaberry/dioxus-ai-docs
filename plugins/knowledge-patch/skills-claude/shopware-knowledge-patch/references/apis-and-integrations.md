# APIs and Integrations

## Store API behavior and schemas

### Stateless Store API requests (6.7.13.0)

Store API requests remain stateless unless application or extension code explicitly starts a Symfony session. Storefront session handling, including customer imitation, is unchanged. This avoids PHP session locks and storage growth caused by sales-channel or Storefront subscribers.

### Complete JSON schema overrides (6.7.13.0)

When `Resources/Schema/StoreApi/components/schemas/` defines an entity component, `StoreApiGenerator` uses that JSON schema as the sole source of truth. It does not merge properties or required fields from the PHP `EntityDefinition`; bundles providing both must keep the JSON component complete.

### Confidential order payload fields (6.7.13.0)

`orders.elements[].lineItems[].payload.purchasePrices` is removed during JSON serialization for existing and new orders, with no Store API replacement. The raw payload remains available through PHP line-item APIs. Headless clients and integrations must stop consuming this field.

### Per-request search limits

`/store-api/product-listing/{categoryId}`, `/store-api/search`, and `/store-api/search-suggest` accept a `limit` request or query parameter, capped by `shopware.api.store.max_limit`, which defaults to 100.

### Lean registration-event customers

Customer entities on registration, login, guest double-opt-in, and registration double-opt-in events no longer preload associations. Subscribers must explicitly query required related data.

### Removed Store API route caching

`Cached*Route` Store API decorators are removed. Header and footer render through `/header` and `/footer`, the `layout/header.html.twig` and `layout/footer.html.twig` entry points, and `base_esi_header` / `base_esi_footer`. Custom data must travel as query parameters on the corresponding ESI request.

## Admin API actions

### Translation management (6.7.13.0)

The synchronous translation-management routes and privileges are:

- `GET /api/_action/translation/list` — `read` on `system:translation`
- `POST /api/_action/translation/install` — `create` on `system:translation`
- `POST /api/_action/translation/update` — `update` on `system:translation`
- `DELETE /api/_action/translation/{locale}` — `delete` on `system:translation`

Install accepts `locales` or `all: true`, with optional `activate: false`. Removal leaves language, locale, and snippet-set entities intact. `Shopware\Core\System\Snippet\Event\TranslationLoadedEvent` and `TranslationRemovedEvent` fire for API and CLI operations. Multi-locale operations are synchronous and non-atomic.

### Media downloads (6.7.13.0)

`GET /api/_action/media/{mediaId}/download` streams a media file or redirects to its resolved storage URL. A `media:read` client can first call `GET /api/_action/media/{mediaId}/download/prepare` to determine whether to use an external URL or authenticated blob request.

## Authentication, permissions, and OAuth

### Integration ACL scoped to an app user (6.7.13.0)

For a standard integration, a valid `sw-app-user-id` request header limits effective permissions to the intersection of the integration ACL and that user's ACL, matching app integrations. Empty or invalid IDs are ignored.

### Sales-channel maintenance allowlist (6.7.13.0)

Migrate `maintenanceIpWhitelist` to `maintenanceIpAllowlist`, entity getters and setters to `getMaintenanceIpAllowlist()` / `setMaintenanceIpAllowlist()`, `SalesChannelRequest::ATTRIBUTE_SALES_CHANNEL_MAINTENANCE_IP_WHITLELIST` to `ATTRIBUTE_SALES_CHANNEL_MAINTENANCE_IP_ALLOWLIST`, and `HttpCacheKernel::MAINTENANCE_WHITELIST_HEADER` to `MAINTENANCE_ALLOWLIST_HEADER`. Old and new DAL fields and database columns stay synchronized in 6.7; deprecated variants are removed in 6.8.

### OAuth requests

Send scopes in the singular `scope` field as a space-delimited string. Array-valued `scopes` is no longer accepted by `/api/oauth/token`. `/api/oauth/authorize` and `AuthController::authorize()` were removed without replacement.

## MCP and OpenAPI

### MCP toolsets and notifications (developer-release-notes-index)

The Shopware MCP server supports toolsets and tool-list-change notifications. Clients can refresh advertised tools when availability changes instead of treating the initial list as static.

### MCP endpoint availability

Remove `MCP_SERVER` from the environment. `/api/_mcp` and `/store-api/_mcp` are reachable whenever `symfony/mcp-bundle` is installed, with no supported flag for disabling them. Their PHP API remains experimental until 6.8.

### swagger-php 6.4 generation

Extensions using swagger-php programmatically must replace static scan and finder APIs and should declare their own Composer dependency rather than relying on Shopware's transitive package.

```php
$openApi = (new OpenApi\Generator($logger))->generate([$sourceDirectory]);
```

For cross-version processors, use `getProcessorPipeline()` / `setProcessorPipeline()` when present and fall back to the v4 `getProcessors()` / `setProcessors()` methods. Use `Generator::isDefault()` instead of direct comparison with `Generator::UNDEFINED`.

## App and sales-channel contracts

### Tax-provider priority on app update (6.7.13.0)

An app manifest's tax-provider `priority` applies only on initial installation. Later app updates preserve the merchant's manual ordering.

### Measurement systems

Store API context and product responses convert database kg/mm values to the sales-channel domain's configured measurement system. Admin API clients can select units with `sw-measurement-weight-unit` and `sw-measurement-length-unit`. Twig can convert arbitrary values with `sw_convert_unit(from: ..., to: ..., precision: ...)`.

### App payment requests

App manifests use schema `manifest-3.0.xsd` and `pay-url` instead of `capture-url`. Async `pay` and `finalize` calls no longer set payment states automatically. Finalize query parameters arrive under `requestData`. `CheckoutGatewayRoute` always filters availability because `onlyAvailable` was removed.
