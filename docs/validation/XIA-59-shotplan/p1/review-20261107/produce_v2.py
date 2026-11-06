#!/usr/bin/env python3
"""Apply Codex-authored, shot-specific source restorations; preserve initial evidence."""
from pathlib import Path
import hashlib,json,re
root=Path(__file__).resolve().parents[1]
extras={
('01-dialogue','native'):[
'The upper bodies and table edge are visible; the cup is in front of <Subject 1> and is untouched. At the cut, she still looks at him and his gaze begins to move away.',
'<Subject 2> remains in his right-hand seat, his body orientation unchanged apart from the movement of his head and eyes; he remains paused and ready to speak at the cut.',
'Return to the first shot’s composition. <Subject 1> listens as <Subject 2> speaks; after his answer her face begins to show concern. The cup stays before her.',
'<Subject 1> remains seated at left, facing <Subject 2>. End on her silent, concerned expression; the cup remains untouched in front of her.'],
('01-dialogue','toonflow'):[
'The view is from the side of the round table at seated eye level. Both are seated and looking toward each other; <Subject 1> keeps her right hand on the table without touching the cup. At the cut his gaze begins to move away.',
'The close view is from behind <Subject 1>’s left shoulder, at eye level or slightly below. His shoulder rises on the breath and his lips tighten; her foreground shoulder stays still. He relaxes his shoulders after the answer, with his gaze back toward her.',
'The reverse over-shoulder view looks from behind <Subject 2>’s right shoulder. <Subject 1> keeps both hands on the table and leaves the cup in place. Maintain the established eyeline axis.'],
('01-dialogue','director'):[
'Both are seated at the round table, with the window, table and cup visible; <Subject 2> initially has both hands on the table. She waits after asking while his gaze starts to waver. Keep their separation unspecified.',
'The camera stays at seated eye level on the established axis. <Subject 2> remains in his right-side seat and turns his head and gaze away, then back toward <Subject 1>; his breathing settles after his answer. The cup remains untouched.',
'The camera stays at seated eye level on the same axis. <Subject 1> remains in her left seat, angled slightly toward him, and ends on her concerned, silent face. The cup and daylight direction do not change.'],
('01-dialogue','vimax'):[
'The round table sits between them near the center. <Subject 1> keeps her hands near the table edge without touching the cup. At the cut <Subject 2> has looked back toward her and his lips are slightly parted after his breath.',
'In the close shot the table edge and cup rim are low in frame, with <Subject 1>’s shoulder blurred at left. After the answer his eyes drop slightly then rise to meet hers, his expression calm but tired.',
'The table edge and cup rim remain low in frame; <Subject 2>’s shoulder is blurred at right. <Subject 1> ends with a faintly furrowed brow, lips closed and eyes on him; the cup remains in its original position.'],
('02-handoff','native'):[
'The round table fills the lower half of the frame; the camera is near the axis between them, slightly toward the window. At the cut the question is over, he has not yet replied, and the cup is still before her.',
'<Subject 2> remains seated on the right, facing left toward her, with his left hand resting naturally on his side of the table. His shoulders are relaxed; the cup remains before <Subject 1> and has not been transferred.',
'Both remain seated; at the start her right hand has not yet touched the cup, and his left hand is near his side of the table. At the end he holds the sole cup with his left hand in front of him.',
'The close two-shot keeps <Subject 1> at the edge and his cup-holding left hand visible. They remain in their original seats; the cup stays with him, without a second transfer.'],
('02-handoff','toonflow'):[
'Both sit facing each other across the round table. <Subject 1> is slightly turned toward him; his shoulders are somewhat lowered. At the cut her gaze remains on him and the cup has not moved.',
'The eye-level close view includes his shoulders and part of the table. <Subject 1> remains off-screen left; the cup remains on her side and is not in his hand. After answering, his gaze rests on her.',
'The full cup and both hands remain in frame. Her right hand starts empty at the table edge and withdraws after pushing; his left hand receives and holds the cup in front of him. The cup does not return to her side.',
'<Subject 2> remains seated facing left and holding the cup with his left hand; <Subject 1> remains at left and smiles. End without another handoff.'],
('02-handoff','vimax'):[
'The view runs from upper chests to part of the table, with window light on it. At the end their seats and the cup are unchanged and her right hand begins to rise toward the table for the following action.',
'The close view contains the middle of the tabletop, both hands and portions of their faces at the edges. Her arm enters from the left, his left hand from the right; the cup ends at his right-side place.',
'Both face each other, she on the left and he on the right. He starts with his eyes toward the table or cup, then looks up while continuing to hold the cup with his left hand.'],
('03-overlap','native'):[
'At the cut <Subject 1> has left her seat and is moving left, <Subject 2> remains seated and his speech is near its end. The cup stays untouched at her former place.',
'The camera is just forward of <Subject 2> on his right, angled toward the left-side exit; the source allows an extremely slight following turn. He remains near his seat as she continues left; the cup remains unique and unmoved.'],
('03-overlap','toonflow'):[
'The two sit at three-quarter angles facing one another, with the cup on the table before <Subject 1>. The exit direction is off-screen left. At the cut her hands have left the table edge and her weight has shifted toward standing.',
'The fixed wider view is from behind and to the side of the round table. <Subject 1> continues from the rising movement and walks left; <Subject 2> remains seated, his mouth briefly half-open before turning left, then motionless and silent. The cup remains at her former place.'],
('03-overlap','director'):[
'<Subject 2> faces <Subject 1>, with small movements of shoulders and mouth; she listens while seated at left. Her hands are below the table or at its edge, not otherwise specified. The cup remains untouched.',
'<Subject 1> starts seated, rises, turns and walks toward the left-side exit; how far she has departed by the end is unspecified. <Subject 2> turns his head and upper body but remains near his right-side seat; the cup remains untouched.'],
('03-overlap','vimax'):[
'Both sit facing each other across the table, <Subject 1> at left, <Subject 2> at right; his speech is described as still in progress at the cut, and she remains seated.',
'The eye-level camera is slightly toward <Subject 2>’s side. She ends on the path toward the left exit; he stays near his right-side seat, turned left and silent. The cup remains unique and unmoved; the space beyond the exit is not shown.']}
for (scene,method),additions in extras.items():
 folder=root/scene/method; orig=(folder/'prompt.txt').read_text(); s=orig.replace(' The actual reference image files were not supplied for this text experiment.','')
 # Analysis is tracked outside executable prompts; unresolved source contradictions remain flagged in review.
 s=s.replace(' The source says fixed and also a very slow slight push from medium to close while keeping both in frame.', ' The camera is fixed and also makes a very slow slight push from medium to close while keeping both in frame.')
 s=s.replace(' The source describes the line as both complete and still in progress at the end of this shot.', ' His speech is still in progress at the end of this shot.')
 s=s.replace(' The source repeats the dialogue field <d>[Chinese] 我以为你会留下来。</d> while also saying the first shot spoke it completely and the speech continues here then cuts off.', ' His speech continues from the previous shot and then cuts off.')
 s=s.replace('as the source allows','').replace('the source’s specified ','').replace('the source’s ','')
 # Place additional observations in the shot to which the source field applies.
 for n,extra in enumerate(additions,1):
  pattern=rf'(\[Shot {n}\][^\n]*)(\n)'
  s,count=re.subn(pattern,lambda m:m.group(1)+' '+extra+m.group(2),s,count=1)
  if count!=1:raise ValueError((scene,method,n))
 p=folder/'prompt-v2.txt'; p.write_text(s)
 m=json.loads((folder/'metadata.json').read_text());m.update(revision='v2',previous_prompt_sha256=hashlib.sha256(orig.encode()).hexdigest(),prompt_sha256=hashlib.sha256(s.encode()).hexdigest(),review='Codex manual targeted restoration; source ambiguities and remaining semantic limits documented in review-20261107')
 (folder/'metadata-v2.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print('new revisions',len(extras))
