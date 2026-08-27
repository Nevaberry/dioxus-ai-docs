# Home Manager

## Activation, profiles, and switching

### User-service activation (since nixos-25.05)

`systemd.user.startServices` defaults to `true`, so activation restarts user
services when needed. The removed `"legacy"` mode fails evaluation;
`"suggest"` remains temporarily.

### Rollback and specialisation switching (since nixos-25.11)

`home-manager switch --rollback` activates the generation before the current
one without adding a profile generation. `home-manager switch
--specialisation NAME` directly activates a named specialisation with the
same profile-preserving behavior.

### Profile ownership (since nixos-25.11)

Generated activation scripts updating the Home Manager Nix profile is
deprecated; callers invoking scripts directly must update the profile.
NixOS/nix-darwin module use no longer creates shadow per-user profiles.
`home-manager.enableLegacyProfileManagement = true` temporarily restores the
old behavior.

### Minimal module imports (since nixos-25.11)

`home-manager.minimal = true` imports only modules essential to Home Manager.
Import every program or service module needed by the configuration explicitly.

### Login-time activation (since nixos-26.05)

`home-manager.startAsUserService` defers activation until login, supporting
homes mounted later by mechanisms such as `pam_mount`.

### Package-provided services (since nixos-26.05)

The `home.services` namespace lifts packaged modular services such as
`pkgs.<name>.passthru.services.default` into user systemd units.

## State-gated paths and behavior

### Git signing at state version 25.05 (since nixos-25.05)

With `home.stateVersion = "25.05"` or newer,
`programs.git.signing.format` no longer defaults to `"openpgp"`. GPG signing
must set it explicitly.

### State version 25.11 defaults (since nixos-25.11)

Password Store returns to `$HOME/.password-store` rather than
`$XDG_DATA_HOME/password-store`. On macOS, `home.packages` applications are
copied to `~/Applications/Home Manager Apps` through
`targets.darwin.copyApps.enable`, replacing the earlier symlink default.

### XDG defaults at state version 26.05 (since nixos-26.05)

When XDG is enabled, Zsh and Docker configuration move to XDG paths and Linux
Firefox moves to `$XDG_CONFIG_HOME/mozilla/firefox`.
`xdg.userDirs.setSessionVariables` defaults to `false`; keys in
`xdg.userDirs.extraConfig` omit both `XDG_` and `_DIR`.

### Generated formats at state version 26.05 (since nixos-26.05)

Neovim plugin `config` fragments are Lua, and Hyprland generation defaults to
Lua instead of Hyprlang. Pin
`wayland.windowManager.hyprland.configType = "hyprlang"` to retain the old
format.

### Automation defaults at state version 26.05 (since nixos-26.05)

Automatic upgrades no longer run `nix flake update`; restore it with
`services.home-manager.autoUpgrade.preSwitchCommands` if intended. Mergiraf
Git and Jujutsu integration defaults off, Yazi's shell wrapper becomes `y`,
and GTK 4 no longer inherits `gtk.theme`.

## Program and service migrations

### Syncthing tray option (since nixos-25.11)

The Boolean `services.syncthing.tray` was removed. Use
`services.syncthing.tray.enable = true`.

### SSH configuration and auth sockets (since nixos-26.05)

Use RFC 42-style `programs.ssh.settings`; `programs.ssh.matchBlocks` is
deprecated and automatically migrated. The `sshAuthSock` module supplies
shell integration for SSH-agent providers, replacing removed
`services.ssh-agent.enable{Bash,Zsh,Fish,Nushell}Integration` options.

### Per-profile application migrations (since nixos-26.05)

Firefox extensions move from removed `programs.firefox.extensions` to each
profile's `extensions.packages` or `extensions.settings`. Anki sync settings
move below `programs.anki.profiles."User 1".sync`, and `uiScale` accepts
1.0–2.0. Thunderbird supports EWS; the `outlook.office365.com` flavor defaults
unspecified IMAP and SMTP authentication to OAuth2.

### Renamed and split modules (since nixos-26.05)

Migrate the following:

- `services.syncthing.passwordFile` → `guiCredentials`.
- VS Code forks → their dedicated modules, not `programs.vscode.package`.
- Man viewer selection → exactly one of `programs.man.man-db.enable` or
  `programs.man.mandoc.enable`.
- `programs.neovim.extraLuaConfig` → `initLua`.
- `services.swww` → `services.awww`.
- Assistant-specific instruction options → their common `context` shape.
- Free-form Aerospace and aria2 configuration → structured `settings`.

## External Nix and Darwin integration

### XDG-aware Nix and Darwin activation (since nixos-26.05)

`nix.assumeXdg` supports Nix installations using XDG base directories outside
Home Manager; NixOS's `nix.settings.use-xdg-base-directories` is detected
automatically. Darwin launchd agents wait for `/nix/store`, activation
replacement waits for `bootout`, nix-darwin dry-run reaches user activation,
and `TERMINFO_DIRS` exposes package-provided terminfo.
