# Terminal, Issuing, Tax, and Risk

## Terminal

### Saving cards and reader contracts

In `2024-09-30.acacia`:

- Saving cards through Terminal uses updated consent modeling.
- Reader configuration can set a reboot time.
- Reader device types include Stripe S700.
- `card_present` PaymentMethods expose offline-collection details.

Review consent capture and offline handling rather than carrying forward an older save-card flow unchanged.

### Reader networking and presentation

- Terminal can configure reader Wi-Fi in `2025-03-31.basil`.
- Terminal Locations add Japan-specific fields in `2025-09-30.clover`.
- BBPOS WisePad 3 readers support custom splash screens.

## Issuing

### Shipping and dispute handling

In `2024-09-30.acacia`, Issuing changes the default for shipping-address validation and adds physical-card address validation. It also emits a webhook event when funds are deducted during a dispute.

### Authorization state and webhook requests

In `2025-03-31.basil`:

- Issuing Authorizations add `expired` status.
- A reason code identifies network-fallback Authorizations created while Stripe is unavailable.
- Issuing Authorization webhook requests send an HTTP `Accept` header that specifies JSON.

Do not reject the additional state or reason, and ensure webhook infrastructure tolerates the header.

### Risk levels and physical cards

- Issuing Authorization risk levels switch to standard values in `2025-09-30.clover`; update exhaustive enum handling.
- Issuing physical cards can print a second line.
- Visa Issuing Tokens can omit the card reference ID in `2026-03-25.dahlia`; treat it as optional.
- Virtual Issuing cards can automatically cancel after a configured number of payments.

## Tax

### Transactions, registrations, and embedded components

In `2024-09-30.acacia`:

- Tax transaction creation accepts a posting time.
- Tax registrations support US state sales-tax elections.
- Tax settings and registrations are available through embedded components.
- Tax Calculations add a retrieve operation.

### Calculation provider

Tax settings expose the tax calculation provider in `2025-09-30.clover`, allowing an integration to identify which provider performed automatic tax calculation.

### Ticket sales preview

The `2026-03-25.dahlia` public preview can calculate ticket-sale tax using event location instead of Customer location. It adds event-related US registration types and tax breakdown values. Keep these values behind preview-compatible models.

## Disputes and Radar

### Dispute classifications

- Card Disputes expose case type in `2024-09-30.acacia`.
- Klarna disputes add a documented chargeback-loss reason in `2025-09-30.clover`.
- Radar manual reviews add enum values; retain an unknown-value branch.

### Crypto fingerprints

Radar value-list items accept crypto fingerprints in `2026-03-25.dahlia`, enabling value-list matching for crypto payments.

## Climate

Climate Orders add marine carbon removal as a pathway in `2026-03-25.dahlia`. Expand pathway enum handling before consuming the new value.
