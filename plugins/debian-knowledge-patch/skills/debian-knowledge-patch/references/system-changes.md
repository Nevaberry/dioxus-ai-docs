# Debian 13 (Trixie) System Changes

## /tmp as tmpfs

Default for trixie: `/tmp` is a tmpfs filesystem (stored in RAM). Allocates up to 50% of physical memory (only used when files are created).

### For upgraded systems

New behavior starts after reboot. Old files in `/tmp` hidden by new mount. Access via:

```bash
mount --bind / /mnt
# Old files at /mnt/tmp
umount /mnt # after cleanup
```

### Customize size

```bash
systemctl edit tmp.mount
```

Add:
```ini
[Mount]
Options=mode=1777,nosuid,nodev,size=2G
```

### Revert to directory

```bash
systemctl mask tmp.mount
# Reboot required
```

Systems with `/tmp` already in `/etc/fstab` are unaffected.

### tmpreaping

New installs get automated cleanup of `/tmp` and `/var/tmp`. Opt-in for upgraded systems (see systemd NEWS.Debian.gz).

## Login Tracking Replacements

The old utmp/wtmp/lastlog files use a format with Y2038 bug. Replacements:

### last -> wtmpdb

```bash
apt install wtmpdb libpam-wtmpdb
wtmpdb # shows login history
# Can import old data: wtmpdb import -f <dest>
```

### lastlog -> lastlog2

```bash
apt install lastlog2 libpam-lastlog2
lastlog2 # shows last login times
```

### lastb -> lslogins

```bash
lslogins --failed # shows failed login attempts
lslogins          # shows when accounts last used
```

### Cleanup

Without wtmpdb installed, remove `/var/log/wtmp*`. Files `/var/log/lastlog*` and `/var/log/btmp*` can be deleted after upgrade (no tool to read them).

### Other util-linux changes

- `mesg` and `write` removed from util-linux-extra
- `exch` and `waitpid` added to util-linux-extra
- New `lslogins` command

## OpenSSH Changes

### DSA Keys Completely Removed

As of OpenSSH 9.8p1 in trixie, DSA keys are no longer supported even with configuration options. For legacy devices, use `ssh1` from `openssh-client-ssh1`.

Generate replacement keys:
```bash
ssh-keygen -t ed25519
ssh-copy-id username@server
```

Check current key type: add `-v` to ssh command, look for "Server accepts key:" line.

### ~/.pam_environment No Longer Read

SSH daemon no longer reads `~/.pam_environment` by default (deprecated for security reasons). Move environment variables to shell init files (`~/.bash_profile`, `~/.bashrc`).

### Interrupted Remote Upgrades

OpenSSH bug in bookworm can cause inaccessible systems if upgrade is interrupted. Update OpenSSH to >= 1:9.2p1-2+deb12u7 via stable-updates before upgrading.

## systemd-cryptsetup Split

Encrypted filesystem support moved from systemd to separate `systemd-cryptsetup` package (recommended by systemd, should auto-install). **Verify it's installed before rebooting.**

## Plain-mode dm-crypt Defaults Changed

New defaults:
- cipher: `aes-xts-plain64` (was `aes-cbc-essiv:sha256`)
- hash: `sha256` (was `ripemd160`)

For existing plain-mode devices using old defaults, add to `/etc/crypttab`:
```
cipher=aes-cbc-essiv:sha256,size=256,hash=ripemd160
```

For command line:
```bash
cryptsetup --cipher aes-cbc-essiv:sha256 --key-size 256 --hash ripemd160
```

LUKS devices store settings internally and are unaffected.

## systemd run0

New privilege escalation tool. Like sudo: checks "sudo" group membership, asks for user's password. Shipped with systemd 257.

## apt modernize-sources

Converts legacy one-liner sources.list format to deb822 format:

```bash
apt modernize-sources
```

## /usr Merge Complete

All trixie systems have merged `/usr`. Packages `usrmerge` and `usr-is-merged` are removable dummy packages.

## 64-bit time_t ABI Transition

All architectures except i386 now use 64-bit `time_t`. On 32-bit arches (armel, armhf), many library ABIs changed without soname changes. Third-party binaries need recompilation. Check for silent data loss.

i386 did not participate (legacy support only).
