## 判定

**阶段 B 设计验收为 Not Accepted。**

审阅固定于 `d2ec0028a63084b54f3a09b173ac989765926177`，开始与结束时工作树均干净。已阅读指定的 Blocking 2–5、阶段 A RC4 验收报告及契约第 29 节，并检查四个目标脚本、RC4 Schema 与 fixture。

原有 Gate **26/26** 和 raw **26/26** 均在避开报告写入段的内存运行中复现通过。但新增反例证明，**遗漏冲突 Decision 仍可恢复批准，执行范围受限的 Intent A 仍可被继承为整门 A**。这两项足以阻塞阶段 B 验收。

## 1. 阻塞项——Decision 清单缺少完整性证明，当前决定的封存也未核验

风险路径会比较 `sealedRiskManifests`，Decision 路径则从调用方提供的 `case["decisions"]` 建立 `competing`。`sealedDecisions` 仅用于核验继承来源，当前 Decision 没有同等检查。

实际复现得到以下结果。

| 输入变体 | `wholePlan` 实测 |
|---|---|
| 基线 | `True` |
| 添加同 target、同 gate 的 rejected Decision，并保留两条记录 | `False` |
| 将该 rejected Decision 从数组删除，保留其可信封存记录 | **`True`** |
| 可信封存保存当前 B 的 rejected 内容，传入同 ID 的 approved 内容 | **`True`** |

第三行直接绕过 §29.3 的冲突拒绝规则。第四行说明，即使已有当前决定的可信封存，判定器也会接受与之不一致的当前内容。

这不要求实现真实认证服务才能修复。研究模型已经引入可信封存输入，需要进一步约束当前 Decision 的内容一致性，以及该 gate/target 下有效决定集合的完整性。否则，“数组中只有一个批准”无法证明没有被遗漏的冲突决定。[phase_b_gate_rules.py](/home/sean/projects/canvas-lab-worktrees/war-35-stage-b-20261117/docs/planning/WAR-35/phase_b_gate_rules.py:94)

## 2. 阻塞项——执行范围受限的 A 可以升级成整门 A

给来源 `D-A2` 添加合法的 `executionTarget`，并按该真实内容更新其可信封存。其余 Plan、Check、直接父边、风险目录和继承映射全部保留。

实测结果为：

- 带 `executionTarget` 的来源 Decision 通过 RC4 Decision Schema。
- 当前 `D-A3` 不带执行范围，仍可从该来源完成 `verified_carry_forward`。
- 最终返回 `intentA=True, shotB=True, wholePlan=True`。
- 单独给当前 `D-A3` 添加 `executionTarget`，同样返回全部 `True`。

源码只在最后限制 B Decision 的 `executionTarget`。来源 A、当前 A 的执行范围，以及继承前后范围的一致性均未检查。局部 Check 的 D-JCS 相同，也无法证明执行范围内的批准已经覆盖整门 Intent A。

阶段 B 的保守策略需要明确限定可用于整门批准的 A 范围，并在来源与当前 Decision 两端实施检查。[继承入口](/home/sean/projects/canvas-lab-worktrees/war-35-stage-b-20261117/docs/planning/WAR-35/phase_b_gate_rules.py:177) · [最终批准检查](/home/sean/projects/canvas-lab-worktrees/war-35-stage-b-20261117/docs/planning/WAR-35/phase_b_gate_rules.py:234)

## 最小复现

在指定工作树根目录运行以下代码即可复现两个阻塞项。它仅加载验证器定义，避开写报告的入口，且关闭 Python 字节码缓存。

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'PY'
from pathlib import Path
import sys

root = Path("docs/planning/WAR-35").resolve()
sys.path.insert(0, str(root))
path = root / "verify-phase-b.py"

env = {"__file__": str(path)}
source = path.read_text().split("results = []")[0]
exec(compile(source, str(path), "exec"), env)

make = env["make_case"]
validate = env["stage_b_validate"]
seal = env["seal"]

# 冲突记录存在时拒绝，遗漏后仍保留其可信封存。
case = make()
env["conflicting_decision"](case)
for decision in case["decisions"]:
    case["sealedDecisions"][decision["id"]] = seal(decision)

print("conflict present:", validate(case))
case["decisions"].pop()
print("conflict omitted:", validate(case))

# 当前 B 的可信内容为 rejected，传入内容改成 approved。
case = make()
decision = case["decisions"][-1]
decision["verdict"] = "rejected"
case["sealedDecisions"][decision["id"]] = seal(decision)
decision["verdict"] = "approved"
print("current decision altered:", validate(case))

# 来源 A 仅具执行范围，当前 A 承接后没有该范围。
case = make()
source_decision = case["decisions"][0]
source_decision["executionTarget"] = {
    "unitRef": "UNIT-1",
    "projectionRevision": "PR1",
    "projectionContentSha256": "a" * 64,
    "projectionHashRule": "war52-projection-test/1",
}
case["sealedDecisions"][source_decision["id"]] = seal(source_decision)

from phase_b_gate_rules import DECISION_VALIDATOR
assert DECISION_VALIDATOR.is_valid(source_decision)
print("scoped source carried:", validate(case))
PY
```

观察到的 `wholePlan` 依次为 **False、True、True、True**。

## 其他入口缺口

下面两项使用了非法结构输入，区别于上面通过 Decision Schema 的反例。它们反映研究判定器的输入校验覆盖不足。

- **Risk 未进行结构校验。** 将已封存的 `hard_conflict` 的 `status` 改为非法值 `"OPEN"`，同步封存与完整风险目录后，判定器返回 `wholePlan=True`。它只将精确等于 `"open"` 的风险纳入开放风险。RC4 Risk Schema 本可拒绝该值，但外置 `case["risks"]` 未经过这个 Schema。
- **Inheritance 未进行结构校验。** 删除继承条目必填的 `basis`，仍返回 `wholePlan=True`。包级 Schema 校验不会覆盖这些外置条目。

需要为外置 Risk、Inheritance 实际执行相应 Schema 校验，或在参考判定器入口明确实施并验证等价的前置条件。[风险处理](/home/sean/projects/canvas-lab-worktrees/war-35-stage-b-20261117/docs/planning/WAR-35/phase_b_gate_rules.py:132) · [继承处理](/home/sean/projects/canvas-lab-worktrees/war-35-stage-b-20261117/docs/planning/WAR-35/phase_b_gate_rules.py:208)

## 本轮通过的检查

| 审查方向 | 本轮证据 |
|---|---|
| 整门成员覆盖 | 原矩阵中的新增 Intent/Shot、遗漏 B Check、错误目标和方法均被拒绝 |
| 风险遗漏 | 保留可信风险目录、删除其中风险正文的反例被拒绝 |
| 可信父边 | 缺失、跳版和错误父边封存均被拒绝 |
| 旧 Check | `/3` 来源 Check、来源快照缺失、来源 Check 改为 fail 均被拒绝 |
| raw 往返 | 原 26 项通过，正负安全整数舍入边界反例被入口拒绝 |
| 扩展数值采样 | 固定随机种子 `35`，共 10,007 个输入，8,942 个接受、1,065 个拒绝，接受样本的两次 JCS 字节均一致 |
| RC4 固定 Golden | 两份 fixture 的 P/D 均与已提交 Golden 匹配，Python 与 Node JCS 输出一致 |

因此，**Blocking 5 的原始数值反例已修复，本轮扩展采样未发现新的接受域往返失败**。采样不能构成穷举证明。另发现超长整数和深嵌套输入分别漏出普通 `ValueError`、`RecursionError`，错误统一与资源限制仍可完善；这两项不作为本轮拒绝验收的依据。[raw_ijson_gate.py](/home/sean/projects/canvas-lab-worktrees/war-35-stage-b-20261117/docs/planning/WAR-35/raw_ijson_gate.py:30)

## 验收与生产授权边界

本轮结论针对固定提交上的**阶段 B 研究性设计与参考判定器**。阶段 A RC4 的独立验收结论保持其既有局部范围，阶段 B 仍须收口上述 Decision 完整性及批准范围问题后重新验收。

即使阶段 B 后续获得 Accepted，公共 Schema 正式冻结、真实用户 A/B 批准和生产执行仍各有独立条件。当前合成封存目录尚未证明真实不可变历史、完整审批目录、用户身份授权、媒体字节归属、生产 API/Gateway 或 WAR-52/H3 执行。

本轮交付为只读审阅与内存复现结果，文件和 Git 状态保持原状。