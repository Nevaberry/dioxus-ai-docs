# Location Search and Addressing

## Search filters and ordering

Location Finder queries can filter by `providerType`, `serviceType`, `locationType`, `hideClosedShops`, `radius`, and `limit`. Address and coordinate searches return the nearest locations in distance order. Use `providerType=parcel` for Post & Parcel results when Express locations must be excluded.

```text
/find-by-geo?latitude=50.7169763&longitude=7.1329916&providerType=parcel&serviceType=parcel%3Apick-up&radius=2500&limit=20
```

## Conjunctive services and meta-services

Repeated `serviceType` parameters form an AND condition. The query-only values `parcel:pick-up-all` and `parcel:drop-off-all` each match any service in their family and are not returned as service values.

In Germany, shops with `parcel:pick-up` and lockers with `parcel:pick-up-registered` require separate calls whose results are merged. As an alternative, `parcel:pick-up-all` can be combined with another requirement such as `handicapped-access`.

```text
?serviceType=parcel%3Apick-up-all&serviceType=handicapped-access
```

## Location types and locker flags

Returned `location.type` values are:

- `servicepoint`
- `postoffice`
- `postbank`
- `locker`
- `pobox`, a last-mile collection box
- `postbox`, a first-mile outgoing-mail box

A locker can have `leanLocker` for app-only operation without a keyboard or `dfLocker` for a gray DeinFach partner-network locker.

## Service identifiers

Parcel service filters distinguish:

- `parcel:pick-up`
- `parcel:pick-up-registered`, for Germany-only locker service
- `parcel:pick-up-unregistered`, for non-German European locker service
- `parcel:drop-off`
- `parcel:drop-off-unregistered`
- `parcel:drop-off-unlabeled`, for label-free drop-off

Express service filters distinguish:

- `express:pick-up`
- `express:drop-off`
- `express:drop-off-account`
- `express:drop-off-easy`
- `express:drop-off-prelabeled`
- `express:drop-off-unlabeled`

Other filterable facilities include `letter-service`, `postbank`, `cash-on-delivery`, `franking`, `cash-service`, `packaging-material`, `postident`, `age-verification`, `handicapped-access`, and `parking`.

## Operational response fields

Alongside name, address, geolocation, and airline `distance`, responses expose:

- `location.ids[]` with provider-specific IDs;
- `keyword` and `keywordId`;
- `serviceTypes`;
- `openingHours`;
- `closurePeriods`;
- `containedInPlace`.

Locker responses can include `availableCapacity`. German lockers can include average capacity by weekday when source data exists. Italian and Greek locations can include break hours.

## Road distance in Sweden

For `countryCode=SE`, `/find-by-address` and `/find-by-geo` can return `routingDistance` with car-based road distance in addition to ordinary airline distance. Prefer it when road proximity determines ranking or display.

## Eligibility for direct shipment addressing

The documented addressing schemes do not apply to DHL Express. A shipment may be sent only to a location with a designated Postfiliale number exposed as `keywordId`. Supply the recipient email address so the pickup notification can be delivered.

## German Packstation and Postfiliale

For a German locker, use `Packstation` as the street, its `keywordId` as the house number, and the recipient PostNumber as the second-name or additional-address line.

For a German shop, use `Postfiliale` and its `keywordId` in the same street and house-number positions. The PostNumber is optional.

```text
Max Sample                 Max Sample
987654321                  987654321  (optional)
Packstation 145            Postfiliale 502
53113 Bonn                 53113 Bonn
DE                         DE
```

## Other European locker and service-point addresses

For a European locker outside Germany, use the response's country-specific `keyword` as the street and `keywordId` as the house number.

For a staffed service point, put `<keyword> <keywordId>` in the additional-address line and retain the location's physical street and house number.

```text
Max Sample                 Max Sample
DHL Packstation NL-110151  DHL Parcelshop NL-110603
1101DZ Amsterdam           Holendrechtplein 14
NL                         1106LN Amsterdam
                           NL
```

## Migration from Location Search Europe

Location Search Europe is decommissioned. Map its fields to Unified v1 as follows:

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

`routingCode`, `district`, `area`, `additionalInfo`, `primaryKeyDeliverySystem`, and `systemID` have no Unified equivalent.
