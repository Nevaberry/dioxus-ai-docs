# Google Play Target API Policy

Source batch: `play-target-api-policy`.

## New apps and updates

From 31 August 2026, new apps and app updates must meet these target API floors:

| Form factor | Minimum target API |
| --- | ---: |
| Mobile and Android Auto | 36 |
| Wear OS | 35 |
| Android Automotive OS | 35 |
| Android TV | 34 |
| Android XR | 34 |

Evaluate each packaged form factor independently rather than applying the
mobile floor to every artifact.

## Existing-app availability

To remain discoverable to new users whose devices run a newer Android version
than the app targets, existing apps must meet these lower floors:

| Form factor | Minimum target API for broad discovery |
| --- | ---: |
| Mobile and Android Auto | 35 |
| Wear OS | 34 |
| Android TV | 33 |
| Android Automotive OS | 32 |
| Android XR | 34 |

Below the relevant floor, an app remains available to new users only when the
device OS API is no higher than the app's target API. Previous installers can
still discover, reinstall, and use the app on every supported OS version.

## Extensions and exemptions

Affected apps can request an extension from the Play Console policy warning or
notification. An approved extension preserves full distribution until
1 November 2026.

Permanently private apps restricted to an organisation are exempt.
Automotive-form-factor apps bundled in the same package remain discoverable to
all Google Play users.
