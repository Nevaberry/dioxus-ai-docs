# Web integration

## Web API platform boundaries

### Outside China

Apple Pay JS supports:

- iOS 10 or later.
- macOS 10.12 or later.

Payment Request supports:

- iOS 11.3 or later.
- macOS 10.12.6 or later with Safari 11.1 or later.

### In China

Apple Pay JS requires iOS 11.2 or later. Payment Request requires iOS 11.3 or
later. Neither API is available on macOS in China.

On iOS, Safari and `SFSafariViewController` both support Apple Pay.

## Apple Pay JS SDK delivery

Sites can load either the latest autoupdating Apple Pay JS SDK or a chosen SDK
version.

## Apple Pay button behavior

`ApplePayButton` can start a payment or prompt the customer to set up a card.

## Apple Pay merchandising

The Apple Pay Merchandising web component displays installment-payment options
and related merchandising information on a seller's site.

## Web order tracking

A website can configure and style a Track with Apple Wallet button to match the
rest of the site.
