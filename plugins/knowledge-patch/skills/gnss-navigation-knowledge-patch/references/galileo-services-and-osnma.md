# Galileo Services and OSNMA

## High Accuracy Service

### Correction products and receiver processing

The free Initial Service declared on 24 January 2023 supplies real-time satellite orbit and clock corrections to broadcast ephemerides plus satellite biases. It supports Galileo E1/E5a/E5b/E6 and GPS L1/L2C, but the receiver must apply the products in a PPP algorithm to compute a high-accuracy PVT solution.

### Signal-in-space and Internet delivery

HAS corrections are available both from the E6-B signal and through the registered Internet Data Distribution interface, which uses Ntrip. These are complementary reception paths for the correction data, not separate positioning services.

### Initial Service limitations

Initial Service is Phase 1 and exposes Service Level 1 with reduced coverage and performance relative to the full-service objectives; phase biases are not yet supplied. A client must therefore not assume either phase-bias products or Service Level 2 availability until the service reaches the planned full capability.

## Time and search-and-rescue services

### Broadcast time-scale offsets

The Galileo navigation message includes the differences between Galileo System Time, UTC, and GPS Time, allowing a timing implementation to use broadcast offsets rather than treating those time scales as identical.

### Search-and-rescue return link

Galileo's MEOSAR transponders relay 406 MHz distress-beacon signals to rescue coordination centres and can send a Return Link Message back to a compatible beacon to confirm that its alert was detected. The Return Link Service has been operational for capable beacons since January 2020.

## OSNMA service boundary

### Initial Service scope and trust boundary

OSNMA Initial Service, operational since 24 July 2025, is a free worldwide delayed-disclosure authentication service for Galileo Open Service I/NAV data. It authenticates navigation-message origin and integrity but not the ranging signal, does not by itself prove the authenticity of a receiver's PVT solution, and is specified for non-safety-critical use without a service guarantee.

## OSNMA receiver trust and verification

### Trust bootstrap and verification flow

An OSNMA receiver first verifies the TESLA root-key signature with an OSNMA public key, verifies a disclosed TESLA key against that root key, and then compares the received MAC with one computed from the navigation data and verified TESLA key. Before processing, it must be synchronized to Galileo System Time within the mode-dependent 30-to-300-second requirement and must protect stored cryptographic material against modification; confidentiality of that material is not required.

The Merkle-tree root is a one-time trust anchor obtainable only through the GSC Internet interface and is needed to authenticate new public keys received over the signal and OSNMA Alert Messages. Public keys are available from either the signal or GSC, can be renewed over the air, and are also published with PKI certificates and revocation lists; a future Merkle root is published at least two years before its rare planned renewal.

## OSNMA signal transport and page processing

### E1-B transport, page handling, and cross-authentication

OSNMA occupies the 40-bit reserved field in each nominal E1-B I/NAV odd page and authenticates I/NAV data carried on both E1-B and E5b-I. Its 8-bit HKROOT portion carries status flags and digital-signature material, while the 32-bit MACK portion carries MACs and TESLA-chain keys; 15 page portions over each 30-second subframe form 120-bit HKROOT and 480-bit MACK messages.

Reject the affected received data when its navigation-message CRC fails, and discard OSNMA fields from I/NAV Dummy Messages and I/NAV Alert Pages. A satellite not currently distributing OSNMA sends forty zero bits; the dynamically changing distributor subset can cross-authenticate other satellites, so reception and authentication satellite sets need not match. E14 and E18 are not themselves authenticated but may disseminate authentication data for other satellites.

## OSNMA state and operational handling

### Status, health, and alert handling

The global, rather than per-satellite, OSNMA status is `Operational`, `Test`, or `Don't use`: only Operational status carries the stated performance commitment, Test has no operational guarantee, and Don't use forbids authentication with the broadcast data. OSNMA status is independent of Open Service signal health, and authentication may cover Healthy, Marginal, Unhealthy, or Extended Operations Mode satellites, so a receiver must still apply the ordinary Open Service health and status rules.

Cryptographic-state flags must drive renewal and revocation handling. If an OSNMA Alert Message is received and authenticated with the Merkle trust anchor, stop using OSNMA and obtain recovery instructions from GSC; this protocol message is distinct from an I/NAV Alert Page, whose OSNMA field must be discarded. During Initial Service, a rare mismatch between E1 and E5b DVS values in one subframe can make affected ADKD0 or ADKD12 tags fail verification in the following subframe.

## OSNMA authentication performance

### Authentication classes and minimum availability

Initial Service requires at least 40 equivalent verified tag bits for a navigation data set. Its worldwide minimum availability levels, measured above 5 degrees elevation over one year and including planned and unplanned outages but excluding dummy tags, are:

- ADKD0, I/NAV Word Types 1–5: at least 95% for four satellites within 30 seconds, and at least 80% for every satellite in view within 600 seconds.
- ADKD12, the low-time-synchronization mode for I/NAV Word Types 1–5: at least 95% for four satellites within 240 seconds.
- ADKD4, GST-UTC and GST-GPS conversion parameters: at least 97% for one satellite within 60 seconds.

### Authenticated-data positioning behavior

For ADKD0, the minimum availability of an OSNMA solution using the same satellites as an ordinary Open Service solution is 95%. Because delayed authentication adds latency, continue using the last authenticated navigation data set while it remains valid under the Open Service rules; the target assumes authentication data are collected as soon as a satellite is tracked above the horizon so it can enter PVT at 5 degrees elevation.

### Time to first fix with authenticated data

Cold start lacks the satellite-broadcast cryptographic information and must acquire the public key, TESLA root/key material, and authenticated ephemerides for four satellites; the Merkle root is provisioned separately because it is never available from the signal. Warm start already has the current public key, and hot start also has a previously verified TESLA root key. The stated 95% TTFF-AD values are 130 seconds hot, 300 seconds warm, and at most 6 hours cold for ADKD0; for ADKD12 they are 460 seconds hot, 520 seconds warm, and at most 6 hours cold. The cold bound is driven by the signal's public-key message, scheduled every six hours, and the warm figures assume an eight-block DSM.

These figures assume optimized processing: eligible Word Types 1–4 may be paired with a MAC from the same subframe when received no later than that MAC and when a matching-IOD word lies within the COP range, while Word Type 5 must lie within the COP range. A warm-start receiver gathers MACK and HKROOT in parallel and applies DSM-HKROOT chain parameters as soon as DSM block ID 0 arrives; for single-frequency reception, only Word Types 2 and 4 arrive early enough for the same-subframe optimization.

## OSNMA event monitoring

### Service and key-event notifications

GSC publishes a NAGU at least 48 hours before a planned OSNMA outage or cryptographic renewal and no later than 30 hours after confirmation of an unplanned outage, revocation, or Alert Message event. OSNMA NAGUs cover the signal interface only; events confined to Internet distribution are emailed to registered users, so operational receivers and services must monitor both channels.

The event types distinguish public-key, TESLA-chain, and Merkle-tree renewals; public-key and TESLA-chain revocations; planned and unplanned outages; Alert Messages; cancellation, rescheduling, extension, and restored usability. Receivers must also process the in-band flags that report cryptographic-material status and the need to retrieve material during renewal or revocation.
