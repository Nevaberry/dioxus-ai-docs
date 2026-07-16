# Hardware Timestamping, Interleaved NTP, and PTP

## Capability checks

Before enabling NTP hardware timestamping, inspect the interface:

```sh
ethtool -T eth2
```

For ordinary NTP packets, confirm all of the following:

- Hardware transmit timestamping is supported.
- Hardware receive timestamping is supported.
- A PTP Hardware Clock number is reported and has a matching `/dev/ptpN` device.
- `HWTSTAMP_FILTER_ALL` is available as a receive filter.

A NIC limited to PTP receive filters cannot hardware-timestamp ordinary NTP packets. A KVM guest also needs kernel support through `CONFIG_PTP_1588_CLOCK_KVM` to expose a virtual PHC.

## Scope hardware timestamping carefully

The `hwtimestamp` directive accepts either one interface or a wildcard:

```conf
hwtimestamp enp1s0
hwtimestamp eno*
```

Use a wildcard only when no other application, such as `ptp4l`, uses hardware timestamping on a matching interface. Otherwise list only interfaces available exclusively to chronyd.

## High-rate local clients

A local hardware-timestamped client can poll both its NTP source and hardware clock at 16 Hz with `minpoll -4`. Filtering five measurements produces about three system-clock updates per second.

```conf
server 192.168.123.1 minpoll -4 maxpoll -4 xleave extfield F323 filter 5
hwtimestamp * minpoll -4
```

F323 is experimental. It improves synchronization stability when both endpoints support the extension.

## Transparent-clock corrections for NTP

Chronyd can encapsulate NTP in PTP event messages so one-step end-to-end transparent clocks add their delay corrections.

Both endpoints need `ptpport 319`. The client also selects port 319 for its server and requests F324 so corrections for the client's requests are returned:

```conf
server 192.168.123.1 xleave extfield F324 port 319
ptpport 319
```

Two-step transparent clocks, peer-to-peer transparent clocks, and boundary PTP clocks do not provide useful corrections for this mode.

## Precision and cross timestamps

At nanosecond-scale precision, the automatically estimated system-clock precision can add substantial timestamp noise. Configure a smaller `clockprecision`, at least on the server:

```conf
clockprecision 1e-9
```

Transparent-clock corrections do not remove asymmetric PCIe latency between the NIC and system clock. Chronyd automatically uses kernel-provided cross timestamping; `nocrossts` disables it.

## NTP-over-PTP constraints

Hardware-timestamped NTP-over-PTP requires the physical PHC to remain free-running. If PTP must share the interface, use a virtual clock rather than disciplining that physical PHC.

Choose the receive filter from the interface capabilities:

- Add `rxfilter ptp` only when `ethtool -T` advertises `ptpv2-event`.
- Omit `rxfilter ptp` on interfaces that expose only `none` and `all`.

```conf
hwtimestamp end0 rxfilter ptp
```

Keep the chrony versions at both NTP-over-PTP endpoints identical. Use `ptpdomain` when the deployment needs to accept only one PTP domain; its default is 123.

## Interleaved-mode server state

Interleaved mode stores per-client transmit timestamps in the server's client log. Its default allocation supports only a few thousand concurrent clients, so raise `clientloglimit` when a hardware-timestamped server must provide `xleave` to a larger population.

```conf
clientloglimit 100000000
```

The allocation does not remove the hash-table constraints described in the monitoring reference: collisions can cause records to be dropped before the nominal memory limit, and the absolute simultaneous-record limit remains 16,777,216.

## Bridge PTP to hardware-timestamped NTP

A host with at least two NICs can bridge a nearby PTP primary to NTP:

1. Run `ptp4l` and `phc2sys` on one interface to synchronize the system clock from PTP.
2. Serve the system clock as stratum-1 NTP through the other interface.
3. Bind chronyd to the NTP-side address and enable hardware timestamping only there.

```conf
bindaddress 203.0.113.74
hwtimestamp enp1s0
local stratum 1
```

## Reciprocal offsets between chrony hosts

Two mutually synchronized chrony hosts can measure a significant offset between each other in ordinary mode because the transmit timestamp types used for serving time and disciplining the local clock can differ.

An average reciprocal offset near zero is expected only when interleaved mode is enabled with `xleave`.

## VMware resume correction

Suspending a VMware guest stops both its clock and its synchronizer. On resume, the guest is behind physical time and NTP observes an abnormal discontinuity. VMware Tools immediately steps the guest system clock to repair this lifecycle-induced offset.
