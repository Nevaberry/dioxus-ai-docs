# Installation and Building

### Installation-source consistency
Remove every part of an older installation before switching between distribution packages and source builds: the daemon, clients, and libraries must come from the same GPSD version. The package named `gpsd` on PyPI is an unrelated, obsolete client that is incompatible with GPSD releases from the last decade; install GPSD from a distribution repository or its source tree instead.

### Build-time and optional dependencies
Python is required by SCons and GPSD's code generators but is not required to run the daemon; when the target interpreter is not available as `python`, select it separately from the interpreter running SCons.

```sh
scons target_python=python3.7
```

A C++ compiler enables `libgpsmm`, Qt enables `libQgpsmm`, curses enables `cgps` and `gpsmon`, `pps-tools` enables KPPS timing, and libusb enables discovery of older Garmin USB devices. Python GI/Cairo enables `xgps` and `xgpsspeed`, pyserial enables direct-serial mode in `ubxtool` and `zerk`, and Matplotlib enables `gpsplot`.

### SCons install targets
Build and test before installing; `udev-install` is a separate target for Linux hotplug rules and wrappers, with `udev-uninstall` as its inverse. SCons is single-phase, so `install` may rebuild and must receive the same feature options as the original build; `uninstall` removes a normal installation.

```sh
scons && scons check
scons install
scons udev-install
scons uninstall
```

### Installation layout and prerequisite paths
The default prefix is `/usr/local`; `prefix`, `DESTDIR`, and directory variables such as `bindir`, `docdir`, `mandir`, and `includedir` customize or stage installation. An `includedir` setting changes only where GPSD headers are installed, not compiler search paths; use `CPPFLAGS` and `LDFLAGS` to find nonstandard prerequisites.

```sh
scons prefix=/usr
DESTDIR=/tmp/pkgroot scons prefix=/usr install
CPPFLAGS=-I/usr/foo/include LDFLAGS=-L/usr/foo/lib scons
```

### Minimal builds
`minimal=yes` changes every Boolean feature default to false, after which required features must be explicitly enabled; the NMEA0183 driver is always built. Disabling the daemon and clients yields only a library, with `shared=True` selecting `libgps.so` instead of the default `libgps.a` in these examples.

```sh
scons minimal=yes socket_export=yes
scons minimal=yes gpsd=False gpsdclients=False
scons minimal=yes shared=True gpsd=False gpsdclients=False
```

### Cross-building contract
For a cross-build, `target` names the toolchain prefix, so a target such as `arm-indigo-linux-gnueabi` expects tools including `arm-indigo-linux-gnueabi-gcc`; `sysroot` supplies target headers and libraries as if rooted at `/`, while `prefix` selects the staging installation. Host-only bindings, Python support, and manual generation can be disabled for an embedded target.

```sh
scons target=arm-indigo-linux-gnueabi \
  sysroot=/work/buildroot/output/staging \
  prefix=/work/buildroot/output/staging/usr \
  python=False libgpsmm=False libQgpsmm=False manbuild=no
```

### Compiled device identity and permissions
Serial device nodes must be group-readable and group-writable, normally mode `0660`, and their group must match the daemon's compiled group; Debian-family systems normally use `dialout`, while several other distributions use `uucp`. Choose the dropped-privilege identity with the SCons `gpsd_user` and `gpsd_group` options, and ensure all hotplugged tty devices use that group.

```sh
scons gpsd_user=gpsd gpsd_group=dialout
```

### Hotplug versus unconditional startup
The bundled udev integration starts GPSD on USB activation and can be relocated with `udevdir`; serial-port receivers and hosts that use GPSD to set system time instead need unconditional init or systemd startup. A source installation does not create `/etc/default/gpsd`; `packaging/deb/etc_default_gpsd.in` is its prototype, and the Debian udev/systemd glue may require a reboot after installation.

```sh
scons install
scons udevdir=/lib/udev udev-install
```

### Regression-test timing and cleanup
Run `scons check` before installation; running it as root avoids expected `seteuid()` and shared-memory errors that a non-root run may report. For sporadic truncated-input failures, retry with `slow=yes`, then raise `WRITE_PAD` above the value printed by the tests; parallel `-j` builds and tests are supported but interleave diagnostics.

```sh
scons check slow=yes
WRITE_PAD=<larger-delay> scons check slow=yes
```

Use `scons -c` and remove `.sconsign.*dblite` when stale configuration produces errors such as `CC doesn't work` or missing link symbols; `scons testclean` additionally removes programs left by an interrupted regression run.

```sh
scons -c
rm -f .sconsign.*dblite
scons testclean
```

### Live installation smoke test
Run a foreground debug instance as root with the receiver named explicitly, connect to port 2947, and enable JSON watching; a version greeting followed by JSON reports verifies the daemon path before service integration. `cgps` or `xgps` can then verify decoded position and satellite data.

```sh
gpsd -D 5 -N -n /dev/ttyUSB0
telnet localhost 2947
?WATCH={"enable":true,"json":true};
```

### Compiled leap-second fallback
Releases embed the then-current leap-second value as `BUILD_LEAPSECONDS` in `gpsd.h`. GPSD uses this fallback to validate receiver UTC when a driver has not supplied the current offset—especially with NMEA-only receivers—so a stale build or a newly powered receiver can temporarily have the wrong internal leap-second value.

