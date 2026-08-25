# Home Manager

## Activation, profiles, and generations

### User-service activation

`systemd.user.startServices` defaults to `true` from nixos-25.05, so activation
restarts user services as necessary. The removed `"legacy"` value causes an
evaluation error; `"suggest"` remains only as a temporary compatibility mode.

For homes unavailable at system boot, nixos-26.05 adds
`home-manager.startAsUserService`. It defers activation until login and works
with late-mounted homes such as those provided by `pam_mount`.

### Rollbacks and specialisations

Nixos-25.11 adds profile-preserving switches:

```sh
home-manager switch --rollback
home-manager switch --specialisation work
```

Rollback selects the generation before the current one without creating an
extra profile generation. A specialisation switch directly activates the
named specialisation with the same preservation behavior.

### Profile ownership

Updating the Home Manager Nix profile from a generated activation script is
deprecated in nixos-25.11. Tools invoking that script directly must update the
profile themselves. The NixOS and nix-darwin modules no longer create
per-user shadow profiles; set
`home-manager.enableLegacyProfileManagement = true` only as a temporary
migration aid.

### Minimal module imports

`home-manager.minimal = true` imports only the modules required for Home
Manager itself (nixos-25.11). Every program, service, and other nonessential
module must then be imported explicitly.

### Package-provided services

The nixos-26.05 `home.services` namespace turns Nixpkgs modular services such
as `pkgs.<name>.passthru.services.default` into user systemd units without
duplicating the packaged module.

## State-version behavior

### Signing and application locations

For `home.stateVersion = "25.05"` or newer,
`programs.git.signing.format` does not default to `"openpgp"`; select it
explicitly for GPG signing.

At state version 25.11, Password Store again defaults to
`$HOME/.password-store` rather than `$XDG_DATA_HOME/password-store`. On macOS,
packages are copied to `~/Applications/Home Manager Apps` by default through
`targets.darwin.copyApps.enable`, replacing symlink-based application exposure.

### XDG defaults in state version 26.05

When XDG is enabled, Zsh and Docker configuration moves under XDG paths and
Linux Firefox moves to `$XDG_CONFIG_HOME/mozilla/firefox`.
`xdg.userDirs.setSessionVariables` defaults to `false`. Keys under
`xdg.userDirs.extraConfig` should omit both the `XDG_` prefix and `_DIR`
suffix.

### Configuration formats in state version 26.05

Neovim plugin `config` fragments are interpreted as Lua. Hyprland generation
changes from Hyprlang to Lua; pin
`wayland.windowManager.hyprland.configType = "hyprlang"` to retain the old
format during migration.

### Automation defaults in state version 26.05

Automatic upgrades no longer run `nix flake update`. Restore it explicitly if
required:

```nix
services.home-manager.autoUpgrade.preSwitchCommands = [
  "nix flake update"
];
```

Mergiraf integration for Git and Jujutsu defaults off, Yazi's shell wrapper is
named `y`, and GTK 4 no longer inherits `gtk.theme`.

## Program configuration migrations

### SSH and agent integration

Use RFC 42-style `programs.ssh.settings` in nixos-26.05.
`programs.ssh.matchBlocks` is deprecated and automatically migrated. The
`sshAuthSock` module supplies shell integration for agent providers, replacing
the removed `services.ssh-agent.enableBashIntegration`,
`enableZshIntegration`, `enableFishIntegration`, and
`enableNushellIntegration` options.

### Firefox, Anki, and Thunderbird profiles

The removed top-level `programs.firefox.extensions` list moves to each
profile's `extensions.packages` or `extensions.settings` (nixos-26.05). Move
Anki synchronization under `programs.anki.profiles."User 1".sync`; `uiScale`
accepts values from 1.0 through 2.0.

Thunderbird supports EWS accounts. For the `outlook.office365.com` flavor,
unspecified IMAP and SMTP authentication defaults to OAuth2.

### Syncthing

The Boolean `services.syncthing.tray` form is removed in nixos-25.11. Use:

```nix
services.syncthing.tray.enable = true;
```

In nixos-26.05, move Syncthing credentials from
`services.syncthing.passwordFile` to `services.syncthing.guiCredentials`.

### Editors, viewers, and wallpaper services

For nixos-26.05:

- Configure VS Code forks through their dedicated modules rather than setting
  `programs.vscode.package`.
- Choose exactly one of `programs.man.man-db.enable` and
  `programs.man.mandoc.enable`.
- Rename `programs.neovim.extraLuaConfig` to `programs.neovim.initLua`.
- Rename `services.swww` to `services.awww`.
- Move tool instruction options to their shared `context` structure.
- Replace free-form Aerospace and aria2 configuration with structured
  `settings`.

## External Nix and Darwin integration

`nix.assumeXdg` supports Nix installations using XDG base directories outside
Home Manager in nixos-26.05. The NixOS setting
`nix.settings.use-xdg-base-directories` is detected automatically.

On Darwin, launchd agents wait for `/nix/store`, replacement activation waits
for `bootout`, nix-darwin dry-run reaches user activation, and
`TERMINFO_DIRS` includes terminfo supplied by installed packages.
