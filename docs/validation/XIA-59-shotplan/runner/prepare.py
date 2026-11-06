#!/usr/bin/env python3
import hashlib,json,pathlib,urllib.request,subprocess,shutil
root=pathlib.Path(__file__).resolve().parent.parent
files={
"toonflow/shotCraft.md":"https://raw.githubusercontent.com/HBAI-Ltd/Toonflow-app/master/packages/skills/v118workflow/references/knowledge/shotCraft.md",
"toonflow/storyboardTable.md":"https://raw.githubusercontent.com/HBAI-Ltd/Toonflow-app/master/packages/skills/v118workflow/references/storyboardTable.md",
"toonflow/directorPlan.md":"https://raw.githubusercontent.com/HBAI-Ltd/Toonflow-app/master/packages/skills/v118workflow/references/directorPlan.md",
"director/SKILL.md":"https://raw.githubusercontent.com/wuwangzhang1216/DirectorSKILL/main/SKILL.md",
"director/beat-sheet-template.md":"https://raw.githubusercontent.com/wuwangzhang1216/DirectorSKILL/main/assets/beat-sheet-template.md",
"director/blocking-and-staging.md":"https://raw.githubusercontent.com/wuwangzhang1216/DirectorSKILL/main/references/blocking-and-staging.md",
"director/shot-plan-template.md":"https://raw.githubusercontent.com/wuwangzhang1216/DirectorSKILL/main/assets/shot-plan-template.md",
"director/continuity-bible.md":"https://raw.githubusercontent.com/wuwangzhang1216/DirectorSKILL/main/references/continuity-bible.md",
"vimax/storyboard_artist.py":"https://raw.githubusercontent.com/HKUDS/ViMax/main/agents/storyboard_artist.py",
"vimax/camera_image_generator.py":"https://raw.githubusercontent.com/HKUDS/ViMax/main/agents/camera_image_generator.py",
"vimax/script2video_pipeline.py":"https://raw.githubusercontent.com/HKUDS/ViMax/main/pipelines/script2video_pipeline.py",
}
manifest={}
for name,url in files.items():
 p=root/"upstream"/name
 p.parent.mkdir(parents=True,exist_ok=True)
 try:
  content=urllib.request.urlopen(url,timeout=22).read()
  p.write_bytes(content)
  manifest[name]={"source":url,"sha256":hashlib.sha256(content).hexdigest(),"size":len(content)}
  print("OK",name,len(content),flush=True)
 except Exception as e: manifest[name]={"error":str(e),"source":url};print("FAIL",name,str(e),flush=True)
src=pathlib.Path("/home/sean/projects/comfy-ops/.pi/skills/h3-prompt-writing")
for f in ("SKILL.md","references/ref-en.txt"):
 content=(src/f).read_bytes();p=root/"upstream"/"h3"/f;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(content)
 manifest["h3/"+f]={"local_source":str(src/f),"sha256":hashlib.sha256(content).hexdigest(),"size":len(content)}
(root/"upstream"/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
common="""时长：8秒，单场景，咖啡馆内日光窗旁圆桌。人物A：女性，短深色卷发，绿色开衫、淡紫上衣，固定坐在画面左侧；人物B：男性，短深色发，藏蓝衬衫外套、白T恤，固定坐在画面右侧。Picture 1=A肖像，Picture 2=B肖像，Picture 3=两人同桌场景。白色陶瓷杯起始在A面前。参考图及衣着/相对位置不可改变。风格现实自然，不添加第三人、第二只杯子或额外台词。"""
scenarios={
"01-dialogue":{"title":"问答迟疑反应","beat":"A看向B并问：「你今天还好吗？」B短暂避开视线，吸一口气，停顿后回答：「还好，只是有点累。」A听到回答，神情变得担心，沉默看着B。杯子一直在A面前，无人触碰。"},
"02-handoff":{"title":"白杯交接","beat":"A问B：「你还好吗？」B轻声回答：「有点累。」A随后用右手沿桌面把唯一白杯推向B；B用左手接住，将白杯停在自己面前，保持左手持杯，然后抬眼看A，回答：「谢谢你。」A微微露出安慰的笑容。交接前杯归A，交接后杯归B；不能重新递杯。"},
"03-overlap":{"title":"并行动作与发现","beat":"B坐在右边说：「我以为你会留下来。」他说话尚未结束时，A从画面左边座位起身，向画面左侧出口走去，没有触碰白杯。B发现A离开，话音戛然而止，转身看向左侧出口，停顿不再说话。A始终是离开者，B始终留在座位附近，杯子一直留在桌上A原先位置，保持唯一。"},
}
for key,val in scenarios.items():
 payload={"id":key,"title":val["title"],"duration_seconds":8,"reference_images":{"Picture 1":"A肖像","Picture 2":"B肖像","Picture 3":"咖啡馆两人同桌空间参考"},"fixed_context":common,"beat":val["beat"]}
 (root/"inputs"/(key+".json")).write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n")
print("Fixture and upstream snapshot ready",flush=True)
