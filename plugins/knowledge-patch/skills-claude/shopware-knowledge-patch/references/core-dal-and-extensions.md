# Core, DAL, and Extension Contracts

## DAL validation, queries, and events

### Foreign-key validation (6.7.13.0)

`dal:validate` rejects foreign keys that do not reference a complete primary or unique key; versioned entities commonly need the missing `version_id` column. Temporarily tolerate a constraint during migration with:

```bash
bin/console dal:validate --tolerate-foreign-key=constraint_name
```

### Search-result wrappers and collections (6.7.13.0)

For 6.8 compatibility, call collection methods on `$result->getEntities()`, iterate `searchResult.entities` in Twig, and stop testing result wrappers as `EntityCollection`. `ProductListingResult` and `ProductReviewResult` cease extending `EntitySearchResult`; construct them with `fromSearchResult()`. Avoid `EntitySearchResult` setters and its `entity` value because the wrapper becomes immutable and its constructor drops and reorders that argument.

### Excluding fields without partial entities (6.7.13.0)

`Criteria::excludeFields()` omits selected storage columns while returning the normal typed entity, with excluded properties at their defaults:

```php
$criteria->excludeFields(['description', 'keywords']);
```

It cannot be combined with `addFields()`. Unknown, required, or write-protected top-level fields cannot be excluded. Reduced product listings use this mechanism, and `ProductListingLoader::PARTIAL_LISTING_FIELDS` is deprecated for 6.8.

### Category index event IDs (6.7.13.0)

Single-category writes dispatch `CategoryIndexerEvent` only for the affected category and descendants, plus the parent's child count when structurally necessary. Subscribers that relied on unrelated siblings in the event must resolve those categories themselves.

### Write-event system scope (6.7.13.0)

Post-write events from Admin API and Sync API writes preserve the original context source but run plugin-side DAL writes in system scope, so callers need privileges only for their submitted payload. Listeners that depend on the initiating identity must inspect `getContext()->getSource()`. Private-media reads still need an explicit `$context->scope(Context::SYSTEM_SCOPE, ...)` block.

### Foreign-key delete exceptions

Restricted foreign-key deletes consistently throw `RestrictDeleteViolationException`, replacing entity-specific language, theme, sales-channel, order, and newsletter exceptions.

## Entity definitions, attributes, and migrations

### Plugin DAL definitions and migration contracts

Plugin `Resources/config/entities.xml` custom entities are unsupported; use `EntityDefinition` or attribute entities. Many-to-many mapping definitions must declare foreign-key fields. `EntityExtension::getEntityName()` is mandatory. Migration timestamps must fit `1..2147483647`. Uninstall with `keepUserData=false` removes migration records before invoking plugin cleanup.

Remove calls to the soon-to-be-removed `EntityDefinition` constructor.

### Final DAL attributes

DAL attribute classes and `IsFlowEventAware` can no longer be subclassed.

### Custom-field declarations (6.7.13.0)

Apps and plugins can put definitions in `Resources/config/custom-fields.xml`; Shopware creates, updates, and removes them with the extension lifecycle. This file takes precedence over an app's deprecated inline manifest definition. `<include-in-search>true</include-in-search>` makes a field available to product search indexing and ranking configuration.

```xml
<?xml version="1.0" encoding="utf-8"?>
<custom-fields xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:noNamespaceSchemaLocation="https://raw.githubusercontent.com/shopware/shopware/trunk/src/Core/System/CustomField/Schema/custom-fields-1.0.xsd">
  <custom-field-set>
    <name>acme_fields</name>
    <label>Acme fields</label>
    <related-entities><product/></related-entities>
    <fields>
      <text name="acme_code"><label>Code</label><include-in-search>true</include-in-search></text>
    </fields>
  </custom-field-set>
</custom-fields>
```

Inline `<custom-fields>` in `manifest.xml` is removed in 6.8. The XML DTO namespace moved from `Framework\App\Manifest\Xml\CustomField` to `System\CustomField\Xml`.

An app custom-field-set `name` must be unique per app. `unit` and `newsletter_recipient` are valid custom-field entities. New custom-field and field-set names cannot contain dots or hyphens and must be valid Twig variable names; existing definitions continue to work.

## Exceptions and deprecations

### `UnmappedFieldException` namespace (6.7.13.0)

Use `Shopware\Core\Framework\DataAbstractionLayer\Exception\UnmappedFieldException` instead of deprecated `...\Dbal\Exception\UnmappedFieldException`. When supporting both feature-flag states in 6.7, catch both classes because they have no shared exception parent.

### System-config APIs

Use factory methods on `SystemConfigException` instead of `InvalidDomainException`, `InvalidKeyException`, or `InvalidSettingValueException`. `SystemConfigService::trace()` and `getTrace()` are deprecated no-ops.

System-config and snippet failures now come from domain exception factory methods. DAL entity property access uses `DataAbstractionLayerException` or `PropertyNotFoundException`; update catches for removed specialized exceptions.

### Deprecation introduction versions

`Feature::triggerDeprecationOrThrow()` accepts an optional third `introducedIn` argument that prefixes the message with `Since shopware/core <version>:`. Omitting it produces a normal unprefixed message.

## Script, framework, and service contracts

### Type-stable plugin configuration defaults

Default values are parsed from the declared field type: `checkbox` and `bool` become booleans, `int` becomes an integer, `float` becomes a float, and all other field types remain strings. Code reading an unset plugin setting must not infer its type from the literal text.

### Hook-specific script response factories (6.7.13.0)

`ScriptResponseFactoryFacade::render()` is deprecated for removal in 6.8. Admin API and Store API hooks should use the core `ScriptResponseFactoryFacade` without `render()`. Storefront hooks rendering Twig must use `Shopware\Storefront\Framework\Script\Api\StorefrontScriptResponseFactoryFacade`.

### Symfony and runtime reset behavior

Shopware 6.7 moves to Symfony 7.3. Long-running runtimes reset Symfony `ResetInterface` services between requests without extra configuration.

### Named constraint arguments

Following the Symfony 7.3 convention, pass Shopware constraint options as named arguments:

```php
new CustomerEmailUnique(salesChannelContext: $context)
```

### Core extension signatures

Preserve these parameters and types:

- `ImportExportFactory::create(..., bool $useBatchImport = ...)`; profiles use `technicalName`, and the CLI uses `--profile-technical-name`.
- `SitemapHandleFactoryInterface::create(..., string $domainId = ...)`.
- `TreeUpdater::batchUpdate(..., bool $recursive = false)`.
- Migration-helper named arguments are `columnName`, `foreignKeyName`, and `indexName`.
- `PromotionGatewayInterface` returns `PromotionCollection`.
- `AbstractCartOrderRoute::order()` gains a mandatory request in the next major.

Custom `ScheduledTaskHandler` constructors require `LoggerInterface` as their second dependency. Elasticsearch `buildTermQuery()` and product-search `build()` return `BuilderInterface`, not `BoolQuery`; decorators should return the generated builder directly.

### Removed or replaced Core APIs

Use `CreateMigrationCommand` instead of `CreateSchemaCommand`, `MigrationQueryGenerator` instead of `SchemaGenerator`, and `AccountService::loginByCredentials()` / `loginById()` instead of `login()`. Mail-action constants move to `SendMailAction`. `MailTemplateActions`, `AttachmentLoader`, the attachment criteria event, and `CustomFieldRule::floatMatch()` / `arrayMatch()` have no replacement.

### HTTP cache constants

Cache-state constants move from `CacheResponseSubscriber` to `CacheStateSubscriber`. Cache-cookie and invalidation-header constants move to `HttpCacheKeyGenerator`.
