#!/usr/bin/env python3
"""Pure-data Chat→Canvas read preflight; never issues HTTP, MCP or Canvas writes.

A matching result is NOT write authorization, not a cross-endpoint CAS, and not
cryptographic proof that a rendered Canvas node matches a Director B candidate.
"""
import hashlib
import re

class PreflightBlocked(ValueError):
    pass

def verify(health, state, selection, authority, *, project_id, client_id,
           node_id, expected_shot_id, approved_b_id, source_sha256, shot_sha256):
    def require(test, reason):
        if not test: raise PreflightBlocked(reason)
    require(health.get('ok') is True and health.get('hasCanvas') is True,
            'no connected Canvas state')
    require(health.get('clients') == 1, 'not exactly one Canvas browser client')
    require(health.get('codexBusy') is False, 'Canvas Codex turn busy or unknown')
    require(project_id and client_id and node_id and expected_shot_id, 'explicit project/client/node/shot identity required')
    require(isinstance(approved_b_id,str) and re.fullmatch(r'[0-9a-f]{32}',approved_b_id),
            'valid approved B id is required')
    require(isinstance(source_sha256,str) and re.fullmatch(r'[0-9a-f]{64}',source_sha256),
            'valid source SHA256 is required')
    require(isinstance(shot_sha256,str) and re.fullmatch(r'[0-9a-f]{64}',shot_sha256),
            'valid Shot SHA256 is required')
    require(state.get('projectId') == project_id, 'project ID changed or missing')
    require(state.get('clientId') == client_id, 'Canvas client ID changed or missing')
    nodes = state.get('nodes') or []
    require(sum(n.get('id') == node_id for n in nodes) == 1, 'target node missing or duplicate')
    selected = state.get('selectedNodeIds') or []
    require(selected == [node_id], 'exactly one intended Canvas selection required')
    chosen = (selection or {}).get('nodes') or []
    require(len(chosen)==1 and chosen[0].get('id')==node_id,
            'selected node readback disagrees')
    require(authority.get('pilot_only') is True,
            'expected WAR-90 pilot projection')
    require(authority.get('authority',{}).get('approved_B_id') == approved_b_id,
            'approved B identity changed')
    require(authority.get('source',{}).get('sha256') == source_sha256,
            'source version changed')
    source_text=(authority.get('source') or {}).get('text')
    require(isinstance(source_text,str) and bool(source_text),
            'source full text missing')
    require(hashlib.sha256(source_text.encode('utf-8')).hexdigest()==source_sha256,
            'source text SHA256 does not match full text')
    target=authority.get('target_shot') or {}
    require(target.get('text_sha256') == shot_sha256,
            'target Shot text SHA changed')
    require(target.get('id') == expected_shot_id, 'target Shot ID mismatch')
    require(target.get('text'), 'target Shot full text missing')
    require(hashlib.sha256(target['text'].encode('utf-8')).hexdigest()==shot_sha256,
            'Shot text SHA256 does not match full text')
    require(authority.get('capabilities',{}).get('production_approval') is False,
            'pilot-only approval boundary missing')
    require(authority.get('capabilities',{}).get('write_canvas') is False,
            'view claims write capability unexpectedly')
    return {'provided_identifiers_consistent': True, 'can_write': False,
            'reason': 'No atomic client/project binding or write approval in /api/tools',
            'project_id':project_id, 'client_id':client_id, 'target_node_id':node_id,
            'target_shot_id':expected_shot_id,
            'approved_B_id':approved_b_id,
            'source_sha256':source_sha256,'shot_sha256':shot_sha256,
            'not_verified':[
                'whether selected Canvas Node actually maps to the claimed Director Shot',
                'whether selection and state originate from one atomic client/project snapshot',
                'whether any supplied snapshot is fresh or still current',
                'whether the rendered Canvas node text is the complete approved B source',
                'identity of user authorizing a future mutation',
                'no race after this check (server has no cross-entry CAS)',
                'permissions of native Codex MCP tools']}

if __name__ == '__main__':
    # Designed as a reusable pure function; no CLI takes the Agent access token.
    print('Pure-data only: import verify() with fresh read results; never treat as write permission.')
