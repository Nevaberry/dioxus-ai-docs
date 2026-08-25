# Extensions and framework

## Plugin and app scaffolding

### Minimal plugin skeleton (since 6.7.13.0)

`plugin:create --no-scaffold` generates only the required plugin skeleton.

```bash
bin/console plugin:create MyPlugin MyNamespace --no-scaffold
```

### Formerly transitive packages (since 6.7.13.0)

`doctrine/inflector`, `symfony/monolog-bridge`, and
`symfony/proxy-manager-bridge` are deprecated as Shopware dependencies and
will disappear in the next major. Extensions using them must add them to their
own `composer.json`.

## Custom fields

### File-based declarations (since 6.7.13.0)

Apps and plugins can put definitions in `Resources/config/custom-fields.xml`.
Shopware creates, updates, and removes them with the extension lifecycle. This
file takes precedence over an app's deprecated inline manifest definition.
`<include-in-search>true</include-in-search>` exposes a field to product search
indexing and ranking configuration.

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

Inline `<custom-fields>` in `manifest.xml` is removed in 6.8. The XML DTO
namespace moves from `Framework\App\Manifest\Xml\CustomField` to
`System\CustomField\Xml`.

### Names and target entities

An app's custom-field-set `name` must be unique per app. `unit` and
`newsletter_recipient` are valid custom-field entities. New custom-field and
field-set names cannot contain dots or hyphens and must be valid Twig variable
names; existing definitions continue to work.

## Scheduled tasks and services

### Scheduled-task executor (since 6.7.13.0)

Container-registered handlers need no changes. Manually constructed
`ScheduledTaskHandler` objects must receive a `ScheduledTaskExecutor` through
`setScheduledTaskExecutor()`. Inline handler orchestration and
`markTaskRunning()`, `markTaskFailed()`, and `rescheduleTask()` are deprecated.
Implement `DynamicallyScheduledTaskHandler::getNextExecutionTime()` for a
non-default next execution time.

### Constructor signature

Custom `ScheduledTaskHandler` constructors require `LoggerInterface` as their
second dependency.

## Hooks, events, and media

### Per-thumbnail post-processing (since 6.7.13.0)

`Shopware\Core\Content\Media\Event\ThumbnailGeneratedEvent` fires after each
thumbnail is written. It exposes the media and thumbnail IDs, path, MIME type,
and `FilesystemOperator`, so a subscriber can read, optimize, and replace that
file. JPEG thumbnails are progressive. Batch generation logs and cleans up an
individual failure before continuing, while
`ThumbnailService::updateThumbnails()` still exposes single-media failures.

### MIME-aware media path hooks

Set `ResolveRemoteThumbnailUrlExtension::$mediaEntity` instead of deprecated
`mediaPath` and `mediaUpdatedAt`. Replace `MediaPathChangedEvent::media()` /
`thumbnail()` with `mediaWithMimeType()` / `thumbnailWithMimeType()`.

### Mail-template simulation form data (since 6.7.13.0)

Declare form variables as `FormDataObjectType` in the event's available data,
then populate simulations through `MailDataSimulatorFormDataEvent`.

```php
public function provideFormData(MailDataSimulatorFormDataEvent $event): void
{
    if ($event->flowEventName === 'my_form.send' && $event->variableName === 'myFormData') {
        $event->setData(['field' => 'value']);
    }
}
```

## Script hooks and response factories

`ScriptResponseFactoryFacade::render()` is deprecated for removal in 6.8.
Admin API and Store API hooks should use the core
`ScriptResponseFactoryFacade` without `render()`. Storefront hooks that render
Twig must use
`Shopware\Storefront\Framework\Script\Api\StorefrontScriptResponseFactoryFacade`
(since 6.7.13.0).

## Configuration contracts

### Type-stable plugin defaults

Plugin configuration defaults are parsed from the declared field type:
`checkbox` and `bool` become booleans, `int` becomes an integer, `float`
becomes a float, and every other field type remains a string. Code reading an
unset plugin setting must not infer its type from the literal text.

### System-config APIs

Use factory methods on `SystemConfigException`, not
`InvalidDomainException`, `InvalidKeyException`, or
`InvalidSettingValueException`. `SystemConfigService::trace()` and
`getTrace()` are deprecated no-ops.

### Sales-channel maintenance terminology (since 6.7.13.0)

Migrate:

- `maintenanceIpWhitelist` → `maintenanceIpAllowlist`
- entity accessors → `getMaintenanceIpAllowlist()` /
  `setMaintenanceIpAllowlist()`
- `SalesChannelRequest::ATTRIBUTE_SALES_CHANNEL_MAINTENANCE_IP_WHITLELIST` →
  `ATTRIBUTE_SALES_CHANNEL_MAINTENANCE_IP_ALLOWLIST`
- `HttpCacheKernel::MAINTENANCE_WHITELIST_HEADER` →
  `MAINTENANCE_ALLOWLIST_HEADER`

The old and new DAL fields and database columns remain synchronized in 6.7;
deprecated variants are removed in 6.8.

## Framework and validation

### Symfony and reset contracts

Shopware 6.7 moves to Symfony 7.3. Following the Symfony 7.3 convention, pass
Shopware constraint options as named constructor arguments.

```php
new CustomerEmailUnique(salesChannelContext: $context)
```

Long-running runtimes reset Symfony `ResetInterface` services between requests
without extra configuration.

### Filterable prices

A custom price definition intended to be filterable must explicitly implement
`Shopware\Core\Checkout\Cart\Price\Struct\FilterableInterface` and its
`getFilter()` method.

### Deprecation introduction versions

`Feature::triggerDeprecationOrThrow()` accepts an optional third
`introducedIn` argument, which prefixes the message with
`Since shopware/core <version>:`. Omitting it produces a normal unprefixed
message instead of a malformed empty-version prefix.

## Core API replacements

### Method signatures

Preserve these parameters and types:

- `ImportExportFactory::create(..., bool $useBatchImport = ...)`; profiles use
  `technicalName`, and the CLI uses `--profile-technical-name`.
- `SitemapHandleFactoryInterface::create(..., string $domainId = ...)`.
- `TreeUpdater::batchUpdate(..., bool $recursive = false)`.
- Migration helper named arguments are `columnName`, `foreignKeyName`, and
  `indexName`.
- `PromotionGatewayInterface` returns `PromotionCollection`.
- `AbstractCartOrderRoute::order()` gains a mandatory request in the next
  major.

### Removed or replaced APIs

- Use `CreateMigrationCommand` instead of `CreateSchemaCommand`.
- Use `MigrationQueryGenerator` instead of `SchemaGenerator`.
- Use `AccountService::loginByCredentials()` / `loginById()` instead of
  `login()`.
- Mail-action constants move to `SendMailAction`.
- `MailTemplateActions`, `AttachmentLoader`, the attachment criteria event,
  and `CustomFieldRule::floatMatch()` / `arrayMatch()` have no replacement.

### Consolidated exception families

System-config and snippet failures use domain exception factory methods. DAL
entity property access uses `DataAbstractionLayerException` or
`PropertyNotFoundException`; update catches for removed specialized exceptions.

### HTTP cache constant owners

Cache-state constants move from `CacheResponseSubscriber` to
`CacheStateSubscriber`. Cache-cookie and invalidation-header constants move to
`HttpCacheKeyGenerator`.
