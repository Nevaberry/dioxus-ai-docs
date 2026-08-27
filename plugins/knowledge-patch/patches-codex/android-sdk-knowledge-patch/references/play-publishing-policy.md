# Google Play Target API Policy

## New apps and updates

Under the `play-target-api-policy` guidance, submissions from 31 August 2026
must meet these target floors:

| Form factor | Minimum target API |
| --- | ---: |
| Mobile and other general Android apps | 36 |
| Wear OS | 35 |
| Android Automotive OS | 35 |
| Android TV | 34 |
| Android XR | 34 |

Apply these floors to both new apps and app updates.

## Existing-app availability

Existing listings use lower floors to remain discoverable to new users whose
devices run a newer Android version than the app targets:

| Form factor | Minimum target API for full discoverability |
| --- | ---: |
| Mobile and Android Auto | 35 |
| Wear OS | 34 |
| Android TV | 33 |
| Android Automotive OS | 32 |
| Android XR | 34 |

Below the applicable floor, the app remains available to a new user only when
the device's OS API level is no higher than the app's target. Previous
installers can still discover, reinstall, and use it on every OS version the
app supports.

## Extension and exemptions

An affected app can request an extension from its Play Console policy warning
or notification. The extension retains full distribution until 1 November
2026.

Permanently private apps restricted to an organisation are exempt.
Automotive-form-factor apps bundled in the same package also remain
discoverable to all Google Play users.
