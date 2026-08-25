# Terminal, Issuing, Tax, and Risk

## Terminal

### Saved-card consent (`2024-09-30.acacia`)

Saving cards with Terminal uses explicit redisplay permission through
`allow_redisplay` instead of the previous customer-consent model. Supply and
preserve redisplay permission in collection and saved-card flows.

### Readers and card-present data (`2024-09-30.acacia`)

Reader settings add a configurable reboot window and the S700 device type.
`card_present` PaymentMethods add offline-collection details, card-present
Charges and PaymentMethods add wallet details, and in-person payments add
Interac support. Preserve these device, collection, wallet, and method fields.

### Reader networking (`2025-03-31.basil`)

Terminal readers support configurable Wi-Fi, allowing network setup through the
Terminal integration.

### Locations and customization (`2025-09-30.clover`)

Terminal Locations add Japan-specific fields, and BBPOS WisePad 3 readers
support custom splash screens. Preserve the location additions and reader
configuration.

## Issuing

### Shipping validation and dispute deductions (`2024-09-30.acacia`)

Physical-card shipping adds address validation and changes its default
validation behavior. Set the desired behavior explicitly. Issuing also adds a
webhook event for funds deducted during a dispute.

### Authorization status and webhooks (`2025-03-31.basil`)

Issuing Authorizations add an `expired` status and a reason for authorizations
created through network fallback while Stripe is unavailable. Authorization
webhooks send an HTTP `Accept` header specifying JSON. Accept the new enum
values and ensure header-sensitive middleware accepts the header contract.

### Risk and personalization (`2025-09-30.clover`)

Issuing Authorization risk levels move to standard risk-level values. Update
generated types and mapping logic instead of relying on the former closed set.
Physical Issuing cards can print a second line; allow it in ordering models and
personalization validation.

### Shipping additions (`2026-07-29.dahlia`)

EU Issuing shipments add Correos as a carrier, and card shipping addresses add
a business-name field. Accept both in carrier enums and address serializers.

## Tax

### Transactions and registrations (`2024-09-30.acacia`)

Tax Transaction creation accepts a posting time, Tax Calculations gain a
retrieve method, and US state registrations can specify sales-tax elections.

### Calculation providers (`2025-09-30.clover`)

Tax settings add a calculation-provider field. Preserve the selected provider
when reading and writing configuration.

### Registration and tax-ID types (`2026-07-29.dahlia`)

Stripe Tax adds US parking-tax registration types and a Canary Islands tax ID
type. Accept both instead of enforcing the previous closed sets.

## Radar, disputes, and payment risk

### Review and risk enums (`2025-09-30.clover`)

Radar manual reviews add enum values. Update generated types and mapping logic
and retain a forward-compatible path.

### Radar referrer (`2026-07-29.dahlia`)

Payment Intent Radar options add `referrer`. Preserve it when supplying Radar
context in Intent builders and serializers.

## Identity and Treasury (`2024-09-30.acacia`)

Identity Verification Sessions can link to Customers. Treasury outbound wires
expose CHIPS tracking details, and ReceivedDebit failures add an enum value for
international-transaction failures. Preserve the relationship and tracking
data, and accept the new failure value.

## Test Clock helpers (`2024-09-30.acacia`)

Advancing `test_helpers.test_clock` objects adds `target_frozen_time`, while
test-helper status details become required. Populate the required status detail
in fixtures and use the target time when advancing a clock.
