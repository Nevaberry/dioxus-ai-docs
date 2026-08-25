# Client Platforms and Managed Policies

Use this reference for managed policy keys and platform-specific behavior on
Windows, macOS, iOS, tvOS, Android, Linux desktops, OpenWrt, NAS devices, and
Apple TV.

## Cross-platform and MDM policies

### Hostname override (since 1.80.0)

The `Hostname` system policy lets an MDM configuration override the hostname
reported by the operating system.

### Always On (since 1.84.0)

Windows, macOS, and iOS provide `AlwaysOn.Enabled` and
`AlwaysOn.OverrideWithReason`. `ForceEnabled` is deprecated on macOS and iOS.
On Windows, Always On connects at sign-in and remains active without the GUI,
including on headless systems. Installing the Windows client starts the GUI for
every signed-in user.

### Reconnect and AD DNS registration (since 1.84.0 and 1.86.0)

Windows and Android provide `ReconnectAfter` to cap how long a user may leave
Tailscale disconnected; macOS adds the policy in 1.86.0. Windows also provides
`EnableDNSRegistration` to control registration of Tailscale addresses in
Active Directory DNS.

### Managed exit-node override (since 1.88.1)

On Windows and macOS, combine `ExitNode.AllowOverride` with
`ExitNodeID=auto:any` to require exit-node use while allowing users to select a
different node.

### AuthKey scope (since 1.96.2)

The `AuthKey` system policy applies only when no user is logged in.

## macOS

### System extensions (since 1.80.0)

The Standalone variant provides `tailscale configure sysext activate`,
`deactivate`, and `status` for programmatic system-extension activation
management.

### Onboarding policies (since 1.86.0 and 1.98.1)

`OnboardingFlow` suppresses the installation onboarding flow and replaces the
deprecated `TailscaleOnboardingSeen` policy. `AppIntroShown` suppresses the
Welcome modal shown after the first device login.

### Proxy and exit-node policies (since 1.88.1)

`UseSystemProxy` controls whether Tailscale respects proxy settings from System
Settings. The `advertiseExitNode` system policy is also available.

### Browser and Dock policies (since 1.94.1)

`AuthBrowser.macos` selects the preferred browser for automatic authentication
URLs. `HideDockIcon` controls whether the Dock icon remains after all Tailscale
windows close.

### Release channel (since 1.94.1)

The About section's Release Channel menu can install release-candidate versions
and keep them automatically updated.

### Windowed UI and account switching (since 1.96.2)

Windowed UI mode is generally available. Double-click an account in the
Accounts section to switch to it.

### Open-source posture reporting (since 1.96.2)

The open-source macOS variant sets the `node:osVersion` posture attribute.

### Standalone Time Machine exclusion (since 1.96.2)

The Standalone client excludes its Tailscale data directories from Time Machine
backups.

### Deep links (since 1.102.2)

The macOS protocol handler can deep-link to devices, exit nodes, and settings
panels in the application window.

## iOS, tvOS, and Android

### Android subnet-router hosting (since 1.80.0)

Configure an Android device as a subnet router from the app's Settings menu.

### Mobile subnet-route acceptance (since 1.84.0)

iOS adds a subnet-routing toggle. Version 1.84.1 corrects an unintended
default-off state for subnet routing on both iOS and Android.

### iOS exit-node hosting (since 1.98.1)

An iOS device can act as an exit node.

### Apple TV web management (since 1.102.2)

Apple TV devices can be managed remotely through the Tailscale web client.

## Linux and appliance platforms

### Desktop tray controls (since 1.88.1)

Linux desktops can enable the system tray application for controls including
fast user switching and exit-node selection.

### Freedesktop systray autostart (since 1.96.2)

```console
tailscale configure systray --enable-startup=freedesktop
```

This creates a freedesktop autostart entry for the systray.

### OpenWrt with `apk` (since 1.96.2)

Tailscale updates are supported on OpenWrt 25.12.0 and later when `apk` is the
package manager.

### Synology ARMv7 binaries (since 1.102.2)

Affected Synology NAS models receive ARMv7 binaries built with software
floating-point support instead of the older ARMv5 binaries.
