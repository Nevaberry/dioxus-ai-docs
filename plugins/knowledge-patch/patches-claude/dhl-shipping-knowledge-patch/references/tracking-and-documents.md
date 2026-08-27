# Tracking and documents

## eCommerce Americas tracking

Every object in the Tracking response `events` collection can include
`postalCode` and `country`. Consumers should preserve both fields when
displaying or processing an event's location.

## MyDHL tracking

### Account-assisted lookup

Tracking can find a shipment by shipment reference when the payer account
number is supplied.

### Detail controls and protected data

Tracking can return:

- remarks at shipment and piece level;
- GMT offsets for events and checkpoints; and
- the `all-check-with-remarks` tracking view together with requested
  controlled-access data codes.

Protected tracking data is masked and subject to authorization.

### Versioned pickup-cutoff field

Versioned Shipment and Rates responses introduced
`pickupCutoffSameDayOutboundProcessing` through `x-version` as the replacement
for legacy `GMTCutoffTime`. Consumers should migrate field handling rather
than treating the two names as unrelated cutoff values.

## MyDHL images and invoices

### Payer-account image lookup

Get Image can retrieve uploaded images with payer account number as a request
parameter.

### Supported document images

Get Image supports:

- DHL-issued proforma invoices as `DPF`;
- transport-accompanying documents as `TAS`;
- generic-entry-summary documents as `GES`; and
- customs documents with either Export or Import function type.

Waybill, commercial-invoice, and customs-entry images are available. A Customs
Entry Document request requires the requester to be the Exporter of Record.

### Invoice upload timing and scale

Invoice data can be uploaded before shipment creation through Invoice, or for
an existing shipment through Shipment. Version 3.2 supports as many as 100
`exportDeclaration` invoices.

### Caller-supplied invoice totals

When `preCalculatedTotalGoodsValue`, `preCalculatedTotalInvoiceValue`,
`preCalculatedLineItemTotalValue`, and `totalWithImportDutiesAndTaxes` are all
supplied, DHL uses them instead of automatically calculating invoice totals.

### Customer roles and piece-to-label linkage

Shipment and Invoice support Broker, Ultimate Consignee, and
`manufacturerDetails` customer roles.

Request `linkLabelsByPieces` under `getAdditionalInformation.typeCode` to add
fields that associate each piece reference with its transport-label or
waybill image.

## Parcel Germany document retrieval

`GET /orders` retrieves documents. `GET /labels` follows the label URL
returned by `POST /orders`; `GET /manifests` retrieves manifests.

The `/labels` URL works until manifesting. If the label was initially
downloaded, its cached label remains available for 48 hours, after which the
URL returns HTTP `500`. `GET /orders` with the shipment number can retrieve the
label for up to three days after manifesting.

The API cannot return label information in place of an actual label, although
the response also exposes generated printed attributes such as shipment
number and routing code.
