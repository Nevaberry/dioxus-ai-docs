# Terminal, Issuing, Tax, and Risk

## Terminal

### Saved-card consent (`2024-09-30.acacia`)

Saving cards through Terminal uses explicit redisplay permission in
`allow_redisplay` instead of the previous Customer-consent model. Supply and
preserve that permission in collection and saved-card flows.

### Reader and card-present contracts (`2024-09-30.acacia`)

Reader settings add a configurable reboot window and the S700 device type.
`card_present` PaymentMethods add offline-collection details. Card-present
Charges and PaymentMethods add wallet details, and in-person payments add
Interac. Preserve these fields and expand device and payment-method handling.

### Wi-Fi configuration (`2025-03-31.basil`)

Terminal readers support configurable Wi-Fi network setup through the Terminal
integration.

### Location and reader customization (`2025-09-30.clover`)

Terminal Locations add Japan-specific fields. BBPOS WisePad 3 readers support
custom splash screens. Preserve the Location additions and reader
configuration.

## Issuing

### Address validation and dispute deductions (`2024-09-30.acacia`)

Physical-card shipping adds address validation and changes its default
validation behavior. Set the intended behavior explicitly. Issuing adds an
Event for funds deducted during a dispute.

### Authorization contracts (`2025-03-31.basil`)

Issuing Authorizations add `expired` status and a reason for Authorizations
created by network fallback while Stripe is unavailable. Authorization webhooks
send an HTTP `Accept` header specifying JSON. Accept the enums and ensure
header-sensitive middleware accepts that header.

### Risk enums (`2025-09-30.clover`)

Issuing Authorization risk levels move to standard risk-level values. Update
generated types and mapping logic instead of retaining the earlier closed set.

### Card personalization (`2025-09-30.clover`)

Physical cards can print a second line. Card-order models and personalization
validation must allow it.

### Shipping fields (`2026-07-29.dahlia`)

EU card shipments add Correos as a carrier, and card shipping addresses add a
business-name field. Accept both in enums and serializers.

## Tax

### Tax ID additions (`2024-09-30.acacia`)

Customer tax IDs add Swiss UID and Croatian OIB. Tax-ID validation must accept
them.

### Transactions, calculations, and registrations (`2024-09-30.acacia`)

Tax Transaction creation accepts a posting time. Tax Calculations add a retrieve
method. US state registrations can specify sales-tax elections. Connect embedded
components add tax settings and registration support.

### Calculation providers (`2025-09-30.clover`)

Tax settings add a calculation-provider field. Configuration readers and
writers must preserve the selected provider.

### Registration and ID additions (`2026-07-29.dahlia`)

Stripe Tax adds US parking-tax registration types and a Canary Islands tax ID
type. Do not enforce the previous closed sets.

## Radar and disputes

### Dispute classification (`2024-09-30.acacia`)

Card Disputes add case-type classification. Deserializers and exhaustive
handling must accept the added values.

### Radar review enums (`2025-09-30.clover`)

Radar manual reviews add enum values. Update generated types and mapping logic
rather than relying on a closed set.

### Radar referrer (`2026-07-29.dahlia`)

PaymentIntent Radar options add `referrer`. Intent builders and serializers must
preserve it when supplying Radar context.

## Test Clocks (`2024-09-30.acacia`)

Advancing `test_helpers.test_clock` adds `target_frozen_time`, while test-helper
status details become required. Fixtures and generated types must populate the
required status detail and use the target time when advancing a clock.
