# Migration, Removals, and Deprecations

Use this reference when an upgrade breaks compilation, linking, process
startup, platform packaging, or operational tooling.

## Launcher and compatibility removals

### Launcher arguments

The `java` launcher no longer accepts `-t`, `-tm`, `-Xfuture`, `-checksource`,
`-cs`, or `-noasyncgc` (24-migration). Search beyond application scripts:
service definitions, container entrypoints, build plugins, test launchers, and
IDE configurations often hide these arguments.

The aliases `-verbosegc`, `-noclassgc`, `-verify`, `-verifyremote`, `-ss`,
`-ms`, and `-mx` are deprecated for removal (24-migration). Move logging to
unified logging and replace aliases with supported current VM options.

### Desktop, naming, and compatibility behavior

Linux GTK 2 support is removed (24-migration). Desktop applications that
depended on it need a supported GTK environment.

The JDK 1.1-compatible interpretation of the short time-zone IDs `EST`, `MST`,
and `HST` is removed (24-migration). Audit persisted configuration and code
that expects the former offsets or daylight-saving behavior.

The following naming compatibility surfaces are removed (24-migration):

- `javax.naming.Context.APPLET`
- `java.naming.rmi.security.manager`
- JNDI remote code downloading

Remote code downloading is permanently disabled; do not design a workaround
that assumes a property can re-enable it.

Legacy `serialVersionUID` compatibility logic in JMX is also removed
(24-migration). Revalidate serialized management payloads rather than relying
on the former accommodation.

## API and tool removals

### Security Manager

Attempting to enable a Security Manager is an error (24). Its APIs remain only
as a migration aid before eventual removal. Remove enablement flags and migrate
authorization or sandboxing assumptions to supported deployment boundaries.

Legacy permission classes associated with the disabled Security Manager are
deprecated for removal (25-migration).

### Applets and thread stopping

The `java.applet` package, `javax.swing.JApplet`, and related Applet
integration are removed (26-migration). Source using them no longer compiles,
and older bytecode can fail to link.

`Thread.stop()` is removed (26-migration). Old bytecode may throw
`NoSuchMethodError`. Replace forced stopping with interruption or another
cooperative cancellation protocol that lets the target thread restore
invariants and release resources safely.

### Tools and modules

These surfaces are deprecated for removal (24-migration):

- `java.util.zip.ZipError`
- `jstatd`
- `jrunscript`
- the `jdk.jsobject` module
- legacy `LockingMode`, `LM_LEGACY`, and `LM_MONITOR` modes
- `jhsdb debugd`

`jrunscript` is subsequently removed (26-migration). Remove script and
automation dependencies rather than merely suppressing deprecation output.

## Socket, monitoring, and JMX migration

`java.net.Socket` constructors can no longer create a datagram socket
(25-migration). Use `DatagramSocket` or `DatagramChannel`.

Old JMX system properties, PerfData sampling, and the private
`sun.rt._sync*` performance counters are removed (25-migration). Monitoring
agents must use supported JFR, JMX, or serviceability APIs.

XML interchange in JMX `DescriptorSupport` is deprecated for removal in
25-migration and removed in 26-migration. Replace XML-dependent interchange
before adopting the later runtime.

## Removed VM and platform components

### 32-bit x86

Windows x86 support is removed and Linux x86 is deprecated for removal
(24-migration). The 32-bit x86 port is then removed (25-migration).

Remove 32-bit x86 assumptions from:

- CI matrices and architecture checks
- native libraries and artifact classifiers
- runtime images and installers
- container and host selection logic

### Graal JIT

The bundled optional experimental Graal JIT is removed (25-migration). Do not
assume that selecting the former bundled compiler remains a standard JDK
runtime option.

### Platform-specific surfaces

JDK 26 removes Linux InfiniBand Sockets Direct Protocol support and the macOS
Unicode Normalization Form D compatibility property (26-migration). Test
platform-specific networking and filename or text normalization behavior
before rollout.

## Deprecated process, locale, and VM controls

JDK 25 deprecates these surfaces for removal (25-migration):

- the Linux `VFORK` process-launch mechanism
- `java.locale.useOldISOCodes`
- `UseCompressedClassPointers`

The compressed-class-pointer feature itself is not disabled. Stop relying on
its explicit tuning option and allow the VM to select supported behavior.

JDK 26 deprecates these VM options for removal (26-migration):

- `Xmaxjitcodesize`
- `AlwaysActAsServerClassMachine`
- `NeverActAsServerClassMachine`
- `AggressiveHeap`
- `MaxRAM`

Remove the corresponding legacy tuning assumptions from launch scripts,
service templates, charts, and image defaults.

## Migration sequence

1. Compile source against the destination JDK to expose removed types.
2. Scan dependencies and packaged bytecode for calls to removed members.
3. Inventory every launch command and reject obsolete flags in CI.
4. Exercise monitoring and management agents against the destination runtime.
5. Rebuild native distributions without 32-bit x86 assumptions.
6. Test platform-specific networking and normalization behavior on target
   hosts.
7. Replace removal-target APIs and tools before they become hard failures.
