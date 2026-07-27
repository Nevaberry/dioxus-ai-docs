# EAS Updates and Distribution

## Control Hermes bytecode diffs

EAS Update and `expo-updates` can send binary diffs instead of complete Hermes bytecode.

This is opt-in in SDK 55. Enable it in app config with:

```json
{
  "expo": {
    "updates": {
      "enableBsdiffPatchSupport": true
    }
  }
}
```

Equivalent native configuration is supported. In SDK 56, bytecode diffs are enabled by default. Opt out with `updates.enableBsdiffPatchSupport: false`. Set an explicit value when update rollout characteristics must not change implicitly during an SDK upgrade.

## Select the EAS Update environment

`eas update` requires `--environment <name>` as of SDK 55, including in CI. Ensure the chosen environment supplies the variables expected by app config and update code.

## Understand EAS native build behavior

For SDK 55 iOS builds, EAS Build defaults to Xcode 26.2. SDK 56 native builds require Xcode 26.4.

In SDK 56, complex Expo modules use prebuilt XCFrameworks by default for local and EAS builds; set `EXPO_USE_PRECOMPILED_MODULES=0` in the EAS environment to compile them from source. EAS also prebuilds major community libraries and exposes per-step `xcodebuild` and Gradle timings.

## Provision Convex through EAS

SDK 56 adds:

```sh
eas integrations:convex:connect
```

The command installs and provisions Convex, links a development deployment, writes `CONVEX_DEPLOY_KEY` and `EXPO_PUBLIC_CONVEX_URL` to `.env.local`, and creates `EXPO_PUBLIC_CONVEX_URL` in the Production, Preview, and Development EAS environments. Review the generated local secret and environment values before committing or deploying.

## Distribute Expo Go deliberately

SDK 56 Expo Go is not distributed through mobile app stores. Expo CLI can install it directly on Android. On iOS, use the external TestFlight beta or create an `eas go` build and upload it to the application's TestFlight team.

Expo Go is not a substitute for a development build: Android push notifications require a development build, and native integrations may not be present in Expo Go.
