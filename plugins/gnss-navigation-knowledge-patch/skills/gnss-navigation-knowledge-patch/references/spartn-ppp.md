# SPARTN & PPP Corrections

## SPARTN Corrections Format

SPARTN (Secure Position Augmentation for Real-Time Navigation) is an SSR-based correction format designed for PPP (Precise Point Positioning). Current version: **v2.0.3** (Nov 2025).

### Content

SSR (State Space Representation) corrections transmitted as separate components:
- **Orbit corrections**: Satellite position adjustments
- **Clock corrections**: Satellite clock adjustments
- **Code/phase biases**: Hardware bias corrections per signal
- **Atmosphere**: Ionosphere (HPAC — High-Precision Atmospheric Corrections) and troposphere (BPAC — Basic Precision Atmospheric Corrections)

### Supported Constellations

GPS, GLONASS, Galileo, BeiDou, QZSS.

### Security

Encrypted with dynamic key management. Keys distributed out-of-band (e.g., u-blox Thingstream MQTT topics or `RXM-SPARTNKEY` UBX message).

### Primary Service: u-blox PointPerfect

Commercial PPP service using SPARTN format. Delivery via:
- **L-band**: Satellite broadcast (requires L-band receiver, e.g., NEO-D9S)
- **IP**: MQTT over internet (lower latency, requires connectivity)

Convergence time: typically 30–60 seconds to cm-level with dual-frequency receiver.

## PPP vs RTK

| Aspect | RTK | PPP |
|--------|-----|-----|
| Corrections source | Nearby base station | Satellite/internet service |
| Baseline limit | ~35 km (accuracy degrades) | Global coverage |
| Convergence | Instant (with fix) | 30–60 s (SPARTN), minutes (IGS) |
| Infrastructure | Base station required | Subscription service or free (Galileo HAS) |
| Accuracy | 1–2 cm | 3–6 cm (converged) |
