# Monitoring, Selection, and Troubleshooting

## Read reachability and selection state

`chronyc sources` prints `Reach` as an eight-bit poll history in octal. A set bit means that a valid NTP response or refclock sample arrived. It does not mean that the sample passed every synchronization test.

```sh
chronyc sources -v
chronyc selectdata -v
```

In `selectdata`, uppercase `S` indicates one of two conditions:

- The source has only measurements older than reachable sources.
- The source has exceeded its configured `maxunreach` poll limit.

The `maxunreach` default is 100000. Even before reaching that limit, an unreachable source remains selected only while it has a sample newer than the oldest sample from any reachable source.

## Connect the exporter through the command socket

The chrony exporter normally queries `[::1]:323`. If `cmdport 0` disables the network command port, point it at the Unix socket instead:

```sh
chrony_exporter --chrony.address=unix:///run/chrony/chronyd.sock \
  --collector.sources.with-ntpdata --collector.chmod-socket
```

The extended `ntpdata` source collector requires a socket connection. The exporter must run as root or as the chrony user. A root-run exporter also needs `--collector.chmod-socket`.

## Calculate an absolute clock-error bound

The exporter tracking metrics can provide an absolute accuracy bound by adding:

1. The absolute value of the last offset
2. Root dispersion
3. Half the root delay

```promql
abs(chrony_tracking_last_offset_seconds) + chrony_tracking_root_dispersion_seconds + (0.5 * chrony_tracking_root_delay_seconds)
```

## Diagnose unresolved source names

A nonzero `sources with unknown address` count from `chronyc activity` means name resolution has not completed. The configured source names remain visible with:

```sh
chronyc -N sources -a
```

A badly wrong boot-time clock can make DNSSEC validation fail before chronyd resolves the servers needed to correct that clock. With systemd-resolved, this service environment override can break the cycle as a last resort:

```systemd
Environment=SYSTEMD_NSS_RESOLVE_VALIDATE=0
```

The override disables DNSSEC validation for chronyd, so do not treat it as the normal fix.

## Select an inaccurate Windows NTP server

Windows NTP servers can advertise root dispersion of several seconds. Their otherwise valid measurements can then remain unselected as too inaccurate.

Confirm the dispersion with `chronyc ntpdata`, then raise `maxdistance` only as far as that source requires:

```conf
maxdistance 16.0
```

## Recover from adaptive-delay rejection

A persistent delay increase can make NTP test C reject new measurements for hours because retained, older low-delay samples define its expected delay.

Inspect the tests, and clear all retained samples if the path change is permanent:

```sh
chronyc ntpdata
chronyc reset sources
```

For frequent recurrence, either increase `maxclockerror` or set a very large `maxdelaydevratio` to effectively disable this test. The latter weakens delay filtering and should be an explicit tradeoff.

## Distinguish `chronyc` transport errors

### `506 Cannot talk to daemon`

For remote access, check:

- Whether chronyd is running
- UDP port 323 reachability
- Firewall rules
- `cmdallow` and `bindcmdaddress`

### `501 Not authorised`

This means either:

- A command that requires the privileged Unix socket was sent over UDP, or
- The Unix socket was not created because its directory has incorrect ownership or permissions.

Only root and the chrony user can access the privileged socket.

## Understand dropped client records

`chronyc serverstats` can report dropped client records before `chronyc clients` appears to reach the configured memory limit.

Each client-log hash slot can hold at most 16 colliding addresses. After the table reaches its maximum size, a seventeenth collision evicts the oldest record in that slot even if `clientloglimit` is larger.

The absolute limit is 16,777,216 simultaneous records, independently of a larger `clientloglimit` value. Raising `clientloglimit` is still necessary when interleaved mode needs per-client transmit timestamp state for more than the default few thousand clients.

## Recover promptly after network changes

If a connection disappears without `chronyc offline`, chronyd continues polling. After connectivity returns, it might wait until the next scheduled poll.

Integrate connection state with chrony:

```sh
chronyc offline
# restore connectivity
chronyc online
```

The `online` command triggers new measurements immediately.

On RHEL, be aware that the NetworkManager dispatcher can leave sources offline when a route managed outside NetworkManager appears after the dispatcher marked them offline. Mask that dispatcher when NetworkManager must not control source state.

## Explain offsets between synchronized peers

Two chrony hosts synchronized with each other can still measure a significant mutual offset in ordinary mode. Serving time and disciplining the local clock can use different transmit timestamp types.

Enable interleaved mode with `xleave` when an average reciprocal offset near zero is required.
