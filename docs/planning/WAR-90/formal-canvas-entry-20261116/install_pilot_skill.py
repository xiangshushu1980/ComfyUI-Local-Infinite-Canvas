#!/usr/bin/env python3
"""WAR-90 internal pilot install/check/reversible retire, no Canvas or model calls.

Only copy the previously validated unchanged seven-file candidate into the
real workspace configured for Canvas Agent. Rollback retains the package in
a quarantined folder outside the discovery tree; never delete user files.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/home/sean/projects/canvas-lab")
SOURCE = ROOT / "docs/planning/WAR-89/director-skill-v0-candidate"
CONFIG = Path.home() / ".infinite-canvas/canvas-agent.json"
EXPECTED_WORKSPACE = Path.home() / ".infinite-canvas/codex-workspaces/canvas-agent"
EXPECTED = {
    "SKILL.md": "3eee7d6f3c3032fc43e97b86a9606f8ae77943fa377aa2f56e2770c2b76e8676",
    "references/knowledge-index.md": "4d8edcb664659d78f897aa7baa8c1f275a57b5ff128ab433c95745b32a5e2519",
    "references/review-method.md": "72b23f163fe1fdea6a547d5b47f39392ba0b9b63b814a7a285db4a7df0e88e8e",
    "stages/beat.md": "6e81d45db1d0249cf33a200135f0ab790a49b65d92c7d036b0e253ac978121a1",
    "stages/blocking.md": "2663d5acc282d636400539aecc643871c26c12867c5d480d9c02793ad45c5563",
    "stages/intent.md": "ac07ecb95cbd511888911a0f85aa08f5fee2824cbf8e23749ef0d6ffec065a38",
    "stages/shot-plan.md": "fa0c7d4cc39fdf6b5df9c8a0e3e9b0ee6eafa921142b5a5f07efcdc8cf989476",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assert_manifest(folder: Path):
    assert folder.is_dir() and not folder.is_symlink(), f"Unexpected directory: {folder}"
    entries = sorted(p for p in folder.rglob("*") if p.is_file() or p.is_symlink())
    actual = {str(p.relative_to(folder)): digest(p) for p in entries if p.is_file() and not p.is_symlink()}
    assert not any(p.is_symlink() for p in entries), "Symlink not allowed"
    assert actual == EXPECTED, f"7-file manifest changed: expected {len(EXPECTED)}, received {len(actual)}"
    for file in folder.rglob("*.md"):
        txt = file.read_text("utf-8")
        for dest in re.findall(r"\]\(([^)]+)\)", txt):
            if dest.startswith(("http:", "https:", "#")):
                continue
            resolved = (file.parent / dest.split("#", 1)[0]).resolve()
            assert resolved.is_file() and resolved.is_relative_to(folder.resolve()), f"Broken relative reference: {file} -> {dest}"
    return actual


def workspace():
    assert CONFIG.is_file(), "Missing Canvas Agent config"
    cfg = json.loads(CONFIG.read_text("utf-8"))
    path = Path(cfg.get("workspace", {}).get("workspacePath", "")).resolve()
    assert path == EXPECTED_WORKSPACE.resolve(), "Canvas Agent workspace differs from previously audited workspace"
    assert path.is_dir(), "Canvas workspace does not exist"
    return path


def guard_service_stopped():
    for name in ("canvas-lab-agent.service",):
        check = subprocess.run(["systemctl", "--user", "is-active", name],
                               capture_output=True, text=True)
        assert check.stdout.strip() != "active", f"Refusing mutation while {name} is active"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["preflight", "install", "verify", "retire"])
    args = parser.parse_args()
    work = workspace()
    target = work / ".agents" / "skills" / "director-skill-v0-candidate"
    source_sha = assert_manifest(SOURCE)
    output = {
        "purpose": "internal pilot only, not WAR-89 knowledge/license signoff",
        "action": args.action,
        "workspace": str(work),
        "skill_name": "director-skill-v0-candidate",
        "target": str(target),
        "source": str(SOURCE),
        "manifest": source_sha,
        "original_source_unchanged": True,
        "no_canvas_data_modified": True,
    }
    if args.action == "preflight":
        assert not target.exists() and not target.is_symlink(), "Skill already exists; do not overwrite"
        guard_service_stopped()
        output["ready_for_reversible_install"] = True
    elif args.action == "install":
        guard_service_stopped()
        assert not target.exists() and not target.is_symlink(), "Skill already exists; do not overwrite"
        target.parent.mkdir(parents=True, exist_ok=True)
        stage = Path(tempfile.mkdtemp(prefix=".director-pilot-stage-", dir=target.parent))
        try:
            # The temporary directory is created inside target.parent but
            # is not recognized by the SkillStore's valid-name check.
            for rel in EXPECTED:
                output_path = stage / rel
                output_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(SOURCE / rel, output_path)
            assert_manifest(stage)
            assert not target.exists(), "Target appeared during staging"
            os.rename(stage, target)
        finally:
            if stage.exists():
                shutil.rmtree(stage)
        assert_manifest(target)
        output["installed"] = True
    elif args.action == "verify":
        assert_manifest(target)
        output["installed_matches_source"] = True
    else:
        guard_service_stopped()
        assert_manifest(target)
        destroot = Path.home() / ".infinite-canvas" / "skill-rollback"
        destroot.mkdir(parents=True, exist_ok=True)
        name = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-war90-director-pilot"
        dest = destroot / name
        assert not dest.exists()
        os.rename(target, dest)
        assert_manifest(dest)
        output["retired_to_preserved_backup"] = str(dest)
        output["active_skill_removed_from_discovery"] = True
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
