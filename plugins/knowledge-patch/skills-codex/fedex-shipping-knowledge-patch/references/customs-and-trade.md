# Customs and Trade

## Commodity-level regulatory data

Ship accepts a `regulatoryDetails` array alongside customs declarations for
per-commodity compliance data such as CPSC certification. The related
Regulatory API can supply that data.

## Simplified commodity shipping in Europe

For goods already in free circulation between European countries, Simplified
Commodity Shipping permits a commodity description instead of the full
commodity details in the ship request.

## Encoded trade-document images

The Trade Documents Upload API provides an Upload Encoded Image endpoint for
submitting encoded images.

## Ireland postal codes

Merchant address data for Ireland must account for the announced Eircode
postal-code requirement rather than treating the postal code as optional.

## Canadian export reporting threshold

The Canadian-export announcement requires electronic reporting for goods
valued at CAD 2,000 or more. Customs workflows must not silently omit the
declaration at that threshold.
