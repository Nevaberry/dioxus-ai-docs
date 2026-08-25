# EAS Updates and Distribution

## Hermes bytecode diffs

EAS Update and `expo-updates` can send binary diffs instead of full Hermes bytecode.

In batch `55`, this behavior is opt-in:

```json
{
  "expo": {
    "updates": {
      "enableBsdiffPatchSupport": true
    }
  }
}
```

Equivalent native configuration is supported.

In batch `56`, bytecode diffs are enabled by default. Opt out with:

```json
{
  "expo": {
    "updates": {
      "enableBsdiffPatchSupport": false
    }
  }
}
```

Pin the setting when deterministic rollout behavior across SDK upgrades matters.

## EAS Build behavior

SDK 55 EAS Build defaults to Xcode 26.2. SDK 56 requires Xcode 26.4 and uses prebuilt iOS XCFrameworks for complex Expo modules. Put `EXPO_USE_PRECOMPILED_MODULES=0` in the EAS environment when source builds are required.

EAS prebuilds major community libraries and reports per-step `xcodebuild` and Gradle timings. Use those timings to distinguish dependency compilation from application compilation.

`eas update` requires `--environment <name>`, including in CI.

## Convex integration

Run:

```sh
eas integrations:convex:connect
```

The command installs and provisions Convex, links a development deployment, writes `CONVEX_DEPLOY_KEY` and `EXPO_PUBLIC_CONVEX_URL` to `.env.local`, and creates `EXPO_PUBLIC_CONVEX_URL` in the Production, Preview, and Development EAS environments.

Review generated secrets and environment selection before deploying.

## Expo Go distribution and native limitations

SDK 56 Expo Go is not distributed through the mobile app stores. Expo CLI can install it directly on Android. On iOS, use the external TestFlight beta or create an `eas go` build and upload it to the application's TestFlight team.

Do not treat Expo Go as a complete native-integration test. Android push notifications require a development build, and `expo-av` is absent from Expo Go.
