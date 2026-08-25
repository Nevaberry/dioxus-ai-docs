# Matkahuolto Pickup Points and Interface Access

## Agreement and credentials

A valid agreement is required to use the open APIs, and free API credentials
are required for testing and implementation. Existing customers without
credentials must request them through the designated form. Customer IDs are
also requested through that form rather than technical-support email.

## Test-to-production behavior

The test environment returns correctly formatted responses but does not
process submitted consignments. Moving the integration to production only
requires changing the contact address.

## Pickup-point integration choices

Integrate pickup points through the real-time search API or periodically
download the pickup-point dataset, such as once daily, into the store's own
database.

## Search request

POST an `MHSearchOfficesRequest` to:

```text
https://extservices.matkahuolto.fi/noutopistehaku/public/v2/searchoffices
```

Use `Content-Type: application/xml` or `text/xml`. `Login` is the registered
customer number. An address search needs `PostalCode` or `City`; `Id` looks up
one known office directly.

```xml
<MHSearchOfficesRequest>
  <Login>1234567</Login>
  <Version>1.0</Version>
  <PostalCode>04300</PostalCode>
  <Country>FI</Country>
  <OfficeType>T</OfficeType>
  <ResponseType>XML</ResponseType>
  <MaxResults>5</MaxResults>
  <Coordinates>Y</Coordinates>
</MHSearchOfficesRequest>
```

The request defaults are:

| Field | Default |
| --- | --- |
| `Country` | `FI` |
| `ResponseType` | `XML` |
| `MaxResults` | `5` |
| `Coordinates` | `N` |

The legacy `/noutopistehaku/public/searchoffices` address runs the same search
but URL-encodes its response.

## Office filters

`OfficeType` accepts:

| Value | Meaning |
| --- | --- |
| `M` | Matkahuolto terminals and Parcel Points |
| `T` | All |
| `R` | R-Kiosks |
| `P` | Safe-delivery offices; agreement required |
| `A` | Parcel lockers |
| `N` | All except lockers |
| `U` | Exclude outdoor lockers |
| `LQ` | LQ-capable only |
| `MHA` | Terminals |
| `MHM` | Parcel Points |

Other values return all types. Reply office types are `MHA`, `MHM`, `MHT`,
`MHN`, `MHE`, and `MHX`.

## Search replies

Each office reply supplies:

- sequence by distance;
- `Id`;
- type;
- name and address;
- country;
- handling office;
- internal shop ID;
- distance;
- optional latitude and longitude.

Set `ResponseType=CSV` for CSV. The supplied examples use semicolon-separated
fields and decimal commas.

XML errors use `ErrorNbr` and `ErrorMsg`:

| Code | Meaning |
| --- | --- |
| `1001` | Login failed |
| `1002` | Location missing |
| `1003` | Address not found |
| `1004` | Offices not found |
| `1005` | Unexpected error |
