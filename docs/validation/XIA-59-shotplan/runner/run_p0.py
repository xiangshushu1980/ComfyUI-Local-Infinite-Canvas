#!/usr/bin/env python3
"""XIA-59 P0: replay upstream text instructions, NOT upstream executable pipelines."""
import argparse,json,pathlib,hashlib,subprocess,datetime,time,os
root=pathlib.Path(__file__).resolve().parent.parent
provider="deepseek";model="deepseek-flash";thinking="off"
def read(name):return (root/"upstream"/name).read_text()
def make_prompt(scenario,condition):
 case=json.loads((root/"inputs"/(scenario+".json")).read_text())
 contract="""\n\n【共同输出契约：仅为跨组评价接口，不含额外导演规则】\n仅输出 JSON 对象。字段: scenario_id(string), shots(array), continuity_notes(array), uncertainties(array)。每个 shots 元素字段: shot_id, start_s, end_s, purpose, framing, angle, camera_motion, visible_action, dialogue (array of {speaker,text}), blocking, state_in, state_out, continuity_handoff, cut_reason。时间覆盖0–8秒，镜头不能时间重叠且不留空白；无对白则 dialogue=[]。不增删或改写原台词，不添加剧情人物道具。可自由选择镜头数量，包括一个镜头。没有证据的空间测量保持未知。只返回 JSON，不带 markdown。\n"""
 preface="""【实验类型】XIA-59 静态 Shot Plan; 不运行图像或视频生成。所有组使用相同素材与统一输出契约。以下已冻结的开源原文为该组唯一方法学依据，不要读取工作区的其他文档或历史样本。参考源里的项目生产/保存/媒体生成步骤不执行，只完成文本 Shot Plan。\n"""
 source=""
 if condition=="native":
  source="【原生基线】不提供任何额外导演方法、Skill 或检查清单。\n"
 elif condition=="toonflow":
  source="【Toonflow 上游原文；原始文件保持完整，仅调用分镜文本步骤】\n"
  for n in ("toonflow/shotCraft.md","toonflow/storyboardTable.md"):
   source+="\n--- ORIGINAL "+n+" ---\n"+read(n)
  source+="\n【接口适配说明】仅跳过上游 UI/用户确认/落盘/媒体步骤；不得将本共同 JSON 契约当作 Toonflow 原生输出格式。\n"
 elif condition=="director":
  source="【DirectorSKILL 上游原文；运行 Beat→Blocking→Shot 的文本部分，跳过后续媒体制作】\n"
  for n in ("director/SKILL.md","director/beat-sheet-template.md","director/blocking-and-staging.md","director/shot-plan-template.md","director/continuity-bible.md"):
   source+="\n--- ORIGINAL "+n+" ---\n"+read(n)
  source+="\n【接口适配说明】仅报告 Shot Plan JSON；不用自动完成导演生产包其余工件；原始启发式保留而非改写。\n"
 elif condition=="vimax":
  source="【ViMax 上游原样 StoryboardArtist 代码与系统提示文本；这是文本阶段 prompt replay，不执行 LangChain/Pydantic 原管线或 Camera Tree】\n"
  source+="\n--- ORIGINAL vimax/storyboard_artist.py ---\n"+read("vimax/storyboard_artist.py")
  source+="\n【接口适配说明】遵守 design_storyboard 的镜头规划语义及 decompose_visual_description 首/运动/尾的提示语义；原生 Pydantic 类型在此映射到共同 JSON 契约。未执行 camera_image_generator.py、图像或视频生成。\n"
 return preface+source+"\n【固定场景与原始 Beat】\n"+json.dumps(case,ensure_ascii=False,indent=2)+contract
def run_one(scenario, condition, batch, provider, model, thinking, timeout):
 directory=root/"p0"/"batches"/batch/scenario/condition
 directory.mkdir(parents=True, exist_ok=False)
 prompt=make_prompt(scenario, condition)
 prompt_bytes=prompt.encode("utf-8")
 (directory/"input-prompt.txt").write_bytes(prompt_bytes)
 cmd=["/home/sean/.pi/agent/bin/pi","--no-tools","--no-extensions","--no-mcp","--no-skills","--no-context-files","--no-session","--provider",provider,"--model",model,"--thinking",thinking,"-p","@"+str(directory/"input-prompt.txt"),"Output the requested JSON Shot Plan only."]
 meta={"condition":condition,"scenario":scenario,"batch":batch,"provider":provider,"model":model,"thinking":thinking,"timeout_seconds":timeout,"method":"upstream text prompt replay (not pipeline execution)","input_sha256":hashlib.sha256(prompt_bytes).hexdigest(),"command":cmd,"cwd":"/home/sean/projects/canvas-lab","start_utc":datetime.datetime.now(datetime.timezone.utc).isoformat()}
 (directory/"metadata.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n")
 started=time.monotonic()
 stdout=b""; stderr=b""
 try:
  p=subprocess.run(cmd,capture_output=True,timeout=timeout,cwd=meta["cwd"])
  stdout,stderr=p.stdout,p.stderr
  meta["exit_code"]=p.returncode
 except subprocess.TimeoutExpired as e:
  stdout=e.stdout or b""; stderr=e.stderr or b""
  meta["error"]="TIMEOUT"
 except OSError as e:
  stderr=str(e).encode("utf-8")
  meta["error"]=type(e).__name__
 finally:
  (directory/"raw-output.txt").write_bytes(stdout)
  (directory/"stderr.txt").write_bytes(stderr)
  meta.update(duration_seconds=time.monotonic()-started,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),output_sha256=hashlib.sha256(stdout).hexdigest(),stderr_sha256=hashlib.sha256(stderr).hexdigest(),output_bytes=len(stdout),stderr_bytes=len(stderr))
  (directory/"metadata.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n")
 print(scenario,condition,json.dumps({k:meta.get(k) for k in ("exit_code","error","output_bytes","duration_seconds")}),flush=True)
 return meta
if __name__=="__main__":
 a=argparse.ArgumentParser();a.add_argument("--scene",default="01-dialogue");a.add_argument("--condition",choices=["all","native","toonflow","director","vimax"],default="all");a.add_argument("--batch",required=True,help="new batch directory name; never overwrites an existing sample");a.add_argument("--provider",default=provider);a.add_argument("--model",default=model);a.add_argument("--thinking",default=thinking);a.add_argument("--timeout",type=float,default=220);args=a.parse_args()
 if pathlib.Path(args.batch).name != args.batch or args.batch in (".",".."):
  a.error("batch must be a single directory name")
 for c in (["native","toonflow","director","vimax"] if args.condition=="all" else [args.condition]):run_one(args.scene,c,args.batch,args.provider,args.model,args.thinking,args.timeout)
