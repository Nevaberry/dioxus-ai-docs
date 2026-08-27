# EAS Updates and Distribution

## Hermes bytecode binary diffs

EAS Update and `expo-updates` can send binary diffs instead of full Hermes bytecode.

In SDK 55 the behavior is opt-in:

```json
{
  "expo": {
    "updates": {
      "enableBsdiffPatchSupport": true
    }
  }
}
```

Equivalent native configuration is also supported.

In SDK 56 bytecode diffs are enabled by default. Opt out when necessary:

```json
{
  "expo": {
    "updates": {
      "enableBsdiffPatchSupport": false
    }
  }
}
```

Pin the value explicitly when rollout reproducibility matters across SDK upgrades.

## Update environment selection

`eas update` requires an explicit environment name, including in CI:

```sh
eas update --environment <name>
```

## Native build behavior

SDK 55 EAS Build defaults to Xcode 26.2. SDK 56 native builds require Xcode 26.4.

In SDK 56, complex Expo modules use prebuilt iOS XCFrameworks by default in both local and EAS builds. Put `EXPO_USE_PRECOMPILED_MODULES=0` in the EAS environment when the remote build must compile those modules from source.

EAS also prebuilds major community libraries and reports per-step `xcodebuild` and Gradle timings.

## Convex integration

SDK 56 adds an EAS integration command:

```sh
eas integrations:convex:connect
```

It installs and provisions Convex, links a development deployment, writes `CONVEX_DEPLOY_KEY` and `EXPO_PUBLIC_CONVEX_URL` to `.env.local`, and creates `EXPO_PUBLIC_CONVEX_URL` in the Production, Preview, and Development EAS environments.

## Development builds versus Expo Go

Android push notifications error in Expo Go beginning in SDK 55 and require a development build. `expo-av` has also been removed from Expo Go and no longer receives patches.

Use a development build to validate native integrations instead of assuming behavior in Expo Go matches a standalone application.

## SDK 56 Expo Go distribution

SDK 56 Expo Go is not distributed through mobile app stores.

- Expo CLI can install it directly on Android.
- On iOS, use the external TestFlight beta or build with `eas go` and upload it to the application's TestFlight team.

## EAS access through Expo MCP

Expo MCP can query EAS services. With a linked App Store Connect key, it can also query TestFlight crashes and feedback.
