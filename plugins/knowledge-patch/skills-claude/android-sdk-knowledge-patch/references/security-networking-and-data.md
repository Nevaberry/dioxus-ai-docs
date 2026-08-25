# Security, Networking, and Data Access

## Intent hardening

### Preserve nested-intent launch protection

Android 16 protects every app from unsafe nested-intent launches. If a
legitimate flow breaks, code compiled against API 36 can call
`removeLaunchSecurityProtection()` on the nested `Intent` before launching it.
Use that escape hatch only after validating the flow because it restores the
intent-redirection risk.

### Opt into strict incoming matching

API 36 apps can require cross-app explicit intents to match the target
component's filter and can prevent actionless intents from matching:

```xml
<application android:intentMatchingFlags="enforceIntentFilter" />
```

A component can override the application setting with `none`.
`allowNullAction` selectively permits an absent action. Test callers before
enforcing the setting because explicit intents that previously bypassed filter
matching can be rejected.

## Local-network access

### Test denial on Android 16

Android 16 local-network protection is opt-in rather than enforced. Enable the
compatibility change and reboot:

```shell
adb shell am compat enable RESTRICT_LOCAL_NETWORK com.example.app
```

The test gates in-process LAN TCP, UDP, multicast, broadcast, and native
sockets, while internet traffic remains available. Out-of-process framework
APIs such as `NsdManager` are not restricted in this test phase. Declaring and
granting `NEARBY_WIFI_DEVICES` restores gated LAN access.

Exercise denial and revocation now rather than assuming the early behavior is
the final permission contract.

### Request the dedicated permission for API 37

API 37 targets must declare and request `ACCESS_LOCAL_NETWORK`, in the
`NEARBY_DEVICES` group, for LAN discovery and connections:

```xml
<uses-permission android:name="android.permission.ACCESS_LOCAL_NETWORK" />
```

An existing nearby-device grant avoids another prompt. Use the system-mediated
device picker when the app can operate without direct permission.

### Cross-profile loopback is blocked

Android 17 blocks loopback traffic between profiles for all apps regardless of
target SDK. Loopback within one profile is unchanged. Replace cross-profile
localhost channels with a supported cross-profile mechanism.

## TLS and cleartext

### Encrypted Client Hello is target-gated

For API 37 targets, TLS connections use ECH when both the networking library
and server support it; otherwise they send ECH GREASE. Network Security
Configuration accepts `<domainEncryption>` beneath `<base-config>` or
`<domain-config>` to enable or disable ECH globally or per domain.

### Certificate transparency defaults on

Certificate transparency is automatically enabled for API 37 targets. Unlike
API 36 behavior, it requires no explicit opt-in. Test private PKI, interception,
and exceptional endpoints before raising the target.

### Move cleartext exceptions into network configuration

`android:usesCleartextTraffic` is planned to stop authorizing HTTP at a future
target SDK. Move domain-specific exceptions to Network Security Configuration.

Apps with a minimum API below 24 must temporarily keep both the manifest
mechanism and network configuration. Apps with a minimum of 24 or later need
only Network Security Configuration.

## SMS and one-time passwords

On Android 17, WebOTP messages are withheld for three hours from every app
except the domain-verified recipient and exempt handlers, regardless of target
SDK. API 37 targets also lose immediate access to ordinary OTP-bearing SMS.

During the delay, both `SMS_RECEIVED_ACTION` delivery and SMS provider queries
are filtered. Use SMS Retriever or SMS User Consent for OTP flows.

## Contacts and URI sharing

### Join contact account data through RawContacts

For API 37 targets, `ContactsContract.Data` no longer exposes `ACCOUNT_NAME`,
`ACCOUNT_TYPE`, or `ACCOUNT_TYPE_AND_DATA_SET`. Obtain these columns from
`RawContacts` by joining on `RAW_CONTACT_ID`.

When querying `Data` without `READ_CONTACTS`, `StrictColumns` and
`StrictGrammar` reject incompatible SQL with an exception. Do not depend on
previously permissive projections or query syntax.

### Make URI grants explicit

Android 18 will stop implicitly granting URI access for `ACTION_SEND`,
`ACTION_SEND_MULTIPLE`, and `ACTION_IMAGE_CAPTURE`. Android 17 adds
`StrictMode.VmPolicy.Builder.detectImplicitUriPermissionGrant()` to expose
dependencies before enforcement.

Add `FLAG_GRANT_READ_URI_PERMISSION` to send intents. Add both read and write
grant flags to image-capture intents.

## Media access and change tokens

### Treat MediaStore versions as opaque

For API 36 targets, `MediaStore.getVersion()` returns an app-specific value.
Use it only as an opaque change token. Do not parse it or use it to infer device
information.

### App ownership does not override limited access

For API 36 targets on Android 16, the Photo Picker initially selects app-owned
photos and videos when the user grants access to selected media only. The user
can deselect those items and immediately revoke access despite app ownership.
Handle loss of access on every reopen or query.

## Keystore and cryptography

### Enforce per-app key budgets

Android 17 caps non-system API 37-targeted apps at 50,000 Android Keystore keys
and other apps at 200,000. Creating another key throws `KeyStoreException`.

For API 37 targets, `getNumericErrorCode()` returns `ERROR_TOO_MANY_KEYS`.
Older targets receive `ERROR_INCORRECT_USAGE`. Bound key creation and clean up
obsolete keys instead of treating creation as unbounded.

### HPKE has a public provider interface

Android 17 exposes a public service-provider interface for hybrid public key
encryption implementations. Use the public interface rather than private or
platform-internal hooks.
