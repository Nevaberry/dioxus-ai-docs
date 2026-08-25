# Rating and pickup

## Hold at Location acceptance filtering

Locations Search accepts optional shipment details in addition to weight and
dimensions when finding a Hold at Location site:

- Total Customs Value.
- Declared Value.
- Package Type.
- Package Count.
- Special Handling.
- Duties and Taxes payor data.

Weight and dimensions alone still work. However, incomplete pre-validation
can select a site that refuses the package or cause a Ship API error.

## One Rate result selection

Optional `rateDisplayOption` accepts:

- `LOWER_RATE`.
- `SELECTED_RATES_INCLUDING_F1R`.
- `SELECTED_RATES_EXCLUDING_F1R`.

`LOWER_RATE` compares One Rate with standard rates. It is also the fallback
when `rateDisplayOption` is omitted or invalid.

With `LOWER_RATE`, omitting dimensions returns only the
customer-supplied-packaging rate.

## Extra Small One Rate packaging

`FEDEX_EXTRA_SMALL_BOX` is available to enabled accounts for FedEx Express
One Rate in both:

- Comprehensive Rates.
- Ship.

It requires FedEx-provided packaging and has the same 50 lb maximum as the
other One Rate packages.

## Pickup charges during shipment creation

Single on-call pickup rates are charged per stop in the U.S. and Canada,
excluding Puerto Rico and other U.S. territories.

Regular automated pickup charges are weekly and are based on selected pickup
days.

Request pickup charges with:

```text
processingOptions=INCLUDE_PICKUPRATES
```

Future-day quotes also require:

- `pickupDetail.requestType=FUTURE_DAY`.
- `requestedShipment.pickupDetail.readyPickupDateTime`.
- `requestedShipment.pickupDetail.latestPickupDateTime`.

## Package-level surcharge details

For supported multipiece and consolidation services, applicable rate and
ship responses expose these charges at package level alongside aggregate
shipment charges:

- AHS Packaging.
- AHS Dimension.
- AHS Weight.
- Oversize.
- AHS Freight Dimension.
- Non-Stackable.

Non-U.S. High Density, Enhanced Security, and Single Piece surcharges remain
shipment-level charges.

## U.S. inbound and handling rating rules

The U.S. Inbound Processing Fee applies to inbound international Express and
Ground shipments, except:

- Puerto Rico-to-U.S. shipments.
- U.S.-to-Puerto Rico shipments.
- U.S.-origin shipments.

Packages subject to Additional Handling Surcharge—Dimension have a 40 lb
(18 kg) minimum billable weight.
