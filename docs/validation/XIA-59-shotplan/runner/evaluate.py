#!/usr/bin/env python3
"""Deterministic format and literal checks only; NOT semantic/directing scores."""
import argparse,json,re,pathlib
root=pathlib.Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--batch",required=True,help="batch directory name under p0/batches")
args=parser.parse_args()
if pathlib.Path(args.batch).name != args.batch or args.batch in (".",".."):
 parser.error("batch must be a single directory name")
batch_dir=root/"p0"/"batches"/args.batch
if not batch_dir.is_dir():
 parser.error("batch directory does not exist")
conditions=("native","toonflow","director","vimax")
report=[]
for src in sorted((root/"inputs").glob("*.json")):
 case=json.loads(src.read_text()); beat=case["beat"]; lines=re.findall(r"「([^」]+)」",beat)
 for cond in conditions:
  folder=batch_dir/case["id"]/cond;path=folder/"raw-output.txt"
  item={"scene":case["id"],"group":cond,"available":path.exists()}
  if not path.exists():report.append(item);continue
  raw=path.read_text();m=re.search(r"\{.*\}",raw,re.S)
  try:obj=json.loads(m.group() if m else raw)
  except Exception as e:item["parse_error"]=str(e);report.append(item);continue
  shots=obj.get("shots",[]);item["shots"]=len(shots)
  item["all_dialogue_literals_in_output"]={s:s in raw for s in lines}
  durations=[(s.get("start_s"),s.get("end_s")) for s in shots]
  item["durations"]=durations
  try:
   item["timeline_contiguous"]=bool(shots) and float(shots[0]["start_s"])==0 and float(shots[-1]["end_s"])==8 and all(abs(float(a["end_s"])-float(b["start_s"]))<0.001 for a,b in zip(shots,shots[1:]))
  except Exception:item["timeline_contiguous"]=False
  item["human_review_required"]=["beat coverage","cut information gain","blocking and eyelines","state transitions and props","invented plot","visual feasibility"]
  report.append(item)
out=batch_dir/"mechanical-report.json"
with out.open("x",encoding="utf-8") as f:
 f.write(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
for r in report:print(r["scene"],r["group"],r.get("shots","missing"),r.get("parse_error",""),"timeline="+str(r.get("timeline_contiguous")))
