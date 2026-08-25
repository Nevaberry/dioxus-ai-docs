# Server, InnoDB, and Resource Sizing

## Container and host resource discovery

### Container-aware InnoDB defaults (9.2-9.3)

InnoDB derives buffer-pool instances, page cleaners, purge threads, read threads,
parallel-read threads, log-writer threads, and dedicated-server redo capacity
from container CPU limits. It derives `temptable_max_ram` and, with
`--innodb-dedicated-server`, `innodb_buffer_pool_size` from the container memory
limit.

### Server memory and reported resources (9.4-9.6)

`back_log` defaults to `10000`. `server_memory` caps the physical-memory value
used to derive automatic defaults; it is not a hard process-memory limit. The
error log always reports the logical CPU and physical-memory totals accessible to
the server.

### Cpuset cgroups (9.7.0)

The server observes the cpuset cgroup controller and calculates its available
logical CPU count from the assigned CPU set, not only from broader container CPU
limits.

## InnoDB behavior and diagnostics

### Change buffering (9.4-9.6)

`innodb_change_buffer_max_size` defaults to `5`, and
`innodb_change_buffering` defaults to `ALL` for secondary-index changes. Set them
explicitly when the workload was tuned for prior behavior.

### Conditional log-writer threads (9.4-9.6)

When binary logging is off, `innodb_log_writer_threads` defaults off at four or
fewer logical CPUs and on above four. With binary logging on, the threshold is 32
logical CPUs. An explicit configuration always wins.

### Redo-log diagnostics (9.4-9.6)

Redo warnings and `MONITOR` output report current LSN, total log capacity, and
used capacity. `ER_IB_WRN_REDO_DISABLED_INFO` and
`ER_IB_MSG_LOG_WRITER_WAIT_ON_NEW_LOG_FILE_INFO` replace their less-informative
predecessors.

## Thread Pool sizing

### Hardware-aware configuration (9.4-9.6)

Thread Pool can derive and validate defaults from available VCPUs for
`thread_pool_size`, transaction limits, query threads per group, scheduling
algorithm, and unused-thread limits. Invalid settings are corrected with
warnings, so monitor startup logs after changing available CPUs.

### Unused-thread default (9.7.2)

`thread_pool_max_unused_threads` defaults to `32`, up from `2`. Set it explicitly
to preserve the former idle-thread limit.
