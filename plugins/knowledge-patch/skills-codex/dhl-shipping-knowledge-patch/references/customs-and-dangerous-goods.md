# Customs and Dangerous Goods

## eCommerce Americas

### DHL Parcel International Expedited

International product code `PLX` identifies DHL Parcel International Expedited. Apply its regulations and content-category rules explicitly. PLX does not support dangerous-goods shipments.

### Paperless Trade geography

For Paperless Trade dangerous-goods content categories `01`–`06` and `40`, the geographic restriction is Canada and Mexico only, rather than Canada only. Eligibility checks must include Mexico and continue to reject other destinations.

## MyDHL quotes and landed cost

Rates and transit promises are indicative and can differ from the tendered shipment. They may omit duties, taxes, customs charges, surcharges, or fees.

Product and Rating data must not be stored, modified, or disclosed to third parties without prior written consent. Landed Cost requires an item catalogue with customs data such as HS codes, plus supplied values such as freight and insurance.

Landed Cost enforces manufacturer country at line-item level and can return item-level tariff rate type `preferential_rate`.

## Manufacturer identifiers

In MyDHL v3.3.1, Shipment and Invoice export-declaration line-item references accept:

- `SRV` for a standardized manufacturer product ID;
- `MF` for a non-standardized manufacturer product ID.

## Customs document codes

At export-declaration and line-item level for Create Shipment and Upload Invoice:

- v3.2.1 adds `BLI` (Broker License), `ICD` (Internal Customs Document), `EAD` (Export Accompanying Document), and `ETD` (Export Transit Document).
- v3.0.1 adds `ORD` at both declaration levels.

For Shipment, v3.1.1 adds `OEI`, `RGR`, `CHA`, and `CP2`; Invoice also supports `OEI`.

## Customs reference codes

- v3.2.1 adds line-item reference `CLN`.
- v3.1.1 adds line-item references `AEI`, `EXN`, `AFK`, `AEA`, and `PTA`, plus declaration-level `PTA`.
- v3.0.1 adds declaration references `TAR`, `TCO`, and `PX`, and line-item references `ARN`, `OP`, `OSC`, `TAR`, and `TCO`.

## Country-specific registrations and references

Current MyDHL schema additions include registration types `FII`, `PEP`, Mexico's `FTN`, Taiwan's `EIC`, and Brazil manifest mapping of a shipper registration number as `CNP`.

Egypt's ACID number uses shipment reference type `AFM` and can render on the waybill and commercial invoice. Registration types `MID`, `DLI`, `GST`, and `SUB` were removed from the documentation.

## Dangerous-goods identifiers

For dangerous goods `HH` and content ID `E01`, `UNCode` is optional. Excepted Quantities (`HH`) can carry multiple UN codes. A shipment can carry multiple MRN values under `content/exportDeclaration/invoice/customerReferences`.

## Parcel Germany customs rules

Customs data is required per parcel for international destinations outside the applicable customs union. UK postcodes beginning `BT` are treated as Northern Ireland/EU and require no customs data.

DHL Europaket `V54EPAK` allows only one `hsCode` goods category per parcel. Shipping-cost and item currencies must match; if shipping-cost currency is omitted, it defaults to EUR.

Current requests allow an optional MRN, up to 99 goods items, and `shipperCustomsRef` and `consigneeCustomsRef` identifiers.
