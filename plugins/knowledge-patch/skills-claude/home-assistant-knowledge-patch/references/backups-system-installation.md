# Backups, System Operations, and Installation

Use the version attributions on individual entries when exact behavior matters.

## Backup creation, storage, and restore

### Backup setup and scheduling (2025.1)

The first visit to backup settings after upgrading opens a wizard for the encryption key, frequency, and retention policy, then starts the first backup. Scheduled jobs run around 04:45 after database maintenance; **Back up now** reuses the scheduled configuration, failures create Repair issues, and 2025.1.2 adds start-time jitter.

### Backup retention and contents (2025.1)

Retention cleanup runs after automatic backups and never deletes manually created backups; existing custom backup add-ons, automations, and blueprints remain compatible. As of 2025.1.3, backups always include the SSL folder.

### Mandatory encryption and universal restore (2025.1)

All backups now use AES-128 encryption by default with a mandatory generated encryption key, which can be saved in an emergency kit and is required for restoration. Restore is now supported by every installation method, including Container installations, and can read local, Cloud, or integration-provided backup locations.

### Cloud and integration-provided backup locations (2025.1)

Home Assistant Cloud subscribers can keep their latest fully encrypted backup in 5 GB of included storage and download it either from Home Assistant or the Cloud account page. The location API is extensible, but in 2025.1 no integration provides another target yet.

### Per-location backup encryption (2025.2)

Encryption can now be disabled separately for each backup location, except Home Assistant Cloud, which is always encrypted. Downloads made through the Home Assistant interface are always delivered unencrypted, decrypting an encrypted stored backup on the fly.

### Custom and automation-driven backup schedules (2025.2)

Automatic backups can run at a chosen time, and weekly schedules can select specific weekdays. Advanced schedules can invoke the new automatic-backup action:

```yaml
actions:
  - action: backup.create_automatic
```

### Backup-before-update behavior (2025.2)

On Home Assistant OS, the backup toggle returns to Core and add-on update dialogs, is off by default, and shows the last backup time. Enabling it for Core creates a full automatic backup synced to all configured locations; for an add-on it backs up only that add-on and its data, retaining one automatic update backup per add-on while leaving manual backups untouched.

### Backup storage and retention refinements (2025.2)

Backup filenames now contain their creation date and time; Google Drive and OneDrive are new backup-location integrations, and Synology DSM can also provide a location. As of 2025.2.2 retention keeps one backup per backup agent, and 2025.2.5 rejects retention settings of zero days or zero copies.

### Backup locations and new integrations (2025.3)

Azure Storage and WebDAV can now serve as backup targets. New integrations also add local IOmeter access, PG LAB Electronics control, SensorPush Cloud devices, and SNOO bassinet state.

### Cloud-backup restore during onboarding (2025.4)

A Home Assistant Cloud subscriber can select and restore a Cloud backup directly during a new installation's onboarding flow, including when replacing or migrating hardware.

### Hardware-update and backup sensors (2025.4)

The Zigbee/Thread chip in Home Assistant Yellow and the Home Assistant ZBT-1 can now receive firmware through update entities. The Backup integration also provides status sensors, including information about when the last backup ran.

### Per-location backup retention (2025.5)

Each configured backup location can now have its own retention policy, allowing different limits for destinations with different storage capacities.

### Upgrade and restart backup safeguards (2025.5)

The Home Assistant Operating System update dialog can create a backup using the automatic-backup settings, upload it to every enabled location, and then begin the upgrade; backup settings can also choose whether pre-upgrade backup toggles default on, with a separate preference for add-ons. A requested restart now waits for an in-progress backup to finish.

### Backup and subscription diagnostics (2025.6)

An incomplete backup now raises a Repair issue when any add-on or folder was not successfully backed up, and an automatic-backup event entity tracks automatic backups. Home Assistant Cloud also raises a Repair issue for an expired subscription.

### Backup-related patch fixes (2026.2)

Version 2026.2.1 corrects multipart R2 and S3 backup uploads to use consistent part sizes. Version 2026.2.2 adds a timeout to Backblaze B2 metadata downloads so a backup cannot hang indefinitely.

### New backup locations (2026.3)

IDrive e2 provides an S3-compatible backup target, while OneDrive for Business provides a Microsoft 365 business backup target distinct from the existing personal OneDrive integration.

### Backup upload progress (2026.4)

The backup page now distinguishes creation from upload and can show per-location upload percentages for Cloud, WebDAV, Google Drive, both OneDrive integrations, S3-compatible targets, and Supervisor backups. Custom backup agents can report upload progress through the corresponding developer interface.

## System and update operations

### Storage insights (2025.9)

**Settings > System > Storage** now shows disk-usage metrics to identify what is consuming storage.

### Core and add-on update progress (2025.11)

Supervisor-managed Home Assistant and add-on updates now report progress through stages such as downloading and unpacking. Progress is an estimate and may not advance linearly.

### Home Assistant OS log-file removal (2025.11)

Home Assistant OS no longer duplicates Core logs into the configuration-folder log file. Logs remain viewable and downloadable under **Settings > System > Logs** and accessible through `ha core logs`.

### Optional duplicate Core log file (2026.1)

Home Assistant OS can re-enable the Core log file that stopped being duplicated in 2025.11. The official Terminal & SSH add-on must be version 9.22.0 or newer to use this option; the Advanced SSH & Web Terminal add-on did not yet support it at this release.

### Add-ons are now Apps (2026.2)

Home Assistant OS-managed standalone software is now called **Apps** throughout the interface; older material may still say “add-ons,” and searches for that term are redirected. Apps run alongside Home Assistant, whereas integrations connect Home Assistant to devices and services.

### Supervisor action failures (2026.5)

Supervisor actions such as `hassio.addon_start`, `hassio.backup_partial`, and `hassio.host_reboot` now raise on failure, stopping scripts and automations by default. Add `continue_on_error: true` to an action step only when the previous continue-after-failure behavior is required.

### Apps management page (2026.6)

Installed Apps are now presented as status-bearing cards with descriptions and optional tags, and the detail layout is redesigned for desktop and tablet use.

### Grouped updates and Update all (2026.7)

The Updates page now groups pending updates into Home Assistant, per-integration, remaining integrations, Apps, and Skipped cards; a card-level **Update all** applies that group without a confirmation dialog. Core, Operating System, and Supervisor updates intentionally have no bulk button, and skipped updates are never included.

### Raspberry Pi bootloader updates (2026.7)

Home Assistant OS 18 or newer exposes supported Raspberry Pi bootloader/EEPROM firmware as an update entity and requests a reboot after installation. The entity is unavailable for a Pi 4 booting from USB, Home Assistant Yellow with Compute Module 4, and other unsupported boards; Pi 4 updates require booting from SD card.

## Installation, runtime, and architecture

### Container networking repair (2025.5)

A Home Assistant Container installation that is not using host networking is now detected and raises a Repair issue.

### Installation and architecture deprecations (2025.6)

Home Assistant Core and Supervised installations, plus `i386`, `armhf`, and `armv7` architectures, are deprecated; affected systems raise a Repair issue, and Home Assistant OS and Container are the supported installation methods going forward. Deprecated installations receive support only until Home Assistant 2025.12, after which they receive neither updates nor official assistance.

### Unsupported installations and architectures (2025.12)

The earlier deprecation is now complete: Home Assistant Core and Supervised installations and the `i386`, `armhf`, and `armv7` architectures no longer receive updates, including security updates. Migrate to a supported installation method and architecture.

### Python 3.14 runtime (2026.3)

Home Assistant now runs on Python 3.14. Officially supported installation methods perform the runtime upgrade automatically during a normal Home Assistant update.

### Container image compression requirement (2026.3)

Container images are now compressed with `zstd` instead of `gzip`. Updating requires Docker 23.0.0 or newer or containerd 1.5.0 or newer, unless the older runtime otherwise supports `zstd` images.

### Web server defaults and UI configuration (2026.8.0)

New Home Assistant OS installations use a normal address without an explicit `:8123`, while existing installations keep their current port. The port, listening network connection, and trusted proxies can now be managed in the UI with automatic rollback after five unconfirmed minutes; existing YAML settings are imported on first startup and a Repair can guide removal of the old YAML.
