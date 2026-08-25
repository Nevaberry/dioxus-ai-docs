# Labels and trade documents

## Thermal-label capabilities

Ship supports 300 DPI thermal output without a label-format change.

It also supports these `labelStockType` values:

- `STOCK_4X85_TRAILING_DOC_TAB`.
- `STOCK_4X105_TRAILING_DOC_TAB`.

## German weight-handling icons

Labels automatically include 10+ kg or 20+ kg handling icons for:

- Inbound-to-Germany parcel and freight shipments.
- Domestic German parcel and freight shipments.

This applies to every automated label channel and replaces the former
manual-sticker workaround.

## Encoded trade-document images

The Trade Documents Upload API provides an Upload Encoded Image endpoint for
submitting encoded images.
