# PushSecret Workflows

Use this reference before pushing Kubernetes Secret data to external providers.
Confirm that the selected provider implements the required existence, set,
delete, merge, and policy operations.

## PushSecret inputs and mappings (`push-secrets`)

A namespaced `PushSecret` accepts exactly one source under `selector`: a
Kubernetes Secret or a `generatorRef`. `template` and `templateFrom` can construct
outgoing properties before mapping. Each `data[].match` maps a source or templated
`secretKey` to a provider `remoteKey` and optional `property`.

`updatePolicy: Replace` permits overwrites. `deletionPolicy` defaults to `None`;
set it to `Delete` if removing the `PushSecret` or its source should clean up the
provider secret.

```yaml
apiVersion: external-secrets.io/v1alpha1
kind: PushSecret
metadata:
  name: app-credentials
spec:
  updatePolicy: Replace
  deletionPolicy: Delete
  refreshInterval: 1h
  secretStoreRefs:
    - name: destination
      kind: SecretStore
  selector:
    secret:
      name: source-credentials
  template:
    data:
      normalized: '{{ index . "raw-key" | toString | upper }}'
    templateFrom:
      - configMap:
          name: push-fragment
          items:
            - key: config.yml
  data:
    - match:
        secretKey: normalized
        remoteRef:
          remoteKey: app-credentials
          property: normalized
    - match:
        secretKey: config.yml
        remoteRef:
          remoteKey: app-config
          property: config.yml
```

## Bulk expansion with dataTo (`2.3-datato`)

`PushSecret.spec.dataTo` expands every key or a regexp-filtered subset from the
Kubernetes Secret selected by `spec.selector`. Every entry requires a `storeRef`
by name or label selector, and that store must also be listed under
`secretStoreRefs`.

```yaml
spec:
  secretStoreRefs:
    - name: target-store
  dataTo:
    - storeRef:
        name: target-store
      match:
        regexp: '^APP_'
      rewrite:
        - regexp:
            source: '^APP_(.*)$'
            target: '$1'
```

Without `remoteKey`, every match becomes a separate provider secret or variable.
With `remoteKey`, all matches are bundled into one JSON object at that remote key.
An absent or empty `match` selects every key. Per-key mode supports regexp and
template rewrites but not merge; bundle mode does not apply rewrites. Configure
provider-specific `metadata` and `conversionStrategy` per entry.

### Expansion order and conflicts

`spec.template` runs before `dataTo` expansion. Key conversion runs before matching
and rewriting. For the same original, unconverted Kubernetes key, an explicit
`spec.data` entry wins.

- An invalid match regexp moves the `PushSecret` into an error state.
- No matches is a successful no-op.
- Duplicate remote keys within or across entries fail reconciliation and identify
  the conflicting sources.
- `UpdatePolicy=IfNotExists` applies independently to each expanded target.
- With `DeletionPolicy=Delete`, every expanded target is recorded in
  `status.syncedPushSecrets` and removed when the source Secret is deleted.

## ClusterPushSecret fan-out (`push-secrets`)

A `ClusterPushSecret` creates its embedded `pushSecretSpec` in each namespace that
matches any entry in the ORed `namespaceSelectors` list. `pushSecretName` defaults
to the parent name, `pushSecretMetadata` is copied to children, and `refreshTime`
sets the fan-out check interval.

Name collisions populate `failedNamespaces`. The parent `Ready` condition reports
child provisioning, not provider synchronization; inspect each generated
`PushSecret` for provider failures.

```yaml
apiVersion: external-secrets.io/v1alpha1
kind: ClusterPushSecret
metadata:
  name: app-credentials
spec:
  pushSecretName: app-credentials-push
  pushSecretMetadata:
    labels:
      managed-by: cluster-push
  namespaceSelectors:
    - matchLabels:
        team: payments
    - matchLabels:
        shared-secrets: "true"
  refreshTime: 1m
  pushSecretSpec:
    updatePolicy: Replace
    deletionPolicy: Delete
    refreshInterval: 1h
    secretStoreRefs:
      - name: destination
        kind: SecretStore
    selector:
      secret:
        name: source-credentials
    data:
      - match:
          secretKey: password
          remoteRef:
            remoteKey: app-credentials
            property: password
```

From 0.15.0, `ClusterPushSecret` can push all Secrets in a namespace rather than
requiring individual selection. Cross-namespace pushes through a
`ClusterSecretStore` work from 2.1.0.

## Deletion and ownership

- A `SecretStore` referenced by a `PushSecret` with `deletionPolicy: Delete` gains
  a finalizer from 0.20.0 so remote cleanup completes safely.
- A deletion bug that could remove the wrong remote key was fixed in 1.3.0.
- Target `objectMeta` and `ownerReferences` propagate from 2.3.0.

## Provider-specific push behavior

### AWS and GCP

- AWS Secrets Manager tag updates and deletions are available from 0.19.0; empty
  resource policies are handled from 2.3.0, replication locations from 2.7.0,
  and replicated secrets are detached before deletion from 2.9.0.
- GCP applies location and replication settings correctly from 0.17.0. Regional
  operations omit replication settings from 0.18.0, version existence is checked
  from 1.1.0, and multiple replication locations work from 2.4.0.
- Azure push accepts `contentType` from 2.4.0.

### Vault, Kubernetes, and integrations

- Vault has the existence and set operations needed for push from 0.20.0.
- Kubernetes supports whole-Secret deletion from 1.1.0 and `SecretExists` from
  2.1.0. From 2.7.0, a push replaces the complete remote Secret rather than
  merging and retaining absent keys.
- 1Password Connect is read-write from 0.18.0. The SDK provider completes
  multi-field push in 2.3.0 and honors `IfNotExists` from 2.8.0.
- Delinea Secret Server supports push from 2.3.0.
- Infisical supports push and maps HTTP 404 to absence from 2.7.0.
- Akeyless is routed as read-write from 2.7.0.
- Conjur returns explicit unsupported-operation errors for push and delete from
  2.4.0.
