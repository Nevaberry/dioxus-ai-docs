# Addresses

## Verification controls on creation

On `POST /v2/addresses`, the presence of `verify` or `verify_strict` triggers
delivery and ZIP verification even when its value is `false`. Omit both keys
to avoid verification.

`verify` returns the Address with per-check results. `verify_strict` takes
precedence and returns an error for an unverified address, although
correctable addresses are corrected and returned.

```json
{
  "address": {
    "street1": "417 Montgomery St",
    "city": "San Francisco",
    "state": "CA",
    "zip": "94104",
    "country": "US"
  },
  "verify_strict": true
}
```

## Carrier verification services

Set `verify_carrier` to `ups` or `fedex` alongside `verify` or
`verify_strict` to use that carrier's Address Verification Service instead of
standard EasyPost verification. The response's `verifications` object
includes a `verify_carrier` key naming the service used.

```json
{"verify": true, "verify_carrier": "fedex"}
```

## Verifying an existing Address

Verify an immutable existing Address with
`GET /v2/addresses/:id/verify`. The response wraps a normalized replacement in
`address`. Its `verifications.zip4` and `verifications.delivery` entries
contain `success`, field errors, and details. Delivery details can include
latitude, longitude, and an IANA time zone.

## Address-line normalization

For US and Canadian addresses, verification can move a recognized trailing
unit from `street1` into an empty `street2` when `street1` exceeds 35
characters.

Since August 25, 2025, street-name abbreviation occurs only for USPS
verification and only when the validated `street1` exceeds 40 characters.
