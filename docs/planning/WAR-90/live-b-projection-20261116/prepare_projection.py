#!/usr/bin/env python3
"""Build exact 4-node approved-B display payload. NO CANVAS WRITE/API.
This is a content-addressed *projection*, not a canonical DirectorPlan update.
"""
import hashlib,json,sys
from pathlib import Path

ROOT=Path('/home/sean/projects/canvas-lab')
B=ROOT/'docs/planning/WAR-90/pilot-D-local-repair-v2'
EXPECTED_STATE_SHA='23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7'
sys.path.insert(0,str(ROOT/'tools/director-runtime-v0'))
from runtime import Pilot

def payload():
    assert hashlib.sha256((B/'state.json').read_bytes()).hexdigest()==EXPECTED_STATE_SHA,'Approved baseline state changed'
    pack=Pilot(B).review_packet()
    assert pack['review']['pilot_B_accepted'] is True
    assert not pack['review']['pending_shots']
    assert pack['authority']['approved_B_id']=='b7b4fd156b884907b2431b6b1e0d9960'
    shots=pack['shots']
    assert [x['id'] for x in shots]==['Shot01','Shot02','Shot03','Shot04']
    items=[]
    for i,shot in enumerate(shots):
        assert hashlib.sha256(shot['text'].encode('utf-8')).hexdigest()==shot['text_sha256']
        head=('【导演计划 B · 文本展示副本｜非权威版本】\n'
              '影片：D《错过的钥匙》\n'
              '批准 B ID：'+pack['authority']['approved_B_id']+'\n'
              '镜头：'+shot['id']+'\n'
              '镜头原文 SHA256：'+shot['text_sha256']+'\n'
              '来源：Eric Director Runtime（pilot-D-local-repair-v2）\n'
              '仅用于画布审阅，不构成镜头修订或新审批。\n\n')
        items.append({'title':'D《错过的钥匙》 · '+shot['id']+'｜B 展示副本',
                      'text':head+shot['text'],'x':1040+i*700,'y':140,
                      'width':650,'height':850 if i==3 else 740})
    return {'name':'canvas_create_text_nodes',
            'input':{'items':items,'direction':'row'},
            'approved_B_id':pack['authority']['approved_B_id'],
            'state_sha256':EXPECTED_STATE_SHA,
            'shot_sha256':{x['id']:x['text_sha256'] for x in shots},
            'display_only':True}

if __name__=='__main__':
    print(json.dumps(payload(),ensure_ascii=False))
