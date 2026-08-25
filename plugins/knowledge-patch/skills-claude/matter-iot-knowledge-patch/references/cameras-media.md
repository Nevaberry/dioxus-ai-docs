# Cameras and Media

Use this reference for camera device types, AV-stream lifecycle, WebRTC, Push
AV, recording, snapshots, PTZ, chimes, and transport configuration.

## Camera device and WebRTC foundation

The generated data model includes all camera device types. A WebRTC abstraction
layer and the required camera-device clusters provide the SDK foundation for
camera-session implementations (sdk-1.5.0.0).

## Certifiable camera capability

Camera behavior includes two-way WebRTC audio and video, local and remote
access, and STUN/TURN traversal. The standardized capability set includes
multiple streams, pan/tilt/zoom, detection and privacy zones, and continuous or
event-triggered recording to local or cloud storage (1.5).

## AV stream lifecycle

Allocated Camera AV Stream Management streams are persistent. Reusing a stream
updates its range parameters. Allocation and modification enforce audio/video
usage constraints, and video starts with the allocated parameters.
Modification and deallocation validation belongs in SDK cluster code. Video or
snapshot modifications produce corrected subscription reports
(sdk-1.5.0.0).

## Push AV transport and overlays

The SDK implements Push AV transport with a delegate, updated transport
options, and push events. Watermark and on-screen-display capabilities are
optional. A modify command must reject use of either feature unless the
implementation advertises the corresponding capability (sdk-1.5.0.0).

## Structured multi-stream sessions

One structured camera session can carry multiple independently optimized audio
and video streams. Separate streams can serve recording, mobile display,
analysis, or different lenses without requiring unrelated sessions solely
because consumers need different media quality (1.5.1).

## Snapshots and recorded-video delivery

Snapshot delivery supports HEIC. Recorded-video uploads can use HLS or DASH
through the CMAF Interface-2 profile (1.5.1).

## PTZ home and recording validation

Pan/tilt/zoom behavior represents installations whose home position lies at the
edge of the rotation range. Recording configuration rejects additional invalid
combinations, so configurations accepted earlier may require changes
(1.5.1).

## Chimes and intercom signaling

A controller can request a particular chime sound instead of always triggering
the default, allowing different sounds for different doorbells or contexts.
Intercom requirements clarify signaling and support integrated chimes
(1.5.1).

## SDK alignment after the initial camera release

Audio/Video Stream Usage Management updates its minimum and maximum pan and
tilt ranges. Push AV updates both XML/SDK behavior and the recorded-clip upload
sequence. Regenerate camera integrations from the tag rather than retaining
earlier range or upload-order assumptions (sdk-1.5.1.0).

## ICE server configuration

`PeerConnection` parses and installs ICE server configuration, providing an
SDK-managed path for applying the WebRTC ICE server set
(sdk-1.5.1.0).
