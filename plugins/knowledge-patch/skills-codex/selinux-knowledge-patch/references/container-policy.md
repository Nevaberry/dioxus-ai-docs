# Container Policy

## Deploying generated Udica policy

Container-selinux carries deployable Udica policy templates. Administrators can
therefore install Udica-generated policies on OpenShift nodes without installing
Udica itself on every node.

On SLE Micro, the default container policy denies access to files outside
container data, including bind-mounted host paths, while allowing all network
access. To grant only the required host access:

1. Capture the container's inspection JSON.
2. Use Udica to derive a custom policy from that JSON.
3. Load the generated policy modules.
4. Relaunch the container with the generated type through `--security-opt`.

Do not treat unrestricted networking as evidence that bind-mounted files are
also accessible; those permissions are governed separately.

## Runtime support

The policy supports Incus-managed containers.

The supplied `container_contexts` configuration supports running containers
inside containers. Use those supplied contexts for nested workloads instead of
inventing an outer-container label mapping.

## Overlay-container directory transitions

File-transition rules cover both `overlay-containers` and
`overlay2-containers`. Newly created directories in those locations receive
`container_ro_file_t` rather than inheriting `data_home_t`, even though their
eventual file-context rules may already name the correct label.

When diagnosing a wrong label, distinguish creation-time transition behavior
from a later `restorecon`: a file-context entry alone does not guarantee the
label assigned at creation.

## Runtime-domain ptrace control

The ptrace permission for `container_runtime_domain` is conditional on
`deny_ptrace` being false, matching the rest of the policy. Enabling
`deny_ptrace` therefore restricts container runtime domains too. Do not add an
allow rule merely to restore behavior that the administrator intentionally
disabled with this boolean.

## Confined-user identity

Systems using confined SELinux users install the `container_u` identity
description for container workloads. Use this supplied identity when mapping
confined users to container activity.
