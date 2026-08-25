# Persistence, Foundation, and Commerce

## Core Data

### Follow the Imported Concurrency Contract

In the iOS 26.0 SDK, `NSManagedObject` imports as nonisolated and non-`Sendable`,
while `NSManagedObjectContext` imports as nonisolated and `Sendable`. The
`perform` and `performBlock` families import with `Sendable` closures. Rebuilding
can therefore expose new concurrency diagnostics.

Keep managed objects within the scope of their context. During diagnosis, add
the launch argument below to catch context violations:

```text
-com.apple.CoreData.ConcurrencyDebug 1
```

### Remove Ubiquity Store Options

The iOS and macOS 26 SDKs make these options compile-time errors:

- `NSPersistentStoreUbiquitousContentNameKey`
- `NSPersistentStoreUbiquitousContentURLKey`
- `NSPersistentStoreUbiquitousPeerTokenOption`
- `NSPersistentStoreRemoveUbiquitousMetadataOption`
- `NSPersistentStoreUbiquitousContainerIdentifierKey`
- `NSPersistentStoreRebuildFromUbiquitousContentOption`

Older builds only log warnings. Removing the options retains the local store but
stops synchronization. Migrate synchronized persistence to
`NSPersistentCloudKitContainer` or SwiftData.

## StoreKit

### Use Advanced Commerce and Signed Introductory-Offer Control

The iOS 18.4 SDK adds Advanced Commerce API purchase support and the purchase
option `introductoryOfferEligibility(compactJWS:)`. The server-signed compact JWS
can request that an introductory offer apply even when the customer would
otherwise be ineligible, or prevent redemption.

### Read Expanded Transaction Metadata

New StoreKit metadata includes `appTransactionID`, `originalPlatform`, and
`period` across `AppTransaction`, `Transaction`, `Transaction.Offer`, and
`Product.SubscriptionInfo.RenewalInfo`. The type used by `originalPlatform`
moved to `AppStore.Platform`; its `watchOS` case was removed and folded into
`iOS`.

### Preserve Family-Shared Entitlements

`Transaction.currentEntitlement(for:)` is deprecated in iOS 18.4. Use
`Transaction.currentEntitlements(for:)`, which does not omit family-shared
transactions. `isEligibleForIntroOffer(for:)` returns `false` when no App Store
account is signed in, so require a signed-in account before interpreting the
result as the customer's eligibility.

## Foundation and POSIX

### Accept ISO-8601 Fractional Seconds Independently

With the iOS 26.0 SDK, `ISO8601FormatStyle` permits fractional seconds whether
or not `includingFractionalSeconds` is set. Do not use that setting as a strict
input-rejection rule.

### Use the Public Fileport Calls

The iOS 18.4 SDK makes `fileport_makeport(2)` and `fileport_makefd(2)` public
APIs and supplies manual pages for both.

### Treat POSIX Named Semaphores as Team-Scoped

On iOS 26, processes signed with a Team ID entitlement cannot use `sem_open`
or `sem_unlink` to observe a named semaphore created by a different development
team. Do not design cross-team process coordination around a shared semaphore
name.
