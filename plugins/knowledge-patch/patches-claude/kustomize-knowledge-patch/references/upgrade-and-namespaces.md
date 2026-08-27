# Upgrade and Namespace Propagation

## Child kustomizations

Kustomize 5.8.0 has a regression in propagation of namespaces to child
kustomizations. Do not adopt 5.8.0 for workloads that rely on that behavior;
wait for a patch release instead. (5.8.0)

Kustomize 5.8.1 completes the fix. Builds that require namespaces to reach
child kustomizations can use 5.8.1 rather than avoiding the entire 5.8 release
line. (5.8.1)

## Upgrade decision

Use the namespace requirement to choose between these outcomes:

| Requirement | Guidance |
| --- | --- |
| Namespace must propagate to child kustomizations | Avoid 5.8.0 |
| Same requirement while adopting the 5.8 line | Use 5.8.1 |

The warning is specifically about child kustomizations. Namespace handling for
Helm chart entries is covered separately in
[helm-charts.md](helm-charts.md).
