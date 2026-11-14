# WAR-35 · DirectorPlan 0.1.0 RC1 最终独立冻结复核

2026-11-14，Eric。**Not ready。暂缓正式冻结 director-plan/0.1.0。** 版本命名可以保留。建议接受仅对无风险、无条件 approved Intent A 承接的政策；现有判定不能证明整门 A 仍适用。下列公共契约问题需要在发布前收口。

## 审阅基线与可重复结果

分支 `war-35-schema-freeze-review-20261114`，依次核对 `f8a288b → 20b6029 → 754105b → f904099 → cbfc75d`。Linear 当前 Issue 为 Backlog，当前讨论根及 RC1 回复与本地 §23–27 对应。上轮独立报告针对 review-v0，本报告使用 RC1。核对正文、RC1 Schema、Golden 报告 SHA-256 分别为 `7a55b4c575aefb2d9b19acfc4b169acb679011487da7cf4d282122e8a507412f`、`f20930d39615abb12bf80c2e9b4ba84bfb257389a52ecaa151913b5e16238c13`、`d86278d7da954d158e591bedb35e2c6f1adf131668c96778ffa23416eac2bb03`。

从该提交 git archive 到临时目录，执行 §27.4 的生成器及六个验证器。D-JCS 14、D-Schema 9、Media 20、Decision 37、Raw 34、RC 23，共 137 项通过。旧 JCS 验证器仅将其硬编码仓库路径指向副本后复跑，21 例及附加入口检查通过。对照归档原件校验全部 JSON，生成结果逐字节相同。专项脚本多使用 review-v0；下方 Decision 反例另将临时夹具和 Schema 指向 RC1 后复验，保留同一判定函数。

| RC1 fixture | P-JCS 长度 | P-JCS-1 SHA-256 | D-JCS-1 SHA-256（报告中指定的文本 Intent Check） |
| --- | ---: | --- | --- |
| no-action-beat | 794 | `c3a7e1b938fb16aedb0f3e28c6693223c80d3cab4c9a450adfe896778b33ef0e` | `a04aeb2dc8f601b5ae21d22cb23166819e127b5670d2edbf69afb29ff22b6711` |
| cross-shot-once | 2679 | `8b163c5db47ef392da2181b3801fef051eb63a0012f773021d434c036df261ac` | `5de00b76a687852101095144a4d849c3797a39d71ad45a3f25cb5acc277ce74f` |

另按这两例的 Intent → Fact → Source 手工构造 canonical payload，以 Eric 的 Node JCS 计算，两列摘要均与归档值一致。只验证了这两种具体输入。RC1 的 contractVersion 为 director-plan/0.1.0，Schema ID 为 urn:canvas-lab:director-plan:0.1.0-rc1。P/D 都绑定 contractVersion，发布时单改 Schema ID 不参与两种哈希。

## Blocking 1 · D-JCS 会漏掉真实依赖，也会改写业务数据的语义顺序

定位 §23.2–23.4，`verify-d-jcs1.py` 的 normalized、collection、payload。下列成对的 RC1 Package 都通过 Draft 2020-12。

| RC1 Cross Shot 变体 | 实测 | 安全预期 |
| --- | --- | --- |
| target 为 subject:CREEK，collectionPaths 含 /intents/0/basisRefs，修改所指 F-ONCE 的 statement | 两次均为 `9a346624efaa5bd77ef47e7fe6450a33fb7ea21be3241965a0e4ff4553fd571e` | 本路径的值是 typed-ref 数组，必须继续遍历 Fact 与 Source，内容变化即失效 |
| 同 target，collectionPaths 为 /storyBasis/sources，删除唯一 sourceSnapshots，且没有 locator | 仍得原摘要 `b348a4a8949d6d847afeaac185528fe4f76d7c39f734b985e3394abde1d18600` | 对依赖实际来源的检查应 unresolved，不产摘要、不继承 |
| target 为 delta:D-LAND，把 after.value 设为业务对象，内含 subjectRefs 数组；交换其中 FOX/CREEK 次序 | 两次均为 `3250a073ac73484360602da2af1677e8d64c22dc1cac7b82e59661b0fd08d4fe` | known.value 允许任意 JSON。业务数组保序，不能因键名碰巧相同而当作引用集合 |

修正与验收：按 Schema 位置遍历，解析 Pointer 后保留所选位置的类型，区分 typed-ref 数组、来源条目和不透明 JSON。列清集合顺序与引用集合归一化优先级，包括直接指向引用数组的情形。验证直接/间接路径的一致性、丢失来源及 StateValue 同名字段；检查依赖同键 baseline、全体成员或逆向关系时，由版本化规格明确所需集合，不能证明完整则禁止承接。整 Plan fallback 也须验证所需外部来源。

## Blocking 2 · 单个 Check 通过可以冒充整门 A 或 B 完成

定位 §21.3、§25.2–25.3，`verify-decision-gates.py` 第 77–93、110–114 行。测试映射只证明某段规格文字/版本归哪个 gate，未证明目标、方法、必须覆盖的成员或最低检查集合。

- R3 添加 I-NEW，creativeGoal 为“隐去落地”，保留旧 I-CROSS 的 Check 映射并重新计算全部 PlanTarget。A carry 仍为 True。可继承 I-CROSS 的局部 Check；I-NEW 没有被审阅，整门不能随它获批。
- 保留 Shot B 的规格与版本，把唯一 B Check 目标换成 subject:CREEK 并重算其真实 D-JCS；approvedPlan 判定 True。单独把同版规格的方法由 text 改为 geometry_proxy 并重算也为 True。
- 两代 A Check 同为 human，却引用不同 evidenceRefs，仍可承接。非 media 的摘要没有纳入该外部证据，映射也不校验同一不可变证据。只要 human/proxy 结论依赖外部观测，这一路径就缺证明。

修正与验收：为每个可审批 gate 明确必需 Check、版本、方法、目标类型、成员覆盖与依赖规则。A 绑定所有待批准 Intent 的当前集合，B 证明所有必审 Shot/判据已覆盖；新增成员强制补审。对依赖外部证据的非媒体 Check 要求同一可验证绑定或禁用自动承接。保留“仅加无关 Shot 可以承接 A”的正例。

## Blocking 3 · 风险与 Decision 的当前有效性可被绕过

定位 §25.3、P10，`verify-decision-gates.py` 的 risk_valid、decide、check_current。

- 给当前 Shot 放入 status=open 的 hard_conflict，为其真实内容重新封存，B Decision 的 acceptedRisks 留空。approvedPlan 判定 **True**。风险版本和 SHA 都正确；校验只遍历申请人引用的风险，省略风险即绕过。建议从目标/作用域解析所有当前适用风险及有效版本，再比对 Decision；不可解析时拒绝有效批准。加入“省略”“已关闭旧版＋新开放版”“另一作用域无关风险”用例。
- 对同一当前 target、同 gate 再加入不同 ID 的 reviewed/rejected Decision，旧 approvedPlan 仍为 True。复现证明现有指针会采信旧肯定记录；仅凭数组顺序无法断定哪条是最新授权。明确唯一有效决定或可验证的取代规则；相互矛盾且无法判定时返回未决。
- B Decision 单独携带一个 executionTarget，所引用 Check 没有该投影目标，整 Plan 指针仍有效。需明确执行限定的批准能否表示整 Plan；建议整 Plan 指针只接收明确为 Plan 范围的 Decision，执行范围独立验证。

## Blocking 4 · A carry-forward 没有证明直接父修订

定位 §25.2 及 `verify-decision-gates.py` 第 80、120 行。前后 target 对象只比较整体是否不同。把两个不同内容都命名为 R2，分别绑定其真实 Plan SHA，仍接受继承。另一反例插入 R-intermediate，并在 R3 的 candidate 明记 basedOnRevisionId=R-intermediate；让 R3 从 R2 跳过父版承接，仍返回 True。

建议强制同一 planId 下 revisionId 唯一且绑定不可变内容，从可信历史解析直接父 PlanTarget；源必须等于该父、两端 revisionId 必须不同。若没有可验证的父边则重新 reviewed。应覆盖同 ID 异内容、跨分支、跳版与合法连续承接，不能根据 revision 字符串排序推断父子。

## Blocking 5 · Raw I-JSON 接受的 Package 不能读回自己的规范输出

定位 §26.2、`raw_ijson_gate.py` 的 _binary64_number。将 RC1 Cross Shot 中第一个 estimatedSeconds 的原始 token 改为 `9007199254740991.9`。精确输入非整数，现有 gate 放行；解析为 binary64 的 `9007199254740992.0`，整个 Package 通过 RC1 Schema；JCS 输出整数 token `9007199254740992`，同一 gate 再次读入抛 RawIJsonError。这也可在任意 JSON 的 StateValue 中触发。普通小数舍入符合已有策略，阻塞点是接收域对规范化不封闭。

建议保留现有精确整数约束，同时检验转换后的 binary64，若规范输出会变成超安全范围整数即拒绝；明确负号对称与边界舍入，补“接受 → JCS → 重新接受且再规范化字节相同”测试。另测 `0e999999999999999999999`，数学值为零却抛 decimal.InvalidOperation；极端非零指数也可漏出此异常。资源上限若需要应明确，入口错误应统一，此极端输入单独不构成冻结阻塞。

## 非阻塞事项、Media 与跨层边界

- Media Check 形状及声明内容参与哈希的设计可保留。已复跑 20 项，缺执行目标/证据、同 evidenceRef 冲突、媒体/条件/投影摘要改变等均有对应检查。当前套件只绑定自报 SHA；其 pass 正例甚至使用占位 Plan/D 摘要。建议用几个固定字节补 resolver 语义反例，分别交换 unitRef、projectionRevision、projectionHashRule、证据归属及必要条件，验证无法解析时只允许 unknown/not_checked。实际媒体 pass 要求具体投影规则可解析、真实字节复算且来自所声明执行目标。§24 已给出该边界，生产 resolver 或真实视频不作为本轮设计冻结门槛。
- `verify-v0-rc.py` 计算并覆盖报告，未断言已提交的 P/D 固定值；两个实现一致且都改变仍可显示全绿。本次通过外部固定原件逐字节比较，候选 Golden 本身已复现。发布回归应读只读 Golden 比较，生成与验收分开。Decision 研究夹具新增 S-ADDED 时复制 S02 的 completionDeltaRef，若作为全 Plan 正例还会触犯 P07；该套件只验证局部门控。
- §23 的 scope 按集合归一化，Decision 映射脚本却按列表原序比对（第 134 行），合法重排可导致额外复审。另外同一个 verified_check 对所有 media 均返回 False；“禁止自动媒体承接”的专项不能用来证明新 reviewed B 能接纳实测媒体。应分别测试。
- WAR-52 design-0.2 路径相对 de755b5 无差异，投影 Schema 只有局部 phase_key，尚缺公共 phase 映射和可互认的投影 hash profile。公共 Plan、两份独立 Golden 及 text A/B 审阅都可在没有投影时定义。可将映射留给 adapter/sidecar 或新投影版本；需要该投影的 media Check 在 profile 未解析时不能通过。独立公共冻结可不等待 WAR-52；跨层无损转换与 H3 执行仍无验收结论。

## 冻结前的判定条件

保留 v0 的保守 Intent A 政策。先修正公共 profile 及 gate 有效性定义，用上述反例证伪旧路径，同时保留安全继承、合法有条件批准、无 Action Beat 和跨 Shot 完成一次等正例。复核通过后再确认正式 ID、固定 Golden、发布。无需建立新审批树、实现完整生产校验器或运行 GPU。此次只交付本报告，未提交 Git。

## 可复跑的反例

下列 Python 在 Eric 的临时归档副本中执行。工作目录为该副本的 docs/planning/WAR-35，使用系统 python3 并将 Eric 的 canvas-lab-jcs/venv/lib/python3.12/site-packages 加入 PYTHONPATH。代码读取研究算法定义，避开模块底部写报告的测试入口。Decision 用例在 make_case 的合成历史上评估，不代表生产服务接受了这些请求。


```python
from pathlib import Path
from copy import deepcopy as cp
import sys,json,hashlib,subprocess
from jsonschema import Draft202012Validator as V
R=Path.cwd()
sys.path.insert(0,str(R))
from raw_ijson_gate import parse_raw_ijson as parse
import rfc8785
def read(n):return json.loads((R/n).read_bytes())
def prefix(n,cut):
 e={'__file__':str(R/n)}
 source=(R/n).read_text().split(cut)[0]
 if n=='verify-decision-gates.py':
  source=source.replace('director-plan.schema.review-v0.json','director-plan.schema.v0-rc1.json').replace('cross-shot-once.example.review-v0.json").read_text()', 'cross-shot-once.example.v0-rc1.json").read_text()')
 exec(source,e);return e
d=prefix('verify-d-jcs1.py','fox=load(')
g=prefix('verify-decision-gates.py','tests=[]')
rc=read('cross-shot-once.example.v0-rc1.json');v=V(read('director-plan.schema.v0-rc1.json'))
def rule(**k):return dict(g['spec'],**k)
def compare(title,x,y,s):
 assert v.is_valid(x) and v.is_valid(y)
 a,b=(d['digest'](z,s) for z in (x,y));print(title,'same',a==b,'digest',a,b)
p=cp(rc);p['plan']['storyBasis']['facts'][0]['statement']+='!'
compare('direct ref collection',rc,p,rule(targetRefs=['subject:CREEK'],collectionPaths=['/intents/0/basisRefs']))
p=cp(rc);p.pop('sourceSnapshots')
compare('source collection unavailable',rc,p,rule(targetRefs=['subject:CREEK'],collectionPaths=['/storyBasis/sources']))
p=cp(rc);q=cp(rc)
for doc,values in [(p,['subject:FOX','subject:CREEK']),(q,['subject:CREEK','subject:FOX'])]:
 doc['plan']['state']['deltas'][0]['after']['value']={'subjectRefs':values}
compare('opaque state array order',p,q,rule(targetRefs=['delta:D-LAND']))
def gate(label,edit):
 c=g['make_case']();edit(c);print(label,g['valid_case'](c,True))
def conflict(c):
 r=c['risks'][0];r['kind']='hard_conflict';c['sealedRisks'][(r['id'],r['riskVersionId'])]=g['seal'](r)
gate('unlisted hard conflict',conflict)
def skip(c):
 mid=cp(c['packages'][0]);mid['plan']['revisionId']='R-intermediate';c['packages'].insert(1,mid)
 c['packages'][-1]['revisionControl']={'candidates':[{'revisionId':'R3','basedOnRevisionId':'R-intermediate','actualChangedPaths':['/shots']}]}
gate('skip recorded parent',skip)
def rebind(c):
 p=c['packages'][-1];before=c['approvedPlan']['target'];p['plan']['revisionId']=c['packages'][0]['plan']['revisionId'];after=g['plan_target'](p)
 def walk(x):
  if isinstance(x,dict):
   for k,y in list(x.items()):
    if y==before:x[k]=cp(after)
    else:walk(y)
  elif isinstance(x,list):
   for y in x:walk(y)
 walk(c);r=c['risks'][0];c['sealedRisks'][(r['id'],r['riskVersionId'])]=g['seal'](r)
gate('same revision different content',rebind)
def swap(c):
 check=c['checks'][-1];check['targetRefs']=['subject:CREEK'];check['dependencyFingerprintSha256']=d['digest'](c['packages'][-1],check)
gate('B spec checks only creek',swap)
def swapmethod(c):
 check=c['checks'][-1];check['method']='geometry_proxy';check['dependencyFingerprintSha256']=d['digest'](c['packages'][-1],check)
gate('B method changed',swapmethod)
def change_evidence(c):
 for ch in c['checks'][:2]:ch['method']='human';ch['evidenceRefs']=['review:'+ch['id']];ch['dependencyFingerprintSha256']=d['digest'](c['packages'][c['checks'].index(ch)],ch)
 c['inheritances'][0]['dependencyFingerprintSha256']=c['checks'][0]['dependencyFingerprintSha256'];c['sealed']['C-A1']=g['seal'](c['checks'][0])
gate('different human evidence',change_evidence)
for tok in [b'9007199254740991.9',b'1e99999999999999999999',b'0e999999999999999999999']:
 try:
  val=parse(tok); canonical=rfc8785.dumps(val);print('raw',tok,val,canonical);parse(canonical)
 except Exception as ex:print('rejected',type(ex).__name__)
raw=(R/'cross-shot-once.example.v0-rc1.json').read_bytes().replace(b'"estimatedSeconds": 4',b'"estimatedSeconds": 9007199254740991.9',1)
x=parse(raw);print('numeric package Schema',v.is_valid(x))
try:parse(rfc8785.dumps(x))
except Exception as e:print('package reimport',type(e).__name__)
def later(c):
 c['decisions'].append(dict(c['decisions'][-1],id='D-B3',verdict='rejected'))
gate('same-target unresolved decision conflict',later)
def projection(c):
 c['decisions'][-1]['executionTarget']={'unitRef':'UNIT-01','projectionRevision':'PR1','projectionContentSha256':'a'*64,'projectionHashRule':'war52-projection-test/1'}
gate('point at execution-scoped B',projection)
for name,row in read('v0-rc1-golden.report.json')['golden'].items():
 doc=read(name);p=doc['plan'];intent=p['intents'][0]
 lookup={'intent:'+intent['id']:intent}
 for fref in intent['basisRefs']:
  f=next(x for x in p['storyBasis']['facts'] if 'fact:'+x['id']==fref);lookup[fref]=f
  for sr in f['sourceRefs']:
   lookup[sr]=next(x for x in p['storyBasis']['sources'] if x['sourceId']==sr)
 obj=dict(profile='war35-dep-jcs8785-sha256/1',contractVersion=doc['contractVersion'],planIdentity={k:p[k] for k in ('planId','sceneId')},checkSpec=dict(text='v0 Intent A dependency test',version='intentA/v0',method='text'),scope=dict(targetRefs=['intent:'+intent['id']],dependencyRefs=[],collectionPaths=[]),resolvedObjects=[dict(ref=k,value=lookup[k]) for k in sorted(lookup)],collections=[])
 for payload,expected in ((obj,row['candidateIntentDependencySha256']),({k:doc[k] for k in ('contractVersion','plan')},row['sha256'])):
  out=subprocess.check_output(['node','/home/sean/.local/share/canvas-lab-jcs/verify_js.mjs'],input=json.dumps(payload).encode()); assert hashlib.sha256(out).hexdigest()==expected
 print('independent fixture D and P match',name)
def newintent(c):
 pkg=c['packages'][-1]; old=cp(g['plan_target'](pkg))
 intent=cp(pkg['plan']['intents'][0]); intent.update(id='I-NEW',creativeGoal='隐去落地');pkg['plan']['intents'].append(intent)
 new=g['plan_target'](pkg)
 def walk(x):
  if isinstance(x,dict):
   for k,y in list(x.items()):
    if y==old:x[k]=cp(new)
    else:walk(y)
  if isinstance(x,list):
   for y in x:walk(y)
 walk(c);r=c['risks'][0];c['sealedRisks'][(r['id'],r['riskVersionId'])]=g['seal'](r)
gate('new intent outside A coverage',newintent)
```
