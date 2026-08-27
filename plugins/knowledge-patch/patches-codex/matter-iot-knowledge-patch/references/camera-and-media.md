# Camera and Media

## Device and WebRTC foundation

The generated data model includes all camera device types. The SDK adds a
WebRTC abstraction and the camera clusters needed as a foundation for session
implementations (since sdk-1.5.0.0).

Certifiable camera capabilities include two-way WebRTC audio and video, local
and remote access, and STUN/TURN traversal. The standard capability set also
includes multiple streams, pan/tilt/zoom, detection and privacy zones, and
continuous or event-triggered recording to local or cloud storage (since 1.5).

`PeerConnection` parses and installs ICE server configuration, providing an
SDK-managed path for WebRTC ICE servers (since sdk-1.5.1.0).

## AV stream allocation and lifecycle

Allocated Camera AV Stream Management streams are persistent. Reusing a stream
updates its range parameters rather than creating an unrelated allocation
(since sdk-1.5.0.0).

Allocation and modification enforce audio/video usage constraints. Video starts
with the allocated parameters, while modification and deallocation validation
is implemented in SDK cluster code. Video and snapshot modifications generate
corrected subscription reports (since sdk-1.5.0.0).

A structured camera session can carry multiple independently optimized video
and audio streams. Recording, mobile display, analysis, or different lenses can
therefore share a session without forcing unrelated sessions solely because
their media qualities differ (since 1.5.1).

## Push AV and overlays

The SDK implements Push AV transport with a delegate, revised transport
options, and push events (since sdk-1.5.0.0).

Watermark and on-screen-display features are optional. A modify command must be
rejected unless the implementation advertises the requested capability (since
sdk-1.5.0.0).

Push AV XML and SDK behavior, including the recorded-clip upload sequence,
changes during camera alignment. Regenerate from sdk-1.5.1.0 and do not keep
the earlier upload-order assumption.

## Images and recorded media

HEIC is available for snapshot delivery. Recorded-video uploads can use HLS or
DASH through the CMAF Interface-2 profile (since 1.5.1).

Recording configuration rejects additional invalid combinations. A
configuration accepted by an earlier implementation may require adjustment
when targeting 1.5.1.

## Pan, tilt, zoom, and ranges

Camera behavior supports installations whose pan/tilt home position is at the
edge of the rotation range (since 1.5.1).

Audio/Video Stream Usage Management corrects pan and tilt minimum/maximum
ranges in the aligned SDK. Regenerate definitions and remove range assumptions
retained from sdk-1.5.0.0 when moving to sdk-1.5.1.0.

## Chimes and intercom

A controller can select a particular chime sound rather than always triggering
the default, enabling distinct sounds by doorbell or context. Intercom
requirements clarify signaling and support integrated chimes (since 1.5.1).

## Camera validation checklist

- Persist allocated streams and test reuse.
- Enforce usage constraints on allocation and modification.
- Verify subscription reports after video or snapshot changes.
- Reject unsupported overlays.
- Install ICE server settings through `PeerConnection`.
- Test independent stream qualities within one structured session.
- Validate PTZ edge-home behavior and corrected ranges.
- Reject invalid recording combinations.
- Verify recorded-clip upload ordering.
- Exercise HEIC snapshots and CMAF Interface-2 delivery where enabled.

