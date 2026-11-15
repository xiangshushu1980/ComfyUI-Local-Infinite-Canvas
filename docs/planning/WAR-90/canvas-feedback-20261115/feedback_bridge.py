#!/usr/bin/env python3
"""Experimental WAR-90 Canvas selection -> Director revision handoff.

Transport-only pilot. NOT a WAR-35 schema, user identity proof, approval,
production Canvas integration, model operator, or media command.
"""
from __future__ import annotations

import copy
import difflib
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools/director-runtime-v0"))
from runtime import Pilot, PilotError, shot_sections, digest  # noqa

PILOT_ROOT = ROOT / "docs/planning/WAR-90"
ORIGINAL = PILOT_ROOT / "pilot-D-local-repair-v2"
PREVIEW_FORMAT = "war90-director-preview-only-v0"
FEEDBACK_FORMAT = "war90-canvas-feedback-pilot-v0"
CATALOG_FORMAT = "war90-canvas-shot-selection-v0"


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def approved_packet(workspace=ORIGINAL):
    """Read back approval each time; never trust a cached UI JSON as authority."""
    return Pilot(workspace).review_packet()


def make_catalog(packet, project_id, nodes):
    """Bind real Canvas node IDs to exact approved Shot versions."""
    if packet["format"] != PREVIEW_FORMAT:
        raise ValueError("Unrecognized preview transport")
    if not isinstance(project_id, str) or not project_id:
        raise ValueError("Missing Canvas project ID")
    if len(nodes) < len(packet["shots"]):
        raise ValueError("Not all Shot nodes were created")
    out = []
    seen = set()
    b = packet["authority"]
    for shot in packet["shots"]:
        title = f"WAR-90｜{shot['id']} · B Review"
        matches = [n for n in nodes if n.get("title") == title]
        if len(matches) != 1:
            raise ValueError(f"Missing/duplicate Canvas shot node: {shot['id']}")
        node = matches[0]
        if not node.get("id") or node["id"] in seen:
            raise ValueError("Duplicate or empty Canvas node IDs")
        seen.add(node["id"])
        # Canvas Agent GET_STATE compact transport truncates node content.
        # Match the prefix but NEVER use it as the authoritative Shot text.
        preview = str(node.get("metadata", {}).get("content", ""))
        if shot["id"] not in preview or b["approved_B_id"] not in preview:
            raise ValueError(f"Canvas review node has mismatched preview: {shot['id']}")
        out.append({"id":node["id"], "title":title, "shot_id":shot["id"],
                    "shot_text_sha256":shot["text_sha256"]})
    return {"format":CATALOG_FORMAT, "project_id":project_id,
            "approved_B_id":b["approved_B_id"],
            "approved_B_content_sha256":b["approved_B_content_sha256"],
            "source_sha256":b["source_sha256"], "nodes":out}


def check_catalog(packet, catalog):
    a = packet["authority"]
    for key in ("approved_B_id", "approved_B_content_sha256", "source_sha256"):
        if catalog.get(key) != a[key]:
            raise ValueError(f"Stale Canvas review catalog: {key}")
    if catalog.get("format") != CATALOG_FORMAT:
        raise ValueError("Unknown Canvas review catalog")
    expected = {s["id"]:s["text_sha256"] for s in packet["shots"]}
    entries = catalog.get("nodes")
    if not isinstance(entries, list) or len(entries) != len(expected):
        raise ValueError("Catalog missing/extra Shot nodes")
    if len({x["id"] for x in entries}) != len(expected):
        raise ValueError("Duplicate node ID")
    if set(x["shot_id"] for x in entries) != set(expected):
        raise ValueError("Wrong Shot membership")
    if any(expected[x["shot_id"]] != x["shot_text_sha256"] for x in entries):
        raise ValueError("Shot text changed while Canvas displayed an old version")


def capture_feedback(packet, catalog, canvas_state, selection, instruction,
                     origin="synthetic-test"):
    """Bind selected Canvas node and actual text, with NO forged human approval."""
    check_catalog(packet, catalog)
    if canvas_state.get("projectId") != catalog["project_id"]:
        raise ValueError("Selected Canvas project changed")
    if origin not in ("synthetic-test", "external-user-unverified"):
        raise ValueError("Unsupported feedback provenance")
    if not isinstance(instruction, str) or not instruction.strip():
        raise ValueError("Empty feedback")
    if len(instruction) > 12000:
        raise ValueError("Feedback exceeds pilot text limit")
    selected = selection.get("nodes", [])
    if len(selected) != 1:
        raise ValueError("Select exactly one Shot")
    node = selected[0]
    match = [n for n in catalog["nodes"] if n["id"] == node.get("id")]
    if len(match) != 1 or node.get("title") != match[0]["title"]:
        raise ValueError("Selection is not a bound Shot node")
    # The display may have been manually edited since the catalog was made.
    # The Agent read API truncates long node contents, but its prefix still
    # contains the immutable Shot/B labels of this experimental projection.
    preview = str(node.get("metadata", {}).get("content", ""))
    if match[0]["shot_id"] not in preview or catalog["approved_B_id"] not in preview:
        raise ValueError("Selected Shot display changed since catalog creation")
    a = packet["authority"]
    return {
        "format": FEEDBACK_FORMAT, "status": "revision-request-only",
        "pilot_only": True, "origin": origin,
        "actor_identity_verified": False, "human_B_decision": False,
        "canvas_project_id":catalog["project_id"],
        "canvas_node_id":node["id"],
        "target_shot_id":match[0]["shot_id"],
        "target_shot_sha256":match[0]["shot_text_sha256"],
        "base_B_id":a["approved_B_id"],
        "base_B_content_sha256":a["approved_B_content_sha256"],
        "source_sha256":a["source_sha256"],
        "instruction":instruction,
        "instruction_sha256":digest(instruction.encode("utf-8")),
        "requires_director_candidate_revision":True,
    }


def validate_feedback(packet, feedback):
    a = packet["authority"]
    if feedback.get("format") != FEEDBACK_FORMAT or feedback.get("pilot_only") is not True:
        raise ValueError("Not a pilot Canvas feedback envelope")
    checks = {"base_B_id":a["approved_B_id"],
              "base_B_content_sha256":a["approved_B_content_sha256"],
              "source_sha256":a["source_sha256"]}
    for key, val in checks.items():
        if feedback.get(key) != val:
            raise ValueError(f"Stale revision feedback: {key}")
    sha_by_shot={s["id"]:s["text_sha256"] for s in packet["shots"]}
    target=feedback.get("target_shot_id")
    if target not in sha_by_shot or sha_by_shot[target]!=feedback.get("target_shot_sha256"):
        raise ValueError("Unknown/stale target Shot")
    text=feedback.get("instruction")
    if not isinstance(text,str) or not text.strip() or digest(text.encode())!=feedback.get("instruction_sha256"):
        raise ValueError("Feedback text empty or changed")
    if feedback.get("human_B_decision") is not False:
        raise ValueError("Feedback is not a B approval")


def stage_scope(packet, feedback):
    validate_feedback(packet, feedback)
    a = packet["authority"]
    return (
        "WAR-90 Canvas selected-Shot local revision REQUEST, not a human B approval.\n"
        f"Approved B baseline: {a['approved_B_id']} content={a['approved_B_content_sha256']}.\n"
        f"Source SHA256: {a['source_sha256']}.\n"
        f"Target and only permitted modified Shot: {feedback['target_shot_id']}, "
        f"Shot text SHA256={feedback['target_shot_sha256']}.\n"
        f"User-edit instruction provenance: {feedback['origin']}; "
        f"identity_verified=false; new_B_approved=false.\n"
        f"Exact request text:\n{feedback['instruction']}\n"
        "Do not alter any non-target Shot. Preserve story facts, current approved Intent,"
        " Beat and Blocking, knowledge order, four dialogue lines, only one key, and final "
        "right-hand transfer. If the request needs Blocking/Beat or source changes, report "
        "the upstream requirement and DO NOT pretend the requested change is a valid "
        "Shot-only revision. Do not approve new B yourself. Report unresolved risks.\n"
    )


def clone_for_revision(packet, feedback, destination, source=ORIGINAL):
    """Prepare isolated workspace with exact approval SHA; no model call."""
    validate_feedback(packet, feedback)
    source = Path(source).resolve(strict=True)
    destination = Path(destination).absolute()
    if destination.exists():
        raise ValueError("Revision workspace already exists")
    if destination.parent.resolve() != PILOT_ROOT.resolve():
        raise ValueError("Revision workspace must be directly under WAR-90")
    if not destination.name.startswith("pilot-D-canvas-"):
        raise ValueError("Only explicitly named isolated pilot workspace allowed")
    orig_sha=sha_file(source/"state.json")
    actual=approved_packet(source)
    if actual["authority"] != packet["authority"]:
        raise ValueError("Approved baseline changed before clone")
    shutil.copytree(source,destination,symlinks=False)
    try:
        if sha_file(destination/"state.json") != orig_sha or sha_file(source/"state.json") != orig_sha:
            raise ValueError("Copied/current pilot changed during clone")
        Pilot(destination).check(Pilot(destination).load())
    except BaseException:
        shutil.rmtree(destination)
        raise
    return {"workspace":str(destination), "original_state_sha256":orig_sha,
            "state_sha256":sha_file(destination/"state.json"),
            "stage":"shot", "mode":"resume",
            "target":feedback["target_shot_id"],
            "scope":stage_scope(packet, feedback),
            "fresh_model_call_performed":False,
            "B_approval_recorded":False}


def compare_local_revision(packet, feedback, destination):
    """Read-only comparison of candidate after separate Director Resume call."""
    validate_feedback(packet,feedback)
    state=Pilot(destination).load()
    Pilot(destination).check(state)
    active=state.get("active")
    if not active or active["id"]==feedback["base_B_id"]:
        raise ValueError("No new local candidate")
    if active["stage"]!="shot" or state["phase"]!="awaiting-human-B":
        raise ValueError("Candidate must await real B review")
    if state.get("pilot_B") is not None:
        raise ValueError("New candidate was incorrectly approved")
    baseline=packet["stages"]["shot"]["text"]
    current=active["artifacts"]["shot"]["proposal"]
    ids=[shot["id"] for shot in packet["shots"]]
    old=shot_sections(baseline,ids)
    new=shot_sections(current,ids)
    changed=[i for i in ids if old[i]!=new[i]]
    if changed!=[feedback["target_shot_id"]]:
        raise ValueError(f"Changed content outside requested Shot: {changed}")
    t=feedback["target_shot_id"]
    diff="\n".join(difflib.unified_diff(old[t].splitlines(),new[t].splitlines(),
                                      fromfile=f"approved-B/{t}",tofile=f"candidate/{t}",
                                      lineterm=""))
    return {"format":"war90-canvas-diff-preview-v0",
            "base_B_id":feedback["base_B_id"],
            "base_B_content_sha256":feedback["base_B_content_sha256"],
            "candidate_id":active["id"],
            "candidate_content_sha256":active["content_sha256"],
            "changed_shots":changed,
            "pending_review_shots":state["pending_shots"],
            "diff":diff,"new_shot_text":new[t],
            "status":"awaiting-real-user-B-review",
            "pilot_B_approved":False,
            "formal_WAR35_approval":False,
            "media_verified":False}


def fake_director_for_transport_only(packet, feedback, workspace):
    """DEMO ONLY: demonstrates propagation, never a professional Director result."""
    validate_feedback(packet,feedback)
    before=Pilot(workspace).load()
    if before["active"]["id"]!=feedback["base_B_id"] or not before["pilot_B"]:
        raise ValueError("Fake demonstration must start at approved B clone")
    art=before["active"]["artifacts"]["shot"]
    ids=art["shot_ids"]
    parts=shot_sections(art["proposal"],ids)
    t=feedback["target_shot_id"]
    synthetic_label="【自动化测试占位行：非导演建议、非用户批准、非真实模型输出。】\n"
    full=art["proposal"]
    end=ids.index(t)+1
    if end<len(ids):
        offset=full.index(parts[ids[end]])
        modified=full[:offset]+synthetic_label+full[offset:]
    else:
        modified=full+"\n"+synthetic_label
    output={"proposal":modified,
            "reason":"synthetic transport-only example, not Director judgement",
            "changes":"synthetic line inserted in selected Shot only",
            "impact":"selected Shot and adjacent review candidates",
            "unknown":["geometry","media","audience"],
            "next_action":"Requires a genuine professional model result and real user B review",
            "handoff":True, "changed_targets":[t], "shot_ids":ids,
            "hard_conflicts":[],"upstream_change":False}
    pilot=Pilot(workspace)
    def generate(_prompt,_run_dir):
        return json.dumps(output,ensure_ascii=False), "SYNTHETIC-NO-CODEX-SESSION"
    meta=pilot.run("shot",mode="resume",scope=stage_scope(packet,feedback),
                   targets=[t],generator=generate)
    if meta["generator"]!="fake" or meta["status"]!="candidate-saved":
        raise ValueError("Fake demonstration did not produce isolated candidate")
    diff=compare_local_revision(packet,feedback,workspace)
    diff["generator_provenance"]="synthetic-fake-NOT-a-real-Director-run"
    return diff
