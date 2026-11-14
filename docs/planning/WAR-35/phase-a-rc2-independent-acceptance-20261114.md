# WAR-35 阶段 A · RC2 最终独立验收

2026-11-14，Eric。**A Not Accepted。** 上轮要求的 Fact → 实际剧本来源证明已修复。剩余一项局部 Check 阻塞：注册表固定了规格文本和来源策略，但没有约束部分规格允许的方法和目标。因此在缺少该规格所需依赖时，仍能得到两版相同的有效格式 /3 指纹。暂缓正式验收 A 和进入 B。WAR-35 整体保持 Not ready。

## 基线及重跑范围

Linear WAR-35 为 In Progress，当前正文记载 RC2 等待独立复核、B 尚未启动。Eric 本地读取最新 linear-task-collab、上一轮独立报告和实现方说明；旧报告 SHA-256 e788395e75325b07c7214cd9e35eb26a1e5d9200ec10d68aa96d60b2feb34109 与其引用一致。独立 git archive 提取 cb7e8fd730a6cfda78a77e30220d68a70b8ad376 和 edcbd82b269c86ce03e7dc746a47b430ed826bcf。RC1 与 RC2 的两份对应 Plan 示例数据相同，继承入口分别使用各自登记的 Intent A 规格版本。独立 Fact 对照在两侧使用完全相同的 fact-script/1 文本。

原版 24 项来源测试在旧归档 10/24、新归档 24/24，逐行 observed/expected 与已提交报告完全相同。该报告 SHA-256 为 6b2b5fcff6f16b7dea5d8a868d2d44fe42f9ed540e5dad4819ee45328fccb0bc。RC2 原阶段 A 专项 10/10。本轮未重跑 B/C 或全套冻结评审。以下为另行构造并运行的探针，包含完整本地 A 继承入口 valid_case(case, False)；该参数仅关闭整 Plan 指针检查。

## 来源与继承验收矩阵

| 同输入变体 | cb7e8fd | edcbd82 |
| --- | --- | --- |
| 目标 Fact 无来源边，原文改为相反内容，binding/snapshot 同步更新真实 SHA | Fact 摘要相同，A 承接 | 两侧均无摘要，A 拒绝 |
| 同上，新修订删除唯一快照 | Fact 摘要相同，A 承接 | 两侧均无摘要，A 拒绝 |
| 另造有真实快照的 AUX 来源与有来源的 AUX Fact，同时传两项 dependencyRefs 和两个 collectionPaths | 有摘要，A 承接 | 无摘要，A 拒绝 |
| 目标自身正确关联，原文改变 / 缺失 / 不变 | 依次为不同摘要 / 无新摘要 / 相同摘要；仅不变可承接 | 同样三种结果 |
| 普通 fact-local/1，检查无来源 Fact 的 statement 是否非空 | 可产生局部摘要 | 可产生局部摘要，换此规格尝试满足 Intent A 被拒 |
| 同一 Intent 有直接 Source、有效 Fact、Constraint；Constraint 下有多个分支，其中一个 Fact 无来源 | 可承接 | 无摘要且拒绝；补齐该 Fact 自身来源后允许承接 |
| 仅直接 Source basis | 可承接 | 有效字节存在时可承接 |
| 目标指向不存在的 Source、两份同 ID binding，或原文被篡改但保留声明 SHA | 拒绝 | 三种情况都无摘要，均拒绝承接 |

RC2 对来源型规格先从每个目标检查各分支；其后通用闭包按 (sourceId, contentSha256) 匹配快照并对实际 UTF-8 内容算 SHA。单纯拥有一份同包的正确快照无法补足空目标边。正负对照核验的是关系与字节，没有以哈希判定文字叙述真假。未注册版本、已知版本与伪装文本、fact-script/1 错指 Subject 均得到无摘要；普通局部规格也不能替换 Intent A 规格完成批准。

## 唯一阻塞：登记规格未充分限定局部 Check 的方法和目标

verify-d-jcs1.py 的 CHECK_SPECS 有八个互异版本键，每个键映射一个确切文本与 sourcePolicy。source_policy 对 closure-only/1 直接返回；payload 依据调用方提供的 method 决定是否要求 mediaBindings。两处合用使以下形状合法的 Check 产生摘要。

| 最小反例 | RC2 实测 | 所缺的必要依赖 |
| --- | --- | --- |
| 用 Cross Shot，targetRefs=[intent:I-CROSS]，版本 media-v1，精确登记文本 “Actual output has visible landing”，空额外依赖；省略 executionTarget、evidenceBindings，只把 method 从 media 改为 text | 正确报 media 时无摘要。改报 text 后为 7310bdc969f99a14b814b8f80a06ac0f0bb5af6b86159e51472c0d5ab2461dc3。换 revisionId 后相同，pass/valid 及 inheritance 记录均通过 RC2 结构校验 | 该具体规格检查实际成片的落地表现；verify-media-check.py 的同版同文本正例明确按 media 处理。实际受检产物及证据绑定完全缺席 |
| fact-local/1，精确文本 “Fact statement is nonempty”，method=text，仅将目标改为 subject:CREEK | 两版同为 1403876b0680ca18b479bb2626c7ca0aa5ffc0e22b05404932047fd288191672，pass/valid 和 inheritance 结构合法 | 目标是没有 statement 的 Subject，闭包没有被检查的 Fact |

两例都通过了实际 D-JCS 计算器，不只是 JSON Schema 宽松。两个规格提交给完整 Intent A 入口都返回 False；没有观察到它们取得 Intent A 批准。阻塞位于 A 自己的局部证据边界：调用方可以为一个明确需要成片或 Fact 的已登记规格提供错误类型，再把计算出的真实摘要记录为 pass。即使没有 gate 消费它，这种摘要也不能作为“依赖完整”的基础。

**最小修正与验收**：在受信规格定义中限定该规格允许的方法与目标种类，或用等效的局部规则，在产摘要前核对。media-v1 改报 text、fact-local/1 指向 Subject 应无摘要；原 method=media 的证据要求及合法无来源 Fact 的普通文本检查应继续通过。保留已有来源与完整 A 继承反例。变更规格语义时复核版本和 Golden 的兼容边界。无需规定整门 A/B 的最低覆盖或引入真实媒体 resolver。

## 版本与独立 Golden

- RC1、RC2 Schema ID 分别以 0.1.0-rc1、0.1.0-rc2 结尾。检查 Check 与 inheritance 定义均只接受相应的 /2 或 /3。用真实 /2 摘要改贴 /3、仅保留旧 Check、仅保留旧 inheritance、修改规格版本和文本却沿用旧摘要，完整 A 入口全部拒绝。
- 独立按两个示例实际的 Intent → Fact → Source 构造完整 D payload，不调用研究计算器的 payload/normalized，用 Node JCS 编码并以 SHA-256 校验。手工 payload 明确包含 checkSpec.sourcePolicy；匹配 RC2 固定值，单独改变策略字段会改变摘要。P payload 同时对照两次提交的已存 Golden。

| 示例 | P-JCS-1（两个候选相同） | RC2 D-JCS-1 /3 |
| --- | --- | --- |
| No Action | c3a7e1b938fb16aedb0f3e28c6693223c80d3cab4c9a450adfe896778b33ef0e | 25f9b12c58afbedd19ceaf392ae311447b3ec615c1e99ed386370193b79cc590 |
| Cross Shot | 8b163c5db47ef392da2181b3801fef051eb63a0012f773021d434c036df261ac | 5f7f678e225ea6e992b45156f2dbfa5d9125cec12bd4c72c44077a95fa139142 |

## 可复跑证据

在 Eric 仓库根目录执行。将下方 Python 保存为临时目录的 independent.py。复制旧版没有的专项脚本只发生在旧归档副本。旧版运行该专项退出 1，对应已预期的 14 项失败。raw 输出中 null 表示没有指纹；它与实际 SHA 分开记录。

```bash
audit=$(mktemp -d)
for rev in cb7e8fd edcbd82; do
  mkdir "$audit/$rev"
  git archive "$rev" docs/planning/WAR-35 | tar -x -C "$audit/$rev"
done
cp "$audit/edcbd82/docs/planning/WAR-35/verify-fact-source-proof.py" "$audit/cb7e8fd/docs/planning/WAR-35/"
for rev in cb7e8fd edcbd82; do
  (cd "$audit/$rev/docs/planning/WAR-35" && python3 verify-fact-source-proof.py)
  (cd "$audit/$rev/docs/planning/WAR-35" && python3 "$audit/independent.py")
done
(cd "$audit/edcbd82/docs/planning/WAR-35" && python3 verify-phase-a.py)
```

```python
from pathlib import Path
from copy import deepcopy
import ast, hashlib, json, runpy, subprocess
from jsonschema import Draft202012Validator as Validator
root=Path.cwd()
def read(name): return json.loads((root/name).read_bytes())
phase=runpy.run_path(str(root/'verify-phase-a.py'))
g=phase['gates']
digest=g['dep_sha']
module=digest.__globals__
old=module['RULE'].endswith('/2')
rc='rc1' if old else 'rc2'
schema=read('director-plan.schema.v0-'+rc+'.json')
validate=Validator(schema).validate
p=read('cross-shot-once.example.v0-'+rc+'.json')
def spec(version,text,*targets,**kwargs):
    return dict(g['spec'],checkSpecVersion=version,checkSpec=text,targetRefs=list(targets),**kwargs)
f=spec('fact-script/1','Target Facts agree with the supplied script text','fact:F-ONCE')
local=spec('fact-local/1','Fact statement is nonempty','fact:F-ONCE')
intent=g['spec']
def h(pkg,s):
    validate(pkg)
    return digest(pkg,s)
def pair(pkg):
    q=deepcopy(pkg);q['plan']['revisionId']='R3'
    return q
path=root/'verify-fact-source-proof.py'
env=dict(g=g)
tree=ast.parse(path.read_text())
exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='carry'],type_ignores=[]),'carry','exec'),env)
def carry(pkg,q,s=intent):return env['carry'](pkg,q,s)
def show(k,x):print(k,json.dumps(x,ensure_ascii=False))
q=deepcopy(p);q['plan']['storyBasis']['facts'][0]['sourceRefs']=[]
def opposite(doc):
    t='狐狸留在近岸，没有跳过小溪。';sha=hashlib.sha256(t.encode()).hexdigest()
    doc['sourceSnapshots'][0].update(text=t,contentSha256=sha)
    doc['plan']['storyBasis']['sources'][0]['contentSha256']=sha
for label,x in [('orphan',q),('linked',p)]:
    for mode in ('same','opposite','missing'):
        y=pair(x)
        if mode=='opposite':opposite(y)
        if mode=='missing':del y['sourceSnapshots']
        show(label+' '+mode,[h(x,f),h(y,f),carry(x,y)])
foreign=deepcopy(q)
src=foreign['plan']['storyBasis']['sources'][0]
foreign['plan']['storyBasis']['sources'].append(dict(src,sourceId='source:AUX'))
foreign['sourceSnapshots'].append(dict(foreign['sourceSnapshots'][0],sourceId='source:AUX'))
foreign['plan']['storyBasis']['facts'].append(dict(p['plan']['storyBasis']['facts'][0],id='AUX',sourceRefs=['source:AUX']))
extra=dict(dependencyRefs=['source:AUX','fact:AUX'],collectionPaths=['/storyBasis/sources','/storyBasis/facts/1/sourceRefs'])
show('unrelated source fact paths',[h(foreign,dict(f,**extra)),carry(foreign,pair(foreign),dict(intent,**extra))])
for label,refs in [('missing',['source:LOST']),('duplicate',['source:S-FOX']),('tampered',['source:S-FOX'])]:
    x=deepcopy(p);x['plan']['storyBasis']['facts'][0]['sourceRefs']=refs
    if label=='duplicate':x['plan']['storyBasis']['sources']*=2
    if label=='tampered':x['sourceSnapshots'][0]['text']+='!'
    show(label,[h(x,f),carry(x,pair(x))])
mix=deepcopy(foreign)
mix['plan']['storyBasis']['constraints']=[dict(id='C',statement='basis',sourceRefs=['fact:F-ONCE','fact:AUX','source:AUX'])]
mix['plan']['intents'][0]['basisRefs']=['source:AUX','fact:AUX','constraint:C']
show('mixed orphan',[h(mix,intent),carry(mix,pair(mix))])
mix['plan']['storyBasis']['facts'][0]['sourceRefs']=['source:S-FOX']
show('mixed linked',[h(mix,intent),carry(mix,pair(mix))])
mix['plan']['intents'][0]['basisRefs']=['source:AUX']
show('direct',[h(mix,intent),carry(mix,pair(mix))])
show('local ordinary',[h(q,local),carry(q,pair(q),local)])
if old: exit()
for label,s in [('spoof',dict(f,checkSpecVersion='fact-local/1')),('unknown',dict(f,checkSpecVersion='??')),('script wrong target',dict(f,targetRefs=['subject:CREEK'])),('local wrong target',dict(local,targetRefs=['subject:CREEK'])),('media as text',spec('media-v1','Actual output has visible landing','intent:I-CROSS')),('media as media',spec('media-v1','Actual output has visible landing','intent:I-CROSS',method='media'))]:
    a=h(p,s)
    check=dict(g['c1'],**s,target=g['plan_target'](p),dependencyFingerprintSha256=a or '0'*64)
    obj=dict(p,reviewLedger={'checks':[check]})
    show(label,[a,Validator(schema).is_valid(obj),h(pair(p),s),carry(p,pair(p),s)])
# Use the same Plan data and old canonical calculator to create genuine /2 claims.
oldroot=root.parents[3]/'cb7e8fd/docs/planning/WAR-35'
og=runpy.run_path(str(oldroot/'verify-phase-a.py'))['gates']
for label in ('old Check','old inheritance','retagged digest','spec changed'):
    case=g['make_case']()
    prior,current=case['checks'][:2]
    if label=='old Check':prior['dependencyHashRule']=og['inherit']['dependencyHashRule']
    if label=='old inheritance':case['inheritances'][0]['dependencyHashRule']=og['inherit']['dependencyHashRule']
    if label=='retagged digest':
        val=og['dep_sha'](case['packages'][0],intent)
        for record in (prior,current,case['inheritances'][0]):record['dependencyFingerprintSha256']=val
    if label=='spec changed':current.update(checkSpecVersion=local['checkSpecVersion'],checkSpec=local['checkSpec'])
    case['sealed'][prior['id']]=g['seal'](prior)
    show(label,g['valid_case'](case,False))
# Independent hand-built closure for the two golden fixtures, separate Node JCS.
def nodehash(x):
    data=subprocess.check_output(['node','/home/sean/.local/share/canvas-lab-jcs/verify_js.mjs'],input=json.dumps(x).encode())
    return hashlib.sha256(data).hexdigest()
gold=read('v0-rc2-golden.report.json')['golden']
for fn,row in gold.items():
    pkg=read(fn);plan=pkg['plan'];it=plan['intents'][0];fact=plan['storyBasis']['facts'][0];src=plan['storyBasis']['sources'][0]
    objs={'intent:'+it['id']:it,'fact:'+fact['id']:fact,src['sourceId']:src}
    assert it['basisRefs']==['fact:'+fact['id']] and fact['sourceRefs']==[src['sourceId']]
    assert hashlib.sha256(pkg['sourceSnapshots'][0]['text'].encode()).hexdigest()==src['contentSha256']
    payload=dict(profile='war35-dep-jcs8785-sha256/3',contractVersion=pkg['contractVersion'],planIdentity={k:plan[k] for k in ['planId','sceneId']},checkSpec=dict(text='v0 Intent A dependency test',version='intentA/v1',method='text',sourcePolicy='intent-basis-fact-sources/1'),scope=dict(targetRefs=['intent:'+it['id']],dependencyRefs=[],collectionPaths=[]),resolvedObjects=[dict(ref=k,value=objs[k]) for k in sorted(objs)],collections=[])
    psha=nodehash(dict(contractVersion=pkg['contractVersion'],plan=plan));dsha=nodehash(payload)
    oldrow=json.loads((oldroot/'v0-rc1-golden.report.json').read_text())['golden'][fn.replace('rc2','rc1')]
    assert row['sha256']==psha==oldrow['sha256'] and row['candidateIntentDependencySha256']==dsha
    payload['checkSpec']['sourcePolicy']='closure-only/1'
    show(fn,[psha,dsha,nodehash(payload)!=dsha])
reg=module['CHECK_SPECS']
tree=ast.parse((root/'verify-d-jcs1.py').read_text())
keys=next(x.value.keys for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(k,ast.Name) and k.id=='CHECK_SPECS' for k in x.targets))
assert len(keys)==len(reg)==len(set(k.value for k in keys))==8
show('registry identities',len(keys))
for part in ('check','inheritance'):
    base=g['c1'] if part=='check' else g['inherit']
    for suffix in ('rc1','rc2'):
        s=read('director-plan.schema.v0-'+suffix+'.json')
        validate_record=Validator({'$defs':s['$defs'],'$ref':'#/$defs/'+part}).is_valid
        show(part+' '+s['$id'],[validate_record(dict(base,dependencyHashRule='war35-dep-jcs8785-sha256/'+v)) for v in ('2','3')])
for name,s in [('media-v1',spec('media-v1','Actual output has visible landing','intent:I-CROSS')),('fact-local/1',dict(local,targetRefs=['subject:CREEK']))]:
    q=pair(p)
    s1=dict(g['c1'],**s,target=g['plan_target'](p),dependencyFingerprintSha256=h(p,s))
    s2=dict(s1,id='C-NEW',target=g['plan_target'](q),dependencyFingerprintSha256=h(q,s))
    inh=dict(g['inherit'],fromCheckId=s1['id'],intoCheckId=s2['id'],intoTarget=s2['target'],dependencyFingerprintSha256=s1['dependencyFingerprintSha256'])
    validate(dict(p,reviewLedger={'checks':[s1]}))
    validate(dict(q,reviewLedger={'checks':[s2],'inheritances':[inh]}))
    show('local pass plus inheritance shapes '+name,s1['dependencyFingerprintSha256']==s2['dependencyFingerprintSha256'])
```

### cb7e8fd 独立探针输出

```text
orphan same ["3c0f6592bad84d1436b17629af91a9e1f76ea83849985262424f806283e55958", "3c0f6592bad84d1436b17629af91a9e1f76ea83849985262424f806283e55958", true]
orphan opposite ["3c0f6592bad84d1436b17629af91a9e1f76ea83849985262424f806283e55958", "3c0f6592bad84d1436b17629af91a9e1f76ea83849985262424f806283e55958", true]
orphan missing ["3c0f6592bad84d1436b17629af91a9e1f76ea83849985262424f806283e55958", "3c0f6592bad84d1436b17629af91a9e1f76ea83849985262424f806283e55958", true]
linked same ["8c52fbce46273777852659f400c7fd95a5901786de563903996171edf5ac0403", "8c52fbce46273777852659f400c7fd95a5901786de563903996171edf5ac0403", true]
linked opposite ["8c52fbce46273777852659f400c7fd95a5901786de563903996171edf5ac0403", "6f3af06d292552142393839060f6babf0b16a2b193089a4c4b950e3d6198fcb6", false]
linked missing ["8c52fbce46273777852659f400c7fd95a5901786de563903996171edf5ac0403", null, false]
unrelated source fact paths ["836ad37604b596b22706ce4a6ddfbcf966d0e5aa3bbb687b7152c0e4b9716962", true]
missing [null, false]
duplicate [null, false]
tampered [null, false]
mixed orphan ["01ec63f6c8e4d5edd23c27d98be4fc8a0293bbaf58005baa76c9332be27cebc6", true]
mixed linked ["637ea1c0d0f2daf92dc5136d2c73fab939b0757c2231e519ee0cb17b8aa78fa0", true]
direct ["aa0facedbea22527a8628048ecc7ab4bd34312e378fd1fec4109ebfd3ab7fabe", true]
local ordinary ["57d534b366691d6b6f329e2f5a17db6a7bbc8d781a27caaeac91cb3b14ea5d4c", false]
```

### edcbd82 独立探针输出

```text
orphan same [null, null, false]
orphan opposite [null, null, false]
orphan missing [null, null, false]
linked same ["f14443641b3486a635869b4e089e893f66b52cbe30d9353edfd758ce61d7e02c", "f14443641b3486a635869b4e089e893f66b52cbe30d9353edfd758ce61d7e02c", true]
linked opposite ["f14443641b3486a635869b4e089e893f66b52cbe30d9353edfd758ce61d7e02c", "2db97482fe3c81b88e80ac459bcd29320ebab3b1a081fbed46cbe41bb930cd94", false]
linked missing ["f14443641b3486a635869b4e089e893f66b52cbe30d9353edfd758ce61d7e02c", null, false]
unrelated source fact paths [null, false]
missing [null, false]
duplicate [null, false]
tampered [null, false]
mixed orphan [null, false]
mixed linked ["ad366fef3b88ae683893b5ef6192919e75f3cf00ba857afc1c394a185b041736", true]
direct ["28cc8b78b5aa57001bf5c31026d945dc6994f69c9c6b8bd178ea6e3376b3a8a9", true]
local ordinary ["6d92eae209a090f4825faf171988f1868f5d88666701da071ebd1145797ffa45", false]
spoof [null, true, null, false]
unknown [null, true, null, false]
script wrong target [null, true, null, false]
local wrong target ["1403876b0680ca18b479bb2626c7ca0aa5ffc0e22b05404932047fd288191672", true, "1403876b0680ca18b479bb2626c7ca0aa5ffc0e22b05404932047fd288191672", false]
media as text ["7310bdc969f99a14b814b8f80a06ac0f0bb5af6b86159e51472c0d5ab2461dc3", true, "7310bdc969f99a14b814b8f80a06ac0f0bb5af6b86159e51472c0d5ab2461dc3", false]
media as media [null, false, null, false]
old Check false
old inheritance false
retagged digest false
spec changed false
no-action-beat.example.v0-rc2.json ["c3a7e1b938fb16aedb0f3e28c6693223c80d3cab4c9a450adfe896778b33ef0e", "25f9b12c58afbedd19ceaf392ae311447b3ec615c1e99ed386370193b79cc590", true]
cross-shot-once.example.v0-rc2.json ["8b163c5db47ef392da2181b3801fef051eb63a0012f773021d434c036df261ac", "5f7f678e225ea6e992b45156f2dbfa5d9125cec12bd4c72c44077a95fa139142", true]
registry identities 8
check urn:canvas-lab:director-plan:0.1.0-rc1 [true, false]
check urn:canvas-lab:director-plan:0.1.0-rc2 [false, true]
inheritance urn:canvas-lab:director-plan:0.1.0-rc1 [true, false]
inheritance urn:canvas-lab:director-plan:0.1.0-rc2 [false, true]
local pass plus inheritance shapes media-v1 true
local pass plus inheritance shapes fact-local/1 true
```
