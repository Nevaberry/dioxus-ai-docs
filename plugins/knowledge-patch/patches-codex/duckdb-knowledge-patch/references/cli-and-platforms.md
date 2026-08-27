# CLI and platforms

Use this reference for interactive workflows, constrained execution, direct
file opening, installation, and operating-system requirements. Relevant source
batches are `1.2-1.4` and `1.5.0`.

## Reuse the last query result

The CLI exposes the previous query result as table `_`, avoiding an expensive
rerun:

```sql
FROM ducks WHERE extinct_year IS NOT NULL;
FROM _;
```

`_` refers to the prior result, not the underlying query definition. Re-run the
original query when the source may have changed and freshness is required.

## Safe mode

Start the CLI with `-safe`:

```sh
duckdb -safe database.db
```

An interactive session can also enter safe mode with:

```text
.safe_mode
```

Safe mode prevents access to external files other than the database initially
opened and blocks interaction with the host file system. Use it when opening an
untrusted database or when a session should remain confined to its initial file.

## Open data files directly

Supplying a Parquet, CSV, or JSON file where the database path normally appears
creates a temporary in-memory database. It contains a `file` view and a second
view named after the file stem:

```sh
duckdb region.parquet -c 'FROM region;'
```

This is a CLI convenience for exploration. It does not attach the data file as a
persistent DuckDB database.

## Python-environment installation

Install the CLI into a Python environment with:

```sh
pip install duckdb-cli
duckdb
```

Distinguish the `duckdb-cli` package from a language binding when provisioning a
tool-only environment; the installed command is `duckdb`.

## Linux builds

Official Linux binaries starting with 1.3 require glibc 2.28 or newer.
Extensions are no longer published for `linux_amd64_gcc4`. Systems below that
floor must build DuckDB from source.

Linux musl builds are available for distributions such as Alpine. They require
`libstdc++`:

```sh
apk add libstdc++
```

Choose the musl artifact for a musl system; installing `libstdc++` does not turn
a glibc artifact into a musl-compatible one.

## Windows installer

The beta Windows installer runs in PowerShell as:

```powershell
powershell -NoExit iex (iwr "https://install.duckdb.org/install.ps1").Content
```

This downloads and executes a remote script. Apply the organization's normal
script-review, network, and execution-policy controls before using it in an
automated or managed environment.

## Platform and CLI checklist

1. Decide whether the task needs the CLI, a language binding, or both.
2. Check glibc versus musl before selecting a Linux build.
3. On Alpine-like systems, install `libstdc++` for the musl build.
4. Build from source when the host is below the supported glibc floor or depends
   on the removed `linux_amd64_gcc4` extension target.
5. Use safe mode for untrusted or deliberately confined sessions.
6. Use `_` only when reusing the actual prior result is correct.
7. Remember that direct CSV, JSON, and Parquet opening creates temporary views,
   not a persistent catalog.
