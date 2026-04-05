#!/usr/bin/env bash
#
# claude-memory-symlink.sh
#
# Creates a symlink so that .claude/memory/ in the project root points to
# ~/.claude/projects/{encoded-repo-path}/memory/
#
# This lets you edit memory files from the project tree while Claude Code
# reads/writes them from its system directory — same files, two paths.
#
# Usage: run from anywhere inside a git repo.

set -euo pipefail

# Portable readlink -f (works on macOS without coreutils)
resolve_path() {
    local target="$1"
    if [ -d "$target" ]; then
        (cd "$target" && pwd -P)
    elif [ -e "$target" ]; then
        local dir
        dir="$(cd "$(dirname "$target")" && pwd -P)"
        echo "$dir/$(basename "$target")"
    else
        echo "$target"
    fi
}

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
    echo "Usage: claude-memory-symlink.sh"
    echo ""
    echo "Creates a symlink so .claude/memory/ in your project root points to"
    echo "Claude Code's system memory directory."
    echo ""
    echo "Run from anywhere inside a git repository."
    exit 0
fi

# Find repo root
repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" || {
    echo "ERROR: not inside a git repository."
    echo "Run this from inside a git repo."
    exit 1
}

# Claude Code encodes the repo path by replacing / with -
encoded="$(echo "$repo_root" | tr '/' '-')"
system_dir="$HOME/.claude/projects/${encoded}/memory"
project_dir="$repo_root/.claude/memory"

echo "[1/3] Checking system memory directory..."

if [ ! -d "$system_dir" ]; then
    echo "  Creating: $system_dir"
    mkdir -p "$system_dir"
else
    echo "  Exists: $system_dir"
fi

echo "[2/3] Checking project symlink..."

# Already a symlink pointing to the right place
if [ -L "$project_dir" ]; then
    current_target="$(resolve_path "$project_dir")"
    expected_target="$(resolve_path "$system_dir")"
    if [ "$current_target" = "$expected_target" ]; then
        echo "  Symlink already exists and is correct."
        echo "  $project_dir -> $system_dir"
        echo ""
        echo "Done. Nothing to do."
        exit 0
    else
        echo "  Symlink exists but points to wrong target: $current_target"
        echo "  Removing and re-creating..."
        rm "$project_dir"
    fi
fi

# If .claude/memory/ is a real directory, merge its contents into system dir
if [ -d "$project_dir" ]; then
    echo "  Found existing directory at $project_dir"
    echo "  Moving files to system directory..."
    for f in "$project_dir"/*; do
        [ -e "$f" ] || continue
        basename="$(basename "$f")"
        if [ -e "$system_dir/$basename" ]; then
            echo "    SKIP (already exists in system dir): $basename"
        else
            echo "    Moving: $basename"
            mv "$f" "$system_dir/"
        fi
    done
    rmdir "$project_dir" 2>/dev/null || {
        echo ""
        echo "ERROR: could not remove $project_dir"
        echo "Some files remain because they already exist in the system directory."
        echo "Resolve the duplicates manually, then re-run this command."
        exit 1
    }
fi

echo "[3/3] Creating symlink..."

mkdir -p "$repo_root/.claude"
ln -s "$system_dir" "$project_dir"

echo "  $project_dir -> $system_dir"
echo ""
echo "Done. Memory files are now accessible from your project tree."
ls -la "$project_dir"/
