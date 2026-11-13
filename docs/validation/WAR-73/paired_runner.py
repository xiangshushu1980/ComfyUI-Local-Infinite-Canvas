#!/usr/bin/env python3
"""WAR-73 minimal text-only A/B Toonflow prompt replay. Never overwrites original evidence."""
import pathlib, hashlib, json, subprocess, datetime, difflib, concurrent.futures, sys
ROOT=pathlib.Path('/home/sean/projects/canvas-lab')
BASE=ROOT/'docs/validation/WAR-73'
UP=ROOT/'docs/validation/WAR-59/toonflow-upstream-v118workflow'
OLD=ROOT/'docs/validation/WAR-61/evidence/raw-package/toonflow-20261107/xia-61-script-C'
RUN=BASE/'paired-text-v1'
RUN.mkdir(exist_ok=False)
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return p.read_text(encoding='utf-8')
def fresh(rel,content):
 p=RUN/rel;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8') as f:f.write(content)
 return p
script=OLD/'script-C.txt'; director=OLD/'director-output.txt'
assert sha(script.read_bytes())=='ba56afb91c117d06ced4089456f5e713435e99cfbf287fd3ee5a5b88ee50153d'
assert sha(director.read_bytes())=='6174646f605b39bcc48b3853a13daf039ecf66a68e4056ec5e0ad2d0d640366e'
d=read(director).rstrip('\n');s=read(script)
rules={rel:read(UP/rel) for rel in ['references/storyboardTable.md','references/knowledge/shotCraft.md']}
# The experiment uses the same source excerpts for both sides, without fabricating a genre decision.
focus={
'A':'本轮导演关注重点：观众关注陈说到“过年的时候……”时主动停住、未能问出口的克制；许的回应按已定剧本和规划保留。',
'B':'本轮导演关注重点：观众关注许已经察觉陈的未尽之言，却选择回避正面回答的瞬间；陈的停顿按已定剧本和规划保留。'}
fresh('frozen-source-manifest.json',json.dumps({
 'script':{'path':str(script),'sha256':sha(script.read_bytes())},
 'director_plan':{'path':str(director),'sha256':sha(director.read_bytes())},
 'rules':{rel:sha((UP/rel).read_bytes()) for rel in rules},
 'upstream_commit':'6086cdffceb704a632eca143dd16cd461a78cdac',
 'execution_kind':'isolated Codex CLI text replay, not Toonflow App or Canvas',
 'historical_C_storyboard_is_NOT_paired_baseline':True},ensure_ascii=False,indent=2)+'\n')
common='''你正在进行 WAR-73 的 Toonflow 原版分镜表隔离文本回放。这不是正式 Toonflow App，缺真实画布节点、素材、已确认类型方法和实时视频模型配置。仅在收到的剧本、导演规划和下列原版分镜规则范围内，依据原版规则输出“场→片段→镜”的完整中文分镜表，并附原规则要求的必要设计说明及问题审阅。绝对不能调用工具、查看本机文件、使用其他 Skill、补造新剧情、确认素材图或者声称画布写入成功。两方案应独立处理，禁止猜测另一个方案的输出。禁止另增实验变量或把当前关注重点视为新剧本事实。严格保留原台词、场景、道具、角色动作及终态。没有确认的叙事类型/资产/风格/模型参数要标“待确认/待模型校验”，不凭空设定。只输出完整结果，不加测试说明。\n\n=== 冻结剧本 ===\n'''+s+'\n=== Toonflow 原版规则（相同完整文字） ===\n'
for rel,body in rules.items(): common+='\n===== '+rel+' =====\n'+body+'\n'
common+='\n=== 从同一个冻结 Director Plan 派生，以下只有一行人工导演关注重点不同 ===\n'
prompts={}
for k,v in focus.items():
 dp=d+'\n\n'+v+'\n'
 fresh(f'{k}/director-plan-derived.txt',dp)
 prompt=common+dp+'\n请根据上述相同规则、相同剧本、此份导演规划独立完成 Storyboard 文本表与审阅。\n'
 prompts[k]=prompt
 fresh(f'{k}/request.txt',prompt)
# Validate only intended A/B difference in the raw requests.
assert prompts['A'].replace(focus['A'],'<FOCUS>')==prompts['B'].replace(focus['B'],'<FOCUS>')
assert read(RUN/'A/director-plan-derived.txt').replace(focus['A'],'<FOCUS>')==read(RUN/'B/director-plan-derived.txt').replace(focus['B'],'<FOCUS>')
fresh('input-diff.txt',''.join(difflib.unified_diff(prompts['A'].splitlines(keepends=True),prompts['B'].splitlines(keepends=True),fromfile='A/request',tofile='B/request')))
def run(k):
 output=RUN/k/'response.txt'
 cmd=['codex','exec','-m','gpt-6.1-terra','-c','model_reasoning_effort="medium"','--ephemeral','--ignore-user-config','--ignore-rules','--sandbox','read-only','--skip-git-repo-check','-C',str(RUN/k),'--json','-o',str(output),'-']
 start=datetime.datetime.now(datetime.timezone.utc).isoformat()
 try:
  proc=subprocess.run(cmd,input=prompts[k],text=True,capture_output=True,timeout=660)
  status={'exit_code':proc.returncode,'timed_out':False}
  stdout,stderr=proc.stdout,proc.stderr
 except subprocess.TimeoutExpired as e:
  status={'exit_code':None,'timed_out':True};stdout=e.stdout.decode(errors='replace') if isinstance(e.stdout,bytes) else (e.stdout or '');stderr=e.stderr.decode(errors='replace') if isinstance(e.stderr,bytes) else (e.stderr or '')
 fresh(f'{k}/events.jsonl',stdout)
 fresh(f'{k}/stderr.txt',stderr)
 status.update({'command':cmd,'started_utc':start,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'response_exists':output.exists(),'request_sha256':sha(prompts[k].encode()),'response_sha256':sha(output.read_bytes()) if output.exists() else None,'response_bytes':output.stat().st_size if output.exists() else None})
 fresh(f'{k}/execution.json',json.dumps(status,ensure_ascii=False,indent=2)+'\n')
 return k,status
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool: results=dict(pool.map(run,focus))
manifest={}
for p in sorted(RUN.rglob('*')):
 if p.is_file() and p.name!='sha256-manifest.json':manifest[str(p.relative_to(RUN))]={'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size}
fresh('sha256-manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'results':results,'file_count':len(manifest),'dir':str(RUN)},ensure_ascii=False))
