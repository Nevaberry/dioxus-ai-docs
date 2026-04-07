# Galileo Services (HAS & OSNMA)

## Galileo HAS (High Accuracy Service)

Free real-time PPP corrections provided by the European GNSS system. Initial service declared **January 2023**.

### Corrections Provided

Orbit, clock, and code/phase bias corrections for:
- **Galileo**: E1, E5a, E5b, E6
- **GPS**: L1, L2C

### Delivery Methods

| Method | Details |
|--------|---------|
| **E6-B signal** | Broadcast on Galileo E6-B data channel at 448 bps. Requires E6-capable receiver hardware. |
| **NTRIP IDD** | Internet distribution via Ntrip. Requires registration at Galileo Service Centre (GSC). |

### Receiver Requirements

- Must implement a PPP (Precise Point Positioning) algorithm — HAS provides raw corrections, not a position solution
- Dual-frequency receiver recommended for ionosphere-free combination
- E6-B reception requires specific hardware support (not all Galileo receivers support E6)

### Performance

- Horizontal accuracy: ~20 cm (95%) after convergence
- Convergence time: several minutes (longer than commercial services like PointPerfect)

---

## Galileo OSNMA (Open Service Navigation Message Authentication)

Broadcast authentication for Galileo navigation messages to protect against spoofing. Initial service declared **July 2025**.

### How It Works

Based on **TESLA** (Timed Efficient Stream Loss-tolerant Authentication) protocol:
1. Satellite broadcasts navigation data + MAC (Message Authentication Code) on **E1-B**
2. Authentication key disclosed after a delay
3. Receiver verifies MAC retroactively using the disclosed key

### Receiver Setup

1. **Install Merkle tree root key**: Download from GSC (Galileo Service Centre) or EUSPA. One-time operation — this is the trust anchor.
2. **Maintain time synchronization**: Receiver must be within **30–300 seconds** of Galileo System Time (GST). TESLA requires loose time sync to validate key disclosure timing.

### Key Renewal

- **Over-The-Air (OTAR)**: New keys broadcast via the signal-in-space (SIS) — automatic for receivers tracking Galileo
- **Manual**: Download from GSC/EUSPA portal if OTAR chain is broken (e.g., extended receiver downtime)

### Limitations

- Only authenticates **Galileo** navigation messages (not GPS, GLONASS, BeiDou)
- Does not protect against **meaconing** (record-and-replay of authentic signals)
- Requires receiver firmware support for TESLA verification
