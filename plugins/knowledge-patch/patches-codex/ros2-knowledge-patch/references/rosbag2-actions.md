# Rosbag2 and Actions

## Action Introspection and Generic Clients

The CLI can introspect a live action:

```sh
ros2 action echo <action_name>
```

Rosbag2 can record and replay action data. Include action traffic when a bag
must preserve an action interaction rather than recording only its related
topics.

`rclcpp` provides generic action client support. This is the client capability
used by tooling that must work with an action discovered at runtime instead of
being compiled for one action type.

## Merge Multiple Bags During Playback

`ros2 bag play` accepts repeated `-i` or `--input` options and merges those
inputs during playback:

```sh
ros2 bag play -i bag1 -i bag2 -i bag3
```

Use one input option per bag. Do not treat multiple input bags as a request for
separate sequential playback processes.

## Select Playback Message Order

The default message order is `received`, which uses reception timestamps. To
order messages by publication timestamp, select `sent`:

```sh
ros2 bag play <bag> --message-order sent
```

Choose the order deliberately when merged bags or transport delay make
reception order differ from publication order.

## Inspect Bag Contents

`ros2 bag info --sort` can sort topics, services, and actions by:

- name;
- type; or
- recorded-message count.

With verbose output, `--size-contribution` reports each topic's share of total
bag size:

```sh
ros2 bag info -v --sort <criterion> --size-contribution <bag>
```

Use sorting to make large inventories comparable and size contribution to find
the topics dominating storage.

## Configure Logging

Both playback and recording accept `--log-level`:

```sh
ros2 bag play <bag> --log-level debug
ros2 bag record <topics...> --log-level debug
```

Set the option on the Rosbag2 command whose diagnostics are needed; it is not
limited to playback.

## Snapshot Output Semantics

Every trigger during snapshot-mode recording writes a new bag file. Snapshot
files are no longer reused.

Consumers must discover or track each newly created bag. Retention, upload,
naming, and cleanup logic should not assume that later triggers overwrite or
append to a single reusable snapshot file.
