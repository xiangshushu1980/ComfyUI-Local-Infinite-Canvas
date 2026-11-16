#!/usr/bin/env python3
"""Offline dry-run of the exact installation/retire script with a mock systemctl.

This does NOT exercise rollback on real Canvas Agent workspace or service.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INSTALLER = ROOT / 'install_pilot_skill.py'
EXPECTED= Path.home()/'.infinite-canvas/codex-workspaces/canvas-agent/.agents/skills/director-skill-v0-candidate'

def check(condition, what):
    if not condition:raise RuntimeError(what)

with tempfile.TemporaryDirectory(prefix='war90-skill-install-test-') as d:
    base=Path(d)
    root=base/'home'
    workspace=root/'.infinite-canvas/codex-workspaces/canvas-agent'
    workspace.mkdir(parents=True)
    (root/'.infinite-canvas/canvas-agent.json').write_text(json.dumps({'workspace':{'workspacePath':str(workspace)}}))
    bindir=base/'bin'
    bindir.mkdir()
    stub=bindir/'systemctl'
    def systemctl(text):
        stub.write_text('#!/bin/sh\necho '+text+'\n')
        stub.chmod(0o755)
    env={**os.environ,'HOME':str(root),'PATH':str(bindir)+':'+os.environ['PATH']}
    def call(action,should_pass):
        r=subprocess.run([sys.executable,str(INSTALLER),action],env=env,capture_output=True,text=True)
        check((r.returncode==0)==should_pass,action+' unexpected status: '+r.stderr[-350:])
        return json.loads(r.stdout) if should_pass else {'error_type':r.stderr.splitlines()[-1].split(':')[0]}
    systemctl('inactive')
    before=call('preflight',True)
    installed=call('install',True)
    verified=call('verify',True)
    blocked=call('install',False)
    target=workspace/'.agents/skills/director-skill-v0-candidate'
    check(target.exists(),'Isolated installed dir absent')
    systemctl('active')
    block_active=call('retire',False)
    check(target.exists(),'Active-service guard did not preserve target')
    systemctl('inactive')
    retired=call('retire',True)
    check(not target.exists(),'Target should no longer be in Skill discovery')
    backup=Path(retired['retired_to_preserved_backup'])
    check(backup.exists() and (backup/'SKILL.md').exists(),'No preserved backup')
    still_ready=call('preflight',True)
    out={'test':'offline installer & reversible retire, mocked systemctl',
         'source_files':len(before['manifest']),
         'install_matches_manifest':installed['installed'] and verified['installed_matches_source'],
         'collision_guard_refused':bool(blocked),
         'active_service_guard_refused':bool(block_active),
         'backup_preserved_and_verified':bool(retired['active_skill_removed_from_discovery']),
         'clean_reinstall_allowed_after_retire':still_ready['ready_for_reversible_install'],
         'did_not_touch_production':True}
    (ROOT/'isolated-install-retire-test-result.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print('ISOLATED_INSTALL_RETIRE',json.dumps(out,ensure_ascii=False))
