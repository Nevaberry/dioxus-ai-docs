# KubeRay Jobs and Services

## Bootstrap a RayCluster and reach the head service

Installing the `kuberay/ray-cluster` chart creates a RayCluster custom resource.
The operator creates its head and worker Pods. Select cluster Pods with
`ray.io/cluster=<name>`. The generated head service exposes the Dashboard and
Ray Jobs endpoint on port 8265.

```sh
helm install raycluster kuberay/ray-cluster --version 1.6.0
kubectl get pods --selector=ray.io/cluster=raycluster-kuberay
kubectl port-forward service/raycluster-kuberay-head-svc 8265:8265
ray job submit --address http://localhost:8265 -- python app.py
```

## Choose a RayJob cluster model

A RayJob can embed `rayClusterSpec`, causing KubeRay to create a cluster, or use
`clusterSelector` to target an existing RayCluster. The operator submits
`entrypoint` after the cluster becomes ready.

`runtimeEnvYAML` is a multiline YAML string. `jobId`, `metadata`, and entrypoint
CPU, GPU, and custom-resource fields map to Ray Jobs submission options.

```yaml
spec:
  rayClusterSpec: ...
  entrypoint: python /home/ray/app.py
  runtimeEnvYAML: |
    pip:
      - requests==2.26.0
    env_vars:
      KEY: "VALUE"
```

## Choose a submission mode

- `K8sJobMode` is the default and creates a submitter Kubernetes Job.
- `HTTPMode` makes the operator submit directly.
- `InteractiveMode` is alpha and waits for user submission.
- `SidecarMode` injects the submitter into the head Pod. It requires the head
  Pod restart policy to be `Never` and does not support `clusterSelector`,
  `submitterPodTemplate`, or `submitterConfig`.

`submitterPodTemplate` applies only to `K8sJobMode`. KubeRay injects
`RAY_DASHBOARD_ADDRESS` as `$HEAD_SERVICE:$DASHBOARD_PORT` and
`RAY_JOB_SUBMISSION_ID` from `RayJob.Status.JobId`.

## Separate retry scopes and deadlines

Top-level `backoffLimit`, added in KubeRay 1.2.0, defaults to zero. Each retry
creates a new RayCluster. `submitterConfig.backoffLimit` instead retries the
submitter Kubernetes Job and defaults to two.

`preRunningDeadlineSeconds` fails a job with `PreRunningDeadlineExceeded` when
deployment does not reach `Running`; zero disables this deadline.
`activeDeadlineSeconds` bounds the time to reach `Complete` or `Failed` and
reports `DeadlineExceeded`. Completion is represented separately as
`status.jobStatus: SUCCEEDED` and `status.jobDeploymentStatus: Complete`.

## Configure cleanup and suspension

`shutdownAfterJobFinishes` defaults to false. `ttlSecondsAfterFinished` applies
only when shutdown is enabled. With shutdown enabled, setting the operator
environment variable `DELETE_RAYJOB_CR_AFTER_JOB_FINISHES=true` also deletes the
RayJob custom resource and everything it created.

KubeRay 1.6.0 provides beta `deletionStrategy` behind the
`RayJobDeletionPolicy` feature gate. Rules can trigger `DeleteWorkers`,
`DeleteCluster`, `DeleteSelf`, or `DeleteNone` for `SUCCEEDED` or `FAILED`, with
an optional per-rule TTL. This enables staged cleanup.

Rules-based cleanup is incompatible with `shutdownAfterJobFinishes` and the
global `ttlSecondsAfterFinished`. The older `onSuccess` and `onFailure` style is
deprecated.

Setting `suspend: true` deletes the RayCluster and submitter. Do not change it
manually when Kueue controls RayJob scheduling.

## Reach RayService applications

RayService manages an underlying RayCluster and Ray Serve applications.
`serveConfigV2` supports multi-application Serve configuration. Once Serve has
endpoints, RayService reports `Ready=True` and creates:

- A head service for Dashboard access on port 8265.
- A Serve service for application HTTP traffic on port 8000.

```sh
kubectl get rayservice
kubectl describe rayservices.ray.io rayservice-sample
kubectl port-forward svc/rayservice-sample-head-svc 8265:8265
```
