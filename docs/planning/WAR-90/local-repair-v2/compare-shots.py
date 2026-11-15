"""Independent textual continuity checkpoints (not proof of audience/media)."""
import json,re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
base=json.loads((root/'pilot-D/state.json').read_text())['active']['artifacts']['shot']['proposal']
new=json.loads((root/'pilot-D-local-repair-v2/state.json').read_text())['active']['artifacts']['shot']['proposal']
def sections(t):
 hits=list(re.finditer(r'(?m)^Shot0([1-4])\s*[｜|：:]',t))
 return {f'Shot0{m.group(1)}':t[m.start():(hits[i+1].start() if i+1<len(hits) else len(t))] for i,m in enumerate(hits)}
b,n=sections(base),sections(new)
for k in ('Shot01','Shot02','Shot03','Shot04'):
 print(k,'OLD_LEN',len(b.get(k,'')),'NEW_LEN',len(n.get(k,'')),
       'EXACT',b.get(k)==n.get(k),'OLD_TITLE',b.get(k,'')[:84].replace('\n',' '),'NEW_TITLE',n.get(k,'')[:84].replace('\n',' '))
print('SHOT01_EXACT',b.get('Shot01')==n.get('Shot01'))
out={'old_lengths':{k:len(v) for k,v in b.items()},'new_lengths':{k:len(v) for k,v in n.items()},'exact':{k:b.get(k)==n.get(k) for k in ('Shot01','Shot02','Shot03','Shot04')}}
(Path(__file__).resolve().parent/'shot-diff-check.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
