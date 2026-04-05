# Project Structure, Source Control & CI/CD

## TwinCAT Project File Extensions (Source Control)
Each POU, DUT, GVL, etc. is stored as a separate file. Key extensions and their SCM properties:

| Extension | What | SCM? | Mergeable? |
|-----------|------|------|------------|
| `.tsproj` | TwinCAT project file | Yes | Yes (use TwinCAT Project Compare Tool) |
| `.plcproj` | PLC project file | Yes | Yes (use TwinCAT Project Compare Tool) |
| `.TcPOU` | Program Organization Unit (program, FB, function) | Yes | Yes |
| `.TcDUT` | Data type (struct, enum, union, alias) | Yes | Yes |
| `.TcGVL` | Global Variable List | Yes | Yes |
| `.TcTTO` | PLC Task Object | Yes | Yes |
| `.TcGTLO` | Global Text List Object | Yes | Yes |
| `.xti` | Separated parts of .tsproj (multi-file mode) | Yes | Yes |
| `.tmc` | TcCOM module class description | Yes | **Not mergeable** for PLC projects |
| `.TcVis` | PLC Visualization | Yes | Not currently mergeable |
| `.TcVMO` | Visualization Manager | Yes | Not currently mergeable |
| `.tpr` | Refactoring info (standalone PLC projects) | Yes | Yes |

**Exclude from source control:** `.sln` (VS solution — causes cross-version issues), `.suo` (user-specific VS options), `.tpy` (compatibility only).

**Key rule:** `.tmc` is auto-regenerated after every PLC compile. From Build 4018+, it does NOT need to be in source control. Never manually merge `.tmc` files for PLC projects.

## Separate LineIDs for Clean Diffs
LineIDs (used for breakpoint mapping) are stored inside `.TcPOU` files by default, causing spurious diffs even when code hasn't changed. Separate them into `LineIDs.dbg` (excluded from SCM).

**Setting:** Tools > Options > TwinCAT > PLC Environment > Write options > Separate LineIDs = True

Add to `.gitignore`:
```
LineIDs.dbg
```

**Caution:** ALL developers on the team must use the same setting — mixing causes constant churn. Remove existing LineIDs from `.TcPOU` files with:
```bash
find . -type f -name "*.TcPOU" -exec sed -i "/LineId/d" {} \;
```

## Git Filter to Strip TargetNetId
Each developer's PLC target Net ID is saved in `.tsproj`, causing merge noise. Use a git clean filter to strip it on commit:

```bash
# .git/config
[filter "ignoreNetId"]
clean = sh ".git/ignoreTargetNetId.sh"

# .gitattributes (committed to repo)
*.tsproj filter=ignoreNetId

# .git/ignoreTargetNetId.sh
sed --regexp-extended "s/}\" TargetNetId=\"[0-9.]+\"/}\" /g" "$@"
```

With the Net ID stripped, TwinCAT defaults to `<Local>` runtime on project open.

## CI/CD via TwinCAT Automation Interface (C#)
Headless TwinCAT builds use two COM APIs: **Visual Studio DTE** (standard VS operations like build/clean) and **TwinCAT Automation Interface (TcAI)** (TwinCAT-specific: PLC config, remote manager, I/O). TcAI does NOT cover static code analysis directly — run a build and filter the error list instead.

```csharp
// 1. Create DTE instance for the correct VS version
string progId = "VisualStudio.DTE." + vsVersion;  // e.g. "15.0"
Type type = Type.GetTypeFromProgID(progId);
EnvDTE80.DTE2 dte = (EnvDTE80.DTE2)Activator.CreateInstance(type);
dte.SuppressUI = true;
dte.MainWindow.Visible = false;

// 2. Open solution
dte.Solution.Open(slnPath);

// 3. Set TwinCAT version via Remote Manager (ITcRemoteManager)
ITcRemoteManager remoteManager = dte.GetObject("TcRemoteManager");
remoteManager.Version = "3.1.4024.22";  // match project version

// 4. Build and collect errors
dte.Solution.SolutionBuild.Clean(true);
dte.Solution.SolutionBuild.Build(true);

// 5. Filter static analysis results (TE1200 rules prefixed "SA")
ErrorItems errors = dte.ToolWindows.ErrorList.ErrorItems;
for (int i = 1; i <= errors.Count; i++) {
    ErrorItem item = errors.Item(i);
    if (item.Description.StartsWith("SA")) {
        // item.ErrorLevel: vsBuildErrorLevelMedium = warning, High = error
        Console.WriteLine($"{item.Description} [{item.FileName}]");
    }
}
```

**References:** Add `EnvDTE`, `EnvDTE80` (.NET assemblies) and `Beckhoff TwinCAT XAE Base Type Library` (COM) to your C# project.

**Critical gotcha:** When running from Jenkins (or any Windows service), the service must run as a **local user account** — not SYSTEM. DTE/TcAI COM automation fails silently or throws `FileNotFoundException` under the SYSTEM account.

## Canonical TwinCAT3 .gitignore
The community-maintained [TwinCAT3.gitignore](https://github.com/github/gitignore/blob/master/TwinCAT3.gitignore) by Jakob Sagatowski is the standard starting point. Key additions beyond what it covers:
- `LineIDs.dbg` — if using Separate LineIDs setting
- Event `.tmc` files — if stored separately from `.tsproj`, they SHOULD be in SCM (override the blanket `.tmc` exclusion)
- Export mapping XMLs — optional backup of I/O mappings (right-click I/O > Mappings > Export Mapping Infos)

## Community Tools

### Plaincat — TwinCAT XML ↔ Plain Text Converter
Converts TwinCAT `.plcproj` XML files to/from plain `.st` text files, enabling editing in VS Code or other editors outside Visual Studio. By Zeugwerk.

```bash
# Convert TwinCAT project to plain .st files
Plaincat encode --source <path_to_plcproj> --target <output_folder>

# Convert plain .st files back to TwinCAT XML
Plaincat decode --target <path_to_empty_folder_for_new_plcproj> --source <path_to_folder_containing_st_files>
```

Also available as a VS Code extension (vscode-plaincat). Pair with the `Serhioromano.vscode-st` extension for ST syntax highlighting.

### blark — Python IEC 61131-3 Structured Text Parser
Lark-based parser that reads TwinCAT files (`.TcPOU`, `.TcGVL`, `.tsproj`, `.sln`) and plain `.st` files into a full AST. Useful for static analysis, code generation, and reformatting in CI/CD.

```bash
pip install blark

# Parse and print syntax tree
blark parse --print-tree MyPOU.TcPOU

# Reformat ST code (rewrites TwinCAT XML in-place)
blark format MyPOU.TcPOU

# Interactive IPython session with parsed dataclasses
blark parse --interactive MyPOU.TcPOU
```

```python
import blark

parsed = blark.parse_source_code("""
PROGRAM Main
    VAR
        iValue : INT;
    END_VAR
    iValue := iValue + 1;
END_PROGRAM
""")
transformed = parsed.transform()
program = transformed.items[0]
# Access declarations, variables, statements as Python dataclasses
```

### TcBlack — Opinionated Code Formatter
Black-style formatter for TwinCAT Structured Text. Available as CLI (`TcBlack.exe`) and Visual Studio extension. Alpha state — use only on source-controlled files.

```bash
# Format specific files (safe mode compiles before/after to verify no semantic change)
TcBlack --safe --file C:\Path\To\File.TcPOU

# Format entire project with custom indentation
TcBlack --safe -f C:\Path\To\Project.plcproj --indentation "  "
```

Formatting rules follow Python Black conventions where applicable: consistent spacing around `:=`, one declaration per line, long IF conditions broken across lines with `AND`/`OR` at line start.

### TwinCatChangelog — Community-Maintained Version Tracker
Unofficial changelog at `tcchanges.cookncode.com` tracking changes across TwinCAT versions (PLC, HMI, XAE). Beckhoff publishes no official release notes — this community resource (106+ stars, 22 contributors) fills that gap. Useful for understanding what changed between builds.
