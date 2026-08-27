# KubeRay operations

## Bootstrapping a RayCluster

Installing the `kuberay/ray-cluster` chart creates a RayCluster custom
resource. The operator creates the corresponding head and worker Pods.

Select the cluster Pods with `ray.io/cluster=<name>`. The generated head
service exposes the Dashboard and Ray Jobs endpoint on port 8265.

```sh
helm install raycluster kuberay/ray-cluster --version 1.6.0
kubectl get pods --selector=ray.io/cluster=raycluster-kuberay
kubectl port-forward service/raycluster-kuberay-head-svc 8265:8265
ray job submit --address http://localhost:8265 -- python app.py
```

## RayJob cluster and submission model

A RayJob can embed `rayClusterSpec` so KubeRay creates a cluster, or use
`clusterSelector` to target an existing RayCluster. KubeRay submits
`entrypoint` after the cluster becomes ready.

`runtimeEnvYAML` is a multiline YAML string. The `jobId`, `metadata`,
and entrypoint CPU, GPU, and custom-resource fields map to Ray Jobs submission
options.

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

## RayJob submission modes

- `K8sJobMode` is the default and creates a submitter Kubernetes Job.
- `HTTPMode` has the operator submit directly.
- `InteractiveMode` is alpha and waits for user submission.
- `SidecarMode` injects the submitter into the head Pod. It requires the head
  Pod restart policy to be `Never` and does not support `clusterSelector`,
  `submitterPodTemplate`, or `submitterConfig`.

A `submitterPodTemplate` applies only to `K8sJobMode`. KubeRay injects
`RAY_DASHBOARD_ADDRESS` as `$HEAD_SERVICE:$DASHBOARD_PORT` and
`RAY_JOB_SUBMISSION_ID` from `RayJob.Status.JobId`.

## Retry scopes

Top-level `backoffLimit`, added in KubeRay 1.2.0, defaults to zero. Every
retry at this scope creates a new RayCluster.

`submitterConfig.backoffLimit` instead retries the submitter Kubernetes Job
and defaults to two.

## Lifecycle deadlines and status

`preRunningDeadlineSeconds` fails a RayJob with
`PreRunningDeadlineExceeded` if deployment never reaches `Running`. Zero
disables this deadline.

`activeDeadlineSeconds` bounds the time to reach `Complete` or `Failed`
and reports `DeadlineExceeded`. Successful completion is represented
separately:

```yaml
status:
  jobStatus: SUCCEEDED
  jobDeploymentStatus: Complete
```

## Cleanup policies

`shutdownAfterJobFinishes` defaults to false.
`ttlSecondsAfterFinished` applies only when shutdown is enabled. When
shutdown is enabled, setting the operator environment variable
`DELETE_RAYJOB_CR_AFTER_JOB_FINISHES=true` also deletes the RayJob custom
resource and every resource it created.

KubeRay 1.6.0 exposes beta `deletionStrategy` behind the
`RayJobDeletionPolicy` feature gate. Rules can respond to `SUCCEEDED` or
`FAILED` with `DeleteWorkers`, `DeleteCluster`, `DeleteSelf`, or
`DeleteNone`, optionally after a per-rule TTL. This supports staged cleanup.

Rules-based cleanup is incompatible with `shutdownAfterJobFinishes` and the
global `ttlSecondsAfterFinished`. The older `onSuccess` and `onFailure`
style is deprecated.

Setting `suspend: true` deletes the RayCluster and the submitter. Do not
change it manually when Kueue controls RayJob scheduling.

## RayService readiness and endpoints

RayService manages an underlying RayCluster and Ray Serve applications.
`serveConfigV2` supports multi-application Serve configuration.

After Serve has endpoints, RayService reports a `Ready=True` condition and
creates:

- a RayService head service for Dashboard access on port 8265; and
- a Serve service for application HTTP traffic on port 8000.

```sh
kubectl get rayservice
kubectl describe rayservices.ray.io rayservice-sample
kubectl port-forward svc/rayservice-sample-head-svc 8265:8265
```
