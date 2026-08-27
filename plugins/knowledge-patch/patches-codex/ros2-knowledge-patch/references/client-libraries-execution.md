# Client Libraries and Execution

## Generic Static Typing in `rclpy`

Publishers, subscriptions, services, actions, tasks, futures, and parameters
support generic type annotations. Preserve concrete ROS interface types in
annotations so static analysis can follow values across entity boundaries.

Clients take request and response types:

```python
client: Client[GetParameters.Request, GetParameters.Response]
```

Action clients take goal, result, and feedback types:

```python
action: ActionClient[
    Fibonacci.Goal,
    Fibonacci.Result,
    Fibonacci.Feedback,
]
```

Futures take the completed value type:

```python
future: Future[bool] = Future()
```

Apply the same generic-annotation approach to publishers, subscriptions,
services, actions, tasks, and parameters rather than leaving those entities
unparameterized.

## Experimental Python Events Executor

`rclpy` includes an experimental `EventsExecutor`. It ports the event-driven
executor concept from `rclcpp` to Python.

Treat it as an experimental option when comparing executor architectures.
Keep that status visible in API choices, testing expectations, and deployment
decisions rather than assuming the same stability as established executors.

## Subordinate Nodes

Generic clients created from an `rclcpp` subordinate node now honor the
subordinate node's sub-namespace. Client names should therefore resolve in the
same namespace context as the subordinate node.

Parameters accessed through a subordinate node now use the parent node's
`rclcpp::node_interfaces::NodeParametersInterface`. Code that wraps subordinate
nodes should preserve this ownership model instead of assuming an independent
parameters interface.

When migrating existing code, test both resolved generic-client names and
parameter reads or writes. These two changes affect different node interfaces
but often appear in the same component composition code.

## DDS Topic Instances

ROS 2 supports DDS topic instances. Multiple objects of one logical kind can
share a topic while their updates remain associated with distinct instances.

Use topic instances when the data model naturally has several keyed objects
that publish the same kind of update. Account for instance identity in the
publisher and subscriber design rather than creating a separate topic solely
to distinguish each object.
