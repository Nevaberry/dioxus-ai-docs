# Agama Installer & System Management

## Agama Replaces YaST

YaST and AutoYaST are fully removed in SUSE 16 (both SLES and openSUSE Leap). The new **Agama** installer provides:

- **Web UI**: Browser-based interactive installation (accessible on port 9090 during install)
- **CLI**: `agama` command for scripted and headless installs
- **HTTP API**: RESTful API for full automation

### Agama Profiles (Replacing AutoYaST XML)

Unattended installs use Agama profiles (JSON or Jsonnet format) instead of AutoYaST XML:

```bash
# Import and apply a profile
agama profile import profile.json
agama install

# Profiles support repeated config import (additive)
agama profile import base.json
agama profile import site-specific.json
agama install
```

Key differences from AutoYaST:
- JSON/Jsonnet format instead of XML
- Profiles are additive (can layer multiple profiles)
- HTTP API allows dynamic profile generation
- No 1:1 mapping from AutoYaST XML — profiles must be rewritten

## Post-Install Management Replacements

| YaST Module | SUSE 16 Replacement |
|-------------|---------------------|
| YaST remote administration | **Cockpit** (web-based, port 9090) |
| AutoYaST config management | **Salt** or **Ansible** |
| YaST firewall | `firewall-cmd` (firewalld) |
| YaST network | `nmcli` / `nmtui` (NetworkManager) |
| YaST user management | Standard `useradd`/`usermod` or Cockpit |
| YaST disk partitioner | Cockpit storage or CLI tools (`parted`, `lvm`) |

### Cockpit

Cockpit provides a web-based management interface on port 9090:

```bash
# Enable and start Cockpit
systemctl enable --now cockpit.socket

# Access at https://<hostname>:9090
```

SUSE-specific Cockpit modules: `cockpit-subscriptions`, `cockpit-repositories`, `cockpit-packages`, `cockpit-packagekit`, `cockpit-selinux`. The `cockpit` pattern installs the full set.

### Kdump Configuration

With YaST removed, configure kdump via `kdumptool` and `/etc/sysconfig/kdump`:

```bash
# Key variables in /etc/sysconfig/kdump:
# KDUMP_CRASHKERNEL - memory reserved for crash kernel
# KDUMP_UPDATE_BOOTLOADER - auto-update bootloader config
```

**Note**: Kdump is NOT enabled by default in SLES 16.0 (fix planned for 16.1).
