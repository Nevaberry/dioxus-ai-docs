# Security Advisories

Use this reference to recognize the reported exposure and remediation state of
recent AlmaLinux-specific advisories. Statuses below are the
`project-news` snapshot dated 2026-07-11; verify current repositories and
advisories before remediation.

## Kernel privilege escalation and container escape

### GhostLock

GhostLock (CVE-2026-43499) is a use-after-free in the kernel real-time mutex
code. It lets an unprivileged local user become root and escape containers,
and affects every supported AlmaLinux release. Patched kernels were available
in the testing repository at the snapshot date.

### Januscape and Bad Epoll

- Januscape (CVE-2026-53359) is a KVM/x86 guest-to-host escape that grants
  root on the host and affects every AlmaLinux release.
- Bad Epoll (CVE-2026-46242) is a local privilege escalation affecting
  AlmaLinux 9 and 10.

Patched kernels for both flaws were available in testing at the snapshot date.

### IPv6 fragmentation escape

An unassigned flaw in the IPv6 fragmentation path lets an unprivileged
container user escape as host root. It affects AlmaLinux 10 and AlmaLinux
Kitten 10. An AlmaLinux 10 kernel fix was in testing; the Kitten fix was
scheduled for its next update.

### CIFSwitch

CIFSwitch (CVE-2026-46243) abuses the `cifs.spnego` request-key helper to
gain root when `cifs-utils` is installed and unprivileged user namespaces
are enabled. Fixed kernels were in production repositories. Apply the kernel
update and reboot into it.

### ssh-keysign-pwn

CVE-2026-46333 is a flaw in `__ptrace_may_access()` that lets an
unprivileged user read root-owned files, including `/etc/shadow` and SSH host
keys. Patched kernels were in testing, and a mitigation was also available.

### Related local-root flaws

These related flaws matter especially on multi-tenant hosts, container build
farms, CI runners, and machines offering untrusted shell access:

- Copy Fail (CVE-2026-31431)
- Dirty Frag (CVE-2026-43284 and CVE-2026-43500)
- Fragnesia (CVE-2026-46300)

Their patched kernels were being tested. Immediate mitigations were available
for Dirty Frag and Fragnesia.

## NGINX rewrite-module overflow

NGINX Rift (CVE-2026-42945) is a heap buffer overflow in nginx's rewrite
module that one unauthenticated HTTP request can trigger. Fixed nginx packages
were released to production repositories for every supported AlmaLinux
release and every nginx module stream.
