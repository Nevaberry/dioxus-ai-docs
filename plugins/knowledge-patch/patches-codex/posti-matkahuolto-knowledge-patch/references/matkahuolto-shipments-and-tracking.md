# Matkahuolto shipments and tracking

## Shipment endpoint and envelope

Send `MHShipmentRequest` XML with `Content-Type: text/xml` to
`https://extservices.matkahuolto.fi/mpaketti/mhshipmentxml`. Use the
`extservicestest` host for testing. `UserId` is the supplied account number
without leading zeroes.

One request may contain multiple `Shipment` elements. Their labels are returned
in one PDF.

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

`ShipmentType` is `N` for normal/default, `A` for activated, or `R` for return.
`MessageType` is `N` for new, `C` for change, or `D` for delete. An empty
`ShipmentNumber` is allocated by the service. Dates use `DD.MM.YYYY`, counts
are integers, and decimal values require a dot.

## Required, routing, payer, and package fields

Mandatory shipment fields are:

- shipment type and message type;
- weight and package count;
- sender account;
- receiver name, postal code, and city; and
- product code.

A payer account must always be represented by `SenderId`, `ReceiverId`, or
`PayerId`. `PayerCode` is `S`, `R`, or `O`; `O` makes `PayerId` mandatory.

Pickup-point selection supplies `DestinationPlaceCode` and
`DestinationPlaceName`. Receiver language is `FI`, `SV`, or `EN`.

`Pickup` and `Delivery` default to `N`. Their payer fields accept `S` or `R`
and default to `S`. `PackageType` accepts `FIN`, `EUR`, `HP`, `RC`, or `SP`.

## Products, labels, and special handling

Product codes are:

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

`DocumentType=NO` suppresses a label. `10X15` returns a 100×150 mm label. The
default is A5.

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
history also assigns `SD` to same-day delivery, although the current code table
omits it.

## Parcel, customs, and dangerous-goods nesting

A shipment permits at most five `ShipmentRow` parcel records. If the caller
supplies `ShipmentNumber`, add one row for every `PackageId`. Each row may carry
dimensions, at most five customs `GoodsRow` records, and at most three
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
`SAMPLE`, or `GIFT`. `CustomsStatus` is `UNCLEARED`, `TRANSIT`, `CLEARANCE`, or
`CLEARED`.

Dangerous-goods rows contain:

- a four-digit `UNCode` without the `UN` prefix;
- description and technical name;
- ADR class, type, and package group;
- weight and volume in liters; and
- up to two subsidiary-risk classes.

## Fields removed in shipment XML 2.24

Do not send COD fields, shipment- or root-level ADR codes, or special-handover
fields. Dangerous-goods data belongs at parcel level in `DangerousGoodsRow`.

## Shipment replies

`MHShipmentReply` correlates each result with `ShipmentNumber` and
`SenderReference`. It includes `ActivationCode` for activated shipments and
carries the base64 PDF in `ShipmentPdf` with `PdfName`.

A successful delete is represented unusually as an error-form reply whose
`ErrorNbr` is `0`.

Errors may be top-level or nested under a shipment:

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

## Tracking request and format

GET `https://extservices.matkahuolto.fi/mpaketti/public/tracking` with HTTP Basic
authentication. The test host is `extservicestest.matkahuolto.fi`.

`ids` is a comma-separated list of at most ten shipment or parcel IDs. `from`
and `to` use date-time values such as `2018-01-11T11:47:30`. Supply IDs or
time-range input.

```http
GET /mpaketti/public/tracking?ids=MH302164795FI&from=2018-01-11T11:47:30&to=2018-01-11T13:47:30
Accept: application/json
```

XML is the default response. `Accept: application/json` selects JSON.

## Tracking event codes

| Code | Meaning |
| --- | --- |
| `02` | Advance notice |
| `08` | Picked up from sender |
| `10` | Received at departing parcel point |
| `12` | Consolidated |
| `15` | Received for carriage |
| `25` | Loaded for main transport |
| `35` | Received at destination terminal |
| `40` | Waiting for delivery loading |
| `41` | Waiting for parcel-point loading |
| `45` | Loaded for delivery |
| `46` | Loaded for parcel-point delivery |
| `47` | Delivered to parcel point |
| `48` | Received at parcel point |
| `50` | Ready for collection |
| `55` | First notification |
| `56` | Second notification |
| `57` | Manual notification |
| `60` | Handed to recipient |
| `61` | Handed to proxy |
| `62` | Handover cancelled |
| `65` | COD paid to sender |
| `70` | Returned uncollected |
| `97` | Unsuccessful delivery attempt |
| `104` | Deviation added |

## Tracking replies and errors

Each event contains `EventId`, shipment and parcel numbers, sender reference,
code, timestamp, place, office code, and remarks. `Signature` appears only for
codes `60` and `61`; `ReturnShipmentNumber` appears only for code `70`.

A valid query with no matching events returns an empty message rather than an
error.

Tracking errors combine HTTP status and application code:

| HTTP / code | Meaning |
| --- | --- |
| `400/10` | Missing parameter |
| `400/11` | Invalid date |
| `400/12` | More than ten IDs |
| `400/13` | Excessive time range |
| `401/50` | Authentication failure |
| `405/60` | Non-GET method |

XML error payloads use an `Error` group containing `EventId`, `ErrorCode`, and
`ErrorText`.
