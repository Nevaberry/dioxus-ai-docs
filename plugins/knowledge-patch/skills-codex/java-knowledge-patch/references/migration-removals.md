# Migration, Removals, and Deprecations

Use this reference to audit source, bytecode, launch configuration, runtime
images, agents, and platform assumptions before changing the deployed JDK.

## Launcher and VM option audit

The `java` launcher no longer accepts `-t`, `-tm`, `-Xfuture`,
`-checksource`, `-cs`, or `-noasyncgc` (24-migration). Search service units,
container entrypoints, shell wrappers, build plugins, test runners, and IDE
launch configurations; these options are often supplied outside source code.

The following old aliases were deprecated for removal in the same migration:

- `-verbosegc`; replace it with unified logging.
- `-noclassgc`, `-verify`, and `-verifyremote`.
- `-ss`, `-ms`, and `-mx`; use current long-form VM options.

Later migration work deprecates `Xmaxjitcodesize`,
`AlwaysActAsServerClassMachine`, `NeverActAsServerClassMachine`,
`AggressiveHeap`, and `MaxRAM` for removal (26-migration). Remove these
legacy tuning assumptions from scripts, images, deployment templates, and
generated launch configuration.

## Removed APIs and compatibility behavior

### Naming, time zones, desktop, and JMX

The 24-migration removes all of the following:

- Linux GTK 2 support.
- The JDK 1.1-compatible interpretation of `EST`, `MST`, and `HST` short
  time-zone IDs.
- `javax.naming.Context.APPLET` and
  `java.naming.rmi.security.manager`.
- JNDI remote code downloading, which is permanently disabled.
- Legacy `serialVersionUID` compatibility logic in JMX.

Do not try to preserve the removed JNDI download behavior with another launch
flag. Replace dependent deployment or lookup designs.

### Datagram sockets

`java.net.Socket` constructors can no longer create a datagram socket
(25-migration). Use `DatagramSocket` or `DatagramChannel` and retest the
networking path explicitly.

### Applets and forced thread stopping

The `java.applet` package, `javax.swing.JApplet`, and related Applet
integration are removed (26-migration). Source references no longer compile,
and previously compiled bytecode may fail during linkage.

`Thread.stop()` is also removed. Previously compiled callers can fail with
`NoSuchMethodError`. Replace forced stopping with interruption or another
cooperative cancellation protocol that gives the target thread a chance to
restore invariants and release resources.

### Platform-specific removals

The 26-migration also removes:

- Linux InfiniBand Sockets Direct Protocol support.
- The macOS Unicode Normalization Form D compatibility property.
- XML interchange in JMX `DescriptorSupport`.

Audit specialized networking, macOS filename/text handling, and JMX
serialization before rollout.

## Tool and module lifecycle

`java.util.zip.ZipError`, `jstatd`, `jrunscript`, the `jdk.jsobject`
module, legacy `LockingMode` / `LM_LEGACY` / `LM_MONITOR` modes, and
`jhsdb debugd` were deprecated for removal in 24-migration.

`jrunscript` is removed in 26-migration. Replace scripts that invoke it rather
than assuming the deprecation still permits its use.

## Monitoring and VM component removals

The 25-migration removes old JMX system properties, PerfData sampling, and
private `sun.rt._sync*` performance counters. Agents consuming these private
or legacy interfaces must migrate to supported JFR, JMX, or serviceability
APIs.

The bundled optional experimental Graal JIT and the 32-bit x86 port are also
removed in 25-migration. Remove x86 JDK assumptions from native artifacts,
custom images, installers, CI jobs, architecture detection, and distribution
logic.

## Platform and runtime-image assumptions

During 24-migration, Windows x86 support is already removed and Linux x86 is
deprecated for removal. Treat all 32-bit x86 JDK assumptions as migration
work rather than preserving them until a later failure.

Custom-image pipelines can use `jlink` without relying on installed JMOD
files as of 24. Retest custom plugins and reproducibility; the relaxed input
assumption does not prove that an existing image pipeline is reproducible.

## Features deprecated for removal

The 25-migration deprecates these surfaces for removal:

- The Linux `VFORK` process-launch mechanism.
- `java.locale.useOldISOCodes`.
- XML interchange in JMX `DescriptorSupport`.
- The `UseCompressedClassPointers` tuning option.
- Legacy permission classes associated with the disabled Security Manager.

Compressed class pointers themselves are not being disabled. Stop relying on
the explicit tuning option and let the VM select supported behavior.

## Migration sequence

1. Inventory compiler, launcher, service, image, container, build-tool, and
   IDE arguments.
2. Remove rejected launcher options; replace removal-target aliases and VM
   options before they become startup errors.
3. Compile the full source tree to expose Applet references and other removed
   APIs.
4. Run linkage and integration tests against old third-party bytecode,
   especially callers of `Thread.stop()`.
5. Exercise agents and dashboards without PerfData or private counters.
6. Rebuild native packaging and CI matrices without 32-bit x86 assumptions.
7. Test custom `jlink` plugins and compare runtime images for reproducibility.
8. Test macOS normalization, specialized Linux networking, and JMX
   serialization where those compatibility surfaces were used.
