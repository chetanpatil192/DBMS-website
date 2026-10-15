#!/usr/bin/env python3
"""Environment and tooling verification diagnostic script for Commerce Insights."""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

ROOT_DIR = Path(__file__).resolve().parent.parent


def check_python() -> Tuple[bool, str]:
    """Validates Python version meets requirement (>= 3.11)."""
    major, minor, micro = sys.version_info[:3]
    version_str = f"{major}.{minor}.{micro}"
    passed = (major > 3) or (major == 3 and minor >= 11)
    if passed:
        return True, f"Python {version_str} (>= 3.11 required)"
    return False, f"Python {version_str} detected (Minimum 3.11 required)"


def check_binary(binary_name: str, min_desc: str = "") -> Tuple[bool, str]:
    """Checks if a binary is discoverable in PATH and extracts its version."""
    path = shutil.which(binary_name)
    if not path:
        return False, f"{binary_name} not found in system PATH"

    try:
        result = subprocess.run(
            [binary_name, "--version"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        first_line = (result.stdout.strip() or result.stderr.strip()).split("\n")[0]
        desc = f"{first_line} ({path})"
        if min_desc:
            desc += f" [{min_desc}]"
        return True, desc
    except Exception as exc:
        return True, f"Found at {path} (version check failed: {exc})"


def check_project_files() -> List[Tuple[bool, str]]:
    """Validates presence of core architectural directories and configuration files."""
    required_paths = [
        ("Directory", "backend/app/main.py"),
        ("Directory", "backend/app/core/config.py"),
        ("Directory", "backend/app/db/client.py"),
        ("Directory", "backend/requirements.txt"),
        ("Directory", "frontend/package.json"),
        ("Directory", "frontend/src/App.tsx"),
        ("Directory", "frontend/vite.config.ts"),
        ("Documentation", "README.md"),
        ("Documentation", "docs/architecture.md"),
        ("Documentation", "docs/api-conventions.md"),
        ("Documentation", "docs/database-guidelines.md"),
        ("Environment", ".env.example"),
        ("Configuration", ".gitignore"),
    ]

    results = []
    for category, rel_path in required_paths:
        target = ROOT_DIR / rel_path
        if target.exists():
            results.append((True, f"[{category}] {rel_path} present"))
        else:
            results.append((False, f"[{category}] {rel_path} MISSING"))
    return results


def main() -> int:
    """Runs all environment checks and prints a formatted diagnostic report."""
    print("=" * 70)
    print("  Commerce Insights - Environment & Foundation Diagnostics")
    print("=" * 70)

    all_passed = True

    # 1. Python Environment Check
    py_ok, py_msg = check_python()
    status_icon = "✔ PASS" if py_ok else "✖ FAIL"
    print(f"\n[Runtime Environment]")
    print(f"  {status_icon} : {py_msg}")
    if not py_ok:
        all_passed = False

    # 2. Node & Build Tooling
    node_ok, node_msg = check_binary("node", ">= 20 recommended")
    npm_ok, npm_msg = check_binary("npm")
    print(f"  {'✔ PASS' if node_ok else '✖ WARN'} : {node_msg}")
    print(f"  {'✔ PASS' if npm_ok else '✖ WARN'} : {npm_msg}")

    # 3. MongoDB Binaries
    print(f"\n[Database Tooling]")
    mongod_ok, mongod_msg = check_binary("mongod", ">= 6.0 required")
    mongosh_ok, mongosh_msg = check_binary("mongosh", "MongoDB Shell")
    print(f"  {'✔ PASS' if mongod_ok else '✖ WARN'} : {mongod_msg}")
    print(f"  {'✔ PASS' if mongosh_ok else '✖ WARN'} : {mongosh_msg}")

    # 4. Project Structure Verification
    print(f"\n[Project Structure & Architectural Layout]")
    file_checks = check_project_files()
    for passed, msg in file_checks:
        icon = "✔ PASS" if passed else "✖ FAIL"
        print(f"  {icon} : {msg}")
        if not passed:
            all_passed = False

    # 5. Summary
    print("\n" + "=" * 70)
    if all_passed:
        print("  RESULT: Foundation files and core prerequisites verified successfully.")
        print("=" * 70)
        return 0
    else:
        print("  RESULT: One or more critical files or prerequisites are missing.")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
