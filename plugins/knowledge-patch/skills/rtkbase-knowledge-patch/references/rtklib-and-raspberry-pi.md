# RTKLIB and Raspberry Pi Operations

## Bundled RTKLIB

RTKBase bundles RTKLIB v2.5.0-EX since 2.7.0.

## Building the console programs

On a headless Raspberry Pi, build the real-time `str2str` and `rtkrcv` programs
from their individual `gcc` directories and install them on `PATH`:

```bash
git clone https://github.com/rtklibexplorer/RTKLIB.git
cd RTKLIB/app/consapp/str2str/gcc
make
sudo cp str2str /usr/local/bin/
cd ../../rtkrcv/gcc
make
sudo cp rtkrcv /usr/local/bin/
```

`convbin`, `rnx2rtkp`, and `pos2kml` can be built from their corresponding
directories. Running `make` in `RTKLIB/app` builds all five console programs as a
group.

## Qt GUI build on Linux

The documented Ubuntu 20.04 build requires the compiler tools, PNG development
files, Qt 5, and the Qt serial-port development package. For the updated demo5 Qt
layout, build and install from `app/qtapp`:

```bash
sudo apt update
sudo apt install build-essential libpng-dev qt5-default libqt5serialport5-dev
cd RTKLIB/app/qtapp
qmake
make
./install_qtapp
```

The Qt interfaces may omit demo5-only fields even though the programs share the
same core processing code. `RTKCONV` and `RTKPOST` are usable; `RTKPLOT` is not
fully functional in this Qt port.

## U-Blox stream preparation

For RTKLIB raw logging, enable `UBX-RXM-SFRBX` navigation data and
`UBX-RXM-RAWX` observations. Verify enabled constellations and measurement rate,
then save the configuration to flash with `CFG`.

NMEA is not required for later RINEX conversion. It is required when a VRS
correction service needs GGA positions from the rover.

Disable unused UARTs where practical. A low baud configured for a UART can
constrain output bandwidth even when RTKLIB reads the receiver over USB.

## Verifying and logging with `str2str`

Read a serial input without an output as a quick stream check. Add a file output
to record it; RTKLIB expands time keywords in the filename:

```bash
str2str -in serial://ttyACM0
str2str -in serial://ttyACM0 -out rover_%m%d_%h%M.ubx
```

Check an NTRIP input similarly by writing it to a temporary file and verifying
nonzero transfer counts with no errors.

## VRS GGA relay and receiver-fed corrections

A VRS mount point normally waits for an approximate rover position in NMEA GGA.
With GGA enabled on the receiver, `-b 1` relays serial GGA to the NTRIP input and
the output sends received corrections back to the receiver:

```bash
str2str \
  -in ntrip://username:password@caster.example:2101/VRS \
  -b 1 \
  -out serial://ttyACM0:115200:8:n:1
```

Full serial settings prevent a baud mismatch. Alternatively,
`-p <lat> <lon> <height> -n 1` supplies a fixed position and GGA request cycle.
Appending `#1000` to the serial output path exposes the receiver-relayed stream
on TCP port 1000 for another RTKLIB process.

## Real-time positioning with `rtkrcv`

Start with demo5's `rtknavi_example.conf`. Configure the rover as the first input
and the RTCM correction stream as the second. This single-frequency U-Blox
example gets the base position from RTCM, requests VRS positions when needed,
writes LLH solutions, and retains both raw inputs:

```ini
pos1-posmode =kinematic
pos1-frequency =l1
pos1-navsys =13
pos2-armode =fix-and-hold
pos2-gloarmode =fix-and-hold
ant2-postype =rtcm

inpstr1-type =serial
inpstr1-path =ttyACM0
inpstr1-format =ubx
inpstr2-type =ntripcli
inpstr2-path =username:password@caster.example:2101/MOUNT
inpstr2-format =rtcm3
inpstr2-nmeareq =single

out-solformat =llh
outstr1-type =file
outstr1-path =rtkrcv_%m%d_%h%M.pos
outstr1-format =llh
logstr1-type =file
logstr1-path =rover_%m%d_%h%M.ubx
logstr2-type =file
logstr2-path =base_%m%d_%h%M.rtcm3
```

Launch and inspect status:

```bash
rtkrcv -s -o rtkrcv_pi.conf
```

At the prompt, enter `status 1` and verify that a base-position message such as
RTCM 1005 is arriving. The `?` prompt lists diagnostics including `stream`,
`satellite`, `observ`, `navidata`, and `error`.

Rerun with `-t 3` to create a trace file, use `shutdown` for a clean exit, and set
`out-outsingle=on` when position output should continue in single mode while
corrections are unavailable.
