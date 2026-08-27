# ZED-F9P Operations

## Variants, signals, and base configuration

### Receiver variants and default signal sets

The `-01B/-02B/-04B/-05B` default is GPS L1 C/A/L2C, GLONASS L1OF/L2OF, Galileo E1B/C/E5b, BeiDou B1I/B2I, and QZSS L1 C/A/L2C, with SBAS L1 C/A available from HPG 1.13. The `-15B` is the L1/L5 variant: its documented default uses GPS L1 C/A, GLONASS L1OF, Galileo E1B/C/E5a, BeiDou B1I/B2a, QZSS L1 C/A/L5, and SBAS L1 C/A; its capability list includes GPS L5 even though the default list does not enable it.

Signal configuration requires both the constellation key and a valid band combination. Unsupported half-enabled dual-band combinations are rejected with `UBX-ACK-NAK` and `inv sig cfg`; documented exceptions allow BeiDou B1 without B2 and GPS L1 without L5, while QZSS requires GPS and SBAS requires GPS, Galileo, or both.

### Firmware rate and raw-output trade-offs

The documented simpleRTK2B firmware paths are not equivalent: HPG 1.13 supports navigation rates through 10 Hz, while HPG 1.51 is limited to 8 Hz but supports PointPerfect/SPARTN-era functionality. High-rate profiles disable BeiDou and UART GSV output to control processing and buffer load; the HPG 1.51 PPK profile uses 115200 baud and emits `UBX-RXM-RAWX` plus `UBX-RXM-SFRBX` on UART1, UART2, and USB, while the supplied HPG 1.13 path does not export that PPK raw stream.

For F9 receivers, use classic u-center rather than u-center2 and select the Generation 9 configuration format. A configuration file that changes the active UART baud rate can interrupt its own transfer, so reconnect at the new rate and resume the load.

## Ports, protocols, and configuration

### Default ports are not interchangeable

UART1 starts at 38400 8N1 with GGA, GLL, GSA, GSV, RMC, VTG, and TXT output; UBX and RTCM protocols are enabled but have no periodic output messages. USB, I2C, and SPI initially expose the same message/protocol set, whereas UART2 starts as a correction port with RTCM enabled, NMEA disabled, and SPARTN input available from HPG 1.30.

UART2 gains configurable UBX input/output in HPG 1.30 and UBX input is enabled by default in HPG 1.32, but it cannot be the sole host interface: firmware update, safeboot, backup-mode functions, and the startup screen are unavailable there.

### Configuration acknowledgments and message-rate gating

Wait for each `UBX-ACK-ACK` or `UBX-ACK-NAK` before sending another configuration operation; otherwise input processing can pause and emit `wait for cfg ACK`. `CFG-MSGOUT-*` values are per-interface event divisors—`1` means every related epoch, `2` every second epoch—and a message is still suppressed unless its protocol is enabled on that interface.

### High-precision NMEA is opt-in

Default NMEA precision cannot represent a high-precision fix. `CFG-NMEA-HIGHPREC` adds seven fractional latitude/longitude digits and three altitude digits, but the mode deliberately violates standard NMEA and cannot coexist with compatibility mode or the 82-character output limit.

## RTCM rover and base operation

### RTCM 3.4 input envelope

The receiver implements RTCM 10403.4/version 3.4. Rover input includes legacy GPS 1001–1004 and GLONASS 1009–1012 observations, reference/descriptor messages 1005, 1006, 1007, and 1033, MSM4/MSM5/MSM7 for GPS, GLONASS, Galileo, and BeiDou, message 1230, and proprietary 4072.0; base output offers MSM4 or MSM7 but not MSM5.

HPG L1L5 1.40 does not accept the legacy GPS/GLONASS observation messages or 4072.0. Message 4072.1 is only valid with HPG 1.12 and belongs to that firmware's moving-base flow.

### Rover correction acceptance and timeout

Ambiguity fixing needs both a matching observation message (MSM4 or MSM7) and reference position 1005 or 1006. Their station IDs must agree, and GLONASS fixing additionally needs 1230 or 1033; otherwise GLONASS ambiguities remain float even when fixed mode is requested.

Corrections older than 60 seconds are rejected by default, after which the solution falls back to 3D or 3D/DGNSS; change this with `CFG-NAVSPG-CONSTR_DGNSSTO`. `CFG-RTCM-DF003_IN` can select a station ID and `CFG-RTCM-DF003_IN_FILTER=RELAXED` is the recommended filtering mode.

### Conservative fixing and RTK status fields

HPG 1.50 adds conservative ambiguity resolution with `CFG-NAVHPG-DGNSSMODE=RTK_CAR`, trading longer time-to-first-fix or more float epochs for a much stricter fix decision. Ordinary fixed mode attempts fixes whenever possible, while float mode never attempts integer fixing.

In RTK output, GGA quality is `4` for fixed and `5` for float; GLL/VTG use mode `D` for either, while RMC/GNS use `R` for fixed and `F` for float. `UBX-NAV-PVT.carrSoln` and the corresponding status/relative-position fields use `2` for fixed and `1` for float.

### RTCM base streams must be internally consistent

All observation messages must run at one rate, use only one observation type per constellation, and use the same MSM family across constellations. Every output port must also carry the same RTCM configuration or the MSM multiple-message bit can be wrong; 1005/1006 may run more slowly, but the rover cannot solve until one arrives.

## Moving-base operation

### Moving-base message contract

Moving-base operation is unavailable on HPG L1L5 1.40. On supported firmware, the base must send 4072.0 at every observation epoch plus same-rate MSM4 or MSM7 observations, and the base and rover must share navigation and measurement rates; HPG 1.12 instead requires MSM7 and 4072.1, while HPG 1.13 and later support MSM4 and should omit obsolete 4072.1.

A moving base can simultaneously consume ordinary RTCM to obtain an absolute fixed solution and generate the relative correction stream. The rover reports the vector, length, heading, accuracies, and validity through `UBX-NAV-RELPOSNED`.

### Moving-base latency changes the effective update rate

Keep link latency below `configured update period - 50 ms`. If time-matched base observations arrive too late, the rover progressively lowers its navigation rate to 1 Hz and then invalidates the relative solution if even 1 Hz cannot be sustained.

## SPARTN, CLAS, and correction selection

### Receiver-specific SPARTN subset

PPP-RTK/SPARTN starts with HPG 1.30, but this receiver consumes the SPARTN 2.0.1 subset rather than every feature of newer specifications: GPS/GLONASS/Galileo OCB and HPAC, BeiDou OCB/HPAC from HPG L1L5 1.40 onward, and geographic-area definitions. Group and embedded authentication messages are not applied, and an HPAC message must include a troposphere model for the receiver to reach RTK fixed.

### SPARTN source selection is host-controlled

Internet corrections arrive as native SPARTN messages, while an L-band receiver supplies `UBX-RXM-PMP`; choose exactly one with `CFG-SPARTN-USE_SOURCE=IP|LBAND`. There is no automatic failover: the host must inspect `UBX-RXM-COR`/`UBX-MON-COMMS` and switch sources, and both UBX and SPARTN input protocols should be enabled on a port carrying L-band `UBX-RXM-PMP` data.

### Encrypted SPARTN keys are a rolling pair

On each power cycle or first encrypted use, poll `UBX-RXM-SPARTNKEY` and load the current and next dynamic keys with that same message when absent or nearing expiry. The receiver automatically promotes the next key when the current one expires, but only decrypts the source selected by `CFG-SPARTN-USE_SOURCE`; without a next key, decryption stops at rollover.

### CLAS ingestion and correction-type switching

QZSS CLAS is accepted as `UBX-RXM-QZSSL6` forwarded directly from a compatible L6 receiver, with no host parsing required. Before changing an active rover between RTCM, SPARTN, and CLAS, reset the ZED-F9P so state from the old correction type is not carried into the new solution.

## Navigation solutions, fallback, and validity

### Parallel standalone navigation output

HPG 1.30 adds a secondary standalone-GNSS solution alongside the full primary solution. Enable `CFG-NAV2-OUT_ENABLED` and at least one `CFG-MSGOUT-UBX_NAV2_*` rate; primary `UBX-NAV-*` messages and `UBX-NAV-EOE` are emitted first for an epoch, followed by payload-compatible `UBX-NAV2-*` messages and `UBX-NAV2-EOE` for that same epoch.

The two solutions run at the same navigation rate, but NAV2 adds computation and interface load and can reduce the maximum achievable update rate. Its independent `CFG-NAV2-*` controls allow, for example, a standalone solution with different SBAS-integrity policy for comparison against the RTK solution.

### Correction fallback and SBAS integrity restriction

SBAS is subordinate to an active correction stream; after correction loss it is considered only after `CFG-NAVSPG-CONSTR_DGNSSTO`, 60 seconds by default. The receiver may track/range with several SBAS satellites but chooses one primary correction source, so configure a regional PRN mask to prevent a distant system from winning selection.

Enabling SBAS integrity removes every measurement lacking SBAS integrity information—including all non-GPS signals—and requires integrity data for at least five GPS satellites. A fallback from service corrections to SBAS/standalone positioning can also change the output reference frame, which is why rover profiles may disable SBAS to avoid jumps during short correction outages.

### QZSS SLAS corrected-measurement policy

SLAS is likewise used only when RTCM, SPARTN, or CLAS is unavailable. With `CFG-QZSS-USE_SLAS_RAIM_UNCORR` set, the solution uses only corrected measurements and abandons corrections if a complete corrected set is unavailable; when clear it may mix corrected and uncorrected measurements, while the strict setting also prevents observing non-QZSS time systems.

### Navigation-model and validity traps

`CFG-NAVSPG-DYNMODEL` changes live: stationary constrains velocity to zero, at-sea assumes zero vertical velocity and sea level, and airborne models do not permit 2D fixes. Violating a model's altitude/velocity sanity limits invalidates the solution, and high-dynamic models can increase reported position deviation.

Do not infer usability from `fixType` alone; check `UBX-NAV-PVT.gnssFixOK` or the NMEA validity flag. `CFG-NAVSPG-OUTFIL` PDOP/accuracy filters govern ordinary 2D/3D fixes but do not govern RTK float/fixed, which is validated internally by the RTK engine.

### Per-axis protection levels

From HPG 1.30, `UBX-NAV-PL` reports a one-dimensional protection level for each coordinate axis and encodes its target misleading-information risk with coefficient/exponent fields. Use the values only when both `plPosValid` is set and `plPosFrame` is nonzero; compare each valid level with the application's alert limit rather than treating the ordinary accuracy estimate as an integrity bound.

## Logging, physical interfaces, and status output

### On-receiver logs are not high-precision observation logs

Flash logging records only valid position fixes, at no more than 1 Hz, rounded to one second, `1e-6` degree latitude/longitude, and 0.1 m mean-sea-level altitude; it can also store host byte strings. Retrieval is limited to 256 entries per `UBX-LOG-RETRIEVE`, and any logging command interrupts an active retrieval, so use `RAWX`/`SFRBX` rather than `UBX-LOG-*` for PPK observations.

### UART backpressure is loss, not flow control

The UARTs have no handshaking or hardware flow control. If enabled output cannot be transmitted within roughly one second, new messages are dropped; retain at least the 38400 default or raise the baud rate/reduce messages, and wait about 100 ms after changing baud before sending at the new rate.

### I2C and SPI stream semantics

I2C is peripheral-only Fast-mode at up to 400 kHz and does not support Standard-mode. Registers `0xFD/0xFE` expose the pending-byte count and repeated reads of `0xFF` drain the message stream (`0xFF` also means empty); raw UBX/NMEA writes must contain at least two bytes, and `CFG-I2C-ADDRESS` stores the seven-bit address plus R/W bit as one eight-bit value.

SPI is also peripheral-only and full-duplex: every written byte clocks one pending output byte, so send `0xFF` dummy bytes while reading and ignore `0xFF` outside framed messages. The receiver pauses parsing after 50 consecutive dummy bytes and resumes on the next non-`0xFF` byte.

### Hardware RTK status encoding

The `RTK_STAT` output is low for RTK fixed, blinks while supported corrections are being received and used without a fixed solution, and remains high when no carrier-phase solution is available. It therefore distinguishes correction ingestion from ambiguity fixing without parsing a serial message.

### AssistNow support and state preservation

ZED-F9P supports AssistNow Online, not AssistNow Offline; the HTTPS response consists of `UBX-MGA-*` messages that can be forwarded unchanged. Preserve aiding and operational state with battery-backed RAM, `UBX-UPD-SOS` save-on-shutdown, or a host-side `UBX-MGA-DBD` database dump/restore.

## Time validity and pulse generation

### Time tags require validity handling

The local 1 kHz clock can produce 999 or 1001 ticks between nominal one-second navigation epochs as it follows GNSS time. Use equal `iTOW` only to group messages from one epoch—`iTOW` itself can be based on an invalid conversion—and use `UBX-NAV-PVT` or a constellation-specific `UBX-NAV-TIME*` message for absolute time.

`validDate`/`validTime` mean the receiver has a value, while `confirmedDate`/`confirmedTime` mean an independent source has made it highly trustworthy; these confirmation flags are meaningful only when `confirmedAvai` is set. Until `fullyResolved` is set, unresolved whole seconds can leave UTC roughly 20 seconds wrong even when the output looks plausible.

### UBX UTC fields need signed-nanosecond normalization

The calendar fields in `UBX-NAV-PVT` and `UBX-NAV-TIMEUTC` are rounded to the nearest hundredth of a second, and `nano` is the signed correction needed to recover precise UTC. It can range from about -5 ms to +995 ms; a negative value means the calendar fields may already have rounded into the next second, day, month, or year, so apply `nano` before normalizing the date.

### Time-pulse grids and delay signs

Choose `CFG-TP-TIMEGRID_TP*` to match an enabled constellation; generating an unavailable constellation's time compromises accuracy, and UTC pulses can be delayed after cold start while UTC-conversion parameters are acquired. Automatic UTC selection prefers GPS/USNO, then GLONASS/SU, BeiDou/NTSC, Galileo/EU, and finally NavIC/NPLI.

RF cable delay is configured positive to advance the pulse and compensate propagation before the receiver, whereas positive user delay retards the output pulse. Locked and unlocked pulse period/length can differ, and neither the high nor low interval may be below 50 ns.

### Timing-message cadence is not one message per edge

`UBX-TIM-TP` is bound to 1 Hz, so use a 1 Hz measurement rate and 1 PPS when a one-to-one pulse/message relationship is required; at higher pulse rates, several reports can refer to the next pulse and the last has the best quantization error. `UBX-TIM-TM2` reports only the last rising and last falling `EXTINT` edge between measurement epochs.

## Security monitoring and configuration protection

### Spoofing and jamming monitoring limits

Spoofing detection looks for a transition from initially genuine signals and therefore cannot detect a receiver that starts while already under spoofing; multi-constellation tracking improves detection. Current state is in `UBX-SEC-SIG`, while `UBX-SEC-SIGLOG` retains only 16 start/stop or trigger/timeout events and is cleared by reset or power cycle.

### Configuration lock persistence

From HPG 1.30, `CFG-SEC-CFG_LOCK=true` prevents changes to every configuration layer once present in runtime RAM. A RAM or BBR lock disappears when that memory is cleared, but a flash-layer lock is permanent except that a firmware upload erases flash and clears it; apply the lock on the same layer as the configuration and test first in RAM.

## Receiver OSNMA support

### ZED-F9P OSNMA provisioning

The `-05B` with HPG 1.50 adds OSNMA, but its public key and Merkle root are not factory-installed. Provision them with `UBX-MGA-GAL-OSNMA_PUBKEY` and `UBX-MGA-GAL-OSNMA_MERKLE`; they persist in nonvolatile storage, and a host-provided public key does not require a Merkle root, while over-the-air public-key replacement does.

### OSNMA trusted time and authenticated-only navigation

Supply trusted UTC or GNSS time with `UBX-MGA-INI-TIME_UTC` or `UBX-MGA-INI-TIME_GNSS` and monitor its free-running propagation with `UBX-NAV-TIMETRUSTED`: under 15 seconds error enables fast MACs, 15–165 seconds uses slow MACs, and 165 seconds or more disables OSNMA. `CFG-GAL-OSNMA_TIMESYNC` enforces this by default.

`CFG-NAVSPG-ONLY_AUTHDATA` and `CFG-NAV2-NAVSPG_ONLY_AUTHDATA` restrict their respective solutions to authenticated navigation data; `CFG-GAL-OSNMA_INAVPRIM` prefers authenticated I/NAV over unauthenticated F/NAV. Verify the result through `UBX-SEC-OSNMA`, per-signal authentication in `UBX-NAV-SIG`, and `UBX-NAV-PVT.nmaFixStatus` rather than assuming that enabling OSNMA authenticated the current fix.

## Raw data, spectrum, and coordinate output

### Raw broadcast-data framing

`UBX-RXM-SFRBX` is emitted only after a complete navigation block passes the receiver's parity checks; GPS L1 C/A inversion has already been undone, so host code must not repeat parity processing. Select the decoder by `gnssId` and `sigId`, ignore all padding bits, and tolerate GLONASS `svId=255` or unknown frame/superframe values during early acquisition.

Signal-specific layouts remain important: BeiDou's two most-significant bits in each 30-bit word are padding, Galileo E1/E5b report paired I/NAV pages while E5a reports F/NAV, and QZSS L1 C/A/L2C/L5/L1S follow the corresponding GPS or SBAS framing.

### Built-in spectrum monitor

From HPG 1.13, `UBX-MON-SPAN` emits one low-resolution spectrum report per second with 256 quarter-dB bins in an L1 block and, where present, an L2/L5 block. Bin `i` is at `center + span * (i - 128) / 256`; use it comparatively for jammer/noise diagnosis, not as an absolute calibrated analyzer, and ignore the benign internal center-frequency spur.

### Correction frames and geoid height

RTK and PPP-RTK coordinates remain in the correction provider's reference frame, so applications comparing against another realization must apply their own datum transformation, including time-dependent drift where relevant. Mean-sea-level height and geoid separation use a limited-resolution EGM96 model; precision height work should take ellipsoidal height and apply a better external geoid model.

## InertialSense IMX integration

### IMX routing values

For IMX firmware 1.8.5 or later, a single onboard F9P on serial 1 uses `ioConfig=0x0244a040` and `RTKCfgBits=0x00000002` for precision rover mode; a dual receiver uses serial 1 for GPS1, serial 0 for GPS2, `ioConfig=0x025ca040`, and `RTKCfgBits=0x00000006` for GPS1 external precision plus GPS2 compass. Base correction output uses `RTKCfgBits=0x00000900`; on a dual system both serial ports are occupied, so route the RTCM stream over USB.

The corresponding base profile sends MSM observations every 0.4 seconds and 1005/1230 every two seconds. Dual-receiver compassing also requires the receivers to share the reference clock and PPS.

### Updating an F9P through an IMX bridge

Enable `SYS_CMD_ENABLE_SERIAL_PORT_BRIDGE_USB_TO_GPS1` or `_GPS2` through `DID_SYS_CMD`, then update from u-center at 921600 baud with “Send training sequence” enabled and “Enter safeboot before update” disabled. Power-cycle the IMX after the transfer; the firmware version is exposed through `DID_GPS1_VERSION`/`DID_GPS2_VERSION`.
