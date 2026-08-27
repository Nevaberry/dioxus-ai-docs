# Rosbag and Actions

Coverage attribution: `kilted-kaiju`.

## Action introspection and generic clients

The action CLI can introspect a running action:

```sh
ros2 action echo <action_name>
```

Rosbag2 can record and replay action data. This makes action traffic part of
bag-based inspection and reproduction workflows, rather than requiring a
separate capture mechanism.

`rclcpp` provides generic action client support. It underpins action tooling
and clients that need to operate without a compile-time-specific action client
shape.

## Playing several bags together

`ros2 bag play` accepts repeated `-i` or `--input` options and merges the given
bags during playback:

```sh
ros2 bag play -i bag1 -i bag2 -i bag3
```

Use one input option per bag. A positional single-bag invocation remains useful
when no merge is needed.

## Choosing replay order

The default message order is `received`, which preserves reception order. To
order messages by their publication timestamps, select `sent`:

```sh
ros2 bag play <bag> --message-order sent
```

Choose the ordering rule explicitly when diagnosing timing behavior: reception
order describes arrival at the recorder, while `sent` uses publication time.

## Sorting bag information

`ros2 bag info --sort` can sort topics, services, and actions. Supported sort
dimensions are name, type, and recorded-message count. Supply the criterion
appropriate to the inspection task:

```sh
ros2 bag info --sort <criterion> <bag>
```

For detailed storage analysis, verbose output and `--size-contribution` report
each topic's share of the bag size:

```sh
ros2 bag info -v --sort <criterion> --size-contribution <bag>
```

## Rosbag command logging

Both playback and recording accept `--log-level`:

```sh
ros2 bag play <bag> --log-level debug
ros2 bag record <topics...> --log-level debug
```

Set the option on the rosbag command whose diagnostics are needed rather than
assuming a single playback-only logging switch.

## Snapshot recording files

Each trigger during snapshot-mode recording writes a new bag file. A later
trigger does not reuse the earlier snapshot file. Consumers and cleanup jobs
must therefore handle a sequence of snapshot bags.
