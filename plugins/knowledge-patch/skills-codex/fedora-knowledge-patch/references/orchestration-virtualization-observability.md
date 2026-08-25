# Orchestration, Virtualization, CI, and Observability

## Contents

- Kubernetes and Helm
- Virtualization and confidential guests
- eBPF, verification, and monitoring
- Fedora build and test infrastructure

## Kubernetes and Helm

### Concurrent Kubernetes and CRI versions (41)

Fedora ships supported Kubernetes releases concurrently in versioned packages
such as `kubernetes1.29`, `kubernetes1.30`, and `kubernetes1.31`, with matching
versioned CRI-O and CRI-Tools packages. When upgrading from the old
unversioned stack, manually select the desired versioned package; it is not
chosen automatically.

### Helm 4 becomes the default with a parallel Helm 3 package (44)

The `helm` package and command provide Helm 4, whose workflows are not fully
compatible with Helm 3. Existing automation can use the parallel `helm3`
package and command:

```console
sudo dnf install helm3
helm3 version
```

## Virtualization and confidential guests

### AMD SEV-SNP virtualization hosts (42)

Fedora virtualization hosts can launch AMD SEV-SNP confidential guests. The
facility protects guest memory from the host software stack and enables
components such as a secure virtual TPM.

### Intel TDX confidential guests are supported (43)

Suitable Intel TDX hosts can run confidential guests, extending Fedora's host
support beyond the AMD SEV-SNP facility. Validate hardware, firmware, kernel,
QEMU, and libvirt support as one stack.

### QEMU drops 32-bit host builds (44)

Fedora no longer builds QEMU for 32-bit hosts, following upstream's
requirement for host support for 64-bit atomic operations. Move virtualization
hosts to a supported 64-bit architecture.

## eBPF, verification, and monitoring

### `bpfman` is packaged (42)

Fedora packages the `bpfman` daemon together with its agent, operator, and
Kubernetes CRDs. Use it to load and inspect eBPF programs centrally instead of
granting every workload direct program-loading privileges.

### Copilot runtime verification is available (42)

The `ghc-copilot` package provides the Copilot stream language and C99 backend
for generating constant-memory, constant-time monitors suitable for hard
real-time programs.

### Debuginfod verifies downloads by default (43)

Debuginfod clients cryptographically verify automatically downloaded
debuginfo and source through IMA by default instead of accepting those
artifacts without client-side integrity checks.

## Fedora build and test infrastructure

### Koji image builds become worker-local only (44)

Koji removes its external Image Builder service integration. Image builds
performed locally on Koji workers remain supported.

### Packit replaces Fedora CI and Zuul for dist-git pull requests (44)

Packit now launches dist-git pull-request builds and Testing Farm tests,
replacing the former Fedora CI and Zuul paths. Update status-check and job
trigger assumptions accordingly.
