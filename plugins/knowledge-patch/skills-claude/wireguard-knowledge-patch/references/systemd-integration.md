# systemd integration

## Aggregate readiness with `wg-quick.target`

Batch `1.0.20260223` changes the relationship between the
`wg-quick@.service` template and `wg-quick.target`:

- Enabled template instances install into `wg-quick.target`.
- Each instance declares itself `Before=wg-quick.target`.
- The target is not considered started until the enabled instances it pulls
  in have been started.

A unit that requires this aggregate point can pull in the target and order
itself after it:

```ini
[Unit]
Wants=wg-quick.target
After=wg-quick.target
```

The two directives have separate jobs:

| Directive | Role |
| --- | --- |
| `Wants=wg-quick.target` | Pulls the aggregate target into the transaction |
| `After=wg-quick.target` | Places the dependent unit after the target |

Use this pattern when the dependency is on all enabled `wg-quick` instances
represented by the target, rather than on one named interface service.

The readiness guarantee follows the units included in the target. It should
not be broadened into a claim about an interface that is not enabled or
otherwise pulled into that target.

## Dependency review

When writing a dependent unit:

1. Decide whether it needs one specific interface or the aggregate of enabled
   instances.
2. For the aggregate case, add both `Wants=` and `After=` for
   `wg-quick.target`.
3. Keep the dependency on a specific `wg-quick@NAME.service` when only that
   named instance matters.
4. Verify that every interface expected at the aggregate point is actually an
   enabled instance associated with the target.
