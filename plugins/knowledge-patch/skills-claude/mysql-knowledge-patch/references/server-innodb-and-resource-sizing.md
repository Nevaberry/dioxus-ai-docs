# Server, InnoDB, and Resource Sizing

Use this reference when sizing a server, setting container limits, tuning
InnoDB background work, or configuring Thread Pool.

## Container and host resource detection

### Include cpuset limits in CPU sizing

The server observes limits from the cpuset cgroup controller and computes its
available logical CPU count from the assigned CPU set.

### Recheck container-derived InnoDB defaults

InnoDB uses container CPU limits to derive defaults for:

- buffer-pool instances
- page cleaners
- purge, read, parallel-read, and log-writer threads
- dedicated-server redo capacity

It uses the container memory limit to derive `temptable_max_ram` and, with
`--innodb-dedicated-server`, `innodb_buffer_pool_size`.

### Use server_memory as an input, not a cap

`back_log` defaults to `10000`. `server_memory` caps the physical memory value
used when deriving automatic configuration; it is not a hard process-memory
limit. The error log always reports the accessible logical CPU and physical
memory totals. Use explicit settings where tuned behavior must not drift with
host or cgroup changes.

## InnoDB background work

### Recheck change-buffer defaults

`innodb_change_buffer_max_size` defaults to `5`, and
`innodb_change_buffering` defaults to `ALL` for secondary-index changes.

### Apply the conditional log-writer default

When binary logging is off, `innodb_log_writer_threads` defaults off at four or
fewer logical CPUs and on above four. When binary logging is on, the threshold
is 32 logical CPUs. An explicit configured value is unchanged.

### Use the richer redo diagnostics

Redo warnings and `MONITOR` output report current LSN, total log capacity, and
used capacity. `ER_IB_WRN_REDO_DISABLED_INFO` and
`ER_IB_MSG_LOG_WRITER_WAIT_ON_NEW_LOG_FILE_INFO` replace their less-informative
predecessors.

## Thread Pool sizing

### Let hardware-aware defaults inform the baseline

Thread Pool can derive and validate defaults from available VCPUs for:

- `thread_pool_size`
- transaction limits
- query threads per group
- the scheduling algorithm
- unused-thread limits

Invalid values are corrected with warnings; inspect the effective settings and
warnings instead of assuming the configured value survived unchanged.

### Decide whether to preserve the old unused-thread limit

In `9.7.2`, `thread_pool_max_unused_threads` defaults to `32`, up from `2`.
Set it explicitly if the deployment must retain the previous idle-thread
limit.
