# Managed Clients and Platforms

## Cross-platform system policy

### Managed hostname (since 1.80.0)

The `Hostname` system policy lets MDM override the device hostname reported by
the operating system.

### Always On and disconnect limits (since 1.84.0)

Windows, macOS, and iOS support `AlwaysOn.Enabled` and
`AlwaysOn.OverrideWithReason`; macOS and iOS deprecate `ForceEnabled`.
Windows Always On connects at sign-in and stays active without the GUI,
including on headless machines. Installing the Windows client also starts the
GUI for every signed-in user.

`tailscale down` accepts `--reason`. Windows and Android provide
`ReconnectAfter` to cap how long a user may leave Tailscale disconnected.
Windows also provides `EnableDNSRegistration` to control registration of
Tailscale addresses in Active Directory DNS.

### Recommended exit node with override (since 1.88.1)

On Windows and macOS, combine `ExitNode.AllowOverride` with
`ExitNodeID=auto:any` to require exit-node use while allowing the user to
choose a different exit node.

### AuthKey scope (since 1.96.2)

The `AuthKey` system policy applies only when no user is logged in.

## Android, iOS, tvOS, and Apple TV

### Android subnet router (since 1.80.0)

Configure an Android device as a subnet router from the app's Settings menu.

### Android release availability (since 1.82.0)

Android 1.82.0 was delayed to 1.82.1. Versions 1.82.1 and 1.82.4 are
Android-only, while 1.82.2 and 1.82.3 were internal-only.

### Mobile subnet-routing controls (since 1.84.0)

iOS adds a subnet-routing toggle. Version 1.84.1 corrects an unintended
default-off state for subnet routing on both iOS and Android.

### iOS exit-node hosting (since 1.98.1)

An iOS device can act as an exit node.

### Apple TV authentication and management

Apple TV can authenticate to a tailnet with an auth key, including with a
custom coordination server (since 1.80.0). Apple TV devices can be managed
remotely through the Tailscale web client (since 1.102.2).

## Windows

### Signing certificate rotation (since 1.84.0)

Windows 1.84.2 uses a new code-signing certificate. Its subject and issuer are
unchanged, but its serial number differs. Update deployments that allowlist
the signing certificate by serial number.

### Proxy compatibility corrections (since 1.86.0)

Proxy auto-detection and PAC handling are improved on Windows 10 version 1607
and earlier.

## Linux and Unix desktops

### Taildrive without `su` (since 1.88.1)

Taildrive folder sharing works on Linux and other Unix-like systems that lack
the `su` command, and shared files remain consistently accessible.

### Desktop tray controls (since 1.88.1)

Linux desktops can enable the system tray application for controls including
fast user switching and exit-node selection.

### Systray autostart (since 1.96.2)

Enable startup through a freedesktop autostart file:

```console
tailscale configure systray --enable-startup=freedesktop
```

### OpenWrt updates (since 1.96.2)

Tailscale updates work on OpenWrt 25.12.0 and later when `apk` is the package
manager.

## macOS

### Managed reconnect and onboarding (since 1.86.0)

`ReconnectAfter` caps how long a user can remain disconnected.
`OnboardingFlow` suppresses installation onboarding and replaces the
deprecated `TailscaleOnboardingSeen` policy.

### Proxy and exit-node policies (since 1.88.1)

`UseSystemProxy` controls whether Tailscale respects proxy settings from
System Settings. The `advertiseExitNode` system policy is also available.

### Supported operating system (since 1.88.1)

macOS 12 is the minimum supported version.

### Taildrive sharing UI (since 1.90.1)

The macOS client no longer provides `tailscale drive`. Share Taildrive
directories through the client GUI.

### Authentication browser and Dock icon (since 1.94.1)

`AuthBrowser.macos` chooses the preferred browser for automatic authentication
URLs. `HideDockIcon` controls whether the Dock icon remains after all
Tailscale windows close.

### Release-candidate channel (since 1.94.1)

The About section's **Release Channel** menu can install release-candidate
client versions and keep them automatically updated.

### Windowed UI (since 1.96.2)

Windowed UI mode is generally available. Double-click an account in the
Accounts section to switch to it.

### Open-source posture reporting (since 1.96.2)

The open-source macOS variant sets the `node:osVersion` posture attribute.

### Standalone backup behavior (since 1.96.2)

The Standalone macOS client excludes its Tailscale data directories from Time
Machine backups.

### First-run introduction (since 1.98.1)

`AppIntroShown` suppresses the **Welcome to the Tailscale app** modal after the
first device login.

### Deep links (since 1.102.2)

The macOS protocol handler can open devices, exit nodes, and settings panels
directly in the application window.

## NAS packages

### QNAP availability (since 1.88.1)

QNAP builds resumed first as manual downloads from the packages site and then
through QNAP App Center.

### Synology ARMv7 compatibility (since 1.102.2)

Affected Synology NAS models receive ARMv7 binaries built with software
floating-point support instead of the older ARMv5 binaries.
