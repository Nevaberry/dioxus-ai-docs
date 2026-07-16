# GKE and Hybrid Cloud

Use this reference for GKE release channels and upgrades, Autopilot, Gateway and load balancing, accelerators, storage, security, and cluster observability.

## Contents

- [Release channels, versions, and upgrades](#release-channels-versions-and-upgrades)
- [Defaults, compatibility, and known issues](#defaults-compatibility-and-known-issues)
- [Networking, gateways, and security](#networking-gateways-and-security)
- [Compute, accelerators, scheduling, and autoscaling](#compute-accelerators-scheduling-and-autoscaling)
- [Storage, telemetry, and workload operations](#storage-telemetry-and-workload-operations)

## Release channels, versions, and upgrades

### Concurrent GKE node-pool upgrades (2026-05)

Preview concurrent upgrades let Standard and Autopilot clusters set a maximum number of node pools for GKE to auto-upgrade simultaneously; the default remains one at a time.

### Expanded GKE maintenance exclusions (2026-06)

Release-channel clusters can apply maintenance exclusions per node pool, and the default **No upgrades** exclusion can now last up to 90 days.

### GKE 2026-R1 channel targets (2026-01)

The `2026-R1` creation defaults became Rapid `1.35.0-gke.1340000`, Regular and Extended `1.33.5-gke.2019000`, Stable `1.33.5-gke.1308000`, and deprecated no-channel `1.33.5-gke.2019000`. General minor auto-upgrades targeted Rapid `1.30→1.31.14-gke.1166000`, `1.31→1.32.9-gke.1728000`, `1.32→1.33.5-gke.2100000`, and `1.33→1.34.1-gke.3947000`; Regular `1.30→1.31.14-gke.1114000`, `1.31→1.32.9-gke.1675000`, and `1.32→1.33.5-gke.2019000`; Stable `1.30→1.31.13-gke.1139000`, `1.31→1.32.9-gke.1239000`, and `1.32→1.33.5-gke.1308000`; Extended `1.27→1.28.15-gke.3251000`, `1.28→1.29.15-gke.2585000`, and `1.29→1.30.14-gke.1820000`; and no-channel `1.30→1.31.14-gke.1114000`, `1.31→1.32.9-gke.1675000`, and `1.32→1.33.5-gke.1308000`.

### GKE 2026-R10 channel targets (2026-03)

The `2026-R10` creation defaults became Regular, Extended, and no-channel `1.34.4-gke.1047000` and Stable `1.33.5-gke.2392000`, while Rapid remained `1.35.1-gke.1396001`. General minor auto-upgrades targeted Rapid `1.31→1.32.12-gke.1127000`, `1.32→1.33.8-gke.1169000`, and `1.33→1.34.4-gke.1193000`; Regular `1.31→1.32.12-gke.1026000`, `1.32→1.33.8-gke.1026000`, and `1.33→1.34.4-gke.1047000`; Stable `1.31→1.32.11-gke.1211000` and `1.32→1.33.5-gke.2392000`; and no-channel `1.31→1.32.12-gke.1026000` and `1.32→1.33.5-gke.2392000`.

### GKE 2026-R11 channel targets (2026-03)

The `2026-R11` creation defaults became Rapid `1.35.2-gke.1269001`, Regular, Extended, and no-channel `1.34.4-gke.1130000`, and Stable `1.33.5-gke.2469000`. General minor auto-upgrades targeted Rapid `1.31→1.32.13-gke.1059000`, `1.32→1.33.9-gke.1060000`, `1.33→1.34.5-gke.1076000`, and `1.34→1.35.2-gke.1269001`; Regular `1.31→1.32.12-gke.1076000`, `1.32→1.33.8-gke.1112000`, and `1.33→1.34.4-gke.1130000`; Stable `1.31→1.32.11-gke.1264000` and `1.32→1.33.5-gke.2469000`; Extended `1.29→1.30.14-gke.2117000`; and no-channel `1.31→1.32.12-gke.1076000` and `1.32→1.33.5-gke.2469000`.

### GKE 2026-R12 channel targets (2026-03)

The `2026-R12` creation defaults became Rapid `1.35.2-gke.1485000`, Regular, Extended, and no-channel `1.35.1-gke.1396002`, and Stable `1.33.8-gke.1026000`. General minor auto-upgrades targeted Rapid `1.31→1.32.13-gke.1090000`, `1.32→1.33.9-gke.1117000`, `1.33→1.34.5-gke.1153000`, and `1.34→1.35.2-gke.1485000`; Regular `1.31→1.32.12-gke.1127000`, `1.32→1.33.8-gke.1169000`, and `1.33→1.34.4-gke.1193000`; Stable `1.31→1.32.12-gke.1026000` and `1.32→1.33.8-gke.1026000`; Extended `1.29→1.30.14-gke.2154000`; and no-channel `1.31→1.32.12-gke.1127000` and `1.32→1.33.8-gke.1026000`.

### GKE 2026-R13 versions (2026-04)

`2026-R13` added Rapid and no-channel versions `1.32.13-gke.1205000`, `1.33.10-gke.1067000`, `1.34.6-gke.1068000`, and `1.35.2-gke.1962000`; Regular and Extended versions `1.32.13-gke.1090000`, `1.33.9-gke.1117000`, `1.34.5-gke.1153000`, and `1.35.2-gke.1485000`; and Stable versions `1.32.12-gke.1127000`, `1.33.8-gke.1169000`, and `1.34.4-gke.1193000`. Extended and no-channel node upgrades also add `1.30.14-gke.2286000` and `1.31.14-gke.1681000`.

### GKE 2026-R14 versions (2026-04)

`2026-R14` added Rapid and no-channel versions `1.32.13-gke.1258000`, `1.33.10-gke.1115000`, `1.34.6-gke.1154000`, and `1.35.3-gke.1234000`; Regular and Extended versions `1.32.13-gke.1147000`, `1.33.9-gke.1166000`, `1.34.5-gke.1208000`, and `1.35.2-gke.1842000`; and Stable versions `1.32.13-gke.1059000`, `1.33.9-gke.1060000`, `1.34.5-gke.1076000`, and `1.35.2-gke.1269001`, with the last becoming the Stable 1.35 auto-upgrade target. Extended and no-channel node upgrades also add `1.30.14-gke.2320000` and `1.31.14-gke.1723000`.

### GKE 2026-R15 versions (2026-04)

`2026-R15` added Rapid and no-channel versions `1.32.13-gke.1318000`, `1.33.10-gke.1176000`, `1.34.6-gke.1237000`, and `1.35.3-gke.1389000`; Regular versions `1.32.13-gke.1205000`, `1.33.10-gke.1067000`, `1.34.6-gke.1068000`, and `1.35.2-gke.1962000`; and Extended versions `1.30.14-gke.2369000` and `1.31.14-gke.1790000`. Stable had no new release.

### GKE 2026-R16 versions (2026-04)

`2026-R16` added Rapid and no-channel versions `1.32.13-gke.1362000`, `1.33.11-gke.1013000`, `1.34.6-gke.1307000`, and `1.35.3-gke.1522000`; Regular versions `1.32.13-gke.1258000`, `1.33.10-gke.1115000`, `1.34.6-gke.1154000`, and `1.35.3-gke.1234000`; and Extended versions `1.30.14-gke.2407000` and `1.31.14-gke.1816000`. Stable had no new release.

### GKE 2026-R17 channel targets (2026-04)

The `2026-R17` creation defaults became Rapid `1.35.3-gke.1522000`, Regular, Extended, and no-channel `1.35.3-gke.1234000`, and Stable `1.33.9-gke.1060000`; Rapid also made GKE `1.36.0-gke.1379000` available. General minor auto-upgrades targeted Rapid `1.31→1.32.13-gke.1362000`, `1.32→1.33.11-gke.1013000`, `1.33→1.34.6-gke.1307000`, and `1.34→1.35.3-gke.1522000`; Regular `1.31→1.32.13-gke.1258000`, `1.32→1.33.10-gke.1115000`, `1.33→1.34.6-gke.1154000`, and `1.34→1.35.3-gke.1234000`; Stable `1.31→1.32.13-gke.1059000` and `1.32→1.33.9-gke.1060000`; Extended `1.29→1.30.14-gke.2320000`; and no-channel `1.31→1.32.13-gke.1258000` and `1.32→1.33.9-gke.1060000`.

### GKE 2026-R18 channel versions (2026-05)

`2026-R18` added Rapid and no-channel versions `1.33.11-gke.1137000`, `1.34.7-gke.1321000`, and `1.35.3-gke.1993000`, plus Rapid `1.36.0-gke.1575000`; Regular and Extended versions `1.33.11-gke.1013000` and `1.34.6-gke.1307000`; Stable versions `1.33.10-gke.1115000`, `1.34.6-gke.1154000`, and `1.35.3-gke.1234000`; and Extended/no-channel node versions `1.30.14-gke.2441000`, `1.31.14-gke.1850000`, and `1.32.13-gke.1449000`. Creation defaults became Rapid `1.35.3-gke.1737000`, Regular, Extended, and no-channel `1.35.3-gke.1389000`, and Stable `1.34.6-gke.1068000`; general minor auto-upgrades targeted Rapid `1.32→1.33.11-gke.1074000`, `1.33→1.34.7-gke.1055000`, and `1.34→1.35.3-gke.1737000`; Regular `1.32→1.33.10-gke.1176000`, `1.33→1.34.6-gke.1237000`, and `1.34→1.35.3-gke.1389000`; Stable and no-channel `1.32→1.33.10-gke.1067000`; and Extended `1.29→1.30.14-gke.2369000`.

### GKE 2026-R19 channel versions (2026-05)

`2026-R19` added Rapid and no-channel versions `1.33.11-gke.1197000`, `1.34.7-gke.1499000`, `1.35.3-gke.2190000`, and Rapid `1.36.0-gke.1759000`; Regular and Extended versions `1.33.11-gke.1074000` and `1.34.7-gke.1055000`; Stable versions `1.33.10-gke.1176000`, `1.34.6-gke.1237000`, and `1.35.3-gke.1389000`, plus Stable and no-channel `1.35.3-gke.1234002`; and Extended/no-channel node versions `1.30.14-gke.2415000`, `1.30.14-gke.2458000`, `1.31.14-gke.1823000`, `1.31.14-gke.1868000`, and `1.32.13-gke.1492000`. Rapid creation moved to `1.35.3-gke.1993000` and Stable to `1.34.6-gke.1154000`; general minor auto-upgrades targeted Rapid `1.34→1.35.3-gke.1993000`, Regular `1.32→1.33.11-gke.1013000` and `1.33→1.34.6-gke.1307000`, Stable and no-channel `1.32→1.33.10-gke.1115000`, and Extended `1.29→1.30.14-gke.2407000`.

### GKE 2026-R2 channel targets (2026-01)

The `2026-R2` creation defaults became Rapid `1.35.0-gke.1403000`, Regular and Extended `1.33.5-gke.2072000`, Stable `1.33.5-gke.1956000`, and no-channel `1.33.5-gke.2072000`. General minor auto-upgrades targeted Rapid `1.30→1.31.14-gke.1175000`, `1.31→1.32.9-gke.1734000`, `1.32→1.33.5-gke.2118000`, and `1.33→1.34.1-gke.3971000`; Regular `1.30→1.31.14-gke.1156000`, `1.31→1.32.9-gke.1711000`, and `1.32→1.33.5-gke.2072000`; Stable `1.30→1.31.14-gke.1081000`, `1.31→1.32.9-gke.1632000`, and `1.32→1.33.5-gke.1956000`; Extended `1.28→1.29.15-gke.2613000` and `1.29→1.30.14-gke.1855000`; and no-channel `1.30→1.31.14-gke.1156000`, `1.31→1.32.9-gke.1711000`, and `1.32→1.33.5-gke.1956000`.

### GKE 2026-R20 versions (2026-05)

`2026-R20` added Rapid versions `1.33.12-gke.1000000`, `1.34.8-gke.1000000`, `1.35.5-gke.1000000`, and `1.36.0-gke.2253000`; Regular `1.35.3-gke.1389002`; Stable `1.33.11-gke.1013000`, `1.34.6-gke.1307000`, and `1.35.3-gke.1389002`; Extended `1.30.14-gke.2530000`, `1.31.14-gke.1942000`, `1.32.13-gke.1551000`, and `1.35.3-gke.1389002`; and no-channel `1.33.12-gke.1000000`, `1.34.8-gke.1000000`, `1.35.3-gke.1389002`, and `1.35.5-gke.1000000`.

### GKE 2026-R21 channel versions (2026-05)

`2026-R21` added Rapid and no-channel versions `1.33.12-gke.1059000`, `1.34.8-gke.1126000`, and `1.35.5-gke.1057000`, plus Rapid `1.36.0-gke.2459000`; Regular and Extended versions `1.33.11-gke.1197000`, `1.34.7-gke.1499000`, and `1.35.3-gke.2190000`; Stable versions `1.33.11-gke.1074000` and `1.34.7-gke.1055000`; and Extended/no-channel node versions `1.30.14-gke.2441000`, `1.30.14-gke.2558000`, `1.31.14-gke.1850000`, `1.31.14-gke.1967000`, `1.32.13-gke.1449000`, and `1.32.13-gke.1592000`. Creation defaults became Rapid `1.35.5-gke.1000000`, Regular, Extended, and no-channel `1.35.3-gke.1389002`, and Stable `1.34.6-gke.1307000`; general minor auto-upgrades targeted Rapid `1.32→1.33.12-gke.1000000`, `1.33→1.34.8-gke.1000000`, and `1.34→1.35.5-gke.1000000`; Regular `1.32→1.33.11-gke.1074000`, `1.33→1.34.7-gke.1055000`, and `1.34→1.35.3-gke.1389002`; Stable and no-channel `1.32→1.33.11-gke.1013000`; and Extended `1.29→1.30.14-gke.2441000`.

### GKE 2026-R22 channel versions (2026-06)

`2026-R22` added Rapid and no-channel versions `1.33.12-gke.1116000`, `1.34.8-gke.1218000`, and `1.35.5-gke.1163000`, plus Rapid `1.36.0-gke.2684000`; Regular and Extended versions `1.33.12-gke.1000000`, `1.34.8-gke.1000000`, and `1.35.5-gke.1000000`; and Extended/no-channel node versions `1.30.14-gke.2608000`, `1.31.14-gke.1986000`, and `1.32.13-gke.1657000`. Creation defaults became Rapid `1.36.0-gke.2459000`, Regular, Extended, and no-channel `1.35.3-gke.2190000`, and Stable `1.34.7-gke.1055000`; general minor auto-upgrades targeted Rapid `1.32→1.33.12-gke.1059000`, `1.33→1.34.8-gke.1126000`, and `1.34→1.35.5-gke.1057000`; Regular `1.32→1.33.11-gke.1197000`, `1.33→1.34.7-gke.1499000`, and `1.34→1.35.3-gke.2190000`; Stable and no-channel `1.32→1.33.11-gke.1074000`; and Extended `1.29→1.30.14-gke.2458000`.

### GKE 2026-R23 channel versions (2026-06)

`2026-R23` added Rapid versions `1.33.12-gke.1166000`, `1.34.8-gke.1278000`, `1.35.5-gke.1241000`, `1.36.0-gke.3009002`, and `1.36.0-gke.3070003`; Regular and Extended versions `1.33.12-gke.1059000`, `1.34.8-gke.1126000`, `1.35.5-gke.1057000`, and `1.36.0-gke.2459000`; Stable versions `1.33.11-gke.1197000`, `1.34.7-gke.1499000`, and `1.35.3-gke.2190000`; no-channel versions `1.33.12-gke.1166000`, `1.34.8-gke.1278000`, `1.35.5-gke.1241000`, `1.36.0-gke.2459000`, `1.36.0-gke.2684000`, `1.36.0-gke.3009002`, and `1.36.0-gke.3070003`; and Extended/no-channel node versions `1.30.14-gke.2681000`, `1.31.14-gke.2074000`, and `1.32.13-gke.1729000`. Creation defaults became Rapid `1.36.0-gke.2684000` and Regular, Extended, and no-channel `1.35.5-gke.1000000`; general minor auto-upgrades targeted Rapid `1.32→1.33.12-gke.1116000`, `1.33→1.34.8-gke.1218000`, and `1.34→1.35.5-gke.1163000`; Regular `1.32→1.33.12-gke.1000000`, `1.33→1.34.8-gke.1000000`, and `1.34→1.35.5-gke.1000000`; Stable `1.33→1.34.7-gke.1055000`; Extended `1.29→1.30.14-gke.2530000` and `1.30→1.31.14-gke.1942000`; and no-channel `1.32→1.33.12-gke.1000000` and `1.33→1.34.7-gke.1055000`.

### GKE 2026-R24 and R25 channel versions (2026-06)

`2026-R24` had no version updates. `2026-R25` added Rapid versions `1.33.12-gke.1165000`, `1.33.12-gke.1208000`, `1.34.8-gke.1284000`, `1.35.5-gke.1241004`, `1.35.5-gke.1324000`, and `1.36.0-gke.3302001`; Regular and Extended versions `1.33.12-gke.1116000`, `1.34.8-gke.1218000`, `1.35.5-gke.1057002`, `1.35.5-gke.1163012`, and `1.36.0-gke.2684000`; Stable versions `1.33.12-gke.1000000`, `1.34.8-gke.1000000`, and `1.35.5-gke.1000004`; no-channel versions `1.33.12-gke.1165000`, `1.33.12-gke.1208000`, `1.34.8-gke.1284000`, `1.35.5-gke.1000004`, `1.35.5-gke.1057002`, `1.35.5-gke.1163012`, `1.35.5-gke.1241004`, `1.35.5-gke.1324000`, and `1.36.0-gke.3302001`; and Extended/no-channel node versions `1.30.14-gke.2710000`, `1.31.14-gke.2116000`, and `1.32.13-gke.1740000`. Creation defaults became Rapid `1.36.0-gke.3070003`, Regular, Extended, and no-channel `1.35.5-gke.1057002`, and Stable `1.34.7-gke.1499000`; general minor auto-upgrades targeted Rapid `1.32→1.33.12-gke.1165000`, `1.33→1.34.8-gke.1278000`, `1.34→1.35.5-gke.1241004`, and `1.35→1.36.0-gke.3070003`; Regular `1.32→1.33.12-gke.1059000`, `1.33→1.34.8-gke.1126000`, and `1.34→1.35.5-gke.1057002`; Stable `1.32→1.33.11-gke.1197000` and `1.33→1.34.7-gke.1499000`; Extended `1.29→1.30.14-gke.2558000` and `1.30→1.31.14-gke.1967000`; and no-channel `1.32→1.33.12-gke.1059000` and `1.33→1.34.7-gke.1499000`.

### GKE 2026-R26 channel versions (2026-06)

`2026-R26` added Rapid and no-channel versions `1.33.12-gke.1270000`, `1.34.9-gke.1065000`, `1.35.6-gke.1049000`, `1.36.0-gke.3302004`, and `1.36.0-gke.3712000`; Regular and Extended versions `1.33.12-gke.1165000`, `1.34.8-gke.1278000`, `1.35.5-gke.1241004`, and `1.36.0-gke.3070003`; Stable versions `1.33.12-gke.1059000`, `1.34.8-gke.1126000`, and `1.35.5-gke.1057002`; and Extended/no-channel node versions `1.30.14-gke.2746000`, `1.31.14-gke.2157000`, and `1.32.13-gke.1829000`. Creation defaults became Rapid `1.36.0-gke.3302004`, Regular, Extended, and no-channel `1.35.5-gke.1163012`, and Stable `1.34.8-gke.1000000`; general minor auto-upgrades targeted Rapid `1.32→1.33.12-gke.1208000`, `1.33→1.34.8-gke.1284000`, `1.34→1.35.5-gke.1324000`, and `1.35→1.36.0-gke.3302004`; Regular `1.32→1.33.12-gke.1116000`, `1.33→1.34.8-gke.1218000`, and `1.34→1.35.5-gke.1163012`; Stable `1.32→1.33.12-gke.1000000` and `1.33→1.34.8-gke.1000000`; Extended `1.29→1.30.14-gke.2608000` and `1.30→1.31.14-gke.1986000`; and no-channel `1.32→1.33.12-gke.1116000` and `1.33→1.34.8-gke.1000000`.

### GKE 2026-R3 channel targets (2026-01)

The `2026-R3` creation defaults became Rapid `1.35.0-gke.1624000`, Regular and Extended `1.33.5-gke.2100000`, Stable `1.33.5-gke.2019000`, and no-channel `1.33.5-gke.2100000`. General minor auto-upgrades targeted Rapid `1.31→1.32.11-gke.1038000`, `1.32→1.33.5-gke.2172000`, and `1.33→1.34.3-gke.1051000`; Regular `1.31→1.32.9-gke.1728000` and `1.32→1.33.5-gke.2100000`; Stable `1.31→1.32.9-gke.1675000` and `1.32→1.33.5-gke.2019000`; Extended `1.28→1.29.15-gke.2617000` and `1.29→1.30.14-gke.1861000`; and no-channel `1.31→1.32.9-gke.1728000` and `1.32→1.33.5-gke.2019000`.

### GKE 2026-R4 channel targets (2026-01)

The `2026-R4` creation defaults became Rapid `1.35.0-gke.1795000`, Regular and Extended `1.33.5-gke.2118001`, Stable `1.33.5-gke.2072001`, and no-channel `1.33.5-gke.2118001`. General minor auto-upgrades targeted Rapid `1.32→1.33.5-gke.2228001` and `1.33→1.34.3-gke.1051003`; Regular `1.31→1.32.9-gke.1734000` and `1.32→1.33.5-gke.2118001`; Stable `1.31→1.32.9-gke.1711000` and `1.32→1.33.5-gke.2072001`; Extended `1.28→1.29.15-gke.2629000` and `1.29→1.30.14-gke.1870000`; and no-channel `1.31→1.32.9-gke.1734000` and `1.32→1.33.5-gke.2072001`.

### GKE 2026-R5 channel targets (2026-02)

The `2026-R5` creation defaults became Rapid `1.35.0-gke.2232000`, Regular, Extended, and no-channel `1.34.3-gke.1051003`, and Stable `1.33.5-gke.2100001`. General minor auto-upgrades targeted Rapid `1.31→1.32.11-gke.1174000`, `1.32→1.33.5-gke.2326000`, and `1.33→1.34.3-gke.1245000`; Regular `1.31→1.32.11-gke.1038000` and `1.32→1.33.5-gke.2172001`; Stable `1.31→1.32.9-gke.1728000` and `1.32→1.33.5-gke.2100001`; Extended `1.29→1.30.14-gke.1901000`; and no-channel `1.31→1.32.11-gke.1038000` and `1.32→1.33.5-gke.2100001`.

### GKE 2026-R6 channel targets (2026-02)

The `2026-R6` creation defaults became Rapid `1.35.0-gke.2398000`, Stable `1.33.5-gke.2118001`, and remained Regular, Extended, and no-channel `1.34.3-gke.1051003`. General minor auto-upgrades targeted Rapid `1.31→1.32.11-gke.1211000`, `1.32→1.33.5-gke.2392000`, `1.33→1.34.3-gke.1318000`, and `1.34→1.35.0-gke.2398000`; Regular `1.32→1.33.5-gke.2228001`; Stable `1.31→1.32.9-gke.1734000` and `1.32→1.33.5-gke.2118001`; Extended `1.29→1.30.14-gke.1922000`; and no-channel `1.32→1.33.5-gke.2118001`.

### GKE 2026-R7 channel targets (2026-02)

The `2026-R7` creation defaults became Rapid `1.35.0-gke.2745003`, Regular, Extended, and no-channel `1.34.3-gke.1245000`, and Stable `1.33.5-gke.2172001`. General minor auto-upgrades targeted Rapid `1.31→1.32.11-gke.1264000`, `1.32→1.33.5-gke.2469000`, `1.33→1.34.3-gke.1444000`, and `1.34→1.35.0-gke.2745003`; Regular `1.31→1.32.11-gke.1174000` and `1.32→1.33.5-gke.2326000`; Stable `1.31→1.32.11-gke.1038000` and `1.32→1.33.5-gke.2172001`; Extended `1.29→1.30.14-gke.1973000`; and no-channel `1.31→1.32.11-gke.1174000` and `1.32→1.33.5-gke.2172001`.

### GKE 2026-R8 channel targets (2026-02)

The `2026-R8` creation defaults became Rapid `1.35.0-gke.3047001`, Regular, Extended, and no-channel `1.34.3-gke.1318000`, and Stable `1.33.5-gke.2228001`. General minor auto-upgrades targeted Rapid `1.31→1.32.12-gke.1026000`, `1.32→1.33.8-gke.1026000`, `1.33→1.34.4-gke.1047000`, and `1.34→1.35.0-gke.3047001`; Regular `1.31→1.32.11-gke.1211000` and `1.32→1.33.5-gke.2392000`; Stable `1.32→1.33.5-gke.2228001`; Extended `1.29→1.30.14-gke.1991000`; and no-channel `1.31→1.32.11-gke.1211000` and `1.32→1.33.5-gke.2228001`.

### GKE 2026-R9 channel targets (2026-03)

The `2026-R9` creation defaults became Rapid `1.35.1-gke.1396001`, Regular, Extended, and no-channel `1.34.3-gke.1444000`, and Stable `1.33.5-gke.2326000`. General minor auto-upgrades targeted Rapid `1.31→1.32.12-gke.1076000`, `1.32→1.33.8-gke.1112000`, `1.33→1.34.4-gke.1130000`, and `1.34→1.35.1-gke.1396001`; Regular `1.31→1.32.11-gke.1264000` and `1.32→1.33.5-gke.2469000`; Stable `1.31→1.32.11-gke.1174000` and `1.32→1.33.5-gke.2326000`; Extended `1.29→1.30.14-gke.2026000`; and no-channel `1.31→1.32.11-gke.1264000` and `1.32→1.33.5-gke.2326000`.

### GKE control-plane upgrade controls (2026-03)

GKE cluster disruption budgets can configure how frequently auto-upgrades disrupt a cluster. Patch-version support can also retain an existing control-plane patch longer to facilitate large-scale upgrades and downgrades.

### GKE no-channel deprecation (2026-06)

The option to leave a cluster unenrolled from a release channel is deprecated and will be removed on June 14, 2027; enroll existing no-channel clusters before then or GKE will enroll them in the Stable channel after removal.

### GKE surge-upgrade concurrency limit (2026-07)

For Standard clusters, `maxSurge + maxUnavailable` can now be at most 100 during surge upgrades. Either setting can individually be as high as 100, provided their sum does not exceed 100.


## Defaults, compatibility, and known issues

### `kubectl` removal from Container-Optimized OS (2026-05)

Container-Optimized OS milestone 129 and later no longer include `kubectl` in `/usr/bin/`.

### Autopilot NRI failure fix (2026-01)

The Autopilot node state that prevented system and user Pods from running after `NRI RunPodSandbox` failures is fixed in GKE `1.34.1-gke.3899000` and later.

### Cloud Storage FUSE mount delays on GKE (2026-04)

Cloud Storage FUSE CSI mounts can take hours on buckets with millions of empty folders and surface `CreateContainer error: failed to reserve container name` on older releases. Upgrade to GKE `1.34.6-gke.1154000` or `1.35.2-gke.1691000` or later; eligible GKE 1.33 clusters can bypass the slow access check with the `skipCSIBucketAccessCheck: "true"` volume attribute.

### Cloud Storage FUSE mount failures during GKE startup (2026-06)

Beginning with affected GKE `1.34.1-gke.3899001` releases, a Cloud Storage FUSE sidecar can fail to mount a volume if the metadata service is not ready. Upgrade to at least `1.34.8-gke.1218000`, `1.35.3-gke.2347000`, or `1.36.0-gke.1266000` on the corresponding minor-version branch, or gate the sidecar with an init container that waits for metadata-service availability.

### Cloud Storage FUSE streaming-write failures (2026-01)

On some GKE versions earlier than `1.34.0-gke.2011000`, Cloud Storage FUSE CSI streaming writes can fail with application I/O errors and sidecar 503s; streaming writes are enabled by default starting in `1.33.2-gke.4655000`. Upgrade to `1.34.1-gke.3849001` or later, or disable the feature with `--enable-streaming-writes=false` or `write:enable-streaming-writes:false`; the workaround is reliable only when staging uses SSD or tmpfs.

### GKE 1.36 internal load balancer default (2026-05)

New L4 Internal Load Balancer Services on GKE 1.36 use GKE subsetting and NEGs by default instead of instance groups. Existing Services continue to use instance groups.

### GKE DNS implementation change (2026-05)

In GKE 1.36, the `kube-dns` image switches from the Kubernetes DNS implementation to CoreDNS, increasing supported headless-service size, upstream DNS services, and concurrent connections.

### GKE OpenSSL security bulletin (2026-02)

GCP-2026-006 reports multiple OpenSSL vulnerabilities in GKE, including critical CVE-2025-15467, which might permit network-based remote code execution or denial of service.

### N4D cluster autoscaling version correction (2026-02)

N4D machine types used with Cluster autoscaler do not require GKE `1.34.1-gke.2037000` or later; that combination works on any available GKE version.

### NodeLocal DNSCache becomes a Standard default (2026-01)

New Standard clusters created at GKE `1.34.1-gke.3720000` or later enable NodeLocal DNSCache by default, running a DNS cache on every node as a DaemonSet.

### Workload Identity timeouts after GKE node startup (2026-05)

On GKE 1.35 and later, Workload Identity workloads can encounter transient timeouts or refused connections to the GKE metadata server immediately after node startup. This advisory was later marked as clarified.


## Networking, gateways, and security

### Confidential Autopilot cluster settings (2026-05)

Confidential GKE Nodes on Autopilot support cluster-level enablement of AMD SEV-SNP and Intel TDX.

### Confidential GKE GPU workloads (2026-07)

Preview support in GKE `1.35.3-gke.1389000` and later lets certain G4 machine types with NVIDIA RTX PRO 6000 GPUs run on Confidential GKE Nodes.

### GKE accelerator network profiles (2026-04)

GA accelerator network profiles automate the VPC and subnet configuration required for GPU and TPU node pools.

### GKE Gateway API v1.5 (2026-04)

GKE `1.35.2-gke.1842000` and later support Gateway API v1.5, and the GKE Gateway controller passes its core conformance tests.

### GKE Gateway backend authenticated TLS (2026-05)

GKE Gateway supports authenticated TLS from Gateways to Pods or InferencePools for `gke-l7-global-external-managed`, `gke-l7-regional-external-managed`, and `gke-l7-rilb` GatewayClasses.

### GKE Gateway backend mutual TLS (2026-07)

GKE Gateway backend mTLS makes the load balancer present a client certificate to backend Pods, extending backend authenticated TLS with load-balancer identity authentication. Configure it through the standard Gateway API field `spec.tls.backend.clientCertificateRef`; it supports `gke-l7-global-external-managed`, `gke-l7-regional-external-managed`, and `gke-l7-rilb` GatewayClasses.

### GKE Gateway frontend mTLS (2026-06)

GKE Gateway can validate client certificates with frontend mTLS for the `gke-l7-global-external-managed`, `gke-l7-regional-external-managed`, and `gke-l7-rilb` GatewayClasses.

### GKE managed DRANET (2026-04)

GA GKE managed DRANET implements Kubernetes Dynamic Resource Allocation for high-performance networking on GKE `1.35.2-gke.1842000` or later. It supports A3 Ultra, A4, A4X, and A4X Max NVIDIA GPU instances plus TPU v6e and TPU v7x instances.

### L4 load balancer logging CRD (2026-05)

GKE `1.36.0-gke.2459000` and later can configure Cloud Logging directly on L4 backend services through the `L4LBConfig` CRD. It supports internal L4 load balancers with subsetting and external L4 load balancers with regional backend services enabled.

### Live migration for Confidential GKE Nodes (2026-05)

Standard clusters can live-migrate C3D nodes that use Confidential GKE Nodes with AMD SEV enabled.

### Mutating Admission Policies on GKE (2026-05)

Mutating Admission Policies are GA on GKE 1.36, providing CEL-based resource mutation without a mutating admission webhook.

### SCTP on GKE Dataplane V2 (2026-01)

Standard clusters at `1.32.2-gke.1297000` or later can use GA SCTP for Pod-to-Pod and Pod-to-Service traffic when they run Dataplane V2 with Ubuntu node images.

### Stricter GKE `HealthCheckPolicy` validation (2026-04)

On GKE 1.34 and later, a Gateway API `HealthCheckPolicy` is rejected when its `type` and configured health-check field do not match, such as `type: TCP` with `httpHealthCheck`. Existing mismatches are grandfathered, but an update cannot introduce a mismatch or change an existing mismatched field to another invalid value; earlier GKE versions instead use `type` and ignore the mismatched configuration field.


## Compute, accelerators, scheduling, and autoscaling

### C4A bare-metal nodes on GKE (2026-02)

Standard clusters at GKE `1.35.0-gke.2232000` or later can use the Preview Arm machine type `c4a-highmem-96-metal`; select it with `--machine-type` when creating a cluster or node pool.

### C4A bare-metal nodes reach GA on GKE (2026-05)

C4A bare-metal instances are GA with GKE clusters.

### C4A bare-metal support expansion (2026-04)

On GKE `1.35.3-gke.1389000` or later, Preview `c4a-highmem-96-metal` nodes support Autopilot, node auto-provisioning, ComputeClasses that create node pools automatically, and cluster autoscaling.

### C4N machines on GKE (2026-07)

Network-optimized C4N machine types are available to Standard and Autopilot clusters running GKE `1.36.0-gke.3009002` or later.

### GKE JobSet goodput metrics (2026-05)

Preview metrics `kubernetes.io/jobset/scheduling_goodput` and `kubernetes.io/jobset/proxy_runtime_goodput` measure, respectively, the fraction of time all required JobSet resources are available and all required accelerators are productive. Both appear in the JobSet monitoring dashboard.

### GKE JobSet placement metrics (2026-01)

GA system metrics `kubernetes.io/jobset/assigned_node_pools`, `kubernetes.io/jobset/assigned_nodes`, `kubernetes.io/node_pool/assigned_jobsets`, and `kubernetes.io/node/assigned_jobsets` show where JobSets and their Pods are scheduled.

### H4D machines on GKE (2026-03)

The H4D HPC machine series is GA for Standard clusters and the Autopilot Performance compute class, providing 192 cores with SMT disabled, up to 1,488 GB of memory, 3,750 GiB of Local SSD, and 200 Gbps Cloud RDMA networking.

### N4A machines reach GA on GKE (2026-01)

N4A Arm machine types are GA for both Autopilot and Standard clusters.

### TPU slice and partition health metrics (2026-02)

Beta GKE system metrics `kubernetes.io/accelerator/slice/state` and `kubernetes.io/accelerator/partition/state` report the status of a TPU slice and the health of a TPU partition.

### Vertical Pod Autoscaler decision logs (2026-07)

GKE `1.36.0-gke.1601000` and later can emit VerticalPodAutoscaler decision logs to Cloud Logging, exposing why particular vertical autoscaling decisions were made. This capability is in Preview.


## Storage, telemetry, and workload operations

### Automated GKE disk-type selection (2026-03)

One StorageClass can let GKE automatically select a compatible Hyperdisk type based on the scheduled node's machine type, using Hyperdisk on machines such as C3 or C4 and falling back to Persistent Disk on other VM generations.

### Cloud Storage FUSE on GKE Dedicated (2026-05)

Google Cloud Dedicated clusters and node pools support the Cloud Storage FUSE CSI driver on GKE `1.36.0-gke.1266000` or later. Mounts must specify the `custom-endpoint` option through the `gcsfuse` CLI or configuration file.

### Cloud Storage FUSE reads on 64 KiB ARM64 nodes (2026-05)

Cloud Storage FUSE CSI could return incomplete reads or premature EOF on 64 KiB-page ARM64 nodes such as A4X and A4X Max. Fixed versions are `1.33.11-gke.1019000`, `1.34.6-gke.1154000`, and `1.35.2-gke.1485000` or later.

### Distributed inference in GKE Inference Quickstart (2026-03)

GKE Inference Quickstart recommends optimized distributed-inference configurations for models such as Qwen and gpt-oss on NVIDIA GPUs and Cloud TPUs. It introduces GKE Inference Gateway through llm-d inference scheduling and can tune configurations for workload-specific latency and throughput goals.

### GKE Pod Snapshots (2026-05)

GKE Pod Snapshots are GA on clusters running `1.35.3-gke.1234000` or later.

### Image streaming on Ubuntu GKE nodes (2026-02)

At GKE `1.35.0-gke.1403000` or later, Standard and Autopilot nodes using `UBUNTU_CONTAINERD` support GA image streaming and secondary boot disks. Image streaming is also available in `asia-southeast3`.

### Managed OpenTelemetry for GKE (2026-03)

Preview Managed OpenTelemetry requires GKE `1.34.1-gke.2178000` or later and provides an in-cluster OTLP endpoint that routes traces, metrics, and logs to the Cloud Telemetry API. An `Instrumentation` custom resource can inject the environment variables needed for OTLP ingestion into workloads.

### Multimodal agent telemetry on GKE (2026-05)

Preview Managed OpenTelemetry can collect multimodal prompts and responses from LangGraph and Agent Development Kit agents for analysis in Trace Explorer and BigQuery.

### Pressure Stall Information metrics on GKE (2026-07)

On GKE 1.34 and later, Managed Service for Prometheus can collect cAdvisor Pressure Stall Information metrics for CPU, memory, and I/O congestion and stall time across containers, Pods, and nodes.

### Privileged Autopilot workload allowlists (2026-03)

On GKE 1.35 and later, organization and cluster administrators can control which privileged partner workloads run in Autopilot clusters; approved customers can also authorize their own privileged workloads with custom allowlists.

### Slurm Operator add-on for GKE (2026-04)

Starting with GKE `1.35.2-gke.1842000`, the Preview managed Slurm Operator add-on can add Slurm scheduling to a GKE cluster for CPU, GPU, and supported TPU platforms.
