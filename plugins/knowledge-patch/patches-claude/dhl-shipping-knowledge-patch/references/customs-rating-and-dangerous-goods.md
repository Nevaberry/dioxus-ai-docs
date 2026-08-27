# Customs, rating, and dangerous goods

## eCommerce Americas international rules

### DHL Parcel International Expedited

International product code `PLX` identifies DHL Parcel International
Expedited. Apply its regulations and content-category rules explicitly. PLX
does not support dangerous-goods shipments.

### International label fields

International Shipping Label requests support an `additionalPartyAddress`
object and an `itemReferences` object inside `customsDetails`. Item reference
values should use the published Item Reference Type Codes.

### Domestic customs details

Domestic Label requests accept the `customsDetails` array only for APO, FPO,
DPO, and non-continental US destinations. It should be omitted for other
domestic shipments.

### Paperless Trade geography

For Paperless Trade dangerous-goods content categories `01`–`06` and `40`,
the geographic restriction is Canada and Mexico only, rather than Canada
only. Eligibility checks must include Mexico and continue to reject other
destinations.

## MyDHL export declarations and reference data

### Manufacturer identifiers

In version 3.3.1, Shipment and Invoice export-declaration line-item references
accept:

- `SRV` for a standardized manufacturer product ID; and
- `MF` for a non-standardized manufacturer product ID.

### Description, reference, and country datasets

In version 3.3, export line-item descriptions must contain at least one
character. Shipment- and package-level customer-reference types are validated
against CI Mask reference data.

The `customerShipmentReferenceType` dataset indicates whether multiple
references are allowed. The `country` dataset contains both ISO currency code
and currency name.

### Customs-document codes

| Since | Codes and scope |
|---|---|
| 3.2.1 | `BLI` (Broker License), `ICD` (Internal Customs Document), `EAD` (Export Accompanying Document), and `ETD` (Export Transit Document) at export-declaration and line-item level for Create Shipment and Upload Invoice |
| 3.1.1 | `OEI`, `RGR`, `CHA`, and `CP2` for Shipment; `OEI` also for Invoice |
| 3.0.1 | `ORD` at declaration and line-item level |

### Customs-reference codes

| Since | Codes and scope |
|---|---|
| 3.2.1 | Line-item reference `CLN` |
| 3.1.1 | Line-item references `AEI`, `EXN`, `AFK`, `AEA`, and `PTA`; declaration-level `PTA` |
| 3.0.1 | Declaration references `TAR`, `TCO`, and `PX`; line-item references `ARN`, `OP`, `OSC`, `TAR`, and `TCO` |

### Country-specific registrations and references

Schema additions include registration types `FII`, `PEP`, Mexico's `FTN`,
and Taiwan's `EIC`. Brazil manifest mapping represents a shipper registration
number as `CNP`.

Egypt's ACID number uses shipment reference type `AFM` and can appear on the
waybill and commercial invoice. Registration types `MID`, `DLI`, `GST`, and
`SUB` were removed from the documentation.

## MyDHL invoice and landed-cost rules

### Invoice scale and item weights

Version 3.2 supports up to 100 `exportDeclaration` invoices. An
export-declaration line item needs either gross or net weight, rather than
both.

### Landed Cost

Landed Cost requires manufacturer country at line-item level. It can return
the item-level tariff rate type `preferential_rate`.

Rates and transit promises are indicative, can differ from the tendered
shipment, and may omit duties, taxes, customs charges, surcharges, or fees.
Landed Cost also requires an item catalogue with customs data such as HS codes
and supplied values such as freight and insurance.

### Caller-supplied totals

When all four of the following are supplied, DHL uses them rather than
auto-calculating invoice totals:

- `preCalculatedTotalGoodsValue`;
- `preCalculatedTotalInvoiceValue`;
- `preCalculatedLineItemTotalValue`; and
- `totalWithImportDutiesAndTaxes`.

## MyDHL declarability and value rules

Declarable non-document shipments require `exportDeclaration`. For
non-declarable shipments, currency code and incoterm are optional.

Shipment data can be validated without creating a label. Monetary, weight,
duty, tax, and additional-charge values must be positive.

## MyDHL dangerous goods

For dangerous goods `HH` and content ID `E01`, `UNCode` is optional. Excepted
Quantities (`HH`) can carry multiple UN codes.

A shipment can carry multiple MRN values under
`content/exportDeclaration/invoice/customerReferences`.

Shipment creation also supports dangerous-goods declaration package counts
and custom dangerous-goods descriptions up to 1,000 characters.

## MyDHL rating and account rules

Since version 3.3.0, pickup validation in Shipment, Create Pickup, and Update
Pickup uses the shipper account number's cutoff. Rates returns pickup
capabilities using the same account-specific cutoff, so cutoff behavior must
not be inferred only from origin or a generic schedule.

Rates can request quoted versus committed estimated delivery dates, expose
dependent or mutually exclusive services, and exactly validate shipper and
receiver postal addresses. Product B (`BBX`) rates are available to onboarded
customers. Verified Delivery service `TF` is shown on labels only when the
shipper account agreement enables it.

## Parcel Germany customs and payment

### Customs by destination

Customs data is required per parcel for international destinations outside the
applicable customs union. UK postcodes beginning `BT` are treated as Northern
Ireland/EU and require no customs data.

### Goods, currencies, and references

DHL Europaket `V54EPAK` allows only one `hsCode` goods category per parcel.
Shipping-cost and item currencies must match. If shipping-cost currency is
omitted, it defaults to EUR.

Requests allow an optional MRN, up to 99 goods items, and
`shipperCustomsRef` and `consigneeCustomsRef` identifiers.

### Cash on delivery

Cash on delivery requires EUR. Depending on portal permissions, bank details
may need to be stored in the portal and selected with `AccountReference`.
