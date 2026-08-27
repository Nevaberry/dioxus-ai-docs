# Labels and Migration

## Thermal-label capabilities

Ship supports 300 DPI thermal output without a label-format change.

It also accepts these `labelStockType` values:

- `STOCK_4X85_TRAILING_DOC_TAB`.
- `STOCK_4X105_TRAILING_DOC_TAB`.

## German weight-handling icons

Labels for inbound-to-Germany and domestic German parcel and freight shipments
automatically include 10+ kg or 20+ kg handling icons. This applies to every
automated label channel and replaces the former manual-sticker workaround.

## FedEx Web Services migration

FedEx Web Services entered maintenance-only support on July 1, 2026 and is
approaching retirement. Integrations should migrate to FedEx APIs rather than
expect further Web Services development.
