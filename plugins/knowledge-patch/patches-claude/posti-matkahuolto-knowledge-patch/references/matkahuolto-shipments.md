# Matkahuolto Shipments, Labels, and EDI

## XML label requests

Submit XML requests with HTTP POST over HTTPS; the server rejects unencrypted
HTTP. A successful request returns an XML response containing both the reply
and an address-label PDF to print and attach to the consignment. The request
format includes optional fields.

## Shipment EDI formats and notification contacts

Shipment information can be sent through an API call or file transfer. EDI
messages are accepted in XML or CSV and include sender and recipient details.
The recipient's mobile number or email address is required when needed for
arrival notifications.

## Shipment request and operations

Send `MHShipmentRequest` XML with `Content-Type: text/xml` to:

```text
https://extservices.matkahuolto.fi/mpaketti/mhshipmentxml
```

Use the `extservicestest` host for testing. `UserId` is the supplied account
number without leading zeroes. One request may contain multiple `Shipment`
elements, whose labels are returned in one PDF.

```xml
<MHShipmentRequest>
  <UserId>9430023</UserId>
  <Password>456</Password>
  <Version>2.0</Version>
  <Shipment>
    <ShipmentType>N</ShipmentType>
    <MessageType>N</MessageType>
    <Weight>1.23</Weight>
    <Packages>1</Packages>
    <SenderId>9430023</SenderId>
    <ReceiverName1>Receiver</ReceiverName1>
    <ReceiverPostal>33100</ReceiverPostal>
    <ReceiverCity>TAMPERE</ReceiverCity>
    <ProductCode>80</ProductCode>
  </Shipment>
</MHShipmentRequest>
```

`ShipmentType` is `N` for normal/default, `A` for activated, or `R` for
return. `MessageType` is `N` for new, `C` for change, or `D` for delete. An
empty `ShipmentNumber` is allocated by the service. Dates use `DD.MM.YYYY`,
counts are integers, and decimal values require a dot.

## Mandatory fields and payer routing

The mandatory shipment fields are:

- shipment type and message type;
- weight and package count;
- sender account;
- receiver name, postal code, and city;
- product code.

A payer account must always be represented by `SenderId`, `ReceiverId`, or
`PayerId`. `PayerCode` is `S`, `R`, or `O`; `O` makes `PayerId` mandatory.

Pickup-point selection feeds `DestinationPlaceCode` and
`DestinationPlaceName`. Receiver language is `FI`, `SV`, or `EN`.

`Pickup` and `Delivery` default to `N`. Their payer fields accept `S` or `R`
and default to `S`. `PackageType` accepts `FIN`, `EUR`, `HP`, `RC`, or `SP`.

## Product codes

| Code | Product |
| --- | --- |
| `30` | Jakopaketti |
| `34` | Kotijakelu |
| `37` | XXS-luukkujakelu |
| `57` | Lavarahti |
| `58` | Rahti |
| `80` | Lähellä-paketti |
| `81` | Asiakaspalautus |
| `84` | XXS |
| `91` | Ulkomaan Asiakaspalautus |
| `95` | Ulkomaan Lähellä-paketti |
| `96` | Ulkomaan Jakopaketti |
| `97` | Ulkomaan Kotijakelu |

## Label formats

`DocumentType=NO` suppresses a label. `10X15` returns a 100×150 mm label. The
default is A5.

## Special handling

Comma-separate multiple `SpecialHandling` values:

| Code | Meaning |
| --- | --- |
| `K02` | Large |
| `K04` | Handle with care |
| `K06` | Delivery without signature |
| `HL` | Hand over in person |
| `SP1` | Postpone timeout return seven days |
| `VA` | Dangerous goods with `DangerousGoodsRow` |
| `LQ` | Limited quantity |
| `SET` | Pre-delivery call |

`E01` is the old ADR code and should be replaced by `VA` or `LQ`. The version
history also assigns `SD` to same-day delivery although the current code table
omits it.

## Parcel, customs, and dangerous-goods nesting

A shipment permits at most five `ShipmentRow` parcel records. If the caller
supplies `ShipmentNumber`, add one row for every `PackageId`. Each row may
carry dimensions, at most five customs `GoodsRow` records, and at most three
`DangerousGoodsRow` records.

```xml
<ShipmentRow>
  <PackageId>MA0183085940000000001</PackageId>
  <GoodsRow>
    <GoodsDescription>Goods 1</GoodsDescription>
    <Quantity>1</Quantity>
    <CustomsValue>15.00</CustomsValue>
    <NetWeight>2.65</NetWeight>
    <CountryOfOrigin>FI</CountryOfOrigin>
    <CommodityCode>1122334455</CommodityCode>
  </GoodsRow>
</ShipmentRow>
```

Customs values use `CurrencyCode`. `CustomsType` is `COMMODITY`, `DOCUMENT`,
`SAMPLE`, or `GIFT`; `CustomsStatus` is `UNCLEARED`, `TRANSIT`, `CLEARANCE`, or
`CLEARED`.

Dangerous-goods rows carry:

- a four-digit `UNCode` without the `UN` prefix;
- description and technical name;
- ADR class, type, and package group;
- weight;
- volume in liters;
- up to two subsidiary-risk classes.

## Version 2.24 removals

Do not send COD fields, shipment/root-level ADR codes, or special-handover
fields; version 2.24 removes them. Dangerous-goods data belongs at parcel
level in `DangerousGoodsRow`.

## Shipment replies

`MHShipmentReply` correlates each result with `ShipmentNumber` and
`SenderReference`. It includes `ActivationCode` for activated shipments and
carries the base64 PDF in `ShipmentPdf` with `PdfName`.

A successful delete is unusually represented as an error-form reply with
`ErrorNbr` equal to `0`.

## Shipment errors

Errors may be top-level or nested under a shipment.

| Code | Meaning |
| --- | --- |
| `1001` | Login |
| `1002` | User ID |
| `1003` | Mandatory data |
| `1004` | Request |
| `1005` | System |
| `1006` | Weight |
| `1007`, `1016` | Parcel count |
| `1008` | Shipment number |
| `1009` | Parcel number |
| `1010` | Shipment type |
| `1011` | Message type |
| `1012` | Product |
| `1013` | Destination |
| `1014` | Volume |
| `1015` | COD sum |
| `1017` | COD/product |
| `1018` | Decimal separator |
| `1019` | Product/cash payer |
| `1020` | COD/pickup point |
| `1021` | Additional service/product |
| `1022` | Customs already defined |
| `1023` | Invalid `UNCode` |
| `1024` | Too many dangerous-goods rows |
