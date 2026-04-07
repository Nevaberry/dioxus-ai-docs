# RTK & RTCM 3.x Corrections

## RTCM 3.x Message Types for RTK

Real-Time Kinematic (RTK) requires a base station to broadcast correction data to the rover. RTCM 3.x is the standard binary format for these corrections.

### Minimum Base Station Output

| Message | Content | Typical interval |
|---------|---------|-----------------|
| **1005** | Antenna Reference Point (ARP) position | 2 s |
| **1074** | GPS MSM4 (code + carrier observations) | 1 s |
| **1084** | GLONASS MSM4 | 1 s |
| **1094** | Galileo MSM4 | 1 s |
| **1124** | BeiDou MSM4 | 1 s |
| **1230** | GLONASS code-phase biases | 10 s |

### MSM4 vs MSM7

- **MSM4** (messages 1074/1084/1094/1124): Standard precision — code, carrier, CNR. Sufficient for most RTK applications.
- **MSM7** (messages 1077/1087/1097/1127): Full precision — adds Doppler, extended carrier phase resolution. Used when highest accuracy needed.

Typical combined throughput: ~2 kB/s for multi-constellation MSM4.

### ARP Messages

| Message | Content |
|---------|---------|
| **1005** | Antenna Reference Point (X, Y, Z ECEF), no antenna height |
| **1006** | Same as 1005 + antenna height above ARP |

### Moving Base RTK

For rover-on-vehicle scenarios where the base is also moving (e.g., heading determination):
- Base outputs **4072.1** (u-blox proprietary moving-base RTCM)
- Both receivers need same constellation/frequency configuration

## NTRIP (Networked Transport of RTCM via Internet)

Protocol for streaming RTCM corrections over the internet. Architecture:
- **Caster**: Server that aggregates and distributes streams (e.g., RTK2Go, UNAVCO)
- **Server** (base station): Pushes RTCM data to caster
- **Client** (rover): Pulls RTCM data from caster

Client sends GGA position to caster for VRS (Virtual Reference Station) networks to generate location-specific corrections.
