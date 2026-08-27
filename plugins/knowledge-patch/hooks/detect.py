#!/usr/bin/env python3
"""Offline knowledge-patch detector used by the SessionStart hook."""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Sequence


PATCH_SUFFIX = "-knowledge-patch"
MAX_FILES = 20_000
MAX_READ_BYTES = 256 * 1024
TIME_BUDGET_SECONDS = 1.5
MAX_WALK_DEPTH = 12
MAX_CONTEXT_NAMES = 15
PRUNE_DIRS = {
    "node_modules",
    ".git",
    "dist",
    "build",
    ".next",
    ".turbo",
    "target",
    "vendor",
    ".venv",
    "__pycache__",
    ".cache",
    "coverage",
}
PROJECT_MANIFESTS = {
    "package.json",
    "deno.json",
    "deno.jsonc",
    "Cargo.toml",
    "pyproject.toml",
    "setup.py",
    "go.mod",
    "mix.exs",
    "Gemfile",
    "composer.json",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "build.sbt",
    "pubspec.yaml",
    "Package.swift",
    "CMakeLists.txt",
}
PROJECT_MANIFEST_GLOBS = ("*.csproj", "*.fsproj")
FALLBACK_CONTEXT = (
    "Use knowledge-patch:using-knowledge-patch. Read matching patch bodies. "
    "Active patches: none."
)


@dataclass
class FileIndex:
    root: Path
    relpaths: list[str] = field(default_factory=list)
    by_basename: dict[str, list[str]] = field(default_factory=dict)
    project_units: set[str] = field(default_factory=lambda: {""})
    _pattern_cache: dict[str, tuple[str, ...]] = field(default_factory=dict)
    _content_cache: dict[str, bytes | None] = field(default_factory=dict)

    @classmethod
    def from_paths(
        cls,
        root: Path,
        relpaths: Iterable[str],
        *,
        deadline: float | None = None,
    ) -> "FileIndex":
        index = cls(root=root)
        seen: set[str] = set()
        for raw in relpaths:
            relpath = raw.replace(os.sep, "/").removeprefix("./")
            if not relpath or relpath in seen:
                continue
            seen.add(relpath)
            index.relpaths.append(relpath)
            basename = relpath.rsplit("/", 1)[-1]
            index.by_basename.setdefault(basename, []).append(relpath)
        index.discover_project_units(deadline)
        return index

    def discover_project_units(self, deadline: float | None = None) -> None:
        for relpath in self.relpaths:
            if deadline is not None and time.monotonic() >= deadline:
                break
            basename = relpath.rsplit("/", 1)[-1]
            unit = relpath.rpartition("/")[0]
            if not unit or unit in self.project_units or not is_project_manifest(basename):
                continue
            content = self.content(relpath)
            if content is not None and valid_manifest_content(basename, content):
                self.project_units.add(unit)

    def candidates(self, pattern: str) -> tuple[str, ...]:
        cached = self._pattern_cache.get(pattern)
        if cached is not None:
            return cached
        basename_pattern = pattern.rsplit("/", 1)[-1]
        basenames = (
            (basename_pattern,)
            if not has_magic(basename_pattern)
            else tuple(
                name
                for name in self.by_basename
                if match_segment(name, basename_pattern)
            )
        )
        matches = tuple(
            relpath
            for basename in basenames
            for relpath in self.by_basename.get(basename, ())
            if match_project_path(relpath, pattern, self.project_units)
        )
        self._pattern_cache[pattern] = matches
        return matches

    def content(self, relpath: str) -> bytes | None:
        if relpath not in self._content_cache:
            self._content_cache[relpath] = read_limited(
                self.root / Path(relpath), MAX_READ_BYTES
            )
        return self._content_cache[relpath]


@dataclass(frozen=True)
class DetectionResult:
    activated: tuple[str, ...]
    detected: tuple[str, ...]
    promoted: tuple[str, ...]
    host_only: tuple[str, ...]
    activation_state_exists: bool
    evidence: dict[str, tuple["MatchEvidence", ...]] = field(default_factory=dict)

    def as_dict(self) -> dict[str, object]:
        return {
            "activated": [display_name(item) for item in self.activated],
            "detected": [display_name(item) for item in self.detected],
            "promoted": [display_name(item) for item in self.promoted],
            "host_only": [display_name(item) for item in self.host_only],
        }


@dataclass(frozen=True)
class MatchEvidence:
    signal: str
    path: str


def catalog_path(detector_file: Path | None = None) -> Path:
    source = (detector_file or Path(__file__)).resolve()
    return source.parent.parent / "catalog" / "detection.json"


def links_path(detector_file: Path | None = None) -> Path:
    return catalog_path(detector_file).with_name("links.json")


def has_magic(pattern: str) -> bool:
    return any(character in pattern for character in "*?[{")


def is_project_manifest(basename: str) -> bool:
    return basename in PROJECT_MANIFESTS or any(
        fnmatch.fnmatchcase(basename, pattern)
        for pattern in PROJECT_MANIFEST_GLOBS
    )


def strip_json_comments(text: str) -> str:
    output: list[str] = []
    index = 0
    in_string = False
    escaped = False
    while index < len(text):
        character = text[index]
        if in_string:
            output.append(character)
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            index += 1
            continue
        if character == '"':
            in_string = True
            output.append(character)
            index += 1
            continue
        following = text[index + 1] if index + 1 < len(text) else ""
        if character == "/" and following == "/":
            index += 2
            while index < len(text) and text[index] not in "\r\n":
                index += 1
            continue
        if character == "/" and following == "*":
            index += 2
            while index + 1 < len(text) and text[index : index + 2] != "*/":
                if text[index] in "\r\n":
                    output.append(text[index])
                index += 1
            if index + 1 >= len(text):
                raise ValueError("unterminated JSON comment")
            index += 2
            continue
        output.append(character)
        index += 1
    return "".join(output)


def strip_trailing_json_commas(text: str) -> str:
    output: list[str] = []
    index = 0
    in_string = False
    escaped = False
    while index < len(text):
        character = text[index]
        if in_string:
            output.append(character)
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            index += 1
            continue
        if character == '"':
            in_string = True
            output.append(character)
            index += 1
            continue
        if character == ",":
            following = index + 1
            while following < len(text) and text[following].isspace():
                following += 1
            if following < len(text) and text[following] in "}]":
                index += 1
                continue
        output.append(character)
        index += 1
    return "".join(output)


def json_object(content: bytes, *, comments: bool = False) -> dict | None:
    try:
        text = content.decode("utf-8-sig")
        if comments:
            text = strip_trailing_json_commas(strip_json_comments(text))
        value = json.loads(text)
    except (UnicodeDecodeError, ValueError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def valid_manifest_content(basename: str, content: bytes) -> bool:
    if basename == "package.json":
        value = json_object(content)
        return value is not None and bool(
            value.keys()
            & {
                "name",
                "version",
                "dependencies",
                "devDependencies",
                "peerDependencies",
                "scripts",
                "workspaces",
                "private",
            }
        )
    if basename in {"deno.json", "deno.jsonc"}:
        value = json_object(content, comments=basename.endswith(".jsonc"))
        return value is not None and bool(
            value.keys()
            & {
                "imports",
                "importMap",
                "tasks",
                "compilerOptions",
                "lint",
                "fmt",
                "exports",
                "nodeModulesDir",
                "lock",
                "workspace",
            }
        )
    if basename == "composer.json":
        value = json_object(content)
        return value is not None and bool(
            value.keys() & {"name", "require", "require-dev", "autoload", "type"}
        )
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        return False
    if basename == "Cargo.toml":
        return "[package]" in text or "[workspace]" in text
    if basename == "pyproject.toml":
        return any(marker in text for marker in ("[project]", "[build-system]", "[tool."))
    if basename == "go.mod":
        return any(line.startswith("module ") for line in text.splitlines())
    if basename == "mix.exs":
        return "defmodule" in text and "def project" in text
    if basename == "Gemfile":
        return "source " in text or "gem " in text
    if basename == "pom.xml":
        return "<project" in text and "<artifactId" in text
    if basename in {"build.gradle", "build.gradle.kts"}:
        return any(
            marker in text
            for marker in ("plugins {", "dependencies {", "apply plugin")
        )
    if basename == "build.sbt":
        return "scalaVersion" in text or "libraryDependencies" in text
    if basename == "pubspec.yaml":
        lines = tuple(line.lstrip() for line in text.splitlines())
        return any(line.startswith("name:") for line in lines) and any(
            line.startswith(("dependencies:", "environment:")) for line in lines
        )
    if basename == "Package.swift":
        return "PackageDescription" in text
    if basename == "setup.py":
        return "setup(" in text
    if basename == "CMakeLists.txt":
        return "project(" in text or "cmake_minimum_required" in text
    if any(fnmatch.fnmatchcase(basename, pattern) for pattern in PROJECT_MANIFEST_GLOBS):
        return "<Project" in text
    return False


def brace_variants(pattern: str) -> tuple[str, ...]:
    start = pattern.find("{")
    if start < 0:
        return (pattern,)
    end = pattern.find("}", start + 1)
    if end < 0:
        return (pattern,)
    choices = pattern[start + 1 : end].split(",")
    if len(choices) < 2:
        return (pattern,)
    variants: list[str] = []
    for choice in choices:
        variants.extend(brace_variants(pattern[:start] + choice + pattern[end + 1 :]))
    return tuple(variants)


def match_segment(value: str, pattern: str) -> bool:
    return any(fnmatch.fnmatchcase(value, variant) for variant in brace_variants(pattern))


def match_segments(path_parts: Sequence[str], pattern_parts: Sequence[str]) -> bool:
    if not pattern_parts:
        return not path_parts
    head = pattern_parts[0]
    if head == "**":
        return match_segments(path_parts, pattern_parts[1:]) or bool(
            path_parts and match_segments(path_parts[1:], pattern_parts)
        )
    return bool(
        path_parts
        and match_segment(path_parts[0], head)
        and match_segments(path_parts[1:], pattern_parts[1:])
    )


def match_project_path(
    relpath: str, pattern: str, project_units: Iterable[str]
) -> bool:
    path_parts = tuple(part for part in relpath.split("/") if part)
    pattern_parts = tuple(part for part in pattern.split("/") if part)
    if not pattern_parts:
        return False
    if pattern_parts[0] == "**":
        return match_segments(path_parts, pattern_parts)
    for unit in project_units:
        if unit:
            prefix = unit + "/"
            if not relpath.startswith(prefix):
                continue
            relative = relpath[len(prefix) :]
        else:
            relative = relpath
        relative_parts = tuple(part for part in relative.split("/") if part)
        if match_segments(relative_parts, pattern_parts):
            return True
    return False


def read_limited(path: Path, limit: int) -> bytes | None:
    try:
        if not path.is_file():
            return None
        if path.stat().st_size > limit:
            return None
        with path.open("rb") as handle:
            return handle.read(limit)
    except OSError:
        return None


def time_left(deadline: float) -> float:
    return max(0.0, deadline - time.monotonic())


def git_paths(root: Path, deadline: float) -> list[str] | None:
    remaining = time_left(deadline)
    if remaining <= 0:
        return []
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=remaining,
            env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if completed.returncode != 0:
        return None
    paths: list[str] = []
    for raw in completed.stdout.split(b"\0"):
        if not raw:
            continue
        paths.append(raw.decode("utf-8", errors="surrogateescape"))
        if len(paths) >= MAX_FILES or time.monotonic() >= deadline:
            break
    return paths


def walked_paths(
    root: Path,
    deadline: float,
    *,
    env_only: bool = False,
    room: int = MAX_FILES,
) -> list[str]:
    found: list[str] = []
    if room <= 0:
        return found
    try:
        iterator = os.walk(root, topdown=True, followlinks=False)
        for directory, dirnames, filenames in iterator:
            if time.monotonic() >= deadline:
                break
            current = Path(directory)
            try:
                depth = len(current.relative_to(root).parts)
            except ValueError:
                break
            if depth >= MAX_WALK_DEPTH:
                dirnames[:] = []
            else:
                dirnames[:] = sorted(
                    name for name in dirnames if name not in PRUNE_DIRS
                )
            for filename in sorted(filenames):
                if env_only and not filename.startswith(".env"):
                    continue
                path = current / filename
                try:
                    relpath = path.relative_to(root).as_posix()
                except ValueError:
                    continue
                found.append(relpath)
                if len(found) >= room or time.monotonic() >= deadline:
                    return found
    except OSError:
        pass
    return found


def build_file_index(root: Path, deadline: float) -> FileIndex:
    tracked = git_paths(root, deadline)
    if tracked is None:
        paths = walked_paths(root, deadline)
    else:
        paths = tracked
        seen = set(paths)
        for relpath in walked_paths(
            root, deadline, env_only=True, room=MAX_FILES - len(paths)
        ):
            if relpath not in seen:
                seen.add(relpath)
                paths.append(relpath)
                if len(paths) >= MAX_FILES:
                    break
    existing = (
        relpath
        for relpath in paths
        if time.monotonic() < deadline and (root / Path(relpath)).is_file()
    )
    return FileIndex.from_paths(root, existing, deadline=deadline)


def split_signal(signal: str) -> tuple[str, str | None]:
    pattern, separator, marker = signal.partition("::")
    return pattern, marker if separator else None


def project_signal_paths(
    index: FileIndex, pattern: str, marker: str | None, deadline: float
) -> tuple[str, ...]:
    marker_bytes = marker.encode("utf-8") if marker is not None else None
    matches: list[str] = []
    for relpath in index.candidates(pattern):
        if time.monotonic() >= deadline:
            break
        if marker_bytes is None:
            matches.append(relpath)
        else:
            content = index.content(relpath)
            if content is not None and marker_bytes in content:
                matches.append(relpath)
        if matches:
            break
    return tuple(matches)


def project_signal_matches(
    index: FileIndex, pattern: str, marker: str | None, deadline: float
) -> bool:
    return bool(project_signal_paths(index, pattern, marker, deadline))


def absolute_candidates(pattern: str, host_root: Path) -> Iterable[Path]:
    rooted = host_root / pattern.lstrip("/")
    if not has_magic(pattern):
        yield rooted
        return
    parent = rooted.parent
    try:
        yield from parent.glob(rooted.name)
    except OSError:
        return


def absolute_signal_paths(
    pattern: str,
    marker: str | None,
    host_root: Path,
    content_cache: dict[Path, bytes | None],
    deadline: float,
) -> tuple[Path, ...]:
    marker_bytes = marker.encode("utf-8") if marker is not None else None
    matches: list[Path] = []
    for path in absolute_candidates(pattern, host_root):
        if time.monotonic() >= deadline:
            break
        if marker_bytes is None:
            try:
                if path.exists():
                    matches.append(path)
            except OSError:
                continue
        else:
            if path not in content_cache:
                content_cache[path] = read_limited(path, MAX_READ_BYTES)
            content = content_cache[path]
            if content is not None and marker_bytes in content:
                matches.append(path)
        if matches:
            break
    return tuple(matches)


def absolute_signal_matches(
    pattern: str,
    marker: str | None,
    host_root: Path,
    content_cache: dict[Path, bytes | None],
    deadline: float,
) -> bool:
    return bool(
        absolute_signal_paths(pattern, marker, host_root, content_cache, deadline)
    )


def load_object(path: Path, limit: int = 8 * 1024 * 1024) -> dict:
    raw = read_limited(path, limit)
    if raw is None:
        raise ValueError(f"missing JSON file: {path}")
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root is not an object: {path}")
    return value


def load_rules(path: Path) -> list[dict]:
    catalog = load_object(path)
    rules = catalog.get("rules")
    if not isinstance(rules, list):
        raise ValueError("detection catalog has no rules list")
    for rule in rules:
        signals = rule.get("signals") if isinstance(rule, dict) else None
        files = signals.get("files") if isinstance(signals, dict) else None
        if (
            not isinstance(rule, dict)
            or not isinstance(rule.get("id"), str)
            or not isinstance(files, list)
            or not all(isinstance(signal, str) for signal in files)
        ):
            raise ValueError("detection catalog contains a malformed rule")
    return rules


def detect_rule_ids(
    rules: Iterable[dict],
    index: FileIndex,
    deadline: float,
    *,
    host_root: Path = Path("/"),
) -> tuple[set[str], set[str], dict[str, tuple[MatchEvidence, ...]]]:
    promoted: set[str] = set()
    host_only: set[str] = set()
    evidence: dict[str, tuple[MatchEvidence, ...]] = {}
    host_content: dict[Path, bytes | None] = {}
    for rule in rules:
        if time.monotonic() >= deadline:
            break
        rule_id = rule.get("id")
        signals = rule.get("signals")
        files = signals.get("files") if isinstance(signals, dict) else None
        if not isinstance(rule_id, str) or not isinstance(files, list):
            continue
        project_match = False
        machine_match = False
        incidental_host_match = False
        promoting_evidence: list[MatchEvidence] = []
        for raw_signal in files:
            if time.monotonic() >= deadline:
                break
            if not isinstance(raw_signal, str):
                continue
            pattern, marker = split_signal(raw_signal)
            if pattern.startswith("/"):
                paths = absolute_signal_paths(
                    pattern, marker, host_root, host_content, deadline
                )
                if pattern == "/etc/os-release":
                    machine_match = machine_match or bool(paths)
                    promoting_evidence.extend(
                        MatchEvidence(raw_signal, str(path)) for path in paths
                    )
                else:
                    incidental_host_match = incidental_host_match or bool(paths)
            else:
                paths = project_signal_paths(index, pattern, marker, deadline)
                project_match = project_match or bool(paths)
                promoting_evidence.extend(
                    MatchEvidence(raw_signal, path) for path in paths
                )
        if project_match or machine_match:
            promoted.add(rule_id)
            evidence[rule_id] = tuple(dict.fromkeys(promoting_evidence))
        elif incidental_host_match:
            host_only.add(rule_id)
    return promoted, host_only, evidence


def canonical_id(name: str) -> str:
    return name if name.endswith(PATCH_SUFFIX) else name + PATCH_SUFFIX


def display_name(name: str) -> str:
    return name[: -len(PATCH_SUFFIX)] if name.endswith(PATCH_SUFFIX) else name


def state_candidates(root: Path, environ: Mapping[str, str]) -> Iterable[Path]:
    raw: list[Path] = []
    configured = environ.get("KNOWLEDGE_PATCH_STATE", "").strip()
    if configured:
        raw.append(Path(configured).expanduser())
    raw.append(root / ".knowledge-patch" / "activation.json")
    xdg_state = environ.get("XDG_STATE_HOME", "").strip()
    if xdg_state:
        raw.append(Path(xdg_state).expanduser() / "knowledge-patch" / "activation.json")
    home = environ.get("HOME", "").strip()
    if home:
        raw.append(
            Path(home).expanduser()
            / ".local"
            / "state"
            / "knowledge-patch"
            / "activation.json"
        )
    seen: set[Path] = set()
    for path in raw:
        if path not in seen:
            seen.add(path)
            yield path


def read_activation_state(
    root: Path, environ: Mapping[str, str]
) -> tuple[list[str], bool]:
    for path in state_candidates(root, environ):
        try:
            exists = path.is_file()
        except OSError:
            continue
        if not exists:
            continue
        raw = read_limited(path, MAX_READ_BYTES)
        if raw is None:
            continue
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        if not isinstance(value, dict):
            continue
        active = value.get("active_patches", [])
        if not isinstance(active, list):
            active = []
        names: list[str] = []
        for name in active:
            if isinstance(name, str) and name.strip():
                canonical = canonical_id(name.strip())
                if canonical not in names:
                    names.append(canonical)
        return names, True
    return [], False


def load_links(path: Path) -> dict[str, list[str]]:
    if not path.is_file():
        return {}
    value = load_object(path)
    links: dict[str, list[str]] = {}
    for source, targets in value.items():
        if (
            not isinstance(source, str)
            or not source
            or not isinstance(targets, list)
            or not all(isinstance(target, str) and target for target in targets)
        ):
            raise ValueError("links.json values must be string arrays")
        links[canonical_id(source)] = [canonical_id(target) for target in targets]
    return links


def expand_links(detected: Iterable[str], links: Mapping[str, Sequence[str]]) -> set[str]:
    original = set(detected)
    expanded = set(original)
    for source in original:
        expanded.update(links.get(source, ()))
    return expanded


def run_detection(
    root: Path,
    *,
    detection_catalog: Path,
    links_catalog: Path | None = None,
    environ: Mapping[str, str] | None = None,
    host_root: Path = Path("/"),
    budget_seconds: float = TIME_BUDGET_SECONDS,
) -> DetectionResult:
    resolved_root = root.expanduser().resolve()
    environment = os.environ if environ is None else environ
    deadline = time.monotonic() + budget_seconds
    activated, state_exists = read_activation_state(resolved_root, environment)
    rules = load_rules(detection_catalog)
    links = load_links(links_catalog) if links_catalog is not None else {}
    index = build_file_index(resolved_root, deadline)
    detected, host_only, evidence = detect_rule_ids(
        rules, index, deadline, host_root=host_root
    )
    direct_detected = set(detected)
    detected = expand_links(direct_detected, links)
    for source in direct_detected:
        for upstream in links.get(source, ()):
            link_evidence = MatchEvidence(
                f"upstream link from {source}", "catalog/links.json"
            )
            evidence[upstream] = tuple(
                dict.fromkeys((*evidence.get(upstream, ()), link_evidence))
            )
    activated_set = set(activated)
    for active in activated_set:
        manual_evidence = MatchEvidence("manual activation", "activation state")
        evidence[active] = tuple(
            dict.fromkeys((*evidence.get(active, ()), manual_evidence))
        )
    detected_not_manual = detected - activated_set
    promoted = activated_set | detected
    return DetectionResult(
        activated=tuple(sorted(activated_set, key=display_name)),
        detected=tuple(sorted(detected_not_manual, key=display_name)),
        promoted=tuple(sorted(promoted, key=display_name)),
        host_only=tuple(sorted(host_only - promoted, key=display_name)),
        activation_state_exists=state_exists,
        evidence={
            rule_id: evidence.get(rule_id, ())
            for rule_id in sorted(promoted, key=display_name)
        },
    )


def format_context(result: DetectionResult) -> str:
    activated = [display_name(item) for item in result.activated]
    detected = [display_name(item) for item in result.detected]
    ordered: list[tuple[str, str]] = [
        *(("activated", item) for item in activated),
        *(("detected", item) for item in detected),
    ]
    visible = ordered[:MAX_CONTEXT_NAMES]
    visible_activated = [name for kind, name in visible if kind == "activated"]
    visible_detected = [name for kind, name in visible if kind == "detected"]
    lines = ["Use knowledge-patch:using-knowledge-patch."]
    if result.activation_state_exists:
        lines.append("Activated: " + (", ".join(visible_activated) or "none"))
    lines.append("Detected: " + (", ".join(visible_detected) or "none"))
    lines.append("Patch body: patches-codex/<name>-knowledge-patch/SKILL.md")
    lines.append("Full catalog: catalog/index.md")
    hidden = len(ordered) - len(visible)
    if hidden:
        lines.append(f"Additional matches in the catalog: {hidden}")
    return "\n".join(lines)


def hook_payload(context: str) -> dict[str, object]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }


def format_explanation(result: DetectionResult) -> str:
    lines: list[str] = []
    for rule_id in result.promoted:
        lines.append(rule_id)
        matches = result.evidence.get(rule_id, ())
        if matches:
            lines.extend(
                f"  {match.signal} -> {match.path}" for match in matches
            )
        else:
            lines.append("  no retained evidence")
    return "\n".join(lines) if lines else "Promoted: none"


def fallback_report() -> dict[str, object]:
    return {
        "activated": [],
        "detected": [],
        "promoted": [],
        "host_only": [],
        "fallback": True,
        "additionalContext": FALLBACK_CONTEXT,
    }


def main(
    argv: Sequence[str] | None = None,
    *,
    detector_file: Path | None = None,
) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--catalog",
        type=Path,
        help="override the default catalog/detection.json path",
    )
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", dest="as_json")
    output_group.add_argument("--explain", action="store_true")
    output_group.add_argument("--hook", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        detection_catalog = (
            args.catalog.expanduser().resolve()
            if args.catalog is not None
            else catalog_path(detector_file)
        )
        result = run_detection(
            args.root,
            detection_catalog=detection_catalog,
            links_catalog=(
                detection_catalog.with_name("links.json")
                if args.catalog is not None
                else links_path(detector_file)
            ),
        )
        context = format_context(result)
        if args.hook:
            output: object = hook_payload(context)
        elif args.as_json:
            output = result.as_dict()
        elif args.explain:
            print(format_explanation(result))
            return 0
        else:
            print(context)
            return 0
    except Exception:
        if args.hook:
            output = hook_payload(FALLBACK_CONTEXT)
        elif args.as_json:
            output = fallback_report()
        else:
            print(FALLBACK_CONTEXT)
            return 0
    print(json.dumps(output, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
