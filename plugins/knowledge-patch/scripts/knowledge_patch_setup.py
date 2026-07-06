#!/usr/bin/env python3
"""Detect and install knowledge patch skills for Codex from the public plugin repo."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import stat
import subprocess
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path

DEPENDENCY_SECTION_KEYS = {
    "dependencies",
    "dev-dependencies",
    "build-dependencies",
}

PACKAGE_DEP_KEYS = (
    "dependencies",
    "devDependencies",
    "peerDependencies",
    "optionalDependencies",
)

PUBLISHED_PATCHES = {
    "almalinux-knowledge-patch",
    "angular-knowledge-patch",
    "arch-knowledge-patch",
    "astro-knowledge-patch",
    "authjs-knowledge-patch",
    "axum-knowledge-patch",
    "beckhoff-knowledge-patch",
    "better-auth-knowledge-patch",
    "biome-knowledge-patch",
    "bun-knowledge-patch",
    "centos-stream-knowledge-patch",
    "clerk-knowledge-patch",
    "debian-knowledge-patch",
    "deno-knowledge-patch",
    "dioxus-knowledge-patch",
    "docker-knowledge-patch",
    "drizzle-knowledge-patch",
    "elixir-knowledge-patch",
    "fastapi-knowledge-patch",
    "flutter-knowledge-patch",
    "gleam-knowledge-patch",
    "go-knowledge-patch",
    "hono-knowledge-patch",
    "htmx-knowledge-patch",
    "kotlin-knowledge-patch",
    "kubernetes-knowledge-patch",
    "leptos-knowledge-patch",
    "nextjs-knowledge-patch",
    "nodejs-knowledge-patch",
    "nuxt-knowledge-patch",
    "playwright-knowledge-patch",
    "podman-knowledge-patch",
    "postgis-knowledge-patch",
    "postgresql-knowledge-patch",
    "prisma-knowledge-patch",
    "python-knowledge-patch",
    "react-knowledge-patch",
    "react-router-knowledge-patch",
    "rhel-knowledge-patch",
    "rocky-knowledge-patch",
    "rust-knowledge-patch",
    "solidjs-knowledge-patch",
    "sqlite-knowledge-patch",
    "sqlx-knowledge-patch",
    "supabase-knowledge-patch",
    "suse-knowledge-patch",
    "svelte-knowledge-patch",
    "swift-knowledge-patch",
    "tailwind-knowledge-patch",
    "tauri-knowledge-patch",
    "terraform-knowledge-patch",
    "trpc-knowledge-patch",
    "typescript-knowledge-patch",
    "ubuntu-knowledge-patch",
    "vercel-ai-sdk-knowledge-patch",
    "vite-knowledge-patch",
    "vitest-knowledge-patch",
    "vuejs-knowledge-patch",
    "workos-knowledge-patch",
    "zig-knowledge-patch",
    "zitadel-knowledge-patch",
}

DEFAULT_PUBLIC_REPO_URL = "https://github.com/Nevaberry/nevaberry-plugins.git"
DEFAULT_PUBLIC_REPO_REF = os.environ.get("KP_PUBLIC_REF", "main")


@dataclass(frozen=True)
class Detection:
    name: str
    reason: str


class DetectionState:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.package_deps = self._load_package_deps()
        self.cargo_deps = self._load_cargo_deps()
        self.python_deps = self._load_python_deps()
        self.docker_images = self._load_docker_images()

    def has_file(self, relative_path: str) -> bool:
        return (self.root / relative_path).exists()

    def has_any_file(self, *relative_paths: str) -> str | None:
        for relative_path in relative_paths:
            if self.has_file(relative_path):
                return relative_path
        return None

    def has_glob(self, pattern: str) -> str | None:
        matches = sorted(self.root.glob(pattern))
        if matches:
            return str(matches[0].relative_to(self.root))
        return None

    def has_dir(self, relative_path: str) -> bool:
        return (self.root / relative_path).is_dir()

    def package_dep(self, *names: str) -> str | None:
        for name in names:
            if name.lower() in self.package_deps:
                return name
        return None

    def package_dep_prefix(self, prefix: str) -> str | None:
        prefix = prefix.lower()
        for name in sorted(self.package_deps):
            if name.startswith(prefix):
                return name
        return None

    def cargo_dep(self, *names: str) -> str | None:
        for name in names:
            if name.lower() in self.cargo_deps:
                return name
        return None

    def python_dep(self, *names: str) -> str | None:
        for name in names:
            if name.lower() in self.python_deps:
                return name
        return None

    def docker_image_contains(self, needle: str) -> str | None:
        needle = needle.lower()
        for image in sorted(self.docker_images):
            if needle in image:
                return image
        return None

    def file_contains(self, relative_path: str, pattern: str) -> bool:
        path = self.root / relative_path
        if not path.is_file():
            return False
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return False
        return pattern in content

    def _load_package_deps(self) -> set[str]:
        path = self.root / "package.json"
        if not path.is_file():
            return set()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return set()
        deps: set[str] = set()
        for key in PACKAGE_DEP_KEYS:
            section = data.get(key)
            if isinstance(section, dict):
                deps.update(name.lower() for name in section.keys())
        return deps

    def _load_cargo_deps(self) -> set[str]:
        path = self.root / "Cargo.toml"
        if not path.is_file():
            return set()
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError:
            return set()

        deps: set[str] = set()

        def visit(node: object) -> None:
            if not isinstance(node, dict):
                return
            for key, value in node.items():
                if key in DEPENDENCY_SECTION_KEYS and isinstance(value, dict):
                    deps.update(name.lower() for name in value.keys())
                elif isinstance(value, dict):
                    visit(value)

        visit(data)
        return deps

    def _load_python_deps(self) -> set[str]:
        deps: set[str] = set()
        deps.update(self._load_pyproject_deps())
        deps.update(self._load_requirements())
        deps.update(self._load_pipfile_deps())
        return deps

    def _load_pyproject_deps(self) -> set[str]:
        path = self.root / "pyproject.toml"
        if not path.is_file():
            return set()
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError:
            return set()

        deps: set[str] = set()
        project = data.get("project", {})
        if isinstance(project, dict):
            deps.update(normalize_requirement(dep) for dep in project.get("dependencies", []))
            optional = project.get("optional-dependencies", {})
            if isinstance(optional, dict):
                for items in optional.values():
                    if isinstance(items, list):
                        deps.update(normalize_requirement(dep) for dep in items)

        tool = data.get("tool", {})
        if isinstance(tool, dict):
            poetry = tool.get("poetry", {})
            if isinstance(poetry, dict):
                poetry_deps = poetry.get("dependencies", {})
                if isinstance(poetry_deps, dict):
                    for name in poetry_deps.keys():
                        if name.lower() != "python":
                            deps.add(name.lower())
                groups = poetry.get("group", {})
                if isinstance(groups, dict):
                    for group in groups.values():
                        if not isinstance(group, dict):
                            continue
                        group_deps = group.get("dependencies", {})
                        if isinstance(group_deps, dict):
                            deps.update(name.lower() for name in group_deps.keys())
        return deps

    def _load_requirements(self) -> set[str]:
        path = self.root / "requirements.txt"
        if not path.is_file():
            return set()
        deps: set[str] = set()
        for line in path.read_text(encoding="utf-8").splitlines():
            dep = normalize_requirement(line)
            if dep:
                deps.add(dep)
        return deps

    def _load_pipfile_deps(self) -> set[str]:
        path = self.root / "Pipfile"
        if not path.is_file():
            return set()
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError:
            return set()
        deps: set[str] = set()
        for key in ("packages", "dev-packages"):
            section = data.get(key, {})
            if isinstance(section, dict):
                deps.update(name.lower() for name in section.keys())
        return deps

    def _load_docker_images(self) -> set[str]:
        images: set[str] = set()
        for name in ("docker-compose.yml", "docker-compose.yaml"):
            path = self.root / name
            if not path.is_file():
                continue
            content = path.read_text(encoding="utf-8")
            for match in re.finditer(r"^\s*image:\s*[\"']?([^\"'\s]+)", content, re.MULTILINE):
                images.add(match.group(1).lower())
        return images


def normalize_requirement(value: str) -> str:
    value = value.strip()
    if not value or value.startswith("#") or value.startswith("-r "):
        return ""
    value = value.split("#", 1)[0].strip()
    value = value.split(";", 1)[0].strip()
    if not value:
        return ""
    value = re.split(r"[<>=!~\[]", value, 1)[0].strip()
    return value.lower()


def detect_patches(state: DetectionState, available_patches: set[str]) -> list[Detection]:
    detections: list[Detection] = []

    def add(patch_name: str, reason: str | None) -> None:
        if not reason or patch_name not in available_patches:
            return
        if any(existing.name == patch_name for existing in detections):
            return
        detections.append(Detection(name=patch_name, reason=reason))

    add("bun-knowledge-patch", (state.has_any_file("bun.lock", "bun.lockb", "bunfig.toml") or "") or (f"package.json dependency `{state.package_dep('bun')}`" if state.package_dep("bun") else ""))
    add("typescript-knowledge-patch", ("tsconfig.json" if state.has_file("tsconfig.json") else "") or (f"package.json dependency `{state.package_dep('typescript')}`" if state.package_dep("typescript") else ""))
    add("nextjs-knowledge-patch", (f"package.json dependency `{state.package_dep('next')}`" if state.package_dep("next") else "") or (state.has_glob("next.config.*") or ""))
    add("react-knowledge-patch", f"package.json dependency `{state.package_dep('react')}`" if state.package_dep("react") else None)
    add("react-router-knowledge-patch", f"package.json dependency `{state.package_dep('react-router', 'react-router-dom')}`" if state.package_dep("react-router", "react-router-dom") else None)
    add("nodejs-knowledge-patch", state.has_any_file("package-lock.json", ".nvmrc", ".node-version", "pnpm-lock.yaml"))
    add("python-knowledge-patch", state.has_any_file("pyproject.toml", "requirements.txt", "Pipfile", ".python-version", "poetry.lock", "uv.lock"))
    add("fastapi-knowledge-patch", f"Python dependency `{state.python_dep('fastapi')}`" if state.python_dep("fastapi") else None)
    add("rust-knowledge-patch", "Cargo.toml" if state.has_file("Cargo.toml") else None)
    add("axum-knowledge-patch", f"Cargo dependency `{state.cargo_dep('axum')}`" if state.cargo_dep("axum") else None)
    add("dioxus-knowledge-patch", (f"Cargo dependency `{state.cargo_dep('dioxus')}`" if state.cargo_dep("dioxus") else "") or ("Dioxus.toml" if state.has_file("Dioxus.toml") else ""))
    add("leptos-knowledge-patch", f"Cargo dependency `{state.cargo_dep('leptos')}`" if state.cargo_dep("leptos") else None)
    add("sqlx-knowledge-patch", f"Cargo dependency `{state.cargo_dep('sqlx')}`" if state.cargo_dep("sqlx") else None)
    add("sqlite-knowledge-patch", (f"Cargo dependency `{state.cargo_dep('rusqlite')}`" if state.cargo_dep("rusqlite") else "") or (f"package.json dependency `{state.package_dep('better-sqlite3', 'sqlite3')}`" if state.package_dep("better-sqlite3", "sqlite3") else ""))
    add("postgresql-knowledge-patch", (f"package.json dependency `{state.package_dep('pg', 'postgres', 'knex', 'typeorm')}`" if state.package_dep("pg", "postgres", "knex", "typeorm") else "") or (f"Python dependency `{state.python_dep('psycopg2', 'psycopg', 'asyncpg', 'sqlalchemy')}`" if state.python_dep("psycopg2", "psycopg", "asyncpg", "sqlalchemy") else "") or (f"Cargo dependency `{state.cargo_dep('sqlx', 'diesel', 'tokio-postgres')}`" if state.cargo_dep("sqlx", "diesel", "tokio-postgres") else "") or (f"docker-compose image `{state.docker_image_contains('postgres')}`" if state.docker_image_contains("postgres") else ""))
    add("postgis-knowledge-patch", (f"package.json dependency `{state.package_dep('postgis', 'knex-postgis')}`" if state.package_dep("postgis", "knex-postgis") else "") or (f"Python dependency `{state.python_dep('geoalchemy2', 'geopandas', 'postgis')}`" if state.python_dep("geoalchemy2", "geopandas", "postgis") else "") or (f"docker-compose image `{state.docker_image_contains('postgis')}`" if state.docker_image_contains("postgis") else ""))
    add("go-knowledge-patch", "go.mod" if state.has_file("go.mod") else None)
    add("docker-knowledge-patch", state.has_any_file("Dockerfile", "docker-compose.yml", "docker-compose.yaml"))
    add("podman-knowledge-patch", state.has_any_file("Containerfile", "containers.conf"))
    add("svelte-knowledge-patch", (f"package.json dependency `{state.package_dep('svelte')}`" if state.package_dep("svelte") else "") or (state.has_glob("svelte.config.*") or ""))
    add("tailwind-knowledge-patch", (f"package.json dependency `{state.package_dep('tailwindcss')}`" if state.package_dep("tailwindcss") else "") or (state.has_glob("tailwind.config.*") or ""))
    add("prisma-knowledge-patch", f"package.json dependency `{state.package_dep('prisma', '@prisma/client')}`" if state.package_dep("prisma", "@prisma/client") else None)
    add("drizzle-knowledge-patch", f"package.json dependency `{state.package_dep('drizzle-orm')}`" if state.package_dep("drizzle-orm") else None)
    add("vite-knowledge-patch", (f"package.json dependency `{state.package_dep('vite')}`" if state.package_dep("vite") else "") or (state.has_glob("vite.config.*") or ""))
    add("vitest-knowledge-patch", (f"package.json dependency `{state.package_dep('vitest')}`" if state.package_dep("vitest") else "") or (state.has_glob("vitest.config.*") or ""))
    add("playwright-knowledge-patch", (f"package.json dependency `{state.package_dep('@playwright/test', 'playwright')}`" if state.package_dep("@playwright/test", "playwright") else "") or (state.has_glob("playwright.config.*") or ""))
    add("deno-knowledge-patch", state.has_any_file("deno.json", "deno.jsonc"))
    add("astro-knowledge-patch", (f"package.json dependency `{state.package_dep('astro')}`" if state.package_dep("astro") else "") or (state.has_glob("astro.config.*") or ""))
    add("zig-knowledge-patch", "build.zig" if state.has_file("build.zig") else None)
    add("vercel-ai-sdk-knowledge-patch", (f"package.json dependency `{state.package_dep('ai')}`" if state.package_dep("ai") else "") or (f"package.json dependency `{state.package_dep_prefix('@ai-sdk/')}`" if state.package_dep_prefix("@ai-sdk/") else ""))
    add("supabase-knowledge-patch", (f"package.json dependency `{state.package_dep('@supabase/supabase-js')}`" if state.package_dep("@supabase/supabase-js") else "") or ("supabase/" if state.has_dir("supabase") else ""))
    add("biome-knowledge-patch", (f"package.json dependency `{state.package_dep('@biomejs/biome')}`" if state.package_dep("@biomejs/biome") else "") or (state.has_any_file("biome.json", "biome.jsonc") or ""))
    add("hono-knowledge-patch", f"package.json dependency `{state.package_dep('hono')}`" if state.package_dep("hono") else None)
    add("trpc-knowledge-patch", f"package.json dependency `{state.package_dep('@trpc/server', '@trpc/client')}`" if state.package_dep("@trpc/server", "@trpc/client") else None)
    add("terraform-knowledge-patch", ("terraform/" if state.has_dir("terraform") else "") or (state.has_glob("*.tf") or ""))
    add("nuxt-knowledge-patch", (f"package.json dependency `{state.package_dep('nuxt')}`" if state.package_dep("nuxt") else "") or (state.has_glob("nuxt.config.*") or ""))
    add("vuejs-knowledge-patch", f"package.json dependency `{state.package_dep('vue')}`" if state.package_dep("vue") else None)
    add("solidjs-knowledge-patch", f"package.json dependency `{state.package_dep('solid-js')}`" if state.package_dep("solid-js") else None)
    add("htmx-knowledge-patch", f"package.json dependency `{state.package_dep('htmx.org')}`" if state.package_dep("htmx.org") else None)
    add("angular-knowledge-patch", (f"package.json dependency `{state.package_dep('@angular/core')}`" if state.package_dep("@angular/core") else "") or ("angular.json" if state.has_file("angular.json") else ""))
    add("flutter-knowledge-patch", "pubspec.yaml" if state.file_contains("pubspec.yaml", "flutter:") else None)
    add("swift-knowledge-patch", ("Package.swift" if state.has_file("Package.swift") else "") or (state.has_glob("*.xcodeproj") or ""))
    add("kotlin-knowledge-patch", ("build.gradle.kts" if state.has_file("build.gradle.kts") else "") or ("settings.gradle.kts" if state.has_file("settings.gradle.kts") else ""))
    add("tauri-knowledge-patch", (f"package.json dependency `{state.package_dep('@tauri-apps/api')}`" if state.package_dep("@tauri-apps/api") else "") or ("src-tauri/" if state.has_dir("src-tauri") else ""))
    add("kubernetes-knowledge-patch", ("k8s/" if state.has_dir("k8s") else "") or ("kubernetes/" if state.has_dir("kubernetes") else "") or ("helmfile.yaml" if state.has_file("helmfile.yaml") else "") or ("Chart.yaml" if state.has_file("Chart.yaml") else "") or (state.has_glob("*.k8s.yaml") or ""))
    add("authjs-knowledge-patch", f"package.json dependency `{state.package_dep('next-auth', '@auth/core')}`" if state.package_dep("next-auth", "@auth/core") else None)
    add("better-auth-knowledge-patch", f"package.json dependency `{state.package_dep('better-auth')}`" if state.package_dep("better-auth") else None)
    add("clerk-knowledge-patch", f"package.json dependency `{state.package_dep('@clerk/nextjs', '@clerk/clerk-sdk-node')}`" if state.package_dep("@clerk/nextjs", "@clerk/clerk-sdk-node") else None)
    add("workos-knowledge-patch", f"package.json dependency `{state.package_dep('@workos-inc/node', '@workos-inc/authkit-nextjs')}`" if state.package_dep("@workos-inc/node", "@workos-inc/authkit-nextjs") else None)
    add("zitadel-knowledge-patch", f"package.json dependency `{state.package_dep('@zitadel/client', '@zitadel/react')}`" if state.package_dep("@zitadel/client", "@zitadel/react") else None)
    add("elixir-knowledge-patch", "mix.exs" if state.has_file("mix.exs") else None)
    add("gleam-knowledge-patch", "gleam.toml" if state.has_file("gleam.toml") else None)
    return sorted(detections, key=lambda item: item.name)


def copy_tree(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dest, dirs_exist_ok=True)


def ensure_executable(path: Path) -> None:
    mode = path.stat().st_mode
    path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def load_hooks_config(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"hooks": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    hooks = data.get("hooks")
    if hooks is None:
        data["hooks"] = {}
    elif not isinstance(hooks, dict):
        raise ValueError(f"{path} field `hooks` must be an object")
    return data


def install_session_start_hook(
    *,
    project_root: Path,
    codex_home: Path,
    hook_scope: str,
    source_hook: Path,
    source_guidance_skill: Path,
) -> dict[str, str] | None:
    if hook_scope == "none":
        return None

    if hook_scope == "repo":
        runtime_root = project_root / ".codex" / "knowledge-patch"
        hooks_config_path = project_root / ".codex" / "hooks.json"
        command = "\"$(git rev-parse --show-toplevel)/.codex/knowledge-patch/hooks/session-start\""
    elif hook_scope == "user":
        runtime_root = codex_home / "knowledge-patch"
        hooks_config_path = codex_home / "hooks.json"
        command = shlex.quote(str(runtime_root / "hooks" / "session-start"))
    else:
        raise ValueError(f"unsupported hook scope: {hook_scope}")

    target_hook = runtime_root / "hooks" / "session-start"
    target_skill_dir = runtime_root / "skills" / "using-knowledge-patch"
    target_skill = target_skill_dir / "SKILL.md"

    target_hook.parent.mkdir(parents=True, exist_ok=True)
    target_skill_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_hook, target_hook)
    shutil.copy2(source_guidance_skill, target_skill)
    ensure_executable(target_hook)

    config = load_hooks_config(hooks_config_path)
    hooks = config.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError(f"{hooks_config_path} field `hooks` must be an object")

    session_start = hooks.setdefault("SessionStart", [])
    if not isinstance(session_start, list):
        raise ValueError(f"{hooks_config_path} field `hooks.SessionStart` must be an array")

    wanted_group = {
        "matcher": "startup|resume",
        "hooks": [
            {
                "type": "command",
                "command": command,
                "statusMessage": "Loading knowledge patch guidance",
            }
        ],
    }

    already_present = False
    for group in session_start:
        if not isinstance(group, dict):
            continue
        if group.get("matcher") != "startup|resume":
            continue
        handlers = group.get("hooks")
        if not isinstance(handlers, list):
            continue
        for handler in handlers:
            if isinstance(handler, dict) and handler.get("type") == "command" and handler.get("command") == command:
                already_present = True
                break
        if already_present:
            break

    if not already_present:
        session_start.append(wanted_group)

    hooks_config_path.parent.mkdir(parents=True, exist_ok=True)
    hooks_config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    return {
        "scope": hook_scope,
        "config_path": str(hooks_config_path),
        "runtime_root": str(runtime_root),
        "command": command,
    }


def resolve_local_public_repo(plugin_root: Path, explicit_path: str | None) -> Path | None:
    if explicit_path:
        path = Path(explicit_path).expanduser().resolve()
        if not path.is_dir():
            raise SystemExit(f"--public-repo path does not exist: {path}")
        return path

    env_path = os.environ.get("KP_PUBLIC_REPO")
    if env_path:
        path = Path(env_path).expanduser().resolve()
        if path.is_dir():
            return path

    repo_root = plugin_root.parents[1]
    local_dev_repo = repo_root.parent / "nevaberry-plugins"
    if local_dev_repo.is_dir():
        return local_dev_repo.resolve()

    return None


def clone_public_repo(repo_url: str, ref: str, selected_patches: list[str], workdir: Path) -> Path:
    clone_dir = workdir / "nevaberry-plugins"
    subprocess.run(
        ["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", "--branch", ref, repo_url, str(clone_dir)],
        check=True,
    )
    sparse_paths = [f"plugins/{name}/skills/{name}" for name in selected_patches]
    subprocess.run(
        ["git", "-C", str(clone_dir), "sparse-checkout", "set", *sparse_paths],
        check=True,
    )
    return clone_dir


def emit_result(result: dict[str, object], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(result, indent=2))
        return

    print(f"Project root: {result.get('project_root')}")
    detected = result.get("detected_patches")
    if isinstance(detected, list):
        if detected:
            print("Detected patches:")
            for item in detected:
                if isinstance(item, dict):
                    print(f"  - {item.get('name')}: {item.get('reason')}")
        else:
            print("Detected patches: none")

    installed = result.get("installed_patches")
    if isinstance(installed, list) and installed:
        print("Installed patches:")
        for item in installed:
            print(f"  - {item}")

    hook = result.get("hook")
    if isinstance(hook, dict):
        print(f"Hook config: {hook.get('config_path')}")


def scan_command(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    detections = detect_patches(DetectionState(project_root), PUBLISHED_PATCHES)
    detected_names = {item.name for item in detections}

    result = {
        "project_root": str(project_root),
        "available_patches": sorted(PUBLISHED_PATCHES),
        "detected_patches": [{"name": item.name, "reason": item.reason} for item in detections],
        "manual_only_patches": sorted(PUBLISHED_PATCHES - detected_names),
    }
    emit_result(result, args.format)
    return 0


def install_command(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    plugin_root = Path(__file__).resolve().parents[1]
    codex_home = Path(args.codex_home).expanduser().resolve()

    detected = detect_patches(DetectionState(project_root), PUBLISHED_PATCHES)
    detected_names = [item.name for item in detected]

    selected = list(args.patch or [])
    if args.all_detected:
        for patch_name in detected_names:
            if patch_name not in selected:
                selected.append(patch_name)

    if not selected:
        raise SystemExit("No patches selected. Use --all-detected or pass one or more --patch values.")

    missing = [name for name in selected if name not in PUBLISHED_PATCHES]
    if missing:
        raise SystemExit(f"Unknown patch names: {', '.join(sorted(missing))}")

    public_repo_root = resolve_local_public_repo(plugin_root, args.public_repo)
    temp_dir: tempfile.TemporaryDirectory[str] | None = None

    try:
        if public_repo_root is None:
            temp_dir = tempfile.TemporaryDirectory(prefix="knowledge-patch-public-")
            public_repo_root = clone_public_repo(args.repo_url, args.repo_ref, selected, Path(temp_dir.name))

        skills_dest = codex_home / "skills"
        skills_dest.mkdir(parents=True, exist_ok=True)

        installed: list[str] = []
        for patch_name in selected:
            src = public_repo_root / "plugins" / patch_name / "skills" / patch_name
            if not src.is_dir():
                raise SystemExit(f"Patch source not found in public repo: {src}")
            dest = skills_dest / patch_name
            copy_tree(src, dest)
            installed.append(patch_name)

        hook_result = install_session_start_hook(
            project_root=project_root,
            codex_home=codex_home,
            hook_scope=args.hook_scope,
            source_hook=plugin_root / "hooks" / "session-start",
            source_guidance_skill=plugin_root / "skills" / "using-knowledge-patch" / "SKILL.md",
        )

        result = {
            "project_root": str(project_root),
            "codex_home": str(codex_home),
            "skills_dir": str(skills_dest),
            "installed_patches": installed,
            "hook": hook_result,
            "public_repo": str(public_repo_root),
        }
        emit_result(result, args.format)
        return 0
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="detect matching knowledge patches")
    scan.add_argument("--project-root", default=os.getcwd())
    scan.add_argument("--format", choices=("json", "text"), default="text")
    scan.set_defaults(func=scan_command)

    install = subparsers.add_parser("install", help="install selected knowledge patches")
    install.add_argument("--project-root", default=os.getcwd())
    install.add_argument("--codex-home", default=os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    install.add_argument("--public-repo", help="Local checkout of Nevaberry/nevaberry-plugins for development/testing.")
    install.add_argument("--repo-url", default=DEFAULT_PUBLIC_REPO_URL)
    install.add_argument("--repo-ref", default=DEFAULT_PUBLIC_REPO_REF)
    install.add_argument("--patch", action="append", default=[])
    install.add_argument("--all-detected", action="store_true")
    install.add_argument("--hook-scope", choices=("repo", "user", "none"), default="repo")
    install.add_argument("--format", choices=("json", "text"), default="text")
    install.set_defaults(func=install_command)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
