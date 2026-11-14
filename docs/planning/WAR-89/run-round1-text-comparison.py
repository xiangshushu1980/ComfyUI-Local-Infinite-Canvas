#!/usr/bin/env python3
"""WAR-89 real C/D/E first-round matched text experiment.
Writes only within this round directory. Launches isolated Codex runs; no production changes.
"""
import hashlib, json, os, pathlib, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

ROOT = pathlib.Path("/home/sean/projects/canvas-lab")
OUT = ROOT / "docs/planning/WAR-89/text-test-round1-20261114"
SRC = ROOT / "docs/validation/WAR-61/evidence/raw-package/toonflow-20261107"
SKILL = ROOT / "docs/planning/WAR-89/director-skill-v0-candidate"
EXPECTED = {
 "C":"ba56afb91c117d06ced4089456f5e713435e99cfbf287fd3ee5a5b88ee50153d",
 "D":"65b8a2f83cefc2281879fb254d3ee25dfd68d72e7cd0d811a2afbade5c1e165d",
 "E":"466d257d3ac684ea20e76eb01f80589270484478cc75b084c1f0640c77d576ec"
}
def hashfile(p):
 return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def clock():
 return datetime.now(timezone.utc).isoformat()
def atomic_json(p,obj):
 t=p.with_suffix(".new")
 t.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 t.replace(p)

TASK = """# 单场景导演方案测试（冻结输入）
请根据同目录的 case-source.txt（全篇包含剧本与已确认创作意图）进行单场导演规划。请自行作出**真正导演选择**，而不是只列术语或固定模板。

工作任务：
1. 给出本场的候选 Director Intent：观众从哪里开始理解、关键变化与最终体验，以及一项有实质区别的表达替代方案和它的代价。
2. 接着给出 Beat（必须有真实的故事/观众认知变化和关键时点）、Blocking（演员可执行动作、道具/站位/视线与必要中间态），最后给出**可直接审阅**的 Shot Plan（逐镜观众任务、实际镜头构造、表演/视听/切点、邻镜接续；允许合理的不同镜数）。
3. 选出一处最关键、最有争议的镜头选择，提出真实替代方案及代价；如 Shot 发现 Blocking 不足以实现观众任务，明确返回上游的**局部候选修订**，说明变化、影响和复检，而不是悄悄改变剧情。
4. 最后给出精简专业 Review：确定文本冲突、可信规划风险、需要媒体/观众验证的未知分开。尽量保留源剧本实际台词和声画时序，不凭空补作者事实。

本次没有用户正式批准的 Intent/Plan；可以沿一个**明确属于探索、未批准**的候选完成四阶段推演，但不得把自己生成的 A/B 标为正式用户批准。
本轮只进行文本，不调用媒体/服务，不修改仓库或制作脚本。若有信息不足，以清楚假设和待证标记；可以做专业选择，不必因每个开放细节先询问用户。
用中文完整回答，务求具体、精练，优先专业理由而不是格式与总字数。不用引用其他历史实验或已知评阅结论。
"""
NATIVE = """任务包：以上 TEST 任务与 case-source.txt 是你唯一的专业依据。请根据既有一般导演知识自主设计；不加载任何外部导演 Skill 或之前的研究资料。"""
CANDIDATE = """专业方法包：使用此目录 ./skill/SKILL.md 作为本次**候选 Director Skill v0** 的入口，按阶段阅读它引用的相关四张阶段卡，并按实际问题触发 knowledge-index/review-method；不要加载全部外部三源的原始工作流。当前测试为同一会话中的探索候选，不含实际用户 A/B 批准，不启动真实工程。遇到资料不足，使用本次剧本与七文件提供的通用方法，不扩展读取任何项目历史案例、评阅表或外部文件。"""
MODEL="gpt-6-astra"
EFFORT="medium"

def prep():
 if OUT.exists(): raise SystemExit("Output dir already exists; refusing overwrite: "+str(OUT))
 OUT.mkdir(parents=True)
 stamp={"generated_at":clock(),"repo_head":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
 "branch":subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip(),
 "codex_version":subprocess.check_output(["codex","--version"],text=True).strip(),
 "model":MODEL,"reasoning_effort":EFFORT, "arm_descriptions":{"native":"TASK + raw script; general model directing knowledge","candidate":"same TASK + raw script + self-contained 7-file skill snapshot; on-demand stage refs"},
 "source_sha256":EXPECTED.copy(),"skill_snapshot":{},
 "read_only":True,"fresh_ephemeral_sessions":True,"identical_model_task":True,
 "evaluation_rubric_visibility":"withheld from generation; held separately at WAR-89"}
 for k,expected in EXPECTED.items():
  p=SRC/f"xia-61-script-{k}"/f"script-{k}.txt"
  if hashfile(p)!=expected: raise SystemExit("Frozen source SHA mismatch "+k)
 shutil.copytree(SKILL,OUT/"skill-snapshot")
 for p in sorted((OUT/"skill-snapshot").rglob("*.md")):
  stamp["skill_snapshot"][str(p.relative_to(OUT))]=hashfile(p)
 stamp["skill_sha256"]=stamp["skill_snapshot"]
 for k in EXPECTED:
  for arm in ("native","candidate"):
   dest=OUT/"workspaces"/f"{k}-{arm}"
   dest.mkdir(parents=True)
   shutil.copy2(SRC/f"xia-61-script-{k}"/f"script-{k}.txt",dest/"case-source.txt")
   (dest/"task.md").write_text(TASK,encoding="utf-8")
   (dest/"arm.md").write_text(NATIVE if arm=="native" else CANDIDATE,encoding="utf-8")
   if arm=="candidate": (dest/"skill").symlink_to(pathlib.Path("../../skill-snapshot"))
   stamp.setdefault("prompts",{})[f"{k}-{arm}"]=hashfile(dest/"arm.md")
 stamp["task_sha256"]=hashfile(OUT/"workspaces"/"C-native"/"task.md")
 atomic_json(OUT/"manifest.json",stamp)
 (OUT/"README.md").write_text(f"# WAR-89 C/D/E 受控文本对照 Round 1（2026-11-14）\n\n此目录由 run_round1.py 自动生成，仅为文本模型试验，不运行媒体、不安装生产 Skill。两组均使用 Codex {MODEL} / {EFFORT}，新会话 read-only，案例与任务一致，仅专业方法输入不同。候选使用冻结七文件快照；结果以 workspaces/* 的 result.md 和 events.jsonl 及 manifest 为准。评阅判据独立保存于 WAR-89 的旧文件，模型不可读取。\n\n注意：三案例每组一次，绝非成功率统计；模型输出不可当作者事实或真实视觉测试。权限：不覆写既存研究证据，既有 WAR-35 工作树保持不动。\n",encoding="utf-8")
 print("PREPARED",OUT,flush=True)

def run_one(k,arm):
 w=OUT/"workspaces"/f"{k}-{arm}"
 combined=(w/"task.md").read_text()+"\n\n"+(w/"arm.md").read_text()+"\n\n请先读取 case-source.txt 原文，并完成任务；只需在最终答复中输出候选方案。"
 (w/"prompt.md").write_text(combined,encoding="utf-8")
 cmd=["codex","exec","--ephemeral","--skip-git-repo-check","-C",str(w),"-m",MODEL,
      "-c",'model_reasoning_effort="medium"',"-s","read-only","--json","-o",str(w/"result.md"),"-"]
 start=time.monotonic()
 events=w/"events.jsonl"
 report={"case":k,"arm":arm,"started_at":clock(),"prompt_sha256":hashfile(w/"prompt.md"),"source_sha256":hashfile(w/"case-source.txt"),
         "result_path":str(w/"result.md"),"model":MODEL,"reasoning_effort":EFFORT}
 try:
  with events.open("wb") as f:
   cp=subprocess.run(cmd,input=combined.encode(),stdout=f,stderr=subprocess.PIPE,timeout=1050)
  report["returncode"]=cp.returncode
  (w/"stderr.txt").write_bytes(cp.stderr)
 except subprocess.TimeoutExpired as e:
  report["returncode"]="timeout"
  (w/"stderr.txt").write_bytes(e.stderr or b"")
 report["finished_at"]=clock()
 report["seconds"]=round(time.monotonic()-start,1)
 if (w/"result.md").exists():
  report["result_sha256"]=hashfile(w/"result.md")
  report["result_bytes"]=(w/"result.md").stat().st_size
 report["events_sha256"]=hashfile(events)
 atomic_json(w/"run.json",report)
 print("FINISHED",k,arm,"exit",report["returncode"],"seconds",report["seconds"],"result_bytes",report.get("result_bytes",0),flush=True)
 return report

def main():
 prep()
 # Matched interleaving mitigates time-order changes, but each is an independent sample.
 jobs=[("D","native"),("D","candidate"),("C","candidate"),("C","native"),("E","native"),("E","candidate")]
 results=[]
 with ThreadPoolExecutor(max_workers=2) as pool:
  futs=[pool.submit(run_one,*j) for j in jobs]
  for f in as_completed(futs):
   try: results.append(f.result())
   except Exception as ex: print("RUN ERROR",repr(ex),flush=True)
 atomic_json(OUT/"results-summary.json",{"finished_at":clock(),"results":sorted(results,key=lambda x:(x["case"],x["arm"]))})
 print("EXPERIMENT_FINISHED",len(results),"of",len(jobs),flush=True)

if __name__=="__main__":
 main()
