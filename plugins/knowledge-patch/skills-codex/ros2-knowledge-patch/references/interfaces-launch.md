# Interfaces and Launch

## Navigation Goal Arrays

The `nav_msgs/msg/Goals` interface carries an array of navigation goals. Use
this interface when one message needs to transport a collection of navigation
goals rather than defining a project-local equivalent.

## NV12 Image Encoding

NV12 is included in the common-interface pixel formats. Images produced by
hardware-accelerated decoders can identify that encoding directly instead of
requiring an unrelated pixel-format label.

Image producers, bridges, and consumers should preserve and recognize NV12
when the underlying buffer uses that layout. Support in the interface does not
by itself imply that every downstream image consumer can process the format,
so validate the complete image path.

## Compound `PathJoinSubstitution` Components

`PathJoinSubstitution` accepts a list of strings or substitutions as one path
component. A nested list can combine a substituted basename with a literal
suffix:

```python
PathJoinSubstitution([
    'robot_description', 'urdf',
    [LaunchConfiguration('model'), '.xacro'],
])
```

Here, the nested component forms the filename before it is joined to the other
path components. Use this form instead of adding a separate concatenation
helper solely to attach the suffix.
