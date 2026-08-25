# Sellers, Catalog, and Inventory

## Seller onboarding and team access (0.9.0)

Sellers can register and onboard, then organize team members with invitations
and role-based access. Mercur also supports extended seller information,
team-member email handling, and vendor file uploads.

## Seller lifecycle administration (1.0.0)

Mercur provides a seller-management API, platform-level seller invitations,
and seller-suspension logic. Operators can administer a seller beyond the
seller's own onboarding and team-management flows.

When a seller has no email address, Mercur uses the member email so
email-dependent seller flows still have a recipient.

## Catalog and product management (0.9.0 and 1.0.0)

The marketplace supports:

- categories;
- collections;
- brands;
- tags and types;
- variants and options;
- draft products; and
- product import and export.

It also introduces a global product catalog with Admin catalog settings.
Products can carry attributes in addition to their existing catalog structure,
enabling richer product metadata in Mercur 1.0.

## Product approval workflows (0.9.0)

Product operations can use request/approval and edit-request flows. A Requests
panel is available to administrators. Product imports create requests rather
than bypassing this governance path.

## Seller-owned inventory (0.9.0)

Inventory items can be linked to sellers, and sellers have their own stock
locations. The inventory and fulfillment flow includes batch stock editing,
reservation management, and default shipping-profile assignment.

## Vendor merchandising and customer targeting (0.9.0 and 1.0.0)

Vendors can use promotions, campaigns, and price lists. Customer groups
participate in customer selection. Mercur also exposes sales-channel access,
service-zone management, and shipping-option management.

When a seller creates a promotion, product selection is restricted to that
seller's products rather than exposing products owned by other sellers.

## Linked-entity filtering (1.0.0)

Deleted linked entities are filtered out, preventing stale linked records from
appearing in marketplace data.

## Seeded configuration rules (1.0.0)

Mercur's seed process creates default configuration rules, so a seeded
environment starts with the marketplace's baseline rule configuration.
