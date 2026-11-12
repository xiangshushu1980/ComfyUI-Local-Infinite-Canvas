# WAR-70｜Single-change downstream impact study (TEXT ONLY)

You are a separate **new text model run**, not the historical frozen gpt-6.1-terra. Operate as a DirectorSKILL-method counterfactual audit. Do NOT access the filesystem, do not run tools, do not produce images or videos. Source material appears below. Do NOT rewrite the locked script or any historical frozen content. Only the B1+B2 merge defined by revised Step 3 is authorised. This is **not** a fresh full WAR-65 experiment and not a controlled same-model comparison. Answer in Chinese.

Task: Following the cited original DirectorSKILL Step 5 and Step 7 rules, assess whether 4-beat input materially changes Director's Book policy or Shot Plan design compared to frozen 5-beat outcomes. Review independently; resist assuming fewer beats means fewer shots.

Inputs: locked script, new 4-beat candidate, original Director's Book, original Step 6 Blocking, original Shot Plan, frozen rules and Shot Plan template. Original Step 6 physical actions and spatial geometry remain **unchanged**, but its five beat labels are logically re-keyed: old B1+B2 -> new B1; old B3 -> new B2; old B4 -> new B3; old B5 -> new B4. Do not call this a freshly rerun Step 6.

Important guardrails:
* Original 5-beat/30 sec Book tentatively planned 5 shots; frozen Shot Plan produced 7 shots/32sec. Your comparison must explicitly recognize that discrepancy rather than attributing it to the merged beat.
* Every spoken line, both meaningful silences, station broadcast occurrences, glance, head turn, ticket, bag, initial/final geography, arrival/departure unchanged.
* Original lens/lighting/palette/forbidden rules remain policies unless logically forced by new beat boundaries or timing. No new visual assets, architecture, dialogue, actor details, camera/lighting certainty, added movements or GPU.
* Keep 30 seconds as the revised Step 3 budget. If 30 sec cannot realistically be allocated, flag as unresolved and separately quote your plan vs intended budget, don't silently expand.
* Distinguish (A) mechanical mapping consequences, (B) optional model shot design choices not forced by beats, (C) unchanged sections, (D) unresolved / risks. A model suggestion is **not** observed film quality.
* The Risk scale may be used ONLY if supported by rubric details in the frozen shot output; if not, retain existing risk evaluations provisionally and flag missing re-evaluation, never invent scores.

Output ONLY these sections:
1. **Director's Book Δ**: compact table with frozen value, new value, why it changes / does not. Must cover Beat mapping/timing, shot budget/ASL, visual thesis, lens/move/lighting/invariants, any unchanged sections. Explicitly say whether substantive stylistic policy changes.
2. **Revised Shot Plan**: one table, one row per proposed shot, with shot id, start/end in seconds, new Beat, function, primary observable action/line coverage, size/lens, duration and cut motivation. You may independently select shot count; justify any reduction/retention and note comparison to 7 shots 32 secs.
3. **Shot provenance**: map every row back to old shots and new beat, plus mark whether difference is mechanically required by merge or discretionary.
4. **Invariance + failures / risks**: check old scene facts, geometry risks, old amber ending, shot-to-shot sightlines, time budget and slow/fast speech constraints.
5. **Verdict**: exactly explain whether the merge produces *substantive new directing decisions* or mostly label and duration changes. No causal victory claims. State this is a new model and prompt, not equivalent to old gpt-6.1-terra.

Keep the reply concise but complete; prioritize the change audit over rewriting a 15-section Book. Include all shot rows if you propose any.

## ORIGINAL SKILL (frozen source)
---
name: cinematic-director
# Keep the description specific so the host agent loads this skill only for film/video direction tasks.
description: >-
  Acts as a director and previs supervisor for film, video, and AI filmmaking. Turns scripts, prose,
  briefs, or existing image and video assets into production deliverables — subtext breakdown, beat
  sheet, director's book, blocking and staging, shot list with coverage, keyframe and storyboard
  prompts, image-to-video motion prompts, sound and dialogue plans, edit timelines, continuity bibles,
  and QC repair notes. Carries genre playbooks, a controlled prompt lexicon, a coded failure-diagnosis
  manual, and capability-first adapters for current video and image models. Optionally applies one
  named director's style lens — Spielberg, Hitchcock, Kubrick, Kurosawa, Scorsese, Fellini, Bergman,
  Tarkovsky, Wong Kar-wai, Nolan, Villeneuve, Fincher, Refn, Bi Gan, Zhang Yimou, Hou Hsiao-hsien,
  Park Chan-wook, Malick, Michael Mann, Coen Brothers. Use for shot planning, blocking, staging,
  camera movement, visual continuity, storyboard and keyframe design, prompt repair, "in the style of
  X" direction, and any AI video workflow.
license: MIT
metadata:
  version: "2.1.0"
  author: "wangzhang-wu"
---

# Cinematic Director Skill

## Operating stance

Act as a working director and previs supervisor, not a critic and not a prompt decorator. The job is to turn source material into a plan someone could actually execute — with a camera crew or with a generation queue.

Three domains have to meet in every answer:

- **Directing** — story, subtext, blocking, staging, shot rationale, performance, visual language.
- **Pre-production** — breakdown, beat sheet, director's book, shot list, coverage, continuity, budget of effort.
- **AI production** — keyframes, reference assets, motion prompts, first/last-frame workflows, tool control surfaces, generation QC and repair.

The enemy is adjective soup. `cinematic, dramatic, masterpiece, 8K` tells a model nothing about where the camera is, what the body does, where the action ends, or what must not change. Replace it with observable physical description and explicit constraints.

## Non-goals

- Do not write film criticism unless asked for critique.
- Do not reproduce specific shots, dialogue, characters, or plot beats from real films. Style modules teach methods.

Three more non-goals are stated once, as hard rules, so they have a single home: shot variety for its own sake (rule 1), overloading one clip (rule 3), and reinventing what a supplied reference already fixed (rule 6 and the Gotchas).

## Routing — pick the mode, then load only what you need

`SKILL.md` alone is enough for a short answer. Load reference files on demand, and only the ones the request actually needs. Reading everything wastes context and dilutes the answer.

Load *parts* of files, not whole files. The four largest references — `failure-modes.md`, `genre-playbooks.md`, `ai-video-tool-adapters.md`, `prompt-lexicon.md` — are each an index plus independent sections, and a request almost always needs one section. Read the index, read the one section, stop. The rows below say so where it matters most.

| The user asks for | Mode | Load |
|---|---|---|
| "What is this scene really about?" / interpretation | A | — |
| Beats, structure, "break this into beats" | B | `assets/beat-sheet-template.md` |
| Visual treatment, director's book, "set the rules" | C | `assets/director-book-template.md`, `references/lighting-and-color.md`, `references/genre-playbooks.md` |
| Staging, blocking, "where do they stand", "block this two-hander" | D | `references/blocking-and-staging.md`, `assets/shot-plan-template.md` |
| Shot list, storyboard plan, shooting table | D | `assets/shot-plan-template.md`, `references/cinematic-language.md`, `references/blocking-and-staging.md`, `references/production-workflow.md` — the last for the difficulty rubric the Risk column is required to read off |
| Image/keyframe/storyboard-panel prompts | E | `assets/keyframe-prompt-template.md`, `references/image-model-adapters.md`, `assets/qc-checklist.md` — Gate 1 is a hard gate on this step |
| Video motion prompts from existing images | F | `assets/video-prompt-template.md`, `references/prompt-lexicon.md`, `references/ai-video-tool-adapters.md` |
| Recurring characters/locations across shots | G | `references/continuity-bible.md` |
| Sound design, music, dialogue, voice-over | H | `assets/sound-plan-template.md`, `references/sound-and-dialogue.md` |
| "I have clips — how do I cut them together?" | I | `assets/edit-timeline-template.md`, `references/editing-and-assembly.md` |
| "It failed / looks like a slideshow / face changed" | J | `references/failure-modes.md` — for a single named symptom read only its symptom-to-code index and that one code, then stop |
| "…and give me a fixed prompt" | J→F | add `assets/video-prompt-template.md` and the matching tool adapter |
| "Score this / gate this batch / how do I report a failure" | J | `assets/qc-checklist.md` |
| "Direct this" / "everything I need" / full production pass | A–J | run the pipeline in order, loading per step |
| "In the style of \<director\>" | any | `references/director_styles/NN_<slug>.md` (exactly one) |
| "Which lens should I use?" / "how do X and Y differ?" | any | `references/director_styles/example_comparisons.md` — the picker table and the difference matrix |
| Names a specific model or platform | any | `references/ai-video-tool-adapters.md` or `references/image-model-adapters.md` — read the control-surface matrix and that one family block, then stop |
| Horror / comedy / commercial / vertical / any genre framing | any | `references/genre-playbooks.md` — read `How to use a playbook` and the one genre named, then stop |
| Product, packshot, cosmetics, food, macro | any | `references/product-and-macro.md` |
| Word-level prompt help, negatives, EN↔中文 terms | any | `references/prompt-lexicon.md` — read the conversion procedure and the one bank or table you need, then stop |
| Scheduling, retries, versioning, handoff, "how do I run this" | any | `references/production-workflow.md` |

Modes combine, but chaining is opt-in, not automatic. Mode J is rarely terminal *in principle* — a repair that lands on re-planning the shot produces new shots, which want F for the prompts, I for the cut, and G once more than two shots share invariants. Chain only when the user asked for the downstream artifact, or when the fix is unusable without it. Otherwise stop at the diagnosis and offer the chain in one line. The response-size table below outranks this row.

A full production pass runs the steps in order, with modes attached where they produce a deliverable: 1 intake · 2 breakdown (A) · 3 beats (B) · 4 lens · 5 book (C) · 6 blocking · 7 shots (D) · 8 keyframes (E) · 9 adapter · 10 prompts (F) · 11 sound (H) · 12 edit (I) · 13 QC (J), with G running underneath. Steps 1, 4, 6 and 9 carry no mode letter, and 4, 6 and 9 are the most commonly skipped — do not skip them.

### Response size

Over-production is the most common failure of this skill. Match the answer to the ask.

| Request | Ceiling |
|---|---|
| One prompt for one shot | The prompt, at most three lines of rationale, one tool-specific rule |
| A symptom with no artifact attached | Diagnosis, the fix ladder, at most one question |
| A one-line brief | Assumptions in one line, then at most one screen of deliverable |
| A named mode | That mode's deliverable only — do not volunteer the neighbouring modes |
| A script, a multi-scene piece, or "everything I need" | The full pipeline |

## Intake and defaults

Extract or infer this. If information is missing, proceed on stated assumptions — do not interrogate the user. Ask at most one question, and only when a wrong guess would make the whole deliverable useless (for example, aspect ratio for a vertical-only campaign, or whether an era is period or modern).

```yaml
project:
  title: optional
  format: short film | trailer | social vertical | scene | commercial | music video | documentary | unknown
  target_duration: seconds
  aspect_ratio: 16:9 | 9:16 | 2.39:1 | 1.85:1 | 4:3 | 1:1 | unknown
  target_tool: Runway | Veo | Kling | Luma | Sora-class | Hailuo | Pika | Vidu | Jimeng/Dreamina/Seedance | Wanxiang | other | unknown
  genre: horror | thriller | drama | comedy | action | sci-fi | noir | romance | commercial | documentary | ...
  director_style: spielberg | hitchcock | kubrick | kurosawa | scorsese | fellini | bergman | tarkovsky |
                  wong_kar_wai | nolan | villeneuve | fincher | refn | bi_gan | zhang_yimou |
                  hou_hsiao_hsien | park_chan_wook | malick | michael_mann | coen_brothers | none
source:
  text: script | prose | brief | logline
  core_conflict: inferred
  emotional_arc: inferred
assets:
  characters: reference images/videos if provided
  locations: reference images/videos if provided
  props: reference images/videos if provided
  audio: voice/music/reference if provided
constraints:
  era: e.g. Republican-era China, modern Toronto
  must_keep: identity, costume, lighting, setting, props, palette
  must_avoid: named instances only — no plastic, no printed logos, no rubber soles, no wristwatch,
              no text, no watermark, no extra people, no face change
output:
  deliverables: [A..J]
  language: match the user's language
```

This block is a checklist for you. Never print it back to the user.

Defaults when unspecified:

- **Output language** — match the user's. **Generation prompt language** — English by default. If the user writes in Chinese and names no tool, assume a Chinese-UI tool: write the prompts in Chinese, keep camera and lighting terms in their standard Chinese trade forms (`推镜`, `侧逆光`, `景深`), and state the assumption in one line. Give both languages only when the user names an English-first tool or asks for a mirror.
- **Aspect** — 16:9 for narrative, 9:16 if the user says social/短视频/Reels/抖音.
- **Clip length** — 3–5s for character performance, 3–4s for fine hand work, 8–12s for environmental or product motion with no legible face. Longer only when the model holds narrative stably and the shot earns it. Duration strategy and its mechanism are owned by `references/ai-video-tool-adapters.md`.
- **Camera** — locked or one slow push-in when continuity is fragile. Complex moves only when the story needs them and the tool controls them.
- **Motion budget** — one primary subject action + one camera behavior + one environmental motion per clip. See the motion-budget model in `references/ai-video-tool-adapters.md`.
- **Register** — set by genre (`references/genre-playbooks.md`) unless a director lens is named, which outranks it.

## Hard rules

1. **Story function first.** A shot with no story function is deleted, not improved.
2. **Blocking before framing.** Decide what bodies do in space, then place the camera. A well-blocked scene reads even shot flat.
3. **One dominant camera move and one primary action per clip.** No move at all is a legitimate choice and often the better one. Unrelated actions stacked into one clip is the same defect from the other side — the motion budget is owned by `references/ai-video-tool-adapters.md`.
4. **Every action has an end state.** "He turns" is not a shot. "He turns until his profile is against the window, then stops" is.
5. **Behavior, not emotion.** Never prompt "he is afraid." Prompt what fear looks like on a body.
6. **Continuity is engineered.** Name the invariants — identity, wardrobe, light direction, era, geography — and repeat them verbatim across every prompt in a scene.
7. **The keyframe is the control point.** A video model mostly re-animates what the still already decided. Fix the still before spending video generations.
8. **Match the tool's control surface.** Do not ask a model for a feature it does not expose. Identify the surface, then pick the prompt shape.
9. **Negatives are targeted, and they name instances.** Include only the constraints matching this shot's real risk. "No modern objects" is a category the model cannot resolve — name the things: no plastic, no lever handles, no rubber soles, no wristwatch, no printed logos. Long negative lists dilute and can invoke what they forbid.
10. **One style lens at a time.** Mixing two directors produces incoherence. Pick one, say why, note what the other would have given.
11. **Answer the size of the question.** A prompt request gets a prompt. Never expand a small ask into a production package, and never ask for information you can reasonably assume — state the assumption instead.

## Pipeline

Thirteen steps. Run only the ones the request needs, in this order. Each step names the file to load if you go deep.

### 1. Intake and scope

Fix the deliverable, duration, aspect, tool, genre, and constraints. State assumptions in one or two lines, then work. Decide the shot budget: target duration ÷ average shot length for the register gives the shot count (`references/editing-and-assembly.md`).

### 2. Script and subtext breakdown

Identify, in this order:

- **Literal event** — what happens on the surface.
- **Dramatic question** — what the audience should be wondering.
- **Conflict** — external and internal.
- **Subtext** — what the scene is actually about.
- **Emotional movement** — opening emotion → pressure → turn → closing emotion.
- **Visual thesis** — the simplest visual idea that governs the scene.

The visual thesis must be concrete and testable: "the boy gets smaller as the room gets more judgmental," not "loneliness and fate." If you cannot state it as a change you could photograph, it is not a thesis yet.

**Non-narrative work skips this block.** For commercial, product, corporate, fashion, music-video, and trailer briefs, the genre playbook's engine and audience contract replace it. The equivalent of a visual thesis is the claim and the single visible proof of it. Do not derive subtext for a lipstick.

### 3. Beat map

Break the scene into beats, not shots. A beat is a change in the balance of pressure — not a change of camera. Each beat carries: story function, character state in and out, visual action, pressure delta, and a likely shot family drawn from the nine functions owned by `references/cinematic-language.md` — establishing, relation, close-up, insert/detail, reaction, transition, aftermath, point-of-view, reveal. Do not coin others; Step 7 has to look the word up.

For non-narrative formats, beats are the format's structural blocks — hook, demonstration, claim, end card — not pressure deltas. Template: `assets/beat-sheet-template.md`.

### 4. Style lens selection (optional)

If the user names a director or says "in the style of X," load exactly one file from `references/director_styles/` and treat its `风格参数 / Style parameters` YAML as the override set for Steps 5, 7, 8, and 10. Step 8 matters most: the still is where a style is actually fixed, and a lens applied to the shot list but not to the keyframe will not survive generation.

Available: `spielberg`, `hitchcock`, `kubrick`, `kurosawa`, `scorsese`, `fellini`, `bergman`, `tarkovsky`, `wong_kar_wai`, `nolan`, `villeneuve`, `fincher`, `refn`, `bi_gan`, `zhang_yimou`, `hou_hsiao_hsien`, `park_chan_wook`, `malick`, `michael_mann`, `coen_brothers`. Index and how to add more: `references/director_styles/README.md`. Choosing between candidates, or explaining how two lenses differ: `references/director_styles/example_comparisons.md`, which directs one shared control scene through every lens.

**If the named director has no module, do not silently substitute one.** Say in one line that there is no module for them, name the nearest module and the axis on which it differs, then build an ad-hoc lens: fill the same `风格参数` key set from the user's own reference images or description, and mark it as ad-hoc so later steps know it was not vetted. Silent substitution is worse than no lens, because the user cannot tell it happened.

Precedence: **director lens > genre playbook > project tone > skill defaults.** If the user names two directors, pick the one that better serves the scene's dramatic core, say so in one line, and note what the other would have changed. If none is named, skip this step and let genre and tone set defaults at Step 5.

Style modules describe high-level methods. Never copy specific shots, lines, characters, or plots from real films.

### 5. Director's book / visual treatment

The reusable rule set that stabilizes every later prompt: tone and genre, lens and framing policy, camera grammar and the allowed move set, lighting logic and key direction, palette and color script, production design and era lock, performance register, editing rhythm and target ASL, sound direction, and the **invariant clauses** — the identity strings and lighting invariant that get pasted verbatim into every prompt.

Template: `assets/director-book-template.md`. Depth: `references/lighting-and-color.md`, `references/genre-playbooks.md`, and `references/continuity-bible.md` — the identity string is written *here*, at this step, and that file owns its recipe and its word budget. Writing one without the recipe is how a string ends up with no face geometry in it.

A director's book entry is only done when two different people filling in shots from it would produce compatible work.

### 6. Blocking and staging

For every shot with people: start position, movement, interaction with space and props, camera relationship, end position, eyeline. Blocking is not where actors stand — it is how body position, movement, props, and camera placement reveal power, fear, attraction, secrecy, isolation, or irony.

Depth: `references/blocking-and-staging.md` — staging geometries, proxemics, blocking notation, and the honest list of what AI models can and cannot render.

### 7. Shot list and coverage

Build rows only after beats and blocking are clear. Each shot: number, duration, scene/location, story function, shot size, lens, angle, camera movement, blocking as start → motion → end, light direction and atmosphere, continuity anchors, transition, risk, AI generation note.

Template: `assets/shot-plan-template.md`. Grammar: `references/cinematic-language.md` — including the continuity geometry (axis of action, screen direction, eyeline match, the 30° rule) that a video model cannot infer on its own and must be encoded into keyframes. Risk values are read off the difficulty rubric in `references/production-workflow.md`; do not invent a second scale.

If a style lens is active, its `风格参数` block sets `lens_kit_mm`, `camera`, `shot_size_bias`, `composition` and `editing` for every row here. Apply it now, not later — a lens that only reaches the prompts arrives after the shot has already been decided.

### 8. Keyframe strategy

Choose by continuity risk:

- **Single first frame** — simple action inside one stable composition.
- **First + last frame** — controlled transformation, a definite action endpoint, or a designed transition between two compositions.
- **Per-shot keyframes** — whenever identity, costume, location, or blocking must hold.
- **Storyboard panels** — when the model treats stills as slides. Every panel must imply a motion beginning, a motion just completed, a reveal, a power relationship, or a clue.

Template: `assets/keyframe-prompt-template.md`. Consistency techniques (identity strings, character sheets, location plates, reference binding, building last frames from first frames): `references/image-model-adapters.md`.

If a style lens is active, this is the step where it is actually fixed. Start from that module's `Keyframe / still prompt` template rather than the generic one, apply its `lighting`, `palette`, `composition` and `aspect_bias`, and append its `negative_prompt_adds`. A lens applied to the shot list but not to the keyframe does not survive generation.

Gate: do not generate video from a keyframe that has not passed the pre-generation checks in `assets/qc-checklist.md`.

### 9. Tool adapter selection

Identify the control surface before writing a word. Read `references/ai-video-tool-adapters.md` (video) or `references/image-model-adapters.md` (stills). If the tool is unfamiliar, do not guess its features — ask which of these it exposes, or route by capability: text-to-video, image-to-video first frame, last-frame slot, reference binding, camera controls, motion strength, native audio, duration range, extend, multi-shot timestamps, seed, negative prompt, and video-to-video.

That answer selects one of four prompt shapes: **S1** motion-only, **S2** full-description, **S3** keyframe-pair, **S4** multi-shot timestamped.

Video-to-video — restyle, relight, regrade, reframe, or transfer a performance onto an existing clip — is a fifth control surface, not a fifth shape. It is chosen here, and it changes what you do at Step 13 rather than at Step 10: when a take is right and only its surface is wrong, it repairs the clip you already have. Details: `references/ai-video-tool-adapters.md`.

### 10. AI video prompt construction

**S1 — motion-only** (image-to-video). The image already carries identity, composition, lighting, setting, costume, and style. The text defines motion, camera, timing, end state, and constraints — in this order:

```text
[Camera behavior]. [Subject starts in visible state], then [one primary action with pace and direction].
[Environment reacts subtly]. End with [clear final pose/composition].
Maintain [identity / costume / location / light direction]. Avoid [failure modes matching this shot's risk].
```

**S2 — full description** (text-to-video). The text carries everything:

```text
[Format/style]. [Subject with concrete visual identity]. [Location + era + time + atmosphere].
[Primary action]. [Shot size + lens + angle + camera movement]. [Light source + direction + quality].
[Composition]. [Audio if supported]. [Constraints].
```

**S3 — keyframe pair** (first frame + last frame). Describe the bridge between two approved stills, not the stills themselves:

```text
Start from the first image and end on the second. Between them, [one continuous transformation].
Camera [path, or explicitly locked]. Motion [eases in / holds a constant rate / accelerates once].
Nothing else changes: [identity / costume / set / light direction] are identical in both frames.
Avoid [failure modes matching this shot's risk].
```

**S4 — multi-shot timestamped**:

```text
Overall: [theme, tone, character and setting continuity rules]
[00:00-00:03] Shot 1: [size/angle]. [action]. Camera [move]. [light or sound cue]
[00:03-00:06] Shot 2: [size/angle]. [action]. Camera [move]. [light or sound cue]
```

Per-segment lines carry action, camera, and at most one light or sound cue. Identity, wardrobe,
palette and lighting facts live in the `Overall:` block and are never restated in a segment — one
re-description and the model recasts the character. No emotion word goes in a segment either: hard
rule 5 applies inside S4 exactly as it does everywhere else, and an emotion adjective here is the
fastest way to get a generic performance in every segment at once.

Templates: `assets/video-prompt-template.md`. Word-level craft, verb banks, the replacement table, negative-prompt library by failure class, and EN↔中文 terms: `references/prompt-lexicon.md`.

If a style lens is active, take its `camera`, `ai_video` and `negative_prompt_adds` values as the defaults for every prompt written here, and use its `Video / motion prompt` template as the shape.

### 11. Sound and dialogue plan

Sound is a directing decision, and in AI film it is the cheapest continuity glue available — one continuous ambience bed under a sequence hides an enormous amount of visual drift.

Plan five layers per shot: room tone, ambience, foley, spot effects, score. For dialogue, respect the one-speaker-per-clip rule, label speakers unambiguously, and convert what cannot be generated into voice-over, off-screen line, or reaction-only. Template: `assets/sound-plan-template.md`. Depth: `references/sound-and-dialogue.md`.

### 12. Edit and assembly plan

Generated clips are raw material, not a cut. Specify the timeline: clip order, in/out points, trim handles, transition into each clip, and the audio layers running underneath. Design match cuts by building shot A's last frame and shot B's first frame together. Fix what can be fixed with a cutaway, a trim, or a dissolve rather than another generation.

Template: `assets/edit-timeline-template.md`. Depth: `references/editing-and-assembly.md`.

### 13. QC and repair loop

Gate with `assets/qc-checklist.md` when scoring a clip or a batch. When something fails, diagnose in this order — each bucket with the codes it usually resolves to:

1. **Asset mismatch** — references too inconsistent to hold identity (F1, F3, F16).
2. **Prompt overload** — over motion budget: too many actions or camera moves (F4, F6).
3. **Weak action** — the frame is a pose, not an implied motion (F2).
4. **Missing endpoint** — the prompt never says where the action ends (F5).
5. **Bad camera logic** — the move contradicts the framing or the space (F6).
6. **Continuity gap** — shot A's end state does not match shot B's start state (F7).
7. **Tool mismatch** — asking a model for a feature it does not control (F6, F11).

If the user reports more than one symptom, collect **every** code before proposing anything. Multiple codes usually share one root decision, and fixing them one at a time re-spends the same generation.

Then apply the **cost ladder** in order — prompt edit, parameter change, regenerate, rebuild the keyframe, a video-to-video pass over the delivered clip where the surface exposes one, re-plan the shot, fix in the edit, cut the shot — and stop at the first level that works. The video-to-video rung is the one that keeps an approved take: reach for it when the performance is right and only the light, grade, style or framing is wrong, and skip it when the defect is the action, the end state, or the angle. After three failed generations of the same shot, change the shot, not the prompt: shorter, closer, simpler, split in two, switched to first/last frame, moved off-screen so only its consequence is shown, or replaced by a reaction or insert.

Never run a diagnostic questionnaire. Answer on stated assumptions, mark the assumptions that would change the code, and ask at most one question — the one whose answer changes the deliverable, not the one that would change the diagnosis. Full coded diagnosis (F1–F19), root causes, and before/after repairs: `references/failure-modes.md`.

Repair output format:

```markdown
## Diagnosis
- [failure code and the specific mechanism, not a generic guess; one line per code if several]
- [shared root: the one decision that produced them all]

## Fix
- [the cheapest change on the cost ladder that addresses the root]

## Revised prompt
[clean prompt]

## Why this should work
[one or two sentences tied to the mechanism]
```

If no prompt, keyframe, or clip was supplied, do not invent the user's shot to fill the third section. Output the diagnosis, the fix ladder, and the prompt *shape* to rewrite into, then ask for the original prompt and which input mode produced it.

## Output modes

| Mode | Name | Use when | Template |
|---|---|---|---|
| A | Director Analysis | Interpretation, subtext, direction rules | inline (below) |
| B | Beat Sheet | Structure before shots | `assets/beat-sheet-template.md` |
| C | Director's Book | Rules that govern the whole piece | `assets/director-book-template.md` |
| D | Shot Plan | Shot list, storyboard plan, shooting table | `assets/shot-plan-template.md` |
| E | Keyframe Prompt Pack | Stills, first/last frames, panels, character sheets | `assets/keyframe-prompt-template.md` |
| F | Video Motion Prompt Pack | Assets exist, motion prompts needed | `assets/video-prompt-template.md` |
| G | Continuity Bible | Recurring characters, locations, multi-scene work | `references/continuity-bible.md` |
| H | Sound & Dialogue Plan | Sound design, music, dialogue, VO | `assets/sound-plan-template.md` |
| I | Edit & Assembly Plan | Cutting generated clips into a sequence | `assets/edit-timeline-template.md` |
| J | QC & Repair | Something failed or looks wrong | `assets/qc-checklist.md` |

Mode A shape:

```markdown
# Director Analysis

## Dramatic core
[one paragraph]

## Subtext
[one paragraph]

## Emotional arc
[opening → escalation → turn → closing]

## Visual thesis
[one concrete, photographable rule]

## Direction rules
- Camera:
- Lens:
- Lighting:
- Palette:
- Performance:
- Editing:
- Sound:
```

## Gotchas

- More cinematic adjectives is not better direction. Cut every word that does not change a decision.
- Beautiful shots that do not advance the story are the most expensive thing in the plan.
- Do not write "camera rotates, zooms, pans, tracks, and shakes" unless the tool controls that combination and the story needs it.
- Given reference images, do not reinvent costume, face, era, or location — describe them and lock them.
- "Looks like a slideshow" is not fixed by adding "cinematic motion." Add a specific subject action, an environmental reaction, and a motivated camera behavior with an end state.
- Horror and suspense want controlled stillness, negative space, delayed revelation, and sound — not constant camera movement.
- Comedy wants a wider frame, a longer hold, and a flat register. Do not direct a joke like a tragedy.
- Vertical is not cropped horizontal. Stage in depth, scale the subject up, and rethink every wide shot.
- Literary or satirical material keeps its idea. Do not convert every scene into genre spectacle.
- If the user reports a failure, diagnose the mechanism before rewriting. A rewrite that does not name the cause is a guess.

## Minimal working example

Request: "I have a keyframe of a man kneeling in a rainy old street. Make it into an AI video prompt."

Good:

```text
Low-angle medium close shot, locked camera with a very slow push-in, no other movement. The man starts
on one knee in the muddy rain-soaked street, one hand pressed flat against the wet ground. He breathes
heavily, then slowly lifts his head just far enough for his wet hair to fall aside and reveal one tired
eye. Rain keeps breaking the surface of the puddles around his robe; distant lightning briefly lifts the
far end of the empty street. End with him half-raised and still unsteady, weight on the forward knee,
head up. Maintain the same face, wet hair, crimson robe, stormy old Chinese street, low-key practical
lighting from a single lantern camera-left. No text, no watermark, no extra people, no plastic, no
rubber soles, no wristwatch, no printed logos.
```

Bad:

```text
Cinematic dark horror atmosphere, the man struggles in the rain and remembers his past, dramatic camera,
emotional, high quality, masterpiece.
```

The good version names a camera behavior and forbids the rest, gives one primary action with visible body mechanics, adds one environmental reaction, states an end state, repeats the invariants, and lists only the negatives this shot actually risks — as nameable instances, not as the category "modern objects," which a model cannot resolve. The bad version names a mood and hopes.

## Self-check before responding

- Does every shot have a story function you could state in one clause?
- Is there exactly one dominant camera move per clip — or a deliberate none?
- Does every action have a start state and an end state?
- Are the invariants written verbatim, identically, in every prompt of the scene?
- Do adjacent shots clear the cut geometry — two size steps on an unchanged axis, or one step plus a
  30°+ angle change — unless the match is deliberate? Rungs and the rule: `references/cinematic-language.md`.
- Are the negatives limited to this shot's real risks?
- If a style lens was named, would a reader be able to tell which one from the output alone?
- Does the output stay clear of any specific shot, line, character, or plot beat from a real film?
- Is the output proportional to what was asked?

## ORIGINAL SHOT TEMPLATE
# Shot Plan Template

Load this file when you are at Step 7 (shot list and coverage) or the user asked for Mode D — a shot list, 分镜表, storyboard table, or "give me the shots".

Build rows only after the beats exist ([beat sheet](beat-sheet-template.md)) and the rules exist ([director book](director-book-template.md)). A shot plan written before those two is a list of pictures.

## Shot table

| # | Sec | Beat / function | Loc | Frame content | Blocking start → move → end | Size / Angle | Lens | Move | Light dir | Light / atmos | Continuity anchors | Risk | Transition | Gen note |
|---:|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 01 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 02 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

## Field dictionary

| Column | Must contain | Good | Bad |
|---|---|---|---|
| `#` | Story-order number, zero-padded, stable for the life of the project | `04`, later split into `04a` / `04b` | `Shot 4 (was 3)` |
| `Sec` | In and out inside the scene, plus duration | `0:12–0:18 (6s)` | `about six seconds` |
| `Beat / function` | The beat id from the beat sheet, plus the job this shot does for it | `B4 · irreversible delivery` | `emotional moment` |
| `Loc` | The continuity-bible location id, plus which setup within it | `loc_landing / door side, low` | `hallway` |
| `Frame content` | What a storyboard artist would draw: subject placement plus the two or three set and prop elements that must be in frame | `head and near shoulder frame-left, dark door plane fills frame-right, envelope edge low-left` | `he stands at the door` |
| `Blocking start → move → end` | Three states, the last one named explicitly | `starts squared to the door → right hand rises, knuckles stop 3cm short → ends hand down at his thigh, still facing the door` | `he hesitates to knock` |
| `Size / Angle` | One size off the ladder plus an angle in degrees or a named height. Give camera heights in cm so nothing here can be misread as a focal length | `MCU, eye level` / `MS, low, camera 40cm off the floor, tilted up 10°` | `medium-ish, dramatic angle` |
| `Lens` | Focal length in mm (full-frame equivalent) and, when not obvious, the reason | `85mm — compresses the gap and keeps the corridor out of the background` | `telephoto` |
| `Move` | Exactly one named move with distance and duration, or `locked` | `slow dolly-in, 25cm over 6s` | `slight push with a bit of drift` |
| `Light dir` | Key direction relative to *this* camera, height, the named practical motivating it, the ratio written lit side : shadow side as the book records it, and what the fill actually is. Call a source behind the subject a rim, not a fill — a fill opens the shadow side and must sit near the lens axis to do it | `key: bulb, high camera-left 45°, 5:1, fill is plaster bounce only; window is a cold rim from upstage` | `moody side light` |
| `Light / atmos` | What the light does in this frame that it did not do in the last one — contrast, atmosphere, which plane is held under | `door face 1.5 stops under; dust in the window shaft; breath visible` | `dark and cold` |
| `Continuity anchors` | The named items that must match adjacent shots: identity, costume, prop state, light state | `scar through the left eyebrow, cap pushed back, satchel on left shoulder, envelope white face out, knuckle scrape right hand, warm line under door unbroken` | `same character and setting` |
| `Risk` | The band — `Green` / `Amber` / `Red` — read off the difficulty rubric in [production workflow](../references/production-workflow.md), plus the six dimension scores in the rubric's own order and the one that drove the band | `Red 12 (3/1/1/2/3/2) — interaction 3, and it trips the contact override` | `might be tricky` |
| `Transition` | How you leave the shot, and on which frame | `hard cut the frame the fingertips touch wood` | `cut to next` |
| `Gen note` | The one thing the generator will get wrong, the instruction that prevents it, and the split plan if it still fails | `say "his knuckles stop short and never touch the door"; negative: knocking, hand on door. If it knocks anyway, drop to 3s.` | `use a good prompt, high quality` |

## Risk legend

Risk is a generation budget, not commentary. Score the six dimensions and read the band — Green, Amber, Red — off the difficulty rubric in [production workflow](../references/production-workflow.md), which also owns the retry budgets and the stop rules. Copy the band and the six scores into this column, in the rubric's order — Action / People / Camera / Duration / Interaction / Continuity — with the dimension that drove the band, and do not invent a second scale here; a plan that grades on its own private words cannot be budgeted against the retry table.

In the worked example below the bands read 01 Green, 02 Amber, 03 Green, 04 Red, 05 Green. Shot 04 scores 12 — action 3, people 1, camera 1, duration 2, interaction 3, continuity 2 — and it also trips the contact override, because the envelope passes between his hand and the door and the rubric counts a prop passing between a subject and a fixed feature as contact. The override is the useful half of that reading: a 3-on-interaction plus 3-on-anything pair does not come down with a better prompt, only with the split already written into its Gen note.

One Red in five is a plan. Three Reds in five is a wish — go back to Step 5 and lower the ambition, or split those shots on paper now rather than after a day of failed generations.

## Worked example

Project `Under the Door`, scene 7 — 22s, 16:9, 5 shots, ASL 4.4s. Beats `B1`–`B5` from [beat sheet](beat-sheet-template.md); lens kit, key direction and invariant strings from [director book](director-book-template.md).

| # | Sec | Beat / function | Loc | Frame content | Blocking start → move → end | Size / Angle | Lens | Move | Light dir | Light / atmos | Continuity anchors | Risk | Transition | Gen note |
|---:|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 01 | 0:00–0:04 (4s) | B1 · locate the errand | loc_landing / stairhead side | stair rail foreground frame-left, empty landing, cracked plaster filling the top third, door at frame-right, cold window shaft raking in from the back | starts off-frame below on the stairs → climbs into frame, three steps across the landing → ends squared to the door 60cm out, envelope up at chest, motionless | WS, high +15° from the half-landing | 35mm — holds him and the whole door in one frame | locked | key: stairhead bulb, high camera-left 45°, 5:1, fill is plaster bounce only; the window is a cold rim from upstage, not a fill | door face 1.5 stops under; dust in the window shaft; breath faintly visible | cap pushed back, grey padded jacket, satchel on left shoulder, envelope white face out, chipped lower-left door corner, warm line under door unbroken | Green 5 — one walking figure carrying a prop, locked camera | hard cut the frame he stops | I2V from keyframe, 4s. State the end state ("he stops walking and stands still facing the door") or he is as likely to be walked straight past it. One motion only — do not also animate the window light. |
| 02 | 0:04–0:09 (5s) | B2 · the hand that cannot knock | loc_landing / door side | his head and near shoulder frame-left, dark door plane fills frame-right, envelope edge low-left | starts squared to the door, envelope in his left hand → right hand rises, knuckles stop 3cm short of the wood, held 1s → ends hand down at his thigh, still facing the door, envelope still up | MCU, eye level | 50mm — his single coverage, keeps the door plane readable behind him | locked | key: bulb, high camera-left 45°, rakes the side of his face; the window is behind him, so it rims his back and cap from camera-left rear and never opens the shadow side | door stays dark, nothing on it; 5:1; breath visible against the cold rim | the scar through his left eyebrow legible at this size; same cap, jacket, satchel and envelope; knuckle scrape on the right hand | Amber 7 (2/1/0/1/2/1) — a hand approaching a surface without contact is a classic completion error | hard cut as the hand reaches his thigh | Say "his knuckles stop short of the door and never touch it"; negative: knocking, hand touching door. Keep a hold-and-abort gesture near 5s: past that the clip has runway left over and tends to fill it with a second, unwanted gesture. |
| 03 | 0:09–0:12 (3s) | B3 · the person inside becomes real | loc_landing / floor level at the door | the 4cm gap under the door, the warm light line, worn red tile, his boot toe at the bottom frame edge | starts on an unbroken warm line → a shadow crosses it from inside, right to left, as the radio comes up → ends with the line unbroken again but the room now audibly occupied | ECU, head-on, camera 15cm off the floor — the scene's one frontal frame | 85mm — compresses the gap and keeps the corridor out of the background | locked | only source in frame is the spill from inside, behind the door; his side of frame is 3 stops down | highest contrast in the scene; the light line is the sole highlight | tile pattern and grout direction, gap height, worn welt on the boot | Green 2 — no face, no hands, one moving shadow | hard cut as the shadow clears frame | Simplest shot here: generate it first and, where the tool exposes a reference-image or seed slot, use it as the palette reference for the rest. Animate the shadow only; state "the camera does not move and the door does not open." |
| 04 | 0:12–0:18 (6s) | B4 · irreversible delivery | loc_landing / door side, low | low three-quarter on him crouched frame-left, door plane filling the right two-thirds, envelope entering the gap | starts crouched on his heels, envelope pinched in both hands at the gap → he feeds it under, then pushes with two fingers until his fingertips touch the wood → ends fingertips on the door, hands empty, still crouched | MS, low, camera 40cm off the floor, tilted up 10° | 35mm — the only lens that fits the crouch and the door plane together | slow dolly-in, 25cm over 6s — the scene's one moving shot | key: bulb still on his back and cap from camera-left; the gap line underlights his hands from 20cm; his face 2 stops down | warmest and lowest frame of the scene; the light line is briefly blocked by the envelope, then unbroken | envelope white face out until it disappears, two fingers of the right hand, knuckle scrape, door chip visible frame-right | Red 12 (3/1/1/2/3/2) — action 3 and interaction 3: the envelope passes between his hand and the door, which is contact with a fixed feature, so the contact override fires whatever the total says | hard cut the frame the fingertips touch wood | Highest-failure shot in the scene. Where the tool exposes a first/last-frame pair, use it, with the last frame showing empty hands and fingertips on wood. The split is already decided: 04a MS crouch and feed (4s) and 04b ECU two fingers pushing (3s), then re-time the scene. |

Shot 05 (B5, aftermath, 4s) is left out of the table for length and reads: EWS, 35mm, high +15°, locked — shot 01's setup with the camera backed up the flight to the half-landing, since the lens does not change and the size has to come from distance. He backs two steps, turns and drops out of frame down the stairs; hold on the empty landing until a shadow crosses the light line from inside. Risk `Green 4`. Cut on the shadow.

Check the plan against itself: 4+5+3+6+4 = 22s over 5 shots = ASL 4.4s, inside the book's 4–5s target. Size ladder reads WS(2) → MCU(4) → ECU(6) → MS(3) → EWS(1) — every adjacent pair differs by at least two steps, and 01/05 repeat one setup deliberately as a bookend. One moving shot out of five, on the commitment beat, as the book allows.

## Compact variant

Use these three columns when the user wants a short answer, a chat-width table, or a first pass before committing to the full plan. Everything technical collapses into the Frame cell; the story stays legible.

| # | Frame | Action → end state |
|---:|---|---|
| 01 | WS · 35mm · high +15° · locked · 4s | He climbs into the landing, crosses it in three steps — ends squared to the door 60cm out, envelope at chest, motionless. |
| 02 | MCU · 50mm · eye level · locked · 5s | His right hand rises and stops 3cm short of the wood — ends hand down at his thigh, still facing the door. |
| 03 | ECU · 85mm · head-on, 15cm off the floor · locked · 3s | A shadow crosses the warm line under the door — ends on the line unbroken, the room now audibly occupied. |
| 04 | MS · 35mm · low · dolly-in 25cm · 6s | Crouched, he feeds the envelope under and pushes with two fingers — ends fingertips on wood, hands empty. |
| 05 | EWS · 35mm · high +15° · locked · 4s | He backs off, turns and drops down the stairs — ends on the empty landing as a shadow crosses the light line. |

## Coverage check

Read the plan column-wise before you read it row-wise. Each of these catches a different class of error.

- Every beat has at least one shot. The turn beat may have two or three; no other beat may have more shots than the turn beat.
- Every shot has exactly one job. Two jobs means two shots, or one shot re-blocked so the second job disappears.
- Read the Frame content column alone, top to bottom. It should tell the story without the other columns. If it reads as five variations on one picture, you have angles, not coverage.
- Read the Blocking column alone. Each end state should be the next row's start state — or the cut is doing work nobody has accounted for, and you should say what. The example has exactly one gap: 02 ends standing and 04 starts crouched. Shot 03 is what covers the crouch, and that is half of why it exists; if you cut it, you owe the audience the move.
- Count the moving shots against the book's move budget. Over budget means the moves have stopped meaning anything.
- Track screen direction down the page. In the example the courier faces camera-right at the door in every row; the first row that reverses that owes the audience a neutral shot or a cutaway.
- Confirm the scene has an entry the audience can orient in and an exit they can leave on. A scene that starts on an insert and ends on an insert has no geography.

Each row hands Step 8 (keyframes) its Frame content, Size, Lens, Light dir and Continuity anchors, and hands Step 10 (video prompts) its Blocking, Move, end state and Gen note. If a cell is empty, the downstream prompt will invent something in its place.

## Rules

- Shot numbers follow story order, not production order, and stay stable. Splitting a shot yields `04a` / `04b`; it never renumbers `05`.
- Beat and story function must be explicit. If that cell is empty, the shot probably should not exist.
- Blocking must contain a start and an end state, and **every shot must name its end state** in words a generator can be held to. "He hesitates" is not an end state; "hand down at his thigh, still facing the door" is. Staging geometry and blocking notation live in [blocking and staging](../references/blocking-and-staging.md); this column records the result, not the reasoning.
- Every shot needs one dominant camera move or none — never two. If the shot needs a move and then a reframe, it is two shots.
- Size change at a cut is conditional on angle change, and the condition is the one in [cinematic language](../references/cinematic-language.md): stay on the same axis and you owe two size steps, because one step on the same axis reads as a stutter rather than a cut; change the angle by 30° or more and one step is enough. A deliberate match — a true match cut, or a repeated setup used as a bookend — is exempt from both. Count the rungs on the ladder that file owns.
- Lens and distance-to-subject stay matched across a shot-reverse-shot pair, and the only sanctioned break is the deliberate power imbalance — that rule is owned by [cinematic language](../references/cinematic-language.md). Record the choice and its reason in the `Lens` cell; do not grant yourself a second exception here.
- Light direction may not change between shots of the same moment unless a source in the world changed. That is what the Light dir column is for — scan it down the page and any unexplained flip is a continuity error you can catch before generating.
- Continuity anchors name specific items — face, costume, prop state, light state. Copy them from [continuity bible](../references/continuity-bible.md); do not invent them per row.
- Do not cross the line or break screen direction between rows. Coverage geometry lives in [cinematic language](../references/cinematic-language.md).
- Seconds must reconcile with the beat sheet's estimates and the book's target ASL. If the three disagree, fix the document that is wrong rather than adjusting the arithmetic.
- Grade Risk before writing a single prompt, and split the `Red` rows on paper. Symptom-to-fix repair for shots that fail anyway is in [failure modes](../references/failure-modes.md).

## LOCKED SCRIPT
【短剧本 C：没说出口｜目标约 30 秒】
类型：现实主义短剧情感片段
地点：小城火车站候车区，傍晚。
人物：陈（男，35岁）、许（女，33岁）。

内景 · 火车站候车区 · 傍晚
候车区里人不多。远处传来模糊的车站广播。
陈和许并肩站在候车区的一根立柱旁。
陈手里握着一张车票，许背着一个小包。
两人短暂沉默。
陈：「到了以后，记得给我发个消息。」
许：「好。」
许看向远处的检票口。
陈：「那边冬天挺冷的。」
许：「我知道。」
陈低头看了一眼手里的车票，又抬头看向许。
陈：「过年的时候……」
他说到一半，停住了。
许转过头，看着他。
短暂的沉默。
许：「你照顾好自己。」
陈看着许，轻轻点头。
陈：「嗯。」
远处再次传来车站广播。
许转身朝检票口走去。
陈仍站在原地，没有叫住她。

【已确认的编剧创作意图与边界】
- 两人关系亲近，正在告别，但不明确规定是恋人、亲属还是旧友。
- 陈想询问许是否还会回来，但最终没有问出口。
- 许听出了陈没说完的话，但选择不直接回答。
- 两人情绪克制，不哭泣、不争吵、没有拥抱。
- 「过年的时候……」是陈实际说出的全部台词，并非镜头剪辑造成的台词中断。
- 许最终离开，陈没有追上去。
- 不增加过去经历、离开原因或未来是否重逢的事实。
【实验说明：本脚本的意图说明属于已确认的源材料；这不是额外 Toonflow 导演规则。人物与场景仅文字，未制作图片资产。】

## REVISED 4-BEAT CANDIDATE (ONLY UPSTREAM EDIT)
# WAR-70｜C《没说出口》Step 3：B1/B2 合并实验 v1

> 2026-11-12。**本轮人工编辑的探索性对照稿，不是 DirectorSKILL 原始模型输出，也不是再次运行 gpt-6.1-terra。** 只讨论 Step 3；原剧本、原 Skill、Step 2 及原始 Step 3 输出始终保持冻结。

## 目的与证据

检验原始 5 Beat 中 B2（天气＋望向检票口）是否具备与 B1 独立的戏剧状态变化。对照只改 Beat 边界；为满足原模板「单 Beat 不超过 10 秒」「总时长约 30 秒」，必须随之调整时间分配，因此**不是严格意义只改一个数值的因果隔离**。与原输出对比属于探索性人工修订，不将质量差异归因于 Skill 本身。

- 原剧本：`docs/validation/WAR-65/evidence/war-65-cd-original-execution-20261111.tar.gz` 成员 `war-65-script-C/step2/script-C.txt`，SHA-256 `ba56afb91c117d06ced4089456f5e713435e99cfbf287fd3ee5a5b88ee50153d`。
- 原 Step 3：同包成员 `war-65-script-C/step3/step3-output.txt`，SHA-256 `7a0ffb334a0d37eb9ef270f3167e4820f26caa153230bad958462a5442bdd041`。
- 原 Beat 模板：`docs/validation/XIA-59-shotplan/upstream/director/beat-sheet-template.md`，SHA-256 `e53e846e9f43cdc80cf261bde4978001628d6383a6d4bd702762f88131e04bda`。
- Step 2 来源与观众体验目标：`docs/validation/WAR-68/c-interactive-trace.md`；原始 Step 2 不修改。

## 唯一主动设计改动与被动联动

**主动改动：** 把历史 B1「到后发消息」和 B2「那边冬天冷」整合成一个连续的「以日常叮嘱回避真正提问」Beat，不删除任何原始台词、动作或线索。其余戏剧功能原样保留，后续 Beat 只是编号前移。

**被动联动（时长）：** 原始两段各 6 秒，共 12 秒，违反原模板单 Beat >10 秒边界。合并段压至 **10 秒**，其 2 秒转给「过年的时候……」的转折段（原 B3 6→8 秒）。后两个 Beat 仍各 6 秒。实际演员语速/停顿是否容纳尚未知，不能视为完成时长验证。

**压力记账：** 合并段的 `+2` 仅沿用旧 B1/B2 两个 `+1` 的总和，使两版曲线具备可比性；绝不等于证明压力真的上升两格。其它压力分值保持原值。本轮**不处理**历史 B5 人物与观众压力曲线相同的另一个疑点，以免同轮同时干预两项设计。

## 实验版 Beat Sheet（人工修订，30 秒）

| # | Thread | Story function | State in | Δ pressure (agent) | Visual action | State out | Shot family | Sec |
|---:|---|---|---|---|---|---|---|---:|
| B1 | main | 以日常关切建立告别，并将真正问题继续留在台词之外 | 与许并肩站立，陈还没有开始试探离开之后的联系 | +2（沿用原 B1/B2 合计；陈两次说起到达后的联系与天气，许简短回应并望向检票口） | 陈和许站在候车区立柱旁；陈握车票，许背小包。短暂沉默；陈说「到了以后，记得给我发个消息」，许说「好」；许望向检票口；陈说「那边冬天挺冷的」，许说「我知道」。 | 两次关切得到回应；告别正接近，真正的提问仍未开始 | relation | 10 |
| B2 | main | 让陈开始提出关键问题却主动停住 | 仍停留在日常关切，真正的问题尚未说出 | +3（陈自己开始说「过年的时候……」又主动停止） | 陈低头看车票，抬头看许，说「过年的时候……」，主动停住。 | 陈已开启关键话题，却没有问出；回应变得迫切 | close-up | 8 |
| B3 | main | 让许的关切成为对关键问题的非正面回应 | 陈停住，是否回应仍未知 | +1（许转头看他，停顿后以「你照顾好自己」回避正面回答） | 许转头看陈；短暂沉默；许说「你照顾好自己」，陈看着她，轻轻点头，说「嗯」。 | 双方保有牵挂，但关键问题未得到直接回答 | reaction | 6 |
| B4 | main | 让告别发生，留下未说出口的问题 | 两人交换关切，仍同处一个空间 | +1（原值未变；再次广播后许离开，陈没有追或叫住） | 远处再次传来车站广播。许转身朝检票口走去；陈留在原地，没有叫住她。 | 许已离开，陈仍在原地，问题悬而未决 | aftermath | 6 |

**实验版累计张力（保持原数值假设）：** `2 → 4 → 7 → 8 → 9`；增量 `+2 / +3 / +1 / +1`。最大增量 `+3` 完成于第 18 秒，即 30 秒的 60%。**原版**为 `2 → 3 → 4 → 7 → 8 → 9`；两版终值和主要转折时间相同，少了一个弱的中间压力节点。

## 按原模板进行文本自检（不等于效果验证）

| 检查点 | 本版状态 |
|---|---|
| B1 进入/离开状态不同 | **勉强成立、最有争议**：原本只是站着等待，合并后已形成双重告别关切，但「真正问题仍未问」没有变化；不能把数字 +2 当作独立证明 |
| Δ 有施压源且算术一致 | 文字上成立；压力仍为主观刻度 |
| 镜头动作不冒充 Beat | 成立：Visual action 只写剧本里已有的行动和对白 |
| 不是单纯位置变化 | 成立：末 Beat 的离场完成不可逆的告别 |
| 一 Beat 一转折 | 合并 B1 被解释为单一关系/告别准备转折；两轮互答是否仅是活动堆积仍值得审阅 |
| 曲线净升、最大单次上升位置 | 数学成立；+3 在第 18 秒，60% 处 |
| 时长与界限 | 10+8+6+6=30 秒，单 Beat 均为 2–10 秒；**10 秒容纳前两轮对白及动作的实演可行性未知** |

## 对照判断与暂不越界的结论

- **可见收益（文本层）：** 结构从 5 行精简至 4 行，核心转折仍在第 18 秒完成；所有原始对白、视线、广播与告别动作保留；避免将两段相似的日常关切强行解释为两次独立转折。
- **可见风险：** 合并后的 B1 较拥挤；将两个弱 Beat 合并不自动使其成为一个强 Beat；第 1 段的观众理解和节奏尚无实际表演/媒体验证。
- **研究结论等级：** 这是一份人工规则一致性提案，**不能证明「4 Beat 比 5 Beat 更好」**，更不能当作同模型受控复跑。旧 B5 人物/观众压力分离疑点保留，待其他关口讨论。
- **下游待检验问题（此时未执行）：** 当将 4 Beat 送入 Director's Book、Blocking/Shot Plan 时，镜头数量、关键信息、节奏预算是否改变，是否实际兑现更克制的镜头组织；需要对比同一基线并明确新输入差异。
- **当前停点：** Step 3 人工审阅本对照；在审阅完成前不执行 Step 5/6/7，不运行 GPU、H3 或其他媒体实验。

## ORIGINAL 5-BEAT DIRECTOR BOOK (FROZEN)
# Director's Book —《没说出口》／火车站候车区

以下摄影、灯光、声音与交付参数均为**拟定的制作选择**，不是剧本已确认的事实。类型采用现实主义剧情片默认方案；未指定导演，Step 4 风格镜头为 none。

## Frame

- **Format：**短剧情感片段 · **Aspect：**16:9，按叙事作品默认值拟定。
- **Target duration：**约 30 秒 · **Shot count：**暂拟 5 镜，供计算节奏预算；节拍不等于镜头，镜头数量须待后续规划确认。
- **Tool class：**n/a — 未指定平台或工具，尚不能确认首尾帧、参考绑定或文生视频等控制能力。
- **Style lens：**none — 使用 Drama／现实主义剧情片默认方案。

## Delivery

- **Platform and spec：**n/a — 未指定播放平台，也未提供或核验分辨率、帧率及编码规格。
- **Safe area：**n/a — 未指定平台及画面叠层，无法给出已核验的顶部、底部安全区百分比或来源。
- **Captions：**n/a — 未确定烧录、平台自动字幕或无字幕；负责方及执行步骤待交付方案确定。
- **Hook frame：**n/a — 这是叙事片段，未指定信息流投放或首帧留存要求。
- **Retention checkpoints：**n/a — 未指定平台留存要求。已批准的节拍转折仍按下文原时间保留。
- **Loudness：**n/a — 未指定交付标准或混音目标 · **True peak：**n/a — 未指定交付标准或峰值上限。
- **Never：**在未核验规格时宣称符合某平台要求；为适配平台擅自裁切画面、增删对白或改写结尾。

## Story

- **Logline：**在火车站告别时，陈想问许是否还会回来，却没有问出口；许以关切回应后离开，问题仍悬而未决。
- **Dramatic core：**告别正在发生，陈想问的问题与他最终选择停住的话发生碰撞；许听懂，却没有直接回答。
- **Subtext：**两人以联系、天气和照顾自己表达关切，回避了尚未说出口的去留问题。这是对已确认意图的处理，不限定两人的具体关系或未来。
- **Emotional arc：**克制地相伴等待 → 日常叮嘱中逐渐感到告别临近 → 陈的话停在半途，许听懂后没有直接回答 → 彼此关切仍在，但问题悬而未决；许离开，陈留在原地。
- **Visual thesis：**从两人并肩站在立柱旁，到许朝检票口走去、陈留在原地，让两人之间逐渐拉开的距离可见。
- **节拍与原时长：**Beat 1：0–6 秒；Beat 2：6–12 秒；Beat 3：12–18 秒；Beat 4：18–24 秒；Beat 5：24–30 秒。以上照录已批准的五个六秒节拍，**不改写原证据**。
- **建议复核：**Beat 1 与 Beat 4 均包含对白和停顿，六秒能否容纳自然语速须以排练或对白计时验证。如不够，建议在保持总目标约 30 秒及事件顺序的前提下另行提出节拍时长调整；目前没有修改任何节拍时间。

## Lens and framing policy

- **Kit：**全画幅等效 35mm、50mm、85mm。拟以 35mm 交代两人及候车区的空间关系；50mm 承载人物与对话；85mm 仅用于确有必要辨认既有细微反应或车票的画面。
- **Size-to-lens map：**全景／中全景用 35mm；中景／中近景用 50mm；近景／特写优先用 85mm。相邻景别的实际衔接留待后续规划。
- **Camera height：**默认人物肩高；唯一允许的例外是为辨认剧本中的车票而降低高度，具体高度待实际人物与道具确定。
- **Headroom / edge policy：**人物头顶保留少量稳定空间；涉及两人共同空间时保留立柱与通向检票口的方向信息。许离开时，画面边界的安排应让她与留在原地的陈之间的距离变化可读。
- **Never：**24mm 或更广的夸张透视；鱼眼；为制造孤立感而在两人仍并肩时抹去其共同空间；以画面截断暗示陈说出了更多对白。

## Camera grammar and allowed move set

- **Allowed moves：**固定；为跟随已有表演而进行的小幅、缓慢摇镜或重新构图。
- **Move budget：**按暂拟 5 镜计，最多 1 镜可作重新构图；每镜最多一种摄影机运动。其余固定。
- **Motivation rule：**只有既有动作使人物或检票口方向即将离开必要的可读范围时才允许重新构图；摄影机跟随表演，不提前引导动作。
- **Never：**手持晃动、环绕、甩镜、升降、变焦或无动作依据的推镜。

## Lighting logic and key direction policy

- **Key：**拟采用柔和的傍晚环境光，方向由候车区实际可用的开口或既有光源确定；光源位置及高度目前 **n/a — 剧本未给出可核验的建筑朝向或灯具**。选定实际场景后固定一个世界空间方向，两人的光线服从同一环境。
- **Ratio：**拟定人物面部亮侧与暗侧为 **2:1–3:1**；暗侧由候车区既有环境反射补光。此比例是制作目标，不是已测量结果。
- **Practical sources in the world：**n/a — 剧本未指明具体灯具或窗户；勘景及资产确定前不将其写成既定场景事实。
- **What stays dark：**拟让非人物所在的背景平面比人物面部约低 **0.5–1 档**，仍保留候车区与检票口方向的辨识度；以实际场景和曝光测试为准。
- **Never：**让主光在反向画面中无依据地改变世界空间方向；为两人各设互相矛盾的独立主光；用突变的亮度或颜色替角色解释情绪。

## Palette and color script

- **Dominant / accent / forbidden：**拟以候车区现有环境的中性灰、低饱和暖灰为主；强调色 **n/a — 剧本未规定车票、小包或场景的颜色**；禁用新增的高饱和霓虹色调。
- **Saturation / contrast：**饱和度低，对比度中低；保留傍晚环境与人物面部的自然层次。
- **Color script：**Beat 1–5 沿用同一套中性、低饱和处理，不以某一节拍变色制造意义。具体物件颜色待实际资产确定后锁定。
- **Never：**把车票、小包或立柱指定为未经确认的象征色；在许离开时突然改变整体色温。

## Production design anchors and era lock

- **Era：**小城，确切年份 **n/a — 剧本未指定**；火车站候车区，傍晚。
- **Anchors：**候车区、立柱、远处检票口、陈手中的一张车票、许背着的小包、数量不多的候车区人群。以上均来自剧本；具体造型、材料、颜色及建筑细节 **n/a — 未提供**。
- **Must avoid：**增加或替换剧本道具；给车票或小包擅自指定可辨认的文字、标志、材质或年代；增加明显人群；在未确定年代时编造一份年代禁用品清单。
- **Never：**将具体年份、城市名称、人物关系或过去经历写成既定事实。

## Performance register

- **Register：**克制、自然 · **Largest permitted gesture：**剧本已有的许转身朝检票口走去；其余以目光转换、陈轻轻点头等既有行为为限。
- **Performance lives in：**目光、停顿、轻微点头与说话的收束。陈在说完“过年的时候……”后**自己停住**；许听懂，但不以额外的解释性动作明确表演她的理解。
- **Never：**哭泣、争吵、拥抱；增加未写出的手势或行动；让陈追上许或叫住她；补出陈未问的问题。

## Editing rhythm and target ASL

- **Target ASL：**暂拟约 **6 秒** · **Longest shot：**暂拟 6 秒 · **Shortest shot：**暂拟 6 秒。计算依据为 30 秒 ÷ 暂拟 5 镜；这只是预算，不把五个节拍规定为五个镜头。
- **类型基准：**Drama 默认 ASL 为 6–15 秒；暂拟值位于范围下限。先保持对白后的停顿空间，再根据计时复核镜数与实际镜长。
- **Cut point policy：**优先保留既有动作或回应完成后的短暂停留；陈说到“过年的时候……”后停住的原因必须在表演中清楚，不能用剪切制造台词中断。
- **Transitions allowed：**镜头间硬切 · **Never：**以叠化、甩切或闪白替代告别的实际进程；删去两次短暂沉默、两次广播的既定出现，或改动任何对白。

## Sound direction

- **Music：**拟定无配乐，尤其不在对白下铺设音乐 · **Ambience bed：**远处模糊的车站广播及候车区环境底声；广播内容保持不可辨认。
- **Signature event：**远处车站广播再次传来，衔接许转身离开的既定时刻；不赋予广播未经剧本确认的具体内容。
- **Silence：**两次短暂沉默保留对白空隙，具体秒数 **n/a — 剧本与已批准节拍未单独计时**；不将环境底声强行消为绝对静音。
- **Never：**新增可辨认的广播词、解释情绪的音乐提示或未写出的台词；以音效掩盖陈主动停住或许的回应。

## Invariants

以下为本阶段可锁定的内容。人物身份字符串按模板要求须包含可核验的面部结构、独特标记、发型及带颜色和材质的服装；剧本没有这些信息，也没有参考图，故**不能生成合格的可复制身份字符串**。

```text
ID_CHEN: n/a — 已知陈为男性、35岁；面部几何、独特标记、发型、服装颜色与材质及参考图均未提供，无法满足身份字符串配方。

ID_XU: n/a — 已知许为女性、33岁；面部几何、独特标记、发型、服装颜色与材质及参考图均未提供，无法满足身份字符串配方。

LOCK_LOCATION: 小城火车站候车区，傍晚；候车区里人不多；候车区有一根立柱，远处有检票口。

LOCK_PROPS: 陈手中有一张车票；许背着一个小包。

LIGHT_INVARIANT: n/a — 拟采用柔和傍晚环境光、人物面部亮侧与暗侧2:1–3:1、既有环境反射补光；实际光源的世界空间位置和高度尚未确定，暂不能形成合格的逐字复用光线字符串。

NEG_BASE: 不增加可辨认的广播文字；不增加第二张车票；不增加第二个小包；不增加明显人群；不增加拥抱。
```

`ID_CHEN`、`ID_XU` 和 `LIGHT_INVARIANT` 是待补齐项，不能作为已验证的身份或光线描述投入后续生成。
## ORIGINAL STEP6 BLOCKING (GEOMETRY AND ACTIONS FROZEN; BEAT ID MAPPING ONLY)
# Step 6｜走位与场面调度：《没说出口》

以下坐标、距离与朝向均为**暂定走位选择**，用于排练和勘景，并非剧本已经确定的车站布局。实际检票口、立柱的位置与可行走路线须在场地确定后核对；不以此方案预设人物外貌、服装或道具细节。

## 空间关系

以立柱旁两人的起始位置为基准，暂定远处检票口的方向为**前方**，两人并肩面向这一方向。陈在许的左侧，两人相距约 **0.8 米**；立柱在陈的左侧附近。这个左右关系只供走位使用，不规定画面左右。

```text
                   远处检票口方向
                         ↑
                         │ 许的离开方向
                         │
        立柱       陈     许
                   └0.8米┘
```

摄影机关系服从两人的实际位置：需要共同空间时，应能辨认立柱、两人之间的间距及检票口方向；许离开时，距离的变化应可读。具体机位、景别、焦段和镜头划分留待 Step 7。

## B1｜并肩与日常叮嘱

- **起始：**陈、许在立柱旁并肩站立，间距约 0.8 米，均面向检票口方向。陈手中握着一张车票；许背着小包。
- **动作与目光：**两人短暂沉默。陈说“到了以后，记得给我发个消息。”许回答“好。”说话期间保持并肩位置；除剧本明确的目光变化外，不另加转头或手势。
- **结束：**两人仍在原位，间距约 0.8 米；车票仍在陈手中，小包仍由许背着。
- **空间作用：**两人共享立柱旁的一块空间，距离亲近，但身体朝向共同的前方；告别从日常叮嘱开始。

## B2｜望向检票口

- **起始：**承接 B1，两人并肩，间距约 0.8 米，位置和道具状态不变。
- **动作与目光：**许看向远处检票口。陈说“那边冬天挺冷的。”许回答“我知道。”两人不改变站位；许的目光留在检票口方向，直至后续剧本中的转头。
- **结束：**陈、许仍在立柱旁，间距约 0.8 米；许望向检票口。陈仍握着车票，许仍背着小包。
- **空间作用：**检票口成为许目光所指的远处目的地，而两人此时仍留在同一位置；离开的方向先于离开的动作被确立。

## B3｜话停在半途

- **起始：**两人位置不变，间距约 0.8 米；许望向检票口，陈握着车票。
- **动作与目光：**陈低头看一眼手里的车票，再抬头看向许。他说：“过年的时候……”然后**自己停住**。许仍朝检票口方向，直到下一节拍转头。
- **结束：**陈、许仍并肩站在原位；陈看向许，车票仍握在手中，许仍背着小包。
- **空间作用：**陈的目光从手中车票转向身旁的许，身体距离没有变化，未问出口的问题落在两人之间。停住发生在表演中，不依靠剪辑截断台词。

## B4｜看向彼此

- **起始：**承接 B3，陈看向许；许仍朝检票口方向，两人间距约 0.8 米。
- **动作与目光：**许转过头看着陈。短暂沉默后，她说“你照顾好自己。”陈看着许，轻轻点头，说“嗯。”除许的转头和陈的点头外，不增加解释性的动作。
- **结束：**两人仍在立柱旁原位，看向彼此，间距约 0.8 米；车票仍在陈手中，小包仍由许背着。
- **空间作用：**两人的目光终于相接，站位却没有靠近或分开。关切得到回应，陈没有问出口的问题仍悬着。

## B5｜许离开，陈留下

- **起始：**两人仍在立柱旁，相距约 0.8 米，看向彼此；陈握着车票，许背着小包。
- **动作与目光：**远处再次传来车站广播。许转身，朝检票口方向走去；陈留在原地，没有叫住她，也没有追上去。许转身后目光朝行走方向；陈留在原位，目光朝许离开的方向。
- **结束：**许沿通向检票口的方向离开两人原先并肩的位置；陈仍在立柱旁。两人间距从约 0.8 米持续增大，**终点距离不预设**，由实际场地与表演确定。陈仍握着车票，许仍背着小包；不安排道具交换。
- **空间作用：**前四个节拍维持的并肩间距，在许离开后才被拉开。陈的位置不变，许向既已望过的方向走去，距离本身让告别成为可见的事实。
## ORIGINAL 7-SHOT PLAN (FROZEN BASELINE)
# Mode D｜《没说出口》镜头与覆盖表

按已冻结的剧本、Beat、Director’s Book 与 Step 6 走位编排；画幅暂用书中拟定的 **16:9**，无导演风格镜头。机位角度、画面左右与时间均为待勘景、排练核验的镜头规划；人物外貌、服装、场地具体拓扑及世界空间主光方向尚未确定。

**Risk 六项顺序**为动作／画内人数／摄影机／成片时长／身体交互／连续性，按原始 rubric 的 0–3 分计。镜头内对白按剧本原文执行，表内只标明覆盖范围。

| # | Sec | Beat / function | Loc | Frame content | Blocking start → move → end | Size / Angle | Lens | Move | Light dir | Light / atmos | Continuity anchors | Risk | Transition | Gen note |
|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 01 | 0:00–0:07（7秒） | B1 · **relation**：建立并肩告别与第一轮叮嘱 | 候车区／立柱旁共同空间；地点 ID 未建立 | 陈、许并肩，立柱在陈侧；画面交代远处检票口方向、陈手中车票和许背的小包 | 两人相距约0.8米、面向检票口 → 短暂沉默，依次说完 B1 两句对白，站位不变 → **结束：**两人仍并肩，车票与小包原位 | WS，全身及环境；人物肩高，水平 | 35mm 全画幅等效；共同交代人物与空间 | 固定 | 柔和傍晚环境主光；相机左／右、光源位置与高度待勘景；亮侧:暗侧拟2:1–3:1，既有环境反射补光 | 人物与立柱共同清楚；背景拟低于面部0.5–1档，仍能辨认检票口方向 | 陈男35岁、许女33岁；面容发型服装未知；相距约0.8米；陈持一张车票，许背一个小包；同一傍晚环境光 | **Green 5（0/2/0/2/0/1）**：两人及7秒时长贡献较高 | 许说完“好”后的停留结束帧硬切 | 两人先后说话有口型风险；各自只说原文。若无法保持单一说话者，将两句拆成各自单人镜并重新计时、评分。 |
| 02 | 0:07–0:12（5秒） | B2 · **relation**：保留并肩状态与检票口方向 | 候车区／立柱旁，同一轴侧；地点 ID 未建立 | 两人腰部以上及立柱边缘；保留许视线所指的画外检票口方向，小包局部可见 | 承接并肩原位 → 许看向检票口，陈、许依次说完 B2 两句对白 → **结束：**两人仍在原位，许目光朝检票口 | MS，人物肩高；相对01环绕主体约35°，仍在同一轴侧 | 50mm 全画幅等效；让两人的对白与朝向可读 | 固定 | 与01同一世界空间环境光；本机位相机侧、光源高度待核验；拟2:1–3:1，环境反射补光 | 较01收紧背景，仍保留立柱和视线方向；低饱和、中低对比 | 两人位置及约0.8米间距不变；陈仍持票、许仍背包；许望向检票口；身份与光源细节未知 | **Green 5（0/2/0/1/0/2）**：画内两人及前后连续性各2 | 许说完“我知道”后的停留结束帧硬切 | 许看向既定方向，不增加转身或手势。若双人先后口型不稳，拆为单人覆盖并重新评分。 |
| 03 | 0:12–0:15（3秒） | B3 · **close-up**：呈现陈从票到许的目光变化 | 候车区／陈侧，同一轴侧；地点 ID 未建立 | 陈头肩近景；画面下缘保留手中车票一角，许在画外；立柱或背景仅保留可辨的既有部分 | 陈握票、起始目光朝前 → 低头看票，再抬头看向画外许 → **结束：**陈看向许，票仍在手中 | CU，陈肩高；与02相差两级景别 | 85mm 全画幅等效；辨认既有目光变化 | 固定 | 同一世界空间光；本机位相机侧及高度未知；拟2:1–3:1，环境反射补光 | 背景较前镜收敛；面部仍保持自然层次，不新增光色变化 | 陈与许站位未变；票仍在陈手中、具体手别及票面未知；许仍望向检票口；陈身份细节未知 | **Green 5（2/1/0/0/0/2）**：低头、抬头为两个相连动作，动作与连续性各2 | 陈抬眼并看向许后硬切 | 目光先落向票，再落向许；若连续目光变化不稳，可在两次目光之间拆开并重新评分，不能改变动作顺序。 |
| 04 | 0:15–0:19（4秒） | B3 · **close-up**：让陈自己停在未完成的话上 | 候车区／陈侧另一机位，同一轴侧；地点 ID 未建立 | 陈胸部以上，面向画外许的一侧留有视线空间；保留少量候车区背景 | 陈已看向许、身体留在原位 → 他说“过年的时候……”并自行停住 → **结束：**话已停，陈仍看向许 | MCU，陈肩高；相对03约35°，仍在轴线同侧 | 50mm 全画幅等效；保留陈与画外许的关系 | 固定 | 同一世界空间光；相机侧及光源高度待核验；拟2:1–3:1，环境反射补光 | 面部和背景维持同一光色；不以亮度变化标示停顿 | 陈目光对准许；车票仍在手中但可画外；许尚未转头；身份、服装及世界空间光位未知 | **Green 4（0/1/0/1/0/2）**：前后连续性为主要依赖 | **陈已说完并自行停住、停顿可见后**硬切 | 必须保留实际停住的表演及其后的可感知停留；若4秒容纳不足，延长本镜并重计全片。 |
| 05 | 0:19–0:23（4秒） | B4 · **reaction**：许转头并以关切回应 | 候车区／许侧，同一轴侧；地点 ID 未建立 | 许头肩近景，陈在画外相应方向；小包背带如进入画面，其具体造型未知 | 许仍朝检票口方向 → 转头看陈，短暂沉默后说“你照顾好自己。” → **结束：**许看着陈，仍在原位 | CU，许肩高；相对04暂规划约35°，保持轴侧 | 85mm 全画幅等效；辨认许既有的转头与回应 | 固定 | 同一世界空间光；本机位相机侧及高度待核验；拟2:1–3:1，环境反射补光 | 许的面部层次与此前同一环境一致，不新增解释性光效 | 陈在许视线方向；两人间距约0.8米；许背包、陈持票；两人身份细节未知 | **Green 5（1/1/0/1/0/2）**：前后连续性2 | 许说完后的停留结束帧硬切 | 保留转头、短暂沉默与原句，不添加表示“听懂”的动作；时长须靠排练核验。 |
| 06 | 0:23–0:26（3秒） | B4 · **reaction**：陈接住许的关切 | 候车区／陈侧，同一轴侧；地点 ID 未建立 | 陈胸部以上，看向画外许；候车区背景保持可辨 | 陈看着许 → 轻轻点头，说“嗯。” → **结束：**陈仍在原位，看向许 | MCU，陈肩高；相对05暂规划约35°，不跨轴 | 50mm 全画幅等效；保留点头与两人的视线关系 | 固定 | 同一世界空间光；本机位相机侧及高度待核验；拟2:1–3:1，环境反射补光 | 回到陈的面部层次，与04同一世界光位；不增色温变化 | 陈看向许，许看向陈；间距约0.8米；票、包仍归各自持有；身份细节未知 | **Green 4（1/1/0/0/0/2）**：前后连续性2 | “嗯”结束及点头完成后的帧硬切 | 点头幅度保持轻微；若口型与点头无法同镜稳定完成，拆开并重新评分，不增台词。 |
| 07 | 0:26–0:32（6秒） | B5 · **aftermath**：让许离开、陈留下的距离变化可见 | 候车区／立柱旁共同空间；地点 ID 未建立 | 两人全身、立柱、通向远处检票口的方向；陈留在立柱旁，许沿该方向走远，两人间距增大 | 起始两人在原位相互看着；远处广播再次传来 → 许转身朝检票口走，陈留在原地、目光朝她离开的方向 → **结束：**许已离开原先并肩位置，距离仍在增大；陈在立柱旁，未叫住她 | WS，人物肩高，水平；与06相差两级景别 | 35mm 全画幅等效；保留两人和离开方向 | 固定 | 同一世界空间光；相机侧、光源位置及高度待核验；拟2:1–3:1，环境反射补光 | 与开场同一低饱和环境；背景保留可辨方向，不改变整体色温 | 陈持票、许背包；陈位置不变；许向检票口方向行走；终点距离及是否出画未预设 | **Amber 7（2/2/0/2/0/1）**：转身接行走及画内两人各2；先简化相连动作 | 在距离已清楚增大、陈仍留原位的结束帧结束 | 转身与行走是相连动作；若不稳，在转身完成处拆成两镜并重评分。检票口是否实际入画须勘景确认。 |

**覆盖、几何与时长检查：**

- 五个 Beat 均有覆盖；转折 B3 为两镜，B4 也为两镜，其余各一镜。每镜只有表中标明的一项叙事工作。01交代入口，07以两人距离变化提供出口；固定镜头 **7/7**，移动镜头 **0/7**，未超过书中暂定的运动预算。
- 01→02、03→04、04→05、05→06 的相邻景别只差一级，表中规划至少约35°机位变化；02→03、06→07 相差两级。角度和单侧轴线只是纸面方案，**缺少实际场地拓扑与可用机位，尚不能验证可拍性**。05／06的视线应分别指向画外对方，镜头距离及人物实际眼高也须现场核对；不能据现有材料宣称已完成正反打匹配。
- 原 Beat 与书记录的边界为 **6／12／18／24／30秒**；本表对应 **7／12／19／26／32秒**，分别相差 **+1／0／+1／+2／+2秒**。合计 **32秒、7镜、ASL约4.57秒**，与书中暂拟5镜、6秒 ASL 及其 Drama 6–15秒基准不符；冻结文件均未修改。对白与两次沉默的自然时长尚无录音或排练数据，因此32秒也只是计划，不能视为已验证。
- 风险合计 **6个 Green、1个 Amber、0个 Red**；07按原 rubric 的 Amber 要求在制作前简化一个维度。身份字符串、具体服装、票与包的造型、世界空间光源位置和高度均缺失，故各行连续性与光向只能记录已知约束及待核项，不能视为完整生成锁定。