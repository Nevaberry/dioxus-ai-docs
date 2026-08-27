# Matkahuolto pickup points

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

Defaults are:

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

Other values return all types. Office types appearing in replies are `MHA`,
`MHM`, `MHT`, `MHN`, `MHE`, and `MHX`.

## Reply fields and formats

Each office reply supplies:

- sequence by distance;
- `Id`, type, name, and address;
- country;
- handling office;
- internal shop ID;
- distance; and
- optional latitude and longitude.

Set `ResponseType=CSV` for CSV. The supplied examples use semicolon-separated
fields and decimal commas.

## Errors

XML errors use `ErrorNbr` and `ErrorMsg`:

| `ErrorNbr` | Meaning |
| --- | --- |
| `1001` | Login failed |
| `1002` | Location missing |
| `1003` | Address not found |
| `1004` | Offices not found |
| `1005` | Unexpected error |
