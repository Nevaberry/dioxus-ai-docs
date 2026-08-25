# Data and search

## DAL schemas and definitions

### MySQL 8.4 foreign-key validation (since 6.7.13.0)

`dal:validate` rejects foreign keys that do not reference a complete primary
or unique key. Versioned entities commonly require the missing `version_id`
column. Temporarily tolerate a constraint during migration with:

```bash
bin/console dal:validate --tolerate-foreign-key=constraint_name
```

### Plugin entity and migration contracts

Plugin `Resources/config/entities.xml` custom entities are unsupported; use
`EntityDefinition` or attribute entities. Many-to-many mapping definitions
must declare foreign-key fields, and `EntityExtension::getEntityName()` is
mandatory. Migration timestamps must fit `1..2147483647`. On uninstall with
`keepUserData=false`, migration records are removed before the plugin cleanup
runs.

### Framework DAL contracts

Remove calls to the soon-to-be-removed `EntityDefinition` constructor. DAL
attribute classes and `IsFlowEventAware` can no longer be subclassed.
Restricted foreign-key deletes consistently throw
`RestrictDeleteViolationException`, replacing entity-specific language, theme,
sales-channel, order, and newsletter exceptions.

### Moved unmapped-field exception (since 6.7.13.0)

Use
`Shopware\Core\Framework\DataAbstractionLayer\Exception\UnmappedFieldException`
instead of the deprecated `...\Dbal\Exception\UnmappedFieldException`. To
support both feature-flag states in 6.7, catch both classes because they have
no shared exception parent.

## Query and result contracts

### Search-result wrappers (since 6.7.13.0)

For 6.8 compatibility, call collection methods on `$result->getEntities()`,
iterate `searchResult.entities` in Twig, and stop testing result wrappers as
`EntityCollection`. `ProductListingResult` and `ProductReviewResult` also stop
extending `EntitySearchResult`; construct them with `fromSearchResult()`.

Avoid `EntitySearchResult` setters and its `entity` value because the wrapper
becomes immutable and its constructor removes and reorders that argument.

### Exclude heavy fields (since 6.7.13.0)

`Criteria::excludeFields()` omits selected storage columns but returns the
usual typed entity, with excluded properties at their defaults.

```php
$criteria->excludeFields(['description', 'keywords']);
```

It cannot be combined with `addFields()`. Unknown, required, or
write-protected top-level fields cannot be excluded. Reduced product listings
use this mechanism; `ProductListingLoader::PARTIAL_LISTING_FIELDS` is
deprecated for 6.8.

### Primary order associations

Use `order.primaryOrderDelivery` and `order.primaryOrderTransaction` instead
of positional collection access. Existing orders are backfilled.
`OrderConverter` keeps the primary delivery first for compatibility.
`ORIGINAL_PRIMARY_ORDER_DELIVERY` and
`ORIGINAL_PRIMARY_ORDER_TRANSACTION` cart extensions are read-only
informational snapshots.

## Indexing and events

### Description teaser backfill (since 6.7.13.0)

`product.description_teaser.indexer` runs once through the post-update flow and
is no longer run by `bin/console dal:refresh:index`. It repairs missing or
stale teasers for pre-6.7.12 products; later product writes synchronize the
field directly.

### Category index event IDs (since 6.7.13.0)

A single-category write dispatches `CategoryIndexerEvent` only for the changed
category and its descendants, plus the parent's child count when structurally
needed. Subscribers that depended on unrelated siblings in the event must
resolve them independently.

### Digital-product state repair

The update post-finish subscriber rebuilds missing legacy `product.states`, so
product-state rules and digital-delivery flows work again. The repair runs
automatically once per installation and records completion in `app_config`.

## Product streams and prices

### Individual variants (since 6.7.13.0)

`product_stream.display_as_group` / `displayAsGroup` defaults to true. Disable
it to prevent matching variants from being grouped or remapped.
`ProductStreamBuilderInterface` and `buildFilters()` are deprecated for 6.8;
extend `AbstractProductStreamBuilder` and use `enrichCriteria()`.

### Cheapest matching variant

Product-listing min/max price logic applies `MIN()` rather than choosing an
arbitrary grouped variant row. Sorting a variant product by price therefore
reflects its cheapest variant.

## Elasticsearch and OpenSearch

### Full Storefront reindex

`TranslatedField::$useForSorting` marks sortable Elasticsearch fields, and
search avoids nested queries. Run `bin/console es:index` after upgrading so
the mappings and implementation take effect.

### Query builder return types

Elasticsearch `buildTermQuery()` and product-search `build()` return
`BuilderInterface`, not `BoolQuery`; decorators should return the generated
builder directly.

### OpenSearch 3 empty properties

An object mapping must omit an empty `properties` member or use `{}` because
OpenSearch 3 rejects `"properties": []`.

```json
{"customFields":{"type":"object","properties":{}}}
```

### Server-side index defaults

Search indices inherit shard and replica counts from the server.

## Search configuration and SEO

The minimum search-term length comes from database configuration, not `.env`.
`SeoResolverData::get()` is deprecated because it silently returns one match;
use `getAll()` and update every matching entity when attaching SEO URLs.

## Cache relevance

With `CACHE_REWORK` enabled, `sw-cache-hash` omits rules that cannot affect
product prices. Storefront output driven by other custom rules must contribute
IDs through `ResolveCacheRelevantRuleIdsExtension`, directly or through a rule
area marked on the DAL association with `RuleAreas`.
`RuleAreas::CATEGORY_AREA` and `RuleAreas::LANDING_PAGE_AREA` are deprecated.
