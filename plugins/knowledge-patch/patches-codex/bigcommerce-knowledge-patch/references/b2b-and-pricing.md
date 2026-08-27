# B2B and pricing

## B2B quote webhook payloads

B2B quote events send these fields in `data`:

- `quote_id`;
- `quote_uuid`.

They do not send the previously documented `type` and `id` fields. Webhook
consumers must parse the quote-specific fields.

## B2B company-address management

### Mutations and lookups

Authenticated company users have alpha `CompanyMutations.addAddress`,
`CompanyMutations.updateAddress`, and `CompanyMutations.deleteAddress` fields.

`CompanyQueries` and `ActiveCompany` support single-address lookup by
`entityId`.

The mutations and lookups are deprecated and not for production.

### Connections and address fields

Company address connections support `city`, `state`, `country`, and
`companyIds` filters.

`CompanyAddress` has nullable `createdAt` and `updatedAt` fields.

## Removed alpha company-user fields

The alpha `companyUser` query, `updateCompanyUser` mutation, and
`CompanyOrdersFiltersInput.search` filter have been removed.

## Customer-group markup

Customer groups can use an early-access `markup` entry in `discount_rules`.
Its `method` can be `percent` or `price`, and it raises member prices across
the entire catalog.

A markup rule cannot coexist with other discount-rule types. Support must
enable the rule.
