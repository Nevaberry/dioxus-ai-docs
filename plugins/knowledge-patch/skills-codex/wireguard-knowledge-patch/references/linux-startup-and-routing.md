# Linux startup and routing

Use this reference when coordinating enabled `wg-quick` instances with
systemd or running IPv4 default-route setup in a restricted namespace.

## Aggregate systemd ordering

Since `1.0.20260223`, the `wg-quick@.service` template installs into
`wg-quick.target` and declares itself `Before=` that target.

The ordering relationship is:

```text
enabled wg-quick@.service instances
                |
                | Before=
                v
        wg-quick.target
                |
                | After=
                v
         dependent unit
```

As a result, `wg-quick.target` is not considered started until its enabled
`wg-quick@.service` instances have been started.

A service that needs the aggregate can pull in and order itself after the
target:

```ini
[Unit]
Wants=wg-quick.target
After=wg-quick.target
```

`Wants=` brings the target into the transaction. `After=` places the
dependent unit after the target, and the template's ordering places the
enabled instances before the target.

Use this pattern when the dependency is on all enabled instances represented
by the target rather than on one explicitly named instance.

## Conditional `src_valid_mark` writes

Since `1.0.20260223`, Linux IPv4 default-route setup first considers the
current value of:

```text
net.ipv4.conf.all.src_valid_mark
```

`wg-quick` writes the sysctl to `1` only when its current value is not already
`1`.

This changes the permission requirement in a restricted namespace:

| Current value | `wg-quick` action | Namespace requirement |
| --- | --- | --- |
| `1` | No sysctl write | Setup can proceed even when writes are forbidden |
| Not `1` | Write `1` | Permission to change the sysctl is still required |

Preconfiguring the value on the host can therefore allow setup inside a
namespace that blocks sysctl writes. Merely blocking writes is not sufficient
when the inherited value differs from `1`.

## Deployment checks

For a unit that must wait for every enabled quick interface:

1. pull in `wg-quick.target`;
2. order the unit after `wg-quick.target`; and
3. rely on the template's before-target relationship for the instances.

For restricted-network-namespace setup:

1. determine whether `src_valid_mark` is already `1`;
2. if it is, no write is attempted by this setup path; and
3. if it is not, ensure the namespace permits the change.
