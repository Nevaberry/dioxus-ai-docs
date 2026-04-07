# CIL Policy Language

CIL (Common Intermediate Language) is the modern SELinux policy language that replaces the legacy M4-based reference policy format (`.te`/`.if`/`.fc` files). CIL uses S-expression syntax and provides native namespacing.

## Key Advantages Over M4 Policy

- No M4 macro preprocessor dependency
- No module load-ordering requirements
- Native namespacing via blocks (no naming collisions)
- Direct compilation without intermediate steps
- Simpler, more readable syntax

## Syntax Renames from Kernel Policy Language

When migrating from kernel/M4 policy to CIL, these statement names change:

| Kernel Policy Statement | CIL Statement | Purpose |
|---|---|---|
| `attribute` | `typeattribute` | Declare a type attribute (grouping mechanism) |
| `typeattribute` | `typeattributeset` | Assign one or more types to an attribute |
| `attribute_role` | `roleattribute` | Declare a role attribute |
| `type` | `type` | Declare a type (unchanged) |
| `role` | `role` | Declare a role (unchanged) |
| `allow` | `allow` | Grant access (S-expression form) |

## Blocks and Namespacing

All CIL declarations can be scoped inside `(block ...)` constructs. Blocks provide namespacing — types declared inside a block are referenced externally as `blockname.typename`:

```cil
(block myapp
    (type process)
    (type data)
    (role app_r)
    (roletype app_r process)
    (allow process data (file (read write open getattr)))
)
```

Referencing from another block:

```cil
(block other
    (type helper)
    (allow helper myapp.data (file (read getattr)))
)
```

## Block Inheritance

Blocks can inherit declarations from other blocks using `blockinherit`:

```cil
(block base_app
    (type process)
    (type data)
)

(block webapp
    (blockinherit base_app)
    ;; webapp now has webapp.process and webapp.data
    (allow process data (file (read write)))
)
```

This replaces the M4 `template`/`interface` pattern — `blockinherit` copies all declarations from the source block into the inheriting block, automatically namespaced.

## Access Rules

CIL access rules use S-expression form with permissions grouped by object class:

```cil
;; Single class, multiple permissions
(allow src_t tgt_t (file (read write open getattr)))

;; Multiple classes in one rule using classpermissionset
(allow src_t tgt_t (file (read write)) (dir (search getattr)))
```

## Loading CIL Policies

CIL modules are loaded directly with `semodule`:

```bash
# Install a single CIL module
semodule -i myapp.cil

# Install with dependencies
semodule -i myapp.cil /usr/share/udica/templates/base_container.cil

# Remove a CIL module
semodule -r myapp
```

CIL files use the `.cil` extension and do not require compilation to a `.pp` package — `semodule` compiles them directly.
