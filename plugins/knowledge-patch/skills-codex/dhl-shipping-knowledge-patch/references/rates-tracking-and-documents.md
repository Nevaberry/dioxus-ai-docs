# Rates, Tracking, Images, and Reference Data

## eCommerce Americas Product Finder

Product Finder responses include:

- a `rate` object with `priceZone`, `amount`, `currency`, and `effectiveFrom`;
- an `estimatedDeliveryDate` object with `calculate`, `deliveryBy`, `expectedShipDate`, and `expectedTransit`.

## MyDHL account-scoped pickup cutoffs

MyDHL v3.3.0 makes pickup validation in Shipment, Create Pickup, and Update Pickup depend on the shipper account number's cutoff time. Rates returns pickup capabilities according to that account-specific cutoff. Do not infer cutoff behavior only from origin or a generic schedule.

## Reference validation and datasets

In v3.3, export line-item descriptions must contain at least one character. Shipment- and package-level customer-reference types are validated against CI Mask reference data.

The `customerShipmentReferenceType` dataset indicates whether multiple references are allowed. The `country` dataset includes both ISO currency code and currency name.

## Invoice scale and payer-account lookup

MyDHL v3.2 supports up to 100 `exportDeclaration` invoices. Get Image can retrieve uploaded images with payer account number as a request parameter. Tracking can find a shipment by shipment reference when given the payer account number.

## Rates response details

Rates can return inbound and outbound sort codes. It can request quoted versus committed estimated delivery dates, expose dependent or mutually exclusive services, and perform exact-match validation of shipper and receiver postal addresses.

Product B (`BBX`) rates are available to onboarded customers. Verified Delivery service `TF` appears on labels only when enabled by the shipper account agreement.

## Versioned cutoff response field

Versioned Shipment and Rates responses introduced `pickupCutoffSameDayOutboundProcessing` through `x-version` as the replacement for legacy `GMTCutoffTime`. Consumers should migrate field handling rather than treating both names as unrelated cutoff values.

## Tracking detail controls

Tracking can return:

- remarks at shipment and piece level;
- GMT offsets for events and checkpoints;
- the `all-check-with-remarks` tracking view together with requested controlled-access data codes.

Protected tracking data is masked and subject to authorization.

## Document-image types and eligibility

Get Image supports:

- DHL-issued proforma invoices as `DPF`;
- transport-accompanying documents as `TAS`;
- generic-entry-summary documents as `GES`;
- customs documents with either Export or Import function type.

Waybill, commercial-invoice, and customs-entry images are available. A Customs Entry Document request requires the requester to be the Exporter of Record.

## Invoice upload and caller-supplied totals

Upload invoice data before shipment creation through Invoice, or for an existing shipment through Shipment.

When all of `preCalculatedTotalGoodsValue`, `preCalculatedTotalInvoiceValue`, `preCalculatedLineItemTotalValue`, and `totalWithImportDutiesAndTaxes` are supplied, DHL uses them instead of automatically calculating invoice totals.
