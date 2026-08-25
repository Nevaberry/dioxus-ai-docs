# Commerce, Distribution, and Platform Services

## StoreKit purchases and offers

### Advanced Commerce and introductory-offer control (18.4)

StoreKit supports Advanced Commerce API purchases. The purchase option
`introductoryOfferEligibility(compactJWS:)` accepts a server-signed compact JWS
that can request applying an introductory offer even when the customer would
otherwise be ineligible, or block redemption.

### Transaction metadata and platform model (18.4)

StoreKit exposes `appTransactionID`, `originalPlatform`, and `period` across
`AppTransaction`, `Transaction`, `Transaction.Offer`, and
`Product.SubscriptionInfo.RenewalInfo`. The type used by `originalPlatform`
moved to `AppStore.Platform`. Its `watchOS` case was removed and combined with
`iOS`, so switches over the old platform model need updating.

### Entitlement migration and signed-out eligibility (18.4)

`Transaction.currentEntitlement(for:)` is deprecated. Use
`Transaction.currentEntitlements(for:)`; the singular lookup can omit
family-shared transactions.

`isEligibleForIntroOffer(for:)` returns `false` when no App Store account is
signed in. Require a signed-in account before interpreting the result as the
customer's actual offer eligibility.

## Advertising attribution

### Overlapping re-engagement conversions (18.4)

AdAttributionKit permits multiple simultaneous re-engagement conversions. Read
the conversion tag from the re-engagement URL parameter and pass it to
`updateConversionValue` so the intended conversion is updated.

### Development postback testing (18.4)

An advertised app built by Xcode can create and interact with development
postbacks without a publisher app or prior store distribution. Enable and
inspect this under **Settings > Developer > Ad Attribution Testing**.

## Background and extension services

### Background Nearby Interaction (18.4)

An app with an active Live Activity can perform Ultra Wideband ranging through
Nearby Interaction while in the background. Tie the ranging lifetime to the
Live Activity rather than assuming unrestricted background execution.

### Broadcast Extension memory (18.5)

iOS and iPadOS 18.5 raise the per-process memory limit for Broadcast Extensions.
Capture and streaming extensions can use the additional headroom for higher
quality when system resources permit, but should continue handling memory
pressure.

### Push to Talk migration (26.0)

Apps built with the iOS 26 SDK or later cannot use
`com.apple.developer.pushkit.unrestricted-voip.ptt`. Migrate to the Push to Talk
framework introduced in iOS 16.

## Enterprise and App Store distribution

### Enterprise launch recovery (18.5)

iOS and iPadOS 18.5 fix an iOS 18-era problem that could prevent some enterprise
apps from launching. A device that already encountered the problem requires all
enterprise apps to be uninstalled and reinstalled; installing only the affected
app again is not the documented recovery.

### App Store SDK requirement

Since April 28, 2026, App Store Connect uploads must be built with Xcode 26 or
later and use a version 26 SDK for iOS, iPadOS, tvOS, visionOS, or watchOS.
