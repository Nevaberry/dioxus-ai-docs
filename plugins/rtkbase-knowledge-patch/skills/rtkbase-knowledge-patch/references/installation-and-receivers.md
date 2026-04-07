# RTKBase Installation & Receiver Support

## install.sh Flags

```bash
sudo ./install.sh --all release          # Full install from latest release
sudo ./install.sh --all repo --rtkbase-repo dev  # Install from git branch
sudo ./install.sh --detect-gnss          # Detect receiver model and port
sudo ./install.sh --detect-gnss --configure-gnss  # Detect + configure receiver
sudo ./install.sh --dependencies         # Install apt packages only
sudo ./install.sh --rtklib               # Compile RTKLib (v2.5.0-EX)
sudo ./install.sh --unit-files           # Deploy systemd services
sudo ./install.sh --gpsd-chrony          # Setup time sync (gpsd + chrony)
sudo ./install.sh --start-services       # Start all services
sudo ./install.sh --user=john            # Install as specific user
```

`--all` combines: `--dependencies --rtklib --unit-files --gpsd-chrony --detect-gnss --configure-gnss --start-services`.

## Supported GNSS Receivers

### u-blox ZED-F9P

- **Detection**: USB + UART
- **Raw format**: `ubx`
- **Full support**: raw logging, PPP processing, rtkrcv solutions
- **Recommended**: `-TADJ=1` receiver option (set via `ntrip_a_receiver_options`)
- **Behavior**: Dynamic model automatically set to static mode

### Septentrio Mosaic-X5

- **Detection**: USB
- **Raw format**: `rtcm3` for streaming, SBF for logging
- **Web UI**: Built-in receiver web interface at `gnss_rcv_web_ip` (default `192.168.3.1`)
- **Reverse proxy**: Flask proxies receiver UI on `gnss_rcv_web_proxy_port` (default `9090`)
- **Default credentials**: `basegnss/basegnss!`

### Unicore UM980/UM982

- **Detection**: Auto-detect
- **Raw format**: `rtcm3` only
- **Limitation**: No raw binary format support in RTKLIB, so no PPP or rtkrcv solutions
- **RTCM3 streaming**: Works for NTRIP caster relay

## Requirements

- **OS**: Debian >= 12 (Bookworm) / Ubuntu >= 24.04
- **Python**: >= 3.11
- **RTKLib**: v2.5.0-EX (from rtklibexplorer fork)
- **Default web password**: `admin`
- **Armbian images**: hostname `basegnss.local`, SSH credentials `basegnss/basegnss!`

## REST API

```
GET /api/v1/infos   # Base station info (position, receiver, mount name)
```
