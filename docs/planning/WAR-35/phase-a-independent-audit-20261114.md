# WAR-35 阶段 A 定向独立复核 · 2026-11-14

**A Not Accepted。** 原 Blocking 1 的三个反例均已修复，human/proxy 的研究路径也已关闭未经验证的继承。仍有一个阻塞：当检查需要对照剧本，而所依赖 Fact 的来源链为空时，局部检查仍可产生可继承摘要。暂缓把 A 作为 B 的可信基础。WAR-35 整体维持 Not ready。

## 基线与方法

Eric，分支 `war-35-schema-freeze-review-20261114`。Linear 当前状态 In Progress，正文记录实现方阶段 A 通过并建议进入 B。本报告给出独立复核判断。已核对当前 Skill、Issue、当前讨论、旧独立报告及阶段 A 证据。将 `f323e15603d309838211cd7c89cfb4f82e01f3d6` 和 `cb7e8fd730a6cfda78a77e30220d68a70b8ad376` 分别用 git archive 提取到临时目录，运行相同探针；新提交原版 verify-phase-a.py 十个测试方法全部通过。旧报告 SHA-256 为 `074963c73eba638565a8de994e30b66cebd968b02994c967df0b912de8fd4d00`，实现方阶段报告为 `c7a0f18327269fff25612c3b5fc03a2ecb4306efbde2ce4e68213275662a5c14`。137/137 是实现方此前的全套回归记录，本轮复跑 A 专项，没有重审 B、C。

## 原 Blocking 1 回放

| 输入（RC1 Cross Shot，两侧过 Schema） | 旧 /1 | 新 /2 |
| --- | --- | --- |
| 直接选 /intents/0/basisRefs，修改所指 Fact | 相同，命中旧报告原摘要 | da1fdb10… → b700cdb7… |
| 选 /storyBasis/sources，删除唯一快照 | 相同，命中旧报告原摘要 | 2c78d6b1… → unresolved |
| 在 Delta.after.value 的业务对象内交换 subjectRefs 数组次序 | 相同，命中旧报告原摘要 | 4640e80a… → 2489f59e… |

专项还覆盖直接选 Beat.actionRefs、从 Plan 根到达未引用来源、合法引用集合重排、业务 JSON 的伪引用键。复核另测重复 binding、重复精确匹配快照、仅 locator、文本与 SHA 不匹配，对有来源边的 Intent 都返回 unresolved。完整摘要在文末。

## 阻塞 · 需要来源的 Fact 可以在来源链为空时被承接

用原 RC1 狐狸示例构造两个修订。R2 保留“狐狸只跳一次并在对岸落地”的 F-ONCE 与原始文本，但将该 Fact 的 sourceRefs 置为 []。R3 保留同一 Fact、Intent 和引用关系，把实际文本改为“狐狸留在近岸，没有跳过小溪。”并同步更新 binding 与 snapshot 的正确 SHA。另一 R3 变体删除唯一快照且无 locator。以上 Package 均通过当前 Schema。

1. 对局部文本 Check “F-ONCE agrees with the supplied script text”，target 为 fact:F-ONCE。三种输入都产生 `c48d4ad4c59dc1d5defa6660db423344a787943aed187459f08717b91bbb1736`。这项检查明确依赖实际剧本，不能用未证来源的事实陈述核实自身。
2. 把同两对 RC1 Package 放入原研究继承夹具，沿用已登记的 narrative consistency 规格及原封存/重算逻辑，仅执行 A 继承入口 valid_case(case, False)。两次均返回 True。此项与上一项的 checkSpec 不同；二者分别证明局部指纹问题和现有继承入口的实际行为。
3. **单变量对照**：同一局部 Check 显式增加 dependencyRefs=[source:S-FOX]。原文本与相反文本得到不同 SHA，删除快照则返回 None。这定位到必需来源边的缺失；已经到达的文本字节校验正常。

原因见 verify-d-jcs1.py 的 normalized、payload 和 verify_source。空引用集合贡献零条边，resolver 只验证已经到达的 sourceBinding。输入 Schema 对 fact.sourceRefs 要求字段存在，允许空数组。§21.3 要求无法证明完整闭包时保守处理。该问题在 /1 也可复现，属于修复后仍存的缺口。

**A 的最小收口条件**：对必须对照来源的局部 Check，证明所核查的 Fact 有可验证的来源路径，或由该版本的局部检查规格强制绑定正确来源；无法证明则不生成可继承指纹。缺来源的草稿仍可保存。加入来源链为空、内容相反、缺快照和显式正确来源的对照用例，同时保留不依赖来源的普通局部检查。本项不要求定义任何整门最低覆盖，也不要求实现外部 resolver。

## 外部观察、版本兼容与非阻塞边界

- human、geometry_proxy 即使没有 evidenceRefs 也返回 None。text 分别带有效形状的 evidenceRefs、evidenceBindings 或 executionTarget 时也均返回 None。配合专项中的旧 SHA/占位 SHA、同引用与异引用继承负例，符合 A 选择的保守策略。未核验真实外部观察。
- 两个版本分别复算两份示例的 D 与 P，对照各自提交的固定报告均一致。P 不变；No Action 的 D 从 a04aeb2d… 变为 24ba48c4…，Cross Shot 从 5de00b76… 变为 048d0bef…。旧 Check/继承规则不被新 Schema 接受；沿用旧 Check、沿用旧 inheritance、两端把真实旧摘要改贴 /2，三种研究承接尝试均拒绝。
- 两份互不兼容的 RC Schema 仍声明同一 $id 与 contractVersion。按 Git 提交或 Schema 文件摘要固定输入可以复现；只按 $id 缓存会遇到所取版本不唯一。属于候选分发的兼容性注意项，未观察到按明确 /2 验证时接受 /1 的路径。
- 数组索引 Pointer 绑定所选值与路径，没有绑定上层 registry 对象身份。让两个 Shot 的 subjectRefs 完全相同，交换 Shot 顺序，选择 /shots/0/visualDesign/subjectRefs 的摘要保持相同。对“首个位置的主体集合”符合值语义；若规格要验证具名 Shot，必须将其稳定身份纳入依赖并核对归属。此探针没有证明两者在具名对象已正确绑定的检查中混淆。
- 给 collectionPaths 传入 5000 位十进制数组索引，Check 形状合法；两版 digest 均因 int(seg) 抛 ValueError，未按普通缺路径返回 None。当前继承夹具捕获 ValueError 并拒绝，此例未产生错误 pass。建议将明显越界索引统一转为 unresolved。

## 复现与证据

在 Eric 的 canvas-lab 仓库根目录执行以下命令。将下方 Python 代码保存为临时目录中的 probe.py。每个提交各有独立副本，probe 通过所在目录读取对应版本的真实计算器。本文记录的运行使用系统 python3 与 Eric 已有 JCS 依赖。

```bash
audit_dir=$(mktemp -d)
for rev in f323e15 cb7e8fd; do
  mkdir "$audit_dir/$rev"
  git archive "$rev" docs/planning/WAR-35 | tar -x -C "$audit_dir/$rev"
done
# 将下方 Python 代码保存到 "$audit_dir/probe.py"
for rev in f323e15 cb7e8fd; do
  (cd "$audit_dir/$rev/docs/planning/WAR-35" && python3 "$audit_dir/probe.py")
done
(cd "$audit_dir/cb7e8fd/docs/planning/WAR-35" && python3 verify-phase-a.py)
```


```python
import sys,json,hashlib
from pathlib import Path
from copy import deepcopy as clone
from jsonschema import Draft202012Validator as V
root=Path.cwd()
def load(n): return json.loads((root/n).read_bytes())
def defs(n,mark):
    env={"__file__":str(root/n)}
    exec((root/n).read_text().split(mark)[0],env)
    return env
g=defs("verify-decision-gates.py","tests=[]")
d=g["dep_sha"]
pkg=load("cross-shot-once.example.v0-rc1.json")
schema=load("director-plan.schema.v0-rc1.json")
v=V(schema)
def probe(label,make_pair,targets,paths=(),title=None):
    a,b=make_pair()
    spec=dict(g["spec"],targetRefs=targets,collectionPaths=list(paths))
    if title: spec["checkSpec"]=title
    for p in (a,b): v.validate(p)
    aa,bb=[d(p,spec) for p in (a,b)]
    print(label,aa,bb)
    return aa,bb
def fact():
    a,b=clone(pkg),clone(pkg)
    b["plan"]["storyBasis"]["facts"][0]["statement"]+="!"
    return a,b
def missing():
    a,b=clone(pkg),clone(pkg)
    del b["sourceSnapshots"]
    return a,b
def opaque():
    a=clone(pkg)
    a["plan"]["state"]["deltas"][0]["after"]["value"]={"subjectRefs":["subject:FOX","subject:CREEK"]}
    b=clone(a);b["plan"]["state"]["deltas"][0]["after"]["value"]["subjectRefs"].reverse()
    return a,b
probe("direct",fact,["subject:CREEK"],["/intents/0/basisRefs"])
probe("missing",missing,["subject:CREEK"],["/storyBasis/sources"])
probe("opaque",opaque,["delta:D-LAND"])
def orphan():
    a=clone(pkg)
    a["plan"]["storyBasis"]["facts"][0]["sourceRefs"]=[]
    b=clone(a);b["plan"]["revisionId"]="R3"
    text="狐狸留在近岸，没有跳过小溪。"
    sha=hashlib.sha256(text.encode()).hexdigest()
    b["sourceSnapshots"][0].update(text=text,contentSha256=sha)
    b["plan"]["storyBasis"]["sources"][0]["contentSha256"]=sha
    return a,b
title="F-ONCE agrees with the supplied script text"
a,b=probe("orphan fact / contradictory authentic source",orphan,["fact:F-ONCE"],title=title)
def no_bytes():
    a,b=orphan();del b["sourceSnapshots"]
    return a,b
probe("orphan fact / no bytes",no_bytes,["fact:F-ONCE"],title=title)
def indexed():
    a=clone(pkg)
    for shot in a["plan"]["shots"]:shot["visualDesign"]["subjectRefs"]=["subject:FOX"]
    b=clone(a);b["plan"]["shots"].reverse();b["plan"]["revisionId"]="R3"
    return a,b
probe("indexed owner",indexed,["subject:FOX"],["/shots/0/visualDesign/subjectRefs"])
for method,fields in [("human",{}),("geometry_proxy",{}),("text",{"evidenceRefs":["x"]}),("text",{"evidenceBindings":[{"evidenceRef":"x","contentSha256":"0"*64}]}),("text",{"executionTarget":{"unitRef":"x","projectionRevision":"r","projectionContentSha256":"0"*64,"projectionHashRule":"h"}})]:
    print("external",method,list(fields),d(pkg,dict(g["spec"],method=method,**fields)))
pref="war35-dep-jcs8785-sha256/"
for row in ["check","inheritance"]:
    obj=clone(g["c1"] if row=="check" else g["inherit"])
    sv=V({"$defs":schema["$defs"],"$ref":"#/$defs/"+row})
    print(row,schema["$id"],[sv.is_valid(dict(obj,dependencyHashRule=pref+k)) for k in ("1","2")])
for fn,record in load("v0-rc1-golden.report.json")["golden"].items():
    p=load(fn)
    spec=dict(g["spec"],targetRefs=["intent:"+p["plan"]["intents"][0]["id"]],checkSpec="v0 Intent A dependency test",checkSpecVersion="intentA/v0")
    assert d(p,spec)==record["candidateIntentDependencySha256"]
    assert g["plan_target"](p)["planContentSha256"]==record["sha256"]
    print("golden",fn,d(p,spec))
spec=dict(g["spec"],collectionPaths=["/shots/"+"9"*5000+"/actionCoverage"])
ch=dict(g["c1"],collectionPaths=spec["collectionPaths"])
V({"$defs":schema["$defs"],"$ref":"#/$defs/check"}).validate(ch)
try: print("missing large index",d(pkg,spec))
except ValueError as e: print("missing large index",type(e).__name__,str(e)[:100])
# Evaluate just the inherited A decision using the research harness on RC1 data.
src=(root/"verify-decision-gates.py").read_text().split("tests=[]")[0]
src=src.replace('director-plan.schema.review-v0.json','director-plan.schema.v0-rc1.json')
start=src.index('fixture=json.loads(');end=src.index('def sha(v):',start)
for label,pair in [('changed-script',orphan),('unavailable-script',no_bytes)]:
    old,new=pair()
    scope={"__file__":str(root/"verify-decision-gates.py"),"prior_pkg":old,"next_pkg":new}
    # cb's synthetic Shot B fixture is unused (check_current=False).
    exec(src[:start]+'older=prior_pkg\nnewer=next_pkg\n'+src[end:],scope)
    case=scope["make_case"]()
    print("local narrative consistency A carry",label,scope["valid_case"](case,False))
spec=dict(g["spec"],targetRefs=["fact:F-ONCE"],dependencyRefs=["source:S-FOX"],checkSpec=title)
for label,pair in [("changed",orphan),("missing",no_bytes)]:
    a,b=pair()
    print("explicit source control",label,d(a,spec),d(b,spec))
for label in ["duplicate binding","duplicate snapshot","locator only","wrong bytes"]:
    q=clone(pkg)
    if label=="duplicate binding":q["plan"]["storyBasis"]["sources"]*=2
    if label=="duplicate snapshot":q["sourceSnapshots"]*=2
    if label=="locator only":
        del q["sourceSnapshots"]
        q["sourceLocators"]=[{"sourceId":"source:S-FOX","locator":"file:///source"}]
    if label=="wrong bytes":q["sourceSnapshots"][0]["text"]+="!"
    v.validate(q)
    print("source integrity",label,d(q,g["spec"]))
if g["inherit"]["dependencyHashRule"]==pref+"2":
    for label in ("prior check","inheritance","old digest retagged"):
        c=g["make_case"]()
        if label=="prior check":c["checks"][0]["dependencyHashRule"]=pref+"1"
        if label=="inheritance":c["inheritances"][0]["dependencyHashRule"]=pref+"1"
        if label=="old digest retagged":
            oldroot=root.parents[3]/"f323e15"/"docs/planning/WAR-35"
            path=oldroot/"verify-decision-gates.py";e={"__file__":str(path)}
            exec(path.read_text().split("tests=[]")[0],e)
            for ch in c["checks"][:2]:ch["dependencyFingerprintSha256"]=e["c1"]["dependencyFingerprintSha256"]
            c["inheritances"][0]["dependencyFingerprintSha256"]=e["c1"]["dependencyFingerprintSha256"]
        ch=c["checks"][0];c["sealed"][ch["id"]]=g["seal"](ch)
        print("mixed version",label,g["valid_case"](c,False))
```

### 本次 /2 运行输出

```text
direct da1fdb100e6c023e8bdebb83c2cc6e7b2230333fd6a9e212d67d8af49e88a495 b700cdb746753078d996a536ec949d35c65f64a05de93c649561b97e1882886f
missing 2c78d6b164460156915873b85110bf02a497ccec29d2a9b0c8cbb9c04053ca8f None
opaque 4640e80ac49f0f24deb94ae36a43a0a3697ae37f209f4383574baf7f70d7e2c8 2489f59e28455f413c998855eded06081eaa7eee8d1c339cbd271dc8c666297a
orphan fact / contradictory authentic source c48d4ad4c59dc1d5defa6660db423344a787943aed187459f08717b91bbb1736 c48d4ad4c59dc1d5defa6660db423344a787943aed187459f08717b91bbb1736
orphan fact / no bytes c48d4ad4c59dc1d5defa6660db423344a787943aed187459f08717b91bbb1736 c48d4ad4c59dc1d5defa6660db423344a787943aed187459f08717b91bbb1736
indexed owner cc382cb87eab1ec95d0b66135529ab4a9d137f89dc154e5f58d98f586d2d23d2 cc382cb87eab1ec95d0b66135529ab4a9d137f89dc154e5f58d98f586d2d23d2
external human [] None
external geometry_proxy [] None
external text ['evidenceRefs'] None
external text ['evidenceBindings'] None
external text ['executionTarget'] None
check urn:canvas-lab:director-plan:0.1.0-rc1 [False, True]
inheritance urn:canvas-lab:director-plan:0.1.0-rc1 [False, True]
golden no-action-beat.example.v0-rc1.json 24ba48c4cc22877df43abe56f7c8b1f91e354b730edaf07979f0ab63a03e83d1
golden cross-shot-once.example.v0-rc1.json 048d0befa6be64eee9305941a8eed9a7ffe8bdcee4add9c03747f8a9635ddba3
missing large index ValueError Exceeds the limit (4300 digits) for integer string conversion: value has 5000 digits; use sys.set_in
local narrative consistency A carry changed-script True
local narrative consistency A carry unavailable-script True
explicit source control changed bc6b7e23eccc07db6af2fa4f1459306f37b826da5fc90049c47c6644ddfddc18 ba4dbfaeb37ce377327e4985110888044c8290256c9d1f2f82e772e970190b87
explicit source control missing bc6b7e23eccc07db6af2fa4f1459306f37b826da5fc90049c47c6644ddfddc18 None
source integrity duplicate binding None
source integrity duplicate snapshot None
source integrity locator only None
source integrity wrong bytes None
mixed version prior check False
mixed version inheritance False
mixed version old digest retagged False
```
