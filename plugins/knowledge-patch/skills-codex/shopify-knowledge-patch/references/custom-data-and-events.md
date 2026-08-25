# Custom Data and Events

## Customer webhook payload migration

In `2025-01`, embedded customer payloads no longer include `tags`,
`email_marketing_consent`, `sms_marketing_consent`, `last_order_id`,
`last_order_name`, `total_spent`, or `orders_count`.

Consume these topics instead:

- `CUSTOMER_TAGS_ADDED` and `CUSTOMER_TAGS_REMOVED`
- `CUSTOMERS_EMAIL_MARKETING_CONSENT_UPDATE`
- `CUSTOMERS_MARKETING_CONSENT_UPDATE`
- `CUSTOMERS_PURCHASING_SUMMARY`

## App-owned data permissions

`PrivateMetafield` is no longer in the public Admin API. Use app-data metafields for
app storage or app-reserved namespaces for per-resource data.

App-reserved metafield and metaobject mutations no longer accept `PRIVATE`,
`PUBLIC_READ`, `PUBLIC_READ_WRITE`, or `LEGACY_LIQUID_ONLY`.
`MetafieldAccessInput.admin` and `MetafieldAccessUpdateInput.admin` are optional.

## Storefront access and definition capabilities

`MetafieldStorefrontVisibility`, its queries and mutations, and
`visibleToStorefrontApi` fields were removed. Read `MetafieldDefinition.access` and
change it with `metafieldDefinitionUpdate`.

`MetafieldDefinitionInput.useAsCollectionCondition` was replaced by
`capabilities.smartCollectionCondition`. Standard-definition enable mutations accept
`capabilities`.

## Conditional definitions and linked values

Create inputs accept `constraints`, while update inputs accept `constraintsUpdates`.
In `2025-01`, product metafield definitions support product-category constraints,
product updates provide `deleteConflictingConstrainedMetafields`, and
`VariantOptionValueInput.linkedMetafieldValue` is available.

## Unique metafield values

`MetafieldCapabilityUniqueValues` can enforce uniqueness only before a definition
has metafields. It supports only `single_line_text_field`, `number_integer`, `url`,
and `id` values.

## Identifier-based deletion

`metafieldDelete(gid)` was removed. Use `metafieldsDelete`, with each array entry
identifying a metafield by `ownerId`, `namespace`, and `key`. A metafield GID is not
accepted.

## Custom IDs and upserts

Custom IDs, formerly external keys, are metafield-backed identifiers available to
any metafield-capable resource. Lookup by custom ID is limited to products and
customers.

`productSet` and unstable `customerSet` provide matching-key upserts, but a custom ID
cannot yet be the matching key.

## Inventory-transfer metafields

Inventory transfers can have metafield definitions and metafield values. Their
webhooks include origin and destination location IDs.

## Metafield query errors and event triggers

Invalid metafield queries return GraphQL Admin API errors. Events adds metafield
triggers and additional topics.

## Next Generation Events

The developer preview adds field-level trigger control, custom GraphQL payloads, and
query-based delivery filters to webhooks.

## Marketing consent and engagement

Cumulative marketing engagements are deprecated. WhatsApp marketing consent is
available through both the Admin and Customer Account APIs.
