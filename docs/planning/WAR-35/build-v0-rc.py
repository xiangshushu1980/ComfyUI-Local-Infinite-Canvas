#!/usr/bin/env python3
"""WAR-35 reproducible public v0.1.0 release candidate synthesis (NOT a freeze)."""
import copy
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OLD_VERSION="director-plan/0.0-review"
NEXT_VERSION="director-plan/0.1.0"
RC_ID="urn:canvas-lab:director-plan:0.1.0-rc3"
REVIEW_SCHEMA="director-plan.schema.review-rc3.json"
RC_SCHEMA="director-plan.schema.v0-rc3.json"
PAIRS=(
    ("no-action-beat.example.review-v0.json","no-action-beat.example.v0-rc3.json"),
    ("cross-shot-once.example.review-v0.json","cross-shot-once.example.v0-rc3.json"),
)

def write(name,data):
    (ROOT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def run():
    schema=json.loads((ROOT/REVIEW_SCHEMA).read_text(encoding="utf-8"))
    assert schema["properties"]["contractVersion"]["const"]==OLD_VERSION
    schema["$id"]=RC_ID
    schema["title"]="DirectorPlan public Schema v0.1.0 — RELEASE CANDIDATE 3 (NOT FROZEN)"
    schema["description"]=(
        "RELEASE CANDIDATE ONLY, NOT FROZEN. Public standalone DirectorPlan contract "
        "with P-JCS-1 and D-JCS-1 profile design evidence. Production raw I-JSON input, "
        "cross-object Review semantics, evidence resolution and WAR-52 projection mapping "
        "require implementation/independent sign-off; this is not execution authorization.")
    schema["properties"]["contractVersion"]["const"]=NEXT_VERSION
    write(RC_SCHEMA,schema)
    for old,new in PAIRS:
        data=json.loads((ROOT/old).read_text(encoding="utf-8"))
        assert data["contractVersion"]==OLD_VERSION
        data["contractVersion"]=NEXT_VERSION
        write(new,data)
    print("RC generated with version",NEXT_VERSION,"schema ID",RC_ID,"and 2 independent fixtures")
if __name__=="__main__":
    run()
