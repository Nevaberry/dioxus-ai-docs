# Kubectl and Kubeadm

## Kubectl preferences and output

### Alpha kubectl preferences use `.kuberc` (1.33-guide)

Set `KUBECTL_KUBERC=true` to separate aliases and overrides from credentials.
Kubectl reads `~/.kube/kuberc` or the file selected by `--kuberc`.

```console
KUBECTL_KUBERC=true kubectl --kuberc /var/kube/rc get pods
```

### `.kuberc` is enabled by default (1.34-guide)

Normal beta `.kuberc` loading no longer requires `KUBECTL_KUBERC=true`.

### `.kuberc` can restrict credential plugins (1.35-guide)

Use `credentialPluginPolicy` to allow or deny plugins and
`credentialPluginAllowlist` to restrict execution to named plugins.

### kubectl can emit KYAML (1.34-guide)

KYAML is a less ambiguous Kubernetes-oriented YAML subset and valid YAML input.
At this alpha stage, enable it explicitly:

```console
KUBECTL_KYAML=true kubectl get pods -o kyaml
```

### KYAML output is default-on beta (1.35-guide)

`kubectl -o kyaml` no longer needs the enabling environment variable. Set
`KUBECTL_KYAML=false` to disable it.

## Kubectl command changes

### `kubectl autoscale` prefers `autoscaling/v2` (1.33.0)

The command creates HPAs through `autoscaling/v2`, falling back to v1 when v2
is unavailable or errors.

### Kubectl drops several legacy beta APIs (1.35.0)

Kubectl does not support `certificates/v1beta1` CSR,
`discovery/v1beta1` EndpointSlice, `networking/v1beta1` Ingress, or
`policy/v1beta1` PodDisruptionBudget objects.

### `kubectl exec` requires a command separator (1.35.0)

The legacy form is removed:

```console
kubectl exec <pod> -- <command>
```

### `kubectl debug` changes its default profile (1.36.0)

The default is `general`, not `legacy`; the legacy profile is planned for
removal in 1.39.

### `kubectl describe` limits implicit event queries (1.36.0)

Related events are automatic only for one object. Use `--show-events` for
multiple objects or fuzzy prefix matching.

## Kubeadm API endpoints and node state

### Kubeadm uses a local API endpoint for control-plane kubelets (1.33.0)

Default-on beta `ControlPlaneKubeletLocalMode` makes init and control-plane join
generate kubelet configuration against the local API server. For
`kubeadm init phase kubeconfig kubelet`, use `--apiserver-advertise-address`, not
`--control-plane-endpoint`, to select the generated `server`.

### Kubeadm stores CRI endpoints per node (1.34.0)

Default-on beta `NodeLocalCRISocket` writes the node's
`containerRuntimeEndpoint` to `/var/lib/kubelet/instance-config.yaml`. During
upgrade kubeadm removes the old `kubeadm.alpha.kubernetes.io/cri-socket` Node
annotation and `--container-runtime-endpoint` from
`/var/lib/kubelet/kubeadm-flags.env`.

### Kubeadm probes use a named port (1.34.0)

Generated control-plane static Pods target `probe-port`. A kubeadm patch that
changes probe ports must also change the matching container `ports` entry.

### Kubeadm can separate external-etcd HTTP endpoints (1.35.0)

v1beta4 `ClusterConfiguration.Etcd.ExternalEtcd.HTTPEndpoints` carries health
and metrics traffic separately from gRPC `Endpoints`; omitting it uses
`Endpoints` for both.

### Kubeadm preserves `extraArgs` order (1.36.0)

Kubeadm sorts default component arguments only and preserves user override
order, so repeated ordered flags such as `--service-account-issuer` retain
precedence.

## Join, upgrade, and reset behavior

### Remove kubelet's sandbox-image flag before upgrading (1.35.0)

`--pod-infra-container-image` is removed and prevents kubelet startup. Kubeadm
upgrade tries to remove it from `/var/lib/kubelet/kubeadm-flags.env`, but users
must clean it from custom `extraArgs`.

### The cgroup-v1 startup block has an explicit override (1.35.0)

Kubeadm `SystemVerification` rejects a 1.35 kubelet on cgroup v1. Proceeding
requires both ignoring that preflight error and setting `failCgroupV1: false`
in the `kube-system/kubelet-config` ConfigMap.

### `kubeadm join` uses the Kubernetes API timeout for cluster configuration (1.34.10)

Fetching `kubeadm-config` during join uses the `KubernetesAPICall` timeout,
default one minute, not the 350 ms optional-component retry. Callers of
`FetchInitConfigurationFromCluster` may select the short retry with its new
`shortConfigMapGet` parameter, as reset does.

### Kubeadm etcd learner promotion tolerates ambiguous success (1.35.7)

If the server promotes a learner but the client receives a transient error,
join recognizes the already-voting member and skips redundant promotion instead
of retrying until timeout.
