# RTKBase settings.conf Reference

RTKBase uses `settings.conf` in INI format. The web GUI reads and writes this file; `run_cast.sh` parses it to launch `str2str` services.

## Complete Section Reference

### [general]

```ini
[general]
version=2.7.0
web_port=80
web_authentification=true
new_web_password=           # Set once, hashed on next web server start
maptiler_key=               # Optional: aerial imagery layer in web GUI
```

### [main]

```ini
[main]
position='47.0983 -1.2655 36.40'   # lat lon height (WGS84)
com_port=''                         # /dev/ttyGNSS0, /dev/ttyUSB0, etc.
com_port_settings='38400:8:n:1'     # baud:databits:parity:stopbits
receiver='unknown'                  # u-blox_zed-f9p, mosaic-x5, unicorecomm
receiver_format=''                  # ubx, rtcm3, oem3, etc.
antenna_info='ADVNULLANTENNA'       # IGS antenna designator
tcp_host_addr='127.0.0.1'          # Bind addr; 0.0.0.0 for external access
tcp_port='5015'                     # Main TCP stream port
gnss_rcv_web_ip=192.168.3.1        # Mosaic-X5 web interface IP
gnss_rcv_web_proxy_port=9090        # Flask reverse proxy port for receiver UI
nmea_port='5014'                    # raw2nmea output port
```

### [local_storage]

```ini
[local_storage]
datadir=$BASEDIR/data
file_name='%Y-%m-%d_%h-%M-%S_GNSS-1'   # strftime format
file_rotate_time='24'               # Hours per file
archive_rotate='60'                 # Days before deletion
min_free_space='500'                # MB minimum free space
```

### [ntrip_A] and [ntrip_B]

Both sections have identical structure (suffix `_a` or `_b`):

```ini
[ntrip_A]
svr_addr_a='caster.centipede.fr'
svr_port_a='2101'
svr_pwd_a=''
mnt_name_a='Your_mount_name'
rtcm_msg_a='1004,1005(10),1006,1008(10),1012,1019,1020,1033(10),1042,1045,1046,1077,1087,1097,1107,1127,1230'
ntrip_a_receiver_options=''         # e.g. '-TADJ=1' for u-blox
```

### [local_ntrip_caster]

```ini
[local_ntrip_caster]
local_ntripc_user=''
local_ntripc_pwd=''
local_ntripc_port='2101'
local_ntripc_mnt_name=''
```

### [rtcm_svr] and Related Sections

```ini
[rtcm_svr]
rtcm_svr_port='5016'

# Also available: [rtcm_client], [rtcm_serial], [rtcm_udp_svr], [rtcm_udp_client]
```

### [log]

```ini
[log]
level=0                             # str2str trace level (0=off, higher=more verbose)
```

### [network]

```ini
[network]
modem_at_port=''                    # 4G Simcom A76XX modem AT port
```

## RTCM Message Rate Syntax

In the `rtcm_msg` fields, message rates are specified as:

- `1004` = send every epoch
- `1005(10)` = send every 10th epoch
- Messages are comma-separated

Common RTCM message set for multi-constellation:
```
1004,1005(10),1006,1008(10),1012,1019,1020,1033(10),1042,1045,1046,1077,1087,1097,1107,1127,1230
```
