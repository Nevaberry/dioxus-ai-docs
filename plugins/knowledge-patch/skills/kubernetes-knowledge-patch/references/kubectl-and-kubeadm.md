# Kubectl and Kubeadm

Use this reference for kubectl behavior and output, kuberc preferences, kubeadm configuration, generated manifests, and command-line migrations.

Entries are grouped by task; the parenthetical identifier is the source batch.

## `.kuberc` can restrict credential plugins (1.35-guide)

The preferences file gains `credentialPluginPolicy` to allow or deny all credential plugins and `credentialPluginAllowlist` to restrict execution to named plugins.

## `.kuberc` is enabled by default (1.34-guide)

The separate kubectl preferences file graduates to beta, so users no longer need `KUBECTL_KUBERC=true` merely to activate normal `.kuberc` loading.

## `kubectl apply` preserves null metadata keys (1.33.0)

Null label and annotation values are now coerced to empty strings, matching typed JSON metadata decoding, instead of causing all labels or annotations to be dropped.

## `kubectl autoscale` prefers `autoscaling/v2` (1.33.0)

The command now creates HPAs through `autoscaling/v2`, falling back to `autoscaling/v1` when the v2 API is unavailable or returns an error.

## `kubectl debug` changes its default profile (1.36.0)

The default debug profile is now `general` instead of `legacy`; the legacy profile is planned for removal in 1.39.

## `kubectl describe` limits implicit event queries (1.36.0)

Related events are shown by default only when describing one object; use `--show-events` when describing multiple objects or using fuzzy prefix matching.

## `kubectl exec` requires a command separator (1.35.0)

The legacy form with the command immediately after the Pod is removed; put `--` before the remote command.

```console
kubectl exec <pod> -- <command>
```

## Alpha kubectl preferences use `.kuberc` (1.33-guide)

Set `KUBECTL_KUBERC=true` to keep aliases and command overrides, such as a server-side-apply default, separate from cluster credentials in kubeconfig. kubectl reads `~/.kube/kuberc` by default, or another file selected with `--kuberc`.

```console
KUBECTL_KUBERC=true kubectl --kuberc /var/kube/rc get pods
```

## Kubeadm can separate external-etcd HTTP endpoints (1.35.0)

The v1beta4 `ClusterConfiguration.Etcd.ExternalEtcd` configuration gains `HTTPEndpoints` for health and metrics traffic, separate from gRPC `Endpoints`; when omitted, `Endpoints` continues to handle both.

## Kubeadm preserves `extraArgs` order (1.36.0)

Kubeadm now sorts only default component arguments and preserves user override order, allowing ordered repeatable flags such as `--service-account-issuer` to retain their intended precedence.

## Kubeadm probes use a named port (1.34.0)

Generated control-plane static Pod manifests now target the named port `probe-port`; kubeadm patches that change probe ports must also patch the matching entry in the container's `ports` list.

## Kubeadm stores CRI endpoints per node (1.34.0)

The beta, default-on `NodeLocalCRISocket` behavior writes `/var/lib/kubelet/instance-config.yaml` with the node's `containerRuntimeEndpoint`. During upgrade, kubeadm removes the old Node annotation `kubeadm.alpha.kubernetes.io/cri-socket` and the `--container-runtime-endpoint` entry from `/var/lib/kubelet/kubeadm-flags.env`.

## Kubeadm uses a local API endpoint for control-plane kubelets (1.33.0)

`ControlPlaneKubeletLocalMode` is beta and default-on, so `kubeadm init` and control-plane `join` generate kubelet configuration against the local API server. In `kubeadm init phase kubeconfig kubelet`, `--control-plane-endpoint` no longer selects the generated `server`; use `--apiserver-advertise-address` instead.

## kubectl can emit KYAML (1.34-guide)

The alpha KYAML format is a less ambiguous Kubernetes-oriented YAML subset that remains valid YAML input. Enable its kubectl output mode explicitly:

```console
KUBECTL_KYAML=true kubectl get pods -o kyaml
```

## Kubectl drops several legacy beta APIs (1.35.0)

Kubectl no longer supports `certificates/v1beta1` CertificateSigningRequest, `discovery/v1beta1` EndpointSlice, `networking/v1beta1` Ingress, or `policy/v1beta1` PodDisruptionBudget objects.

## KYAML output is default-on beta (1.35-guide)

`kubectl -o kyaml` no longer needs `KUBECTL_KYAML=true`; set `KUBECTL_KYAML=false` to disable the beta output format.

