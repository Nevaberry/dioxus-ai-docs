# Networking, Security, and Distribution

## HTTP Loading and Testing

### Opt In to URLSession's New Loader

The iOS 18.4 SDK exposes `usesClassicLoadingMode`. Set it to `false` on the
configuration before creating the session to opt in to the new HTTP loading
mode, which is planned to become the default in a future release:

```swift
let configuration = URLSessionConfiguration.default
configuration.usesClassicLoadingMode = false
let session = URLSession(configuration: configuration)
```

Test request, redirect, authentication, caching, and connectivity behavior in
the opted-in session before broad adoption.

### Use a Fixed Simulator Runtime for iOS 18.3 Networking

Xcode 16.4 fixes an iOS 18.3 Simulator runtime defect that caused
`NSURLSession` requests to time out and fail consistently. Reproduce an apparent
application networking failure on the fixed runtime before debugging higher
layers.

### Test Safari Extensions on Devices

Safari extensions do not appear in the iOS or visionOS Simulator as of the
18.4 SDK. Use physical devices for extension discovery and behavior tests on
those platforms.

## Transport and VPN Security

### Account for the TLS 1.2 Linked-On Minimum

For applications linked on or after iOS 26 or macOS 26, `URLSession` and the
Network framework default to TLS 1.2 as their minimum, replacing TLS 1.0.
Upgrade legacy servers. Where a temporary exception is unavoidable, configure
`URLSessionConfiguration.tlsMinimumSupportedProtocolVersion` or call
`sec_protocol_options_set_min_tls_protocol_version` explicitly.

### Remove Obsolete IKEv2 Algorithms

iOS 26 no longer supports DES, 3DES, SHA1-96, SHA1-160, or Diffie-Hellman
groups below 14 for IKEv2 VPNs. Update both the client profile and the VPN server
to mutually supported stronger algorithms.

## Entitlements and Enterprise Distribution

### Migrate the Legacy Push to Talk Entitlement

Applications built with the iOS 26.0 SDK or later can no longer use
`com.apple.developer.pushkit.unrestricted-voip.ptt`. Migrate to the Push to Talk
framework introduced in iOS 16.

### Recover Enterprise Apps After the Launch-Failure Fix

iOS and iPadOS 18.5 resolve an iOS 18-era issue that could prevent some
enterprise applications from launching. A device that encountered the issue
must uninstall and reinstall all enterprise applications to recover; merely
installing the OS fix is insufficient.

## Ad Attribution

### Target an Overlapping Re-engagement Conversion

AdAttributionKit in iOS 18.4 supports multiple simultaneous re-engagement
conversions. Read the conversion tag from the re-engagement URL parameter and
pass that tag to `updateConversionValue` so the intended conversion is updated.

### Exercise Development Postbacks Without Store Distribution

An advertised application built by Xcode can create and interact with
development postbacks under **Settings > Developer > Ad Attribution Testing**.
This flow does not require a publisher application or prior store distribution.

## App Store Submission

### Use Xcode 26 and a Version 26 SDK

The `app-store-sdk-requirements` policy requires App Store Connect uploads made
since April 28, 2026 to use Xcode 26 or later and an SDK for iOS 26, iPadOS 26,
tvOS 26, visionOS 26, or watchOS 26. Check both the toolchain and the archive's
base SDK before upload.
