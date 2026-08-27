# Shipment, labels, and manifests

## eCommerce Americas

### Product-scoped closeout

The Manifest request accepts an optional `products` field for closing out
packages by product. Use it when closeout must be limited or grouped by the
selected products.

### Consignee delivery instructions

Label requests can put optional `deliveryInstructions` in
`consigneeAddress`. This keeps last-mile guidance with the consignee address
rather than treating it as an unrelated shipment note.

## MyDHL shipment creation and pickup

### Shipment behavior

In version 3.3, Shipment creation supports:

- a fallback for label-free shipments where label-free service is unavailable;
- dangerous-goods declaration package counts;
- custom dangerous-goods descriptions up to 1,000 characters;
- `shipperDetails` on courier requests for the manifest's shipper role; and
- up to 100 customer references of type `CU` printed in notification emails.

### Packaging, pieces, and dimensions

For DHL Express standardized packaging, provide the package type code so
Rating and Shipment can populate and omit dimensions. An export-declaration
line item needs either gross or net weight, not both.

`addPiece` can extend a shipment only before DHL has picked it up or recorded
a scan. Package dimensions must be positive and greater than `0.001`.

### Pickup instructions and account cutoff

A shipment pickup request supports three additional pickup instructions, each
at most 80 characters. Since version 3.3.0, pickup validation in Shipment,
Create Pickup, and Update Pickup depends on the shipper account number's cutoff
time. Rates also returns pickup capabilities according to that account-specific
cutoff. Cutoff behavior must not be inferred only from origin or a generic
schedule.

Rates can return inbound and outbound sort codes.

### Customer roles and piece-to-label linkage

Shipment and Invoice support Broker, Ultimate Consignee, and
`manufacturerDetails` customer roles.

Request `linkLabelsByPieces` under `getAdditionalInformation.typeCode` to add
the fields that associate each piece reference with its transport-label or
waybill image.

## Parcel Germany shipment inputs

### Parcel and measurement invariants

Each physical parcel is one shipment. Multipackage shipments are unsupported;
`costCenter` values such as `1/2` and `2/2` can visually relate separate
labels.

Weight is mandatory in grams or kilograms. Dimensions are optional, but unit,
length, width, and height must all be supplied together. Omit a missing
consignee phone or email, or send it as `null`; do not send whitespace.

### Packstation, supplements, and encoding

Identify a Packstation address with `lockerID`. Address-supplement fields
generally do not print, except on some country-specific international labels.

A warning response does not invalidate an accompanying label. An unencodable
street can incur a surcharge and produce a routing code ending in six or more
zeros. Set `mustEncode=true` when label creation must require an encodable
address.

## Parcel Germany manifest and edit lifecycle

Created shipments remain editable only until their data is manifested to DHL.
Cancel with `DELETE /orders` and recreate with `POST /orders`; manifested
shipments cannot be changed.

International parcels must be manifested before physical handoff. Trigger
closeout with `POST /manifests` for a selected `billingNumber`, or leave it to
the configured daily run, normally 17:45. DHL Paket International has an
additional 20:45 run for shipments created after the regular run.

## Parcel Germany label retrieval and rendering

### Retrieval lifetime

The `/labels` URL works until manifesting. If the label was initially
downloaded, its cached copy remains available for 48 hours; after that the URL
returns HTTP `500`.

As the longer fallback, call `GET /orders` with the shipment number. It can
retrieve the label for up to three days after manifesting.

### Formats and rendering rules

Do not scale labels. Thermal formats assume 203 dpi. Supported standard values
are:

- `A4`;
- `910-300-700` and `910-300-700-oz`;
- `910-300-710`;
- `910-300-600` and `910-300-610`;
- `910-300-400` and `910-300-410`; and
- `910-300-300` and `910-300-300-oz`.

PDF is the default implementation. Common Label requires separate DHL
approval. The 100 x 70 mm format is restricted to DHL Kleinpaket and Warenpost
International; because of its size, it omits some sender or recipient name
lines.

### Portal defaults and per-shipment controls

Portal settings provide defaults. `printFormat`, `retourePrintFormat`, and
`combine` override them for one shipment. In v2.1.14, `printDhlLogo` and
`printDhlLogoRetoure` do the same; omission falls back to portal settings.

The API cannot return label information instead of an actual label. Its
response also exposes generated printed attributes such as shipment number and
routing code.

## Parcel Germany shipper references

`shipperRef` addresses are configured in the Business Customer Portal. An
unknown reference returns HTTP `400`.

In v2.1.14, a reference and an individual shipper can be supplied together. A
logo-only reference adds its logo. With PAN data, the reference is recorded as
regulator and the individual shipper as depositor; the depositor address
controls both the label and the undeliverable-return destination.

## Parcel Germany products, services, and returns

### Kleinpaket and Premium

DHL Kleinpaket replaced Warenpost on January 1, 2025.
`Consignee.ContactAddress.country` is mandatory for Kleinpaket as an ISO
3166-1 alpha-3 code; it no longer defaults to `DEU`.

Requested `premium=false` can still become Premium when a destination has no
Economy product, as in most EU countries. Switzerland offers both.

### Returns and cash on delivery

Shipping v2 can create an enclosed national return label with the outbound
shipment. International returns require the separate Parcel DE Returns API.

Cash on delivery requires EUR. Depending on portal permissions, bank details
may need to be stored in the portal and selected with `AccountReference`.

## Parcel Germany response additions

Responses include `status` with the same value as `statusCode`. Shipment
creation can return recipient and return routing codes and `returnShipmentNo`
for a booked return. v2.1.14 adds a shipment UUID for stable identification
during maintenance.

## GoGreen label changes

GoGreen ends on August 31, 2026, and its logo must be removed by that date.
The existing GoGreen Plus logo must be removed by September 27, 2026. A new
GoGreen Plus claim is optional. The service remains available for national
outbound and return shipments.
