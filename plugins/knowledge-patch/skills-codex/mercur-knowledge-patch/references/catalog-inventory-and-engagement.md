# Catalog, inventory, and engagement

## Catalog and global product management (0.9.0)

The marketplace supports:

- categories, collections, brands, tags, and types;
- variants and options;
- draft products;
- product import and export.

Mercur also provides a global product catalog with Admin catalog settings.

## Product approval and import governance (0.9.0)

Product operations can use request/approval and edit-request flows. Administrators
work with these through a Requests panel. Product imports create requests rather than
bypassing the governance path.

## Product attributes (1.0.0)

Products can carry attributes in addition to their existing catalog structure,
enabling richer product metadata.

## Seller-owned inventory (0.9.0)

Inventory items can be linked to sellers, and sellers have their own stock locations.
The inventory and fulfillment flow includes:

- batch stock editing;
- reservation management;
- default shipping-profile assignment.

## Merchandising and customer targeting (0.9.0)

Vendors can use promotions, campaigns, and price lists. Customer groups participate
in customer selection. Mercur also exposes sales-channel access and service-zone and
shipping-option management.

## Seller-scoped promotions (1.0.0)

When a seller creates a promotion, product selection is restricted to that seller's
products instead of exposing products owned by other sellers.

## Linked-entity filtering (1.0.0)

Deleted linked entities are filtered out, preventing stale linked records from
appearing in marketplace data.

## Algolia synchronization (0.9.0, 1.0.0)

The Algolia integration handles enhanced product data and product upserts and
updates. Modifying inventory items triggers an Algolia update, allowing indexed
product availability to follow inventory changes without a separate product edit.

## Reviews, wishlists, email, and chat (0.9.0, 1.0.0)

Mercur includes wishlists and seller and product reviews. It enforces one review per
order.

Resend provides email integration. A TalkJS conversation endpoint supports
marketplace conversations.
