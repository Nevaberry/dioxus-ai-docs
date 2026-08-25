# Discovery and locations

## eCommerce Americas Product Finder

Product Finder responses include:

- a `rate` object with `priceZone`, `amount`, `currency`, and `effectiveFrom`;
  and
- an `estimatedDeliveryDate` object with `calculate`, `deliveryBy`,
  `expectedShipDate`, and `expectedTransit`.

## Location Finder searches

### Search modes and distance bounds

Find locations by address, coordinates, location ID, or `keywordId`.
`/find-by-address` first resolves the address to coordinates and requires at
least three characters in total across `addressLocality`, `postalCode`, and
`streetAddress`.

The default radius is 5,000 metres and the maximum is 1,000,000 metres.
`/find-by-geo` also accepts an optional `countryCode` to filter results.

### Filters and ordering

Narrow results with `providerType`, `serviceType`, `locationType`,
`hideClosedShops`, `radius`, and `limit`. Address and coordinate searches
return nearest locations in distance order. Use `providerType=parcel` for Post
& Parcel results when Express locations must be excluded.

```text
/find-by-geo?latitude=50.7169763&longitude=7.1329916&providerType=parcel&serviceType=parcel%3Apick-up&radius=2500&limit=20
```

### AND filters and meta-services

Repeated `serviceType` parameters are an AND condition. The query-only
`parcel:pick-up-all` and `parcel:drop-off-all` each match any service in their
respective family; they are not returned as service values.

In Germany, shops with `parcel:pick-up` and lockers with
`parcel:pick-up-registered` require separate calls and merged results.
Alternatively, combine `parcel:pick-up-all` with another requirement such as
`handicapped-access`.

```text
?serviceType=parcel%3Apick-up-all&serviceType=handicapped-access
```

## Location and service identifiers

### Location types and locker flags

Returned `location.type` values are `servicepoint`, `postoffice`, `postbank`,
`locker`, `pobox`, and `postbox`. `pobox` is a last-mile collection box;
`postbox` is a first-mile outgoing-mail box.

A locker can carry `leanLocker` for app-only operation without a keyboard or
`dfLocker` for a gray DeinFach partner-network locker.

### Parcel services

Parcel filters distinguish:

- `parcel:pick-up`;
- Germany-only locker service `parcel:pick-up-registered`;
- non-German European locker service `parcel:pick-up-unregistered`;
- `parcel:drop-off`;
- `parcel:drop-off-unregistered`; and
- label-free `parcel:drop-off-unlabeled`.

### Express and facility services

Express filters distinguish `express:pick-up`, `express:drop-off`,
`express:drop-off-account`, `express:drop-off-easy`,
`express:drop-off-prelabeled`, and `express:drop-off-unlabeled`.

Other filterable facilities are `letter-service`, `postbank`,
`cash-on-delivery`, `franking`, `cash-service`, `packaging-material`,
`postident`, `age-verification`, `handicapped-access`, and `parking`.

## Operational response data

In addition to name, address, geolocation, and airline `distance`, responses
expose:

- `location.ids[]` with provider-specific IDs;
- `keyword` and `keywordId`;
- `serviceTypes`;
- `openingHours`;
- `closurePeriods`; and
- `containedInPlace`.

Locker responses can include `availableCapacity`. German lockers can also
include average capacity by weekday where source data exists. Italian and
Greek locations can include break hours.

For `countryCode=SE`, `/find-by-address` and `/find-by-geo` can return a
`routingDistance` object with car-based road distance in addition to ordinary
airline distance. Consumers should prefer it when road proximity determines
ranking or display.

## Addressing shipments to returned locations

### Eligibility

The documented addressing schemes do not apply to DHL Express. A shipment can
be sent only to a location with a designated Postfiliale number exposed as
`keywordId`. Supply the recipient's email address for pickup notification.

### German Packstation and Postfiliale

For a German locker, use `Packstation` as the street, its `keywordId` as the
house number, and the recipient's PostNumber in the second-name or
additional-address line.

For a German shop, use `Postfiliale` and its `keywordId` in the street and
house-number positions. The PostNumber is optional.

```text
Max Sample                 Max Sample
987654321                  987654321  (optional)
Packstation 145            Postfiliale 502
53113 Bonn                 53113 Bonn
DE                         DE
```

### Lockers and service points elsewhere in Europe

For a European locker outside Germany, use the response's country-specific
`keyword` as the street and `keywordId` as the house number.

For a staffed service point, put `<keyword> <keywordId>` in the
additional-address line and retain the location's physical street and house
number.

```text
Max Sample                 Max Sample
DHL Packstation NL-110151  DHL Parcelshop NL-110603
1101DZ Amsterdam           Holendrechtplein 14
NL                         1106LN Amsterdam
                           NL
```

## Migration from Location Search Europe

Location Search Europe is decommissioned. Map its response fields into Unified
v1 as follows:

```text
zipCode             -> postalCode
city                -> addressLocality
street + houseNo    -> streetAddress
keyWord             -> keyword
shopType            -> type
shopName            -> name
primaryKeyZipRegion -> keywordId
id                  -> locationId
psfServicetypes     -> serviceTypes
psfTimeinfos        -> openingHours
psfClosureperiods   -> closurePeriods
```

`routingCode`, `district`, `area`, `additionalInfo`,
`primaryKeyDeliverySystem`, and `systemID` have no Unified equivalent.

## MyDHL discovery resources

### Reference Data and service points

The MyDHL Reference Data resource supplies DHL Express reference datasets, so
enum lists do not have to be hard-coded.

Its Service Point operation finds Express pickup/drop-off points from a postal
address, service-point ID, or geocode. This is a MyDHL-specific contract and
should not be substituted for another DHL division's location API.

### Rates and account-dependent products

Rates can request quoted versus committed estimated delivery dates, expose
dependent or mutually exclusive services, and perform exact-match validation
of shipper and receiver postal addresses.

Product B (`BBX`) rates are available to onboarded customers. Verified
Delivery service `TF` appears on labels only when enabled by the shipper
account agreement.
