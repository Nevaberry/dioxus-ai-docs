# RHEL MLS Administration

## Contents

- [Activating MLS and preparing the first boot](#activating-mls-and-preparing-the-first-boot)
- [Administrative SSH access](#administrative-ssh-access)
- [Provisioning user clearances](#provisioning-user-clearances)
- [Changing clearance in a secure terminal](#changing-clearance-in-a-secure-terminal)
- [Promoting files on lower-level writes](#promoting-files-on-lower-level-writes)
- [Persisting file sensitivity](#persisting-file-sensitivity)
- [Separating system and security administration](#separating-system-and-security-administration)

## Activating MLS and preparing the first boot

The RHEL 10 MLS policy has no `unconfined` module, so even `root` remains
confined. It must not be used on a system running the X Window System. Users
created while another SELinux policy was active cannot be used under MLS.

Switch from targeted policy while permissive, request a complete on-boot
relabel, and resolve denials before enforcing:

```console
dnf install selinux-policy-mls
# Set SELINUX=permissive and SELINUXTYPE=mls in /etc/selinux/config
fixfiles -F onboot
reboot
ausearch -m AVC,USER_AVC,SELINUX_ERR,USER_SELINUX_ERR -ts recent -i
```

Do not skip the forced relabel or use enforcing mode for the diagnostic first
boot.

## Administrative SSH access

If MLS administration over SSH is required, enable `ssh_sysadm_login` before
the first MLS boot. Once MLS is active, a `root` login in `staff_r` must first
enter the administrative role:

```console
newrole -r sysadm_r
```

Only then can it enable the boolean. Plan this access path before activation so
the machine does not depend on an unavailable role transition.

## Provisioning user clearances

An SELinux user's default level (`-L`) and allowed range (`-r`) are separate.
After changing both, regenerate and restore home-directory contexts, set the
login mapping's level, and relabel the affected home:

```console
semanage user -m -L s1 -r s1-s15 staff_u
genhomedircon
restorecon -R -F -v /home/
semanage login -m -r s1 example_user
chcon -R -l s1 /home/example_user
```

Do not interpret the user's default level as a replacement for the allowed
range or the login mapping.

## Changing clearance in a secure terminal

`newrole -l` opens a nested shell. Supplying one level changes the lower bound
of the existing range: from `s0-s2`, `newrole -l s1` produces `s1-s2`. Exit the
nested shell to return to the earlier clearance:

```console
newrole -l s1
exit
```

The transition works only for terminal types listed in
`/etc/selinux/mls/contexts/securetty_types`. The console is secure by default;
SSH is not. Determine the current terminal type with:

```console
ls -Z "$(tty)"
```

Add that type to the secure-terminal list only after assessing the security
risk of allowing MLS clearance changes through that channel.

## Promoting files on lower-level writes

MLS normally denies writes below the lower bound of a user's current clearance
range. A local CIL rule can add selected domains to `mlsfilewrite`:

```cil
(typeattributeset mlsfilewrite (staff_t))
```

Install the rule and enter the intended range before testing:

```console
semodule -i ~/local_mlsfilewrite.cil
newrole -l s1-s2
touch /path/to/file
```

A write by such a domain promotes the file's classification to the lower bound
of the current range. This label is not durable policy configuration;
`restorecon` reverts it to the configured default.

## Persisting file sensitivity

Set a file-context MLS range and force restoration when the classification must
survive `restorecon`:

```console
semanage fcontext -a -r s2 /path/to/file
restorecon -F -v /path/to/file
```

Use automatic `mlsfilewrite` promotion for write semantics and an fcontext rule
for persistent labeling; they solve different problems.

## Separating system and security administration

In MLS, `sysadm_r` receives security-policy administration rights from the
enabled `sysadm_secadm` module. Before disabling that module, provision a
reachable `staff_u` user whose sudo rule enters `secadm_r`:

```sudoers
sec_adm_user ALL=(ALL) TYPE=secadm_t ROLE=secadm_r ALL
```

Then disable the module without deleting its packaged copy:

```console
semodule -d sysadm_secadm
```

Do not use `semodule -r` for this operation. Removal deletes the packaged
module, and recovering it requires reinstalling `selinux-policy-mls`.
