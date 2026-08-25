# Cards and bank payments

Use this reference for Card, UPI, ACH, EFT PAD, bank transfer, OpenInvoice,
PayByBankUS, Econtext, and Brazilian meal-voucher changes. Items come from
`adyen-web-releases-current` and `adyen-web-releases-history`.

## Card callbacks and funding

### Healthcare BIN data (since v6.41.0)

The value passed to `onBinLookup` includes `healthcare`, so card integrations
can consume it directly from the callback result.

### Dual-branded card selection (since v6.21.0)

The SDK does not preselect a brand for dual-branded cards outside Europe,
preserving low-cost-routing choice.

## Installments

### Japanese bonus installments (since v6.31.0)

Card payments support Japanese bonus installments.

## UPI

### Required mandate end time (since v6.34.1)

The UPI Autopay mandate type requires `endsAt`. TypeScript integrations must
provide it rather than treating it as optional.

### UPI Collect removal (since v6.30.0)

UPI Collect is no longer supported. The default UPI flow is QR code on desktop
and Intent on mobile.

## ACH

- V6.12.0 adds an account-type dropdown and an account-number verification
  input.
- V6.21.0 adds configuration for prefilling the account-holder name.

## Canadian EFT PAD (since v6.17.0)

Web integrations can use the `PreAuthorizedDebitCanada` component for EFT PAD.

## Bank transfer variants (since v6.18.0)

Supported variants include:

- `bankTransfer_BE`
- `bankTransfer_NL`
- `bankTransfer_PL`
- `bankTransfer_FR`
- `bankTransfer_CH`
- `bankTransfer_IE`
- `bankTransfer_GB`
- `bankTransfer_DE`

## OpenInvoice gender removal (since v6.26.0)

The deprecated `gender` field is removed from OpenInvoice components used by
Oney, Riverty, and RatePay.

## PayByBankUS property correction (since v6.26.0)

Use `showOtherInsteadOfNumber`; the misspelled
`showOtherInsteafOfNumber` property name was corrected.

## Econtext voucher references (since v6.29.0)

Econtext voucher results can include `alternativeReference`.

## Brazilian meal-voucher restrictions (since v6.29.0)

Brazilian meal vouchers no longer offer installments or Click to Pay.
