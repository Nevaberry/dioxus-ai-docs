# Security & Networking

## SELinux (Replaces AppArmor)

SELinux is enforcing by default in SUSE 16 with policies for 400+ modules. AppArmor is no longer the default security framework.

### Common Operations

```bash
# Check current mode
sestatus
getenforce # "Enforcing" or "Permissive"

# Temporarily switch to permissive (for debugging only)
setenforce 0

# Permanently change mode (edit and reboot)
# /etc/selinux/config
# SELINUX=permissive
```

### Managing Booleans

```bash
# List all booleans
getsebool -a

# Set a boolean persistently
setsebool -P httpd_can_network_connect on
setsebool -P container_manage_cgroup on
```

### Troubleshooting Denials

```bash
# View recent AVC denials
ausearch -m AVC -ts recent

# Generate a policy module from denials
ausearch -m AVC -ts recent | audit2allow -M mypolicy
semodule -i mypolicy.pp

# Check what context a file should have
matchpathcon /var/www/html/index.html

# Restore file contexts
restorecon -Rv /var/www/html/
```

### File Contexts

```bash
# View file context
ls -Z /path/to/file

# Set custom file context
semanage fcontext -a -t httpd_sys_content_t "/srv/www(/.*)?"
restorecon -Rv /srv/www/

# Port labeling (e.g., allow httpd on non-standard port)
semanage port -a -t http_port_t -p tcp 8080
```

## NetworkManager (wicked Removed)

`wicked` is fully removed. NetworkManager is the sole network stack.

### Interface Naming

SUSE 16 uses systemd predictable naming (different from SUSE 15's persistent naming scheme). For custom naming, use `systemd.link` files:

```ini
# /etc/systemd/network/10-custom.link
[Match]
MACAddress=00:11:22:33:44:55

[Link]
Name=lan0
```

### Common nmcli Operations

```bash
# List connections
nmcli connection show

# Add static IP connection
nmcli connection add type ethernet con-name static-eth0 ifname enp0s3 \
  ipv4.method manual ipv4.addresses 192.168.1.10/24 ipv4.gateway 192.168.1.1 \
  ipv4.dns "8.8.8.8 8.8.4.4"

# Add VLAN
nmcli connection add type vlan con-name vlan100 dev enp0s3 id 100

# Add bond
nmcli connection add type bond con-name bond0 bond.options "mode=802.3ad,miimon=100"
nmcli connection add type ethernet slave-type bond con-name bond0-port1 ifname enp0s3 master bond0
nmcli connection add type ethernet slave-type bond con-name bond0-port2 ifname enp0s4 master bond0

# Bring connection up/down
nmcli connection up static-eth0
nmcli connection down static-eth0
```

## SSH Root Password Login Disabled

New SUSE 16 installs disable password-based SSH for root by default:

- If no SSH key is provided during install, `sshd` won't be enabled at all
- Key-based authentication is the expected default

```bash
# Restore password login (not recommended for production)
zypper install openssh-server-config-rootlogin

# Better: ensure SSH key is provided during Agama install
```
