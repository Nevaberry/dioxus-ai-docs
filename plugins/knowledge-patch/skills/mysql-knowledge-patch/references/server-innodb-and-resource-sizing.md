# Server, InnoDB, and Resource Sizing

Use this reference when deploying in containers, setting automatic-memory
inputs, tuning InnoDB background work, configuring change buffering, or sizing
Thread Pool.

## Server resource discovery

### CPU sets are authoritative

In batch 9.7.0, the server observes limits imposed by the cpuset cgroup
controller and derives its available logical CPU count from the assigned CPU
set. Capacity calculations should use the server-reported count rather than the
host total.

### Accessible resources are logged

In batch 9.4-9.6, the error log always reports the server's accessible logical
CPU and physical-memory totals. Capture those lines when diagnosing different
automatic defaults between hosts or containers.

## General sizing defaults

`back_log` defaults to `10000` in batch 9.4-9.6.

The new `server_memory` variable caps the physical-memory amount considered
when the server derives automatic configuration defaults. It is not a hard
process-memory limit. Use operating-system or container controls for a hard
limit, and account for all explicitly sized caches and components.

## Container-aware InnoDB defaults

In batch 9.2-9.3, InnoDB derives these settings from container CPU limits:

- buffer-pool instances;
- page cleaners;
- purge threads;
- read threads;
- parallel-read threads;
- log-writer threads; and
- dedicated-server redo capacity.

It derives `temptable_max_ram` from the container memory limit. With
`--innodb-dedicated-server`, it also derives `innodb_buffer_pool_size` from that
limit. Compare resolved values, not host resources, during performance triage.

## Change buffering

In batch 9.4-9.6:

- `innodb_change_buffer_max_size` defaults to `5`; and
- `innodb_change_buffering` defaults to `ALL` for secondary-index changes.

An upgrade can therefore change both the amount and kinds of buffered work.
Preserve old behavior explicitly only after measuring write and recovery costs.

## Conditional log-writer threads

The default for `innodb_log_writer_threads` depends on binary logging and the
available logical CPU count in batch 9.4-9.6:

| Binary logging | Default off | Default on |
| --- | --- | --- |
| Off | 4 or fewer CPUs | More than 4 CPUs |
| On | 32 or fewer CPUs | More than 32 CPUs |

An explicitly configured value is unchanged.

## Thread Pool hardware awareness

Thread Pool can derive and validate defaults from available VCPUs for:

- `thread_pool_size`;
- transaction limits;
- query threads per group;
- the scheduling algorithm; and
- unused-thread limits.

In batch 9.4-9.6, invalid values are corrected with warnings. Treat a warning as
configuration drift: inspect the effective value rather than assuming the
configured value took effect.

## Redo-log diagnostics

Redo warnings and `MONITOR` output now report:

- the current LSN;
- total log capacity; and
- used log capacity.

In batch 9.4-9.6,
`ER_IB_WRN_REDO_DISABLED_INFO` and
`ER_IB_MSG_LOG_WRITER_WAIT_ON_NEW_LOG_FILE_INFO` replace their less-informative
predecessors. Update alert matching and parsers to the new identifiers.
