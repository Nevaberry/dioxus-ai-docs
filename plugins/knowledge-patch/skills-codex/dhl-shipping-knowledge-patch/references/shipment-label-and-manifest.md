# Shipment, Label, and Manifest Lifecycle

## eCommerce Americas request and response fields

### International labels

International Shipping Label requests support `additionalPartyAddress` and `itemReferences` inside `customsDetails`. Item reference values should use the published Item Reference Type Codes.

### Restricted domestic customs details

Domestic Label requests accept the `customsDetails` array only for APO, FPO, DPO, and non-continental US destinations. Omit it for other domestic shipments.

### Product-scoped closeout

The Manifest request accepts optional `products` to close out packages by product. Use it when closeout must be limited or grouped by selected products.

### Delivery and tracking locations

Label requests can put optional `deliveryInstructions` in `consigneeAddress`, carrying last-mile guidance with the consignee address rather than as an unrelated shipment note.

Each Tracking response `events` object can include `postalCode` and `country`. Preserve these fields when displaying or processing event location.

## MyDHL shipment behavior

### Shipment and invoice additions

Shipment creation supports:

- a fallback for label-free shipments where label-free service is unavailable;
- dangerous-goods declaration package counts;
- custom dangerous-goods descriptions of up to 1,000 characters.

Courier requests can carry `shipperDetails` for the manifest's shipper role. Notification emails can print up to 100 customer references of type `CU`.

### Standard packaging and Add Piece

For DHL Express standardized packaging, providing the package type code lets Rating and Shipment omit dimensions because the code populates them. An export-declaration line item needs either gross or net weight, not both. `addPiece` can extend a shipment only before DHL has picked it up or recorded a scan.

### Dimensions and pickup instructions

Package dimensions must be positive and greater than `0.001`. A shipment pickup request supports three additional pickup instructions, each no more than 80 characters.

### Validation without label creation

Declarable non-document shipments require `exportDeclaration`. For non-declarable shipments, currency code and incoterm are optional. Shipment data can be validated without creating a label. Monetary, weight, duty, tax, and additional-charge values must be positive.

### Customer roles and label linkage

Shipment and Invoice support Broker, Ultimate Consignee, and `manufacturerDetails` customer roles. Request `linkLabelsByPieces` under `getAdditionalInformation.typeCode` to add the fields that associate each piece reference with its transport-label or waybill image.

## Parcel Germany shipment input

### Parcel and field invariants

Each physical parcel is one shipment; multipackage shipments are unsupported. `costCenter` values such as `1/2` and `2/2` can visually relate separate labels.

Weight is mandatory in grams or kilograms. Dimensions are optional, but unit, length, width, and height must all be supplied together. Missing consignee phone or email must be omitted or sent as `null`, not whitespace.

### Address encoding and warnings

A Packstation address is identified with `lockerID`. Address-supplement fields generally do not print, except on some country-specific international labels.

Warnings do not invalidate an accompanying label. An unencodable street can incur a surcharge and produce a routing code ending in six or more zeros. Set `mustEncode=true` when label creation must require an encodable address.

## Parcel Germany manifest and edit lifecycle

Created shipments remain editable only until their data is manifested to DHL. Cancel with `DELETE /orders` and recreate with `POST /orders`; manifested shipments cannot be changed.

International parcels must be manifested before physical handoff. Trigger closeout with `POST /manifests` for a selected `billingNumber`, or leave it to the configured daily run, normally 17:45. An additional DHL Paket International run occurs at 20:45 for shipments created after the regular run.

## Label retrieval lifetime

The `/labels` URL works until manifesting. If the label was initially downloaded, its cached copy remains available for 48 hours after manifesting; after that, the URL returns HTTP `500`.

As the longer fallback, `GET /orders` with the shipment number can retrieve the label for up to three days after manifesting.

## Label formats and rendering

Do not scale labels. Thermal formats assume 203 dpi. Supported standard values are:

- `A4`
- `910-300-700`
- `910-300-700-oz`
- `910-300-710`
- `910-300-600`
- `910-300-610`
- `910-300-400`
- `910-300-410`
- `910-300-300`
- `910-300-300-oz`

PDF is the default implementation. Common Label requires separate DHL approval. The 100 x 70 mm format is restricted to DHL Kleinpaket and Warenpost International and omits some sender or recipient name lines because of its size.

## Portal defaults and print controls

Portal settings provide defaults. Request fields `printFormat`, `retourePrintFormat`, and `combine` override them for one shipment. v2.1.14 also adds `printDhlLogo` and `printDhlLogoRetoure`; omission falls back to portal settings.

The API cannot return label information in place of an actual label, although its response exposes generated printed attributes such as shipment number and routing code.

## Shipper references in v2.1.14

`shipperRef` addresses are configured in the Business Customer Portal. An unknown reference returns HTTP `400`.

A reference and an individual shipper can be supplied together. A logo-only reference adds its logo. PAN data records the reference as regulator and the individual shipper as depositor; the depositor address controls the label and undeliverable-return destination.

## Product behavior

DHL Kleinpaket replaced Warenpost on January 1, 2025. `Consignee.ContactAddress.country` is mandatory for Kleinpaket as an ISO 3166-1 alpha-3 code rather than defaulting to `DEU`.

A requested `premium=false` can still become Premium when the destination has no Economy product, as in most EU countries. Switzerland offers both.

## Returns and cash on delivery

Shipping v2 can create an enclosed national return label with the outbound shipment. International returns require the separate Parcel DE Returns API.

Cash on delivery requires EUR. Depending on portal permissions, bank details may need to be stored in the portal and selected with `AccountReference`.

## Response and schema changes

Responses include `status` with the same value as `statusCode`. Shipment creation can return recipient and return routing codes plus `returnShipmentNo` for a booked return. v2.1.14 adds a shipment UUID for stable identification during maintenance.

The version check does not disclose patch-level updates. `officeOfOrigin` is deprecated. Follow the corrected `GET /labels`, `GET /manifests`, `shippingConditions`, and `product` schemas.

## GoGreen deadlines

GoGreen ends on August 31, 2026, and its logo must be removed by that date. The existing GoGreen Plus logo must be removed by September 27, 2026. A new GoGreen Plus claim is optional, while the service remains available for national outbound and return shipments.
