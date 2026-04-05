# TwinCAT for Linux & Docker Containers

## TwinCAT RT Linux Runtime
TwinCAT 3.1 XAR (eXtended Automation Runtime) runs on Beckhoff RT Linux as a usermode systemd service. Packages come from `deb.beckhoff.com` (requires myBeckhoff credentials).

```bash
# Install runtime
sudo apt install tc31-xar-um

# Check service status
sudo systemctl status TcSystemServiceUm

# System configuration tools
sudo apt install tcsysconf
```

Service name is `TcSystemServiceUm` — the `Um` suffix indicates usermode (vs kernel-mode on Windows).

## Docker Containerized TwinCAT XAR
TwinCAT XAR can run in Docker containers on Beckhoff RT Linux IPCs. This enables multiple isolated TwinCAT runtime instances on a single IPC. Official sample: `github.com/Beckhoff/TC_XAR_Container_Sample`.

**Key architecture**: Containers communicate via **ADS-over-MQTT** (not direct ADS routes). A Mosquitto broker runs as a sidecar container.

```bash
# Build image — uses Docker secrets for Beckhoff package server credentials
# Credentials go in ./tc31-xar-base/apt-config/bhf.conf
sudo docker build --secret id=apt,src=./apt-config/bhf.conf --network host -t tc31-xar-base .

# Or via Makefile wrapper
sudo make build-image

# Start containers (TwinCAT XAR + Mosquitto broker)
sudo docker compose up -d
```

**ADS-over-MQTT connection from Engineering PC**: Copy the provided `mqtt.xml` template (with container host IP) to `C:\Program Files (x86)\Beckhoff\TwinCAT\3.1\Target\Routes\` and restart TwinCAT System Service.

## Real-Time Ethernet in Containers
Requires `vfio-pci` driver for PCI network devices. Use `TcRteInstall` CLI tool:

```bash
# List available network devices
sudo TcRteInstall -l

# Assign VFIO driver to a PCI device by location
sudo TcRteInstall -b <PCI-device-location>

# Restart container to pick up new config
sudo make restart-containers
```

## Firewall for MQTT (nftables)
Container ADS-over-MQTT requires port 1883 open. Create `/etc/nftables.conf.d/60-mosquitto-container.conf`:

```
table inet filter {
  chain input {
    tcp dport 1883 accept
  }
  chain forward {
    type filter hook forward priority 0; policy drop;
    tcp sport 1883 accept
    tcp dport 1883 accept
  }
}
```

```bash
sudo nft -f /etc/nftables.conf.d/60-mosquitto-container.conf
```
