# Graphics, Media, and Spatial APIs

## Nearby Interaction

### Range in the Background with an Active Live Activity

On iOS 18.4, an application with an active Live Activity can perform Ultra
Wideband ranging through Nearby Interaction while it runs in the background.
Structure the background-ranging lifetime around the active Live Activity.

## Broadcast Extensions

### Use the Higher Memory Limit Conservatively

iOS and iPadOS 18.5 raise the per-process memory limit for Broadcast
Extensions. The additional headroom can support higher-quality capture and
streaming when system resources permit.

## Metal 4

### Add Indirect-Command Pipelines to the Residency Set

When encoding with Metal 4 on iOS 26.0, add render and compute pipelines that
support indirect command buffers to the residency set. The Metal driver does
not currently enforce this rule, but applications must not rely on that leniency.
