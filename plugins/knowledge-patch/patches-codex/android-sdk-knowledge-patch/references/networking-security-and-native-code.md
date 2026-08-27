# Networking, Security, and Native Code

## Intent launch and matching security

### Nested-intent redirection

Android 16 (`api-36`) protects every app against unsafe launches of nested
intents. If a legitimate flow breaks, code compiled against API 36 can call
`removeLaunchSecurityProtection()` on the nested `Intent` before launching
it. Limit that exception to the exact flow: removing protection restores the
intent-redirection risk.

### Strict incoming-intent matching

API 36 apps can require cross-app explicit intents to match the target
component's intent filter and can prevent actionless intents from matching.
Enable the application policy with `intentMatchingFlags`; a component can
override it with `none`, while `allowNullAction` selectively permits a missing
action.

```xml
<application android:intentMatchingFlags="enforceIntentFilter" />
```

## Local-network access

### Testing the Android 16 restriction

Android 16 offers local-network protection as an opt-in compatibility test.
Enable `RESTRICT_LOCAL_NETWORK` and reboot:

```shell
adb shell am compat enable RESTRICT_LOCAL_NETWORK com.example.app
```

The test gates in-process LAN TCP, UDP, multicast, broadcast, and native
sockets while leaving internet traffic available. Out-of-process framework
APIs such as `NsdManager` are not restricted in this phase. Declaring and
granting `NEARBY_WIFI_DEVICES` restores gated LAN access. Test denial and
revocation in preparation for the dedicated permission.

### Android 17 runtime permission

Apps targeting API 37 must declare and request `ACCESS_LOCAL_NETWORK`, in the
`NEARBY_DEVICES` group, for direct LAN discovery and connections. An existing
nearby-device grant avoids a second prompt. A system-mediated device picker is
the permissionless alternative.

```xml
<uses-permission android:name="android.permission.ACCESS_LOCAL_NETWORK" />
```

Android 17 also blocks loopback traffic between profiles for all apps,
regardless of target SDK. Loopback within one profile is unchanged.

## TLS and cleartext traffic

### Encrypted Client Hello

TLS connections from API 37-targeted apps use ECH when both the networking
library and server support it; otherwise they send ECH GREASE. Network
Security Configuration accepts `<domainEncryption>` under `<base-config>` or
`<domain-config>` to enable or disable ECH globally or for an individual
domain.

### Certificate transparency

Certificate transparency is automatically enabled for API 37-targeted apps.
Unlike API 36 behavior, it needs no explicit opt-in.

### Cleartext migration

`android:usesCleartextTraffic` is on a path to stop authorizing HTTP at a
future target SDK. Move domain exceptions into Network Security Configuration.
If `minSdk` is below 24, temporarily retain both mechanisms; with `minSdk` 24
or higher, only the network configuration is needed.

## Native code

### 16 KB page alignment

Android 16 can run some 4 KB-aligned apps in compatibility mode on 16 KB-page
devices and informs the user with a dialog. Compiling with API 36 and setting
the `android:pageSizeCompat` manifest property suppresses the dialog, but it
does not replace rebuilding native libraries with 16 KB alignment.

### Read-only dynamic code

For API 37-targeted apps, dynamic-code-loading protection covers native
libraries. A file supplied to `System.load()` must already be read-only or
loading fails with `UnsatisfiedLinkError`.

## Android Keystore limits

Android 17 caps non-system API 37-targeted apps at 50,000 keys and other apps
at 200,000. Creating another key throws `KeyStoreException`. For API 37
targets, `getNumericErrorCode()` returns `ERROR_TOO_MANY_KEYS`; older targets
receive `ERROR_INCORRECT_USAGE`.

## APK signing and cryptography providers

Android 17 introduces APK Signature Scheme v3.2. It combines RSA or
elliptic-curve signatures with ML-DSA signatures for post-quantum hybrid
verification.

Android 17 also exposes a public service-provider interface for hybrid public
key encryption implementations.
