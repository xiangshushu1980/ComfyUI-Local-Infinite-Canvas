#!/usr/bin/env python3
import ast,json,hashlib,subprocess,pathlib,datetime,sys
ROOT=pathlib.Path('/home/sean/projects/canvas-lab')
BASE=ROOT/'docs/validation/WAR-66/minimal-C-text-v1'
UP=ROOT/'docs/validation/XIA-59-shotplan/upstream/vimax'
BASE.mkdir(parents=True,exist_ok=True)
def get_assignment(file,name):
    tree=ast.parse((UP/file).read_text())
    for x in tree.body:
        if isinstance(x,ast.Assign) and any(isinstance(y,ast.Name) and y.id==name for y in x.targets):
            return ast.literal_eval(x.value)
    raise KeyError(name)
def write_new(name,s):
    path=BASE/name
    if path.exists():raise RuntimeError('refuse overwrite '+name)
    path.write_text(s,encoding='utf-8')
    return path
shots=[
 {'idx':0,'cam_idx':0,'visual_desc':'宽全景，傍晚的小城火车站候车区。立柱靠画面左侧，陈站在左、手持一张车票，许背着小包站在右，两人并肩面向检票口方向。两人短暂沉默后，陈侧头说“到了以后，记得给我发个消息。”许回答“好。”镜头静止，候车区稀疏人群与远处检票口可见。'},
 {'idx':1,'cam_idx':1,'visual_desc':'中近景，陈在画面左侧，半侧面朝右，手中始终握着车票。陈低头看车票，再抬头看向画面右侧的许，说“过年的时候……”，在话语未完时主动停住。镜头固定，焦点在陈的面部与持票的手。'},
 {'idx':2,'cam_idx':0,'visual_desc':'原先双人机位的宽全景，陈仍在立柱旁左侧原地，手里握着车票；许背着小包处于右侧，先朝陈转头，说“你照顾好自己。”陈轻轻点头回应“嗯。”随后许转身面向远处检票口并逐渐走远，陈没有追上去。镜头保持静止，最终两人距离拉开。'}
]
characters='陈: (static) 男，35岁，服装外貌细节未指定; (dynamic) 手里握着车票。\n许: (static) 女，33岁，背小包，服装外貌细节未指定; (dynamic) 最终转身走向检票口。'
schema={'type':'object','properties':{'decompositions':{'type':'array','items':{'type':'object','properties':{'idx':{'type':'integer'},'ff_desc':{'type':'string'},'ff_vis_char_idxs':{'type':'array','items':{'type':'integer'}},'lf_desc':{'type':'string'},'lf_vis_char_idxs':{'type':'array','items':{'type':'integer'}},'motion_desc':{'type':'string'},'variation_type':{'type':'string','enum':['large','medium','small']},'variation_reason':{'type':'string'}},'required':['idx','ff_desc','ff_vis_char_idxs','lf_desc','lf_vis_char_idxs','motion_desc','variation_type','variation_reason'],'additionalProperties':False}}},'required':['decompositions'],'additionalProperties':False}
write_new('fixture-shots.json',json.dumps({'source':'frozen C script, manually authored shot briefs; NOT ViMax storyboard model output','shots':shots,'characters':characters},ensure_ascii=False,indent=2)+'\n')
system=get_assignment('storyboard_artist.py','system_prompt_template_decompose_visual_description')
human=get_assignment('storyboard_artist.py','human_prompt_template_decompose_visual_description')
single_schema=dict(schema['properties']['decompositions']['items'])
single_schema['properties']={k:v for k,v in single_schema['properties'].items() if k!='idx'}
single_schema['required']=[x for x in single_schema['required'] if x!='idx']
# For original per-shot prompt use original template, with a compact schema replacement for parser.get_format_instructions().
prompt_parts=[]
for s in shots:
    sy=system.replace('{format_instructions}',json.dumps(single_schema,ensure_ascii=False))
    hu=human.replace('{visual_desc}',s['visual_desc']).replace('{characters_str}',characters)
    prompt_parts.append({'idx':s['idx'],'system':sy,'human':hu})
write_new('decomposition-messages.json',json.dumps(prompt_parts,ensure_ascii=False,indent=2)+'\n')
full='你将收到 3 次相互独立的原始 ViMax 单镜头拆解调用；每次均包含上游的 SYSTEM 和 HUMAN 消息，按顺序逐个完成，禁止把某一镜的信息作为另一镜的额外上下文。按指定 JSON Schema 仅返回 decompositions 数组，idx 与镜头编号对应。这里的多镜包装与 JSON Schema 是研究调用适配，不属于 ViMax 原版代码；原始 SYSTEM/HUMAN 文本存于 decomposition-messages.json，并逐字内嵌如下。\n\n'
for e in prompt_parts:full+=f'\n===独立调用 {e["idx"]}===\nSYSTEM:\n{e["system"]}\nHUMAN:\n{e["human"]}\n'
write_new('decomposition-request.txt',full)
write_new('decomposition-schema.json',json.dumps(schema,ensure_ascii=False,indent=2))
def run(stage,request,schema):
    out=BASE/(stage+'-raw.txt');log=BASE/(stage+'-events.jsonl');err=BASE/(stage+'-stderr.txt')
    cmd=['codex','exec','-m','gpt-6.1-terra','-c','model_reasoning_effort="medium"','--ephemeral','--ignore-user-config','--ignore-rules','--sandbox','read-only','--skip-git-repo-check','-C',str(BASE),'--json','--output-schema',str(schema),'-o',str(out),'-']
    t=datetime.datetime.now().isoformat()
    p=subprocess.run(cmd,input=request.read_text(),text=True,capture_output=True,timeout=540)
    write_new(stage+'-events.jsonl',p.stdout)
    write_new(stage+'-stderr.txt',p.stderr)
    write_new(stage+'-execution.json',json.dumps({'command':cmd,'start':t,'end':datetime.datetime.now().isoformat(),'returncode':p.returncode,'response_exists':out.exists()},ensure_ascii=False,indent=2))
    if p.returncode:raise RuntimeError(stage+' exit '+str(p.returncode)+' '+p.stderr[-500:])
    parsed=json.loads(out.read_text())
    return parsed
decomp=run('decomposition',BASE/'decomposition-request.txt',BASE/'decomposition-schema.json')
if len(decomp['decompositions'])!=3:raise ValueError('bad number of decompositions')
tree_schema={'type':'object','properties':{'camera_parent_items':{'type':'array','items':{'type':['object','null'],'properties':{'parent_cam_idx':{'type':['integer','null']},'parent_shot_idx':{'type':['integer','null']},'reason':{'type':'string'},'is_parent_fully_covers_child':{'type':['boolean','null']},'missing_info':{'type':['string','null']}},'required':['parent_cam_idx','parent_shot_idx','reason','is_parent_fully_covers_child','missing_info'],'additionalProperties':False}}},'required':['camera_parent_items'],'additionalProperties':False}
camera_seq='<CAMERA_SEQ>\n<CAMERA_0>\nShot 0: '+shots[0]['visual_desc']+'\nShot 2: '+shots[2]['visual_desc']+'\n</CAMERA_0>\n<CAMERA_1>\nShot 1: '+shots[1]['visual_desc']+'\n</CAMERA_1>\n</CAMERA_SEQ>'
tree_sys=get_assignment('camera_image_generator.py','system_prompt_template_select_reference_camera').replace('{format_instructions}',json.dumps(tree_schema,ensure_ascii=False))
tree_human=get_assignment('camera_image_generator.py','human_prompt_template_select_reference_camera').replace('{camera_seq_str}',camera_seq)
# ViMax implementation wraps <CAMERA_SEQ> again in the human template; retain exact.
write_new('camera-tree-messages.json',json.dumps({'system':tree_sys,'human':tree_human},ensure_ascii=False,indent=2)+'\n')
tree_prompt='这是 ViMax 原始 Camera Tree SYSTEM/HUMAN 消息的文本回放。仅返回对应 JSON Schema；不要执行任何工具。镜头是研究者从剧本 C 提炼的输入，并非 ViMax 自动生成的 storyboard。\n\nSYSTEM:\n'+tree_sys+'\nHUMAN:\n'+tree_human
write_new('camera-tree-request.txt',tree_prompt)
write_new('camera-tree-schema.json',json.dumps(tree_schema,ensure_ascii=False,indent=2))
camera=run('camera-tree',BASE/'camera-tree-request.txt',BASE/'camera-tree-schema.json')
assert len(camera['camera_parent_items'])==2
manifest={}
for p in sorted(BASE.iterdir()):
    if p.is_file():
        manifest[p.name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
write_new('sha256-manifest.json',json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'decomp_count':len(decomp['decompositions']),'camera_tree':camera,'manifest_count':len(manifest),'folder':str(BASE)},ensure_ascii=False))
