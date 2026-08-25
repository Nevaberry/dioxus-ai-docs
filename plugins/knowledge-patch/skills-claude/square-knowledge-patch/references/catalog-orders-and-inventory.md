# Catalog, orders, and inventory

## Catalog items and modifier selection

`CatalogItem.is_alcoholic` marks alcoholic items. Modifier-list selection
constraints can live at list level.

New modifier-related fields are:

- `CatalogModifier.hidden_online`
- `CatalogModifier.on_by_default`
- `CatalogModifierList.allow_quantities`
- `CatalogModifierList.min_selected_modifiers`
- `CatalogModifierList.max_selected_modifiers`
- `CatalogModifierList.hidden_from_customer`
- `CatalogItemModifierListInfo.allow_quantities`
- `CatalogItemModifierListInfo.is_conversational`
- `CatalogItemModifierListInfo.hidden_from_customer_override`
- `CatalogModifierOverride.hidden_online_override`
- `CatalogModifierOverride.on_by_default_override`

Deprecated fields are:

- `CatalogModifierList.selection_type`
- `CatalogModifierList.max_quantity`
- `CatalogItemModifierListInfo.hidden_from_customer`
- `CatalogModifierOverride.hidden_online`
- `CatalogModifierOverride.on_by_default`

## Nested modifiers

In Beta, `CatalogModifier.child_modifier_list_ids` links nested modifier lists
for multi-step choices. Set `include_options` on `BatchRetrieveCatalogObjects`,
`SearchCatalogItems`, or `SearchCatalogObjects` to include related modifier
lists in responses.

## Kitchen display fields

For restaurant kitchen displays:

- `CatalogItem` adds `kitchen_name` and `buyer_facing`.
- `CatalogItemVariation` adds `kitchen_name`.
- `CatalogModifier` adds `kitchen_name`.
- `CatalogModifierToggleOverrideType` is new.

## Catalog vendor information

In Beta, `CatalogItemVariation.vendor_information` exposes the default unit
cost, vendor, and vendor code for an item variation.

## Inventory cost and vendor tracking

In Beta, stock-receiving adjustments accept `cost_money` and `vendor_id`.
`UpdateInventoryAdjustment` can edit a past adjustment's `quantity`,
`cost_money`, `vendor_id`, and `reason_id`.

Writing cost or vendor data requires an active Retail Plus, Restaurants Plus,
or Restaurants Premium subscription.

## Inventory adjustment reasons and sorting

Beta adjustment reasons use `InventoryAdjustment.reason_id` for standard or
seller-defined categories. List, retrieve, create, update, delete, and restore
operations are available under `/v2/inventory/adjustment-reasons`.

Change history can be filtered by `reason_ids`.
`BatchRetrieveInventoryChanges.sort` orders history by `occurred_at`.

## Cross-location inventory movement

As of Square version `2026-07-15`, cross-location movement is an `ADJUSTMENT`
with `from_location_id` and `to_location_id`. `TRANSFER`, `InventoryTransfer`,
`RetrieveInventoryTransfer`, and `InventoryAdjustment.location_id` are retired.

Responses expose the `UNTRACKED` state plus Square-generated inferred and
component adjustments.

## Transfer Orders API

The Beta Transfer Orders API manages and tracks inventory movements between a
seller's Square locations.

## Subscription checkout

For subscription checkout, `CreatePaymentLink.subscription_plan_id` must
contain a subscription plan variation ID, not a subscription plan ID.

## Order charge metadata

`OrderLineItem.blocked_service_charges` can block ad hoc service charges per
line item. The following fields and type add charge classification metadata:

- `OrderLineItemAppliedTax.auto_applied`
- `OrderReturnServiceCharge.type`
- `OrderCardSurchargeTreatmentType`

## In-store fulfillment

The new `IN_STORE` fulfillment type represents an order received by the buyer
at the seller's location at sale time. Writing it is limited to partners in the
closed Beta.
