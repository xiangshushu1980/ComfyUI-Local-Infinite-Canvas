## USER-APPROVED DUAL-ENTRY PRIORITY
Canvas Agent inside Canvas main; ChatGPT via Eric as half-automated second formal entry; separate Eric Codex backup only.

## DOCUMENT: DUAL ENTRY ARCHITECTURE
# Canvas Lab｜Director Skill 双入口执行决策（2026-11-16）

决策来源：用户明确要求 **Eric 上 Canvas Agent 为主力，ChatGPT 可以半自动参与，Eric 独立 Codex 为备用**。

## 目标与适用边界

Canvas Lab 的真实创作入口有两个，复用同一导演方法与工程工具，而非为 Chat 与 Canvas 分别维护两套导演引擎。每次具体修订由一个执行者负责专业判断，外围独立 Reviewer 只负责设计/代码/导演产物的质量检查。单 Agent 是一次任务的执行拓扑，不是限制用户只有一个入口。

### 路径 A：主力，Eric Canvas Agent（画布内置 Codex）

- 用户在 Canvas Lab 中使用 @画布元素、选区、节点引用与对话；Canvas Agent 自己加载可发现的 Director Skill（正式安装仍未批准），按阶段调用本地 Director Runtime CLI 的只读、准备与提交命令，并直接通过既有 infinite-canvas MCP 读写所连接的画布。
- 已在**隔离** Canvas Agent 真实验证 Skill 发现/选择、原生 Codex turn、按需读 Shot Plan 知识、Runtime review-pack 和 Canvas MCP 双读取，结论是只读 no-handoff。尚未在现有正式 Canvas Agent 上安装该候选 Skill；媒体、真实候选写入、人类 B 重审未证。
- Canvas Agent 会根据启动环境继承 CODEX_HOME 配置。独立对话不等于配置隔离；正式 Agent 启用状态不能依据一次隔离 smoke 的全局配置继承现象判断。

### 路径 B：协作，ChatGPT → Eric

- ChatGPT 负责讨论设计、召集外围审阅 Agent、查阅 Eric 的本地权威 Markdown、组织半自动审阅和明确授权范围的画布操作。
- ChatGPT 通过 DCR 显式访问 Eric；可以读取适用 Director Skill 文件，执行**同一** Director Runtime CLI，必要时通过**现有** Canvas Agent API 控制已确认的画布，或将一段受控任务交给 Canvas Agent 原生对话。没有为 Chat 新建长期运行的 Director Agent 或专门的 HTTP 桥接服务。
- Chat **不能自动将远端 Eric Skill/MCP 当成本会话的内建工具**：实际需要显式读取 Skill 文件、经远程命令执行 CLI 或通过已有 API 操作画布。Chat 路径的 API 实验曾在独立测试画布验证节点创建、选区、差异回显；完整的真实用户修改与 B 再批准仍未测。
- Chat 没有 Canvas UI 内置 @ 元素交互语义；如需访问元素，必须显式核对项目/节点/选区 ID、B/Source/Shot 版本及实际 Canvas Agent 连接归属。不能凭 Chat 文本里的“@某元素”假设已解析到当前画布，也不能自动回退到未知的最近画布。

### 备用执行端：Eric 独立 Codex

- 仅用于画布内 Agent 不可用、自动化批处理、独立验证/代码审阅等情况；不作为主力和 Chat 的日常必经中转。
- 备用执行时仍指向同一套 Skill、Runtime CLI 和被授权的 Canvas Agent 工具；不用自己的另一本专业规范或独立 DirectorPlan 状态。
- 多 Reviewer + 主审阅 Agent 是**外围质量控制**，不加入每次导演运行的调用链，也不代签用户 A/B。

## 共享的单套能力与数据

1. **Director Skill 权威**：Eric 项目中的七文件专业 Skill；Canvas Agent 安装的是可发现副本/引用，Chat 按阶段读取原件。正式安装需七文件 SHA 清单、相对路径可用性与更新回退检查，不能让两入口使用不一致版本。
2. **Director Runtime CLI**：同一实现、同一试点权限及来源校验；只读视图不生成新候选，prepare/submit 也不自行启动专业模型。未来正式持久化归 WAR-35，不在此复制第二套数据契约。
3. **Canvas 工具**：Eric 已有 Canvas Agent 的 infinite-canvas MCP / HTTP 工具；Chat 用 HTTP/API 协作并不意味着它拥有 UI 内置 Codex 的一切上下文，Canvas 内置 Agent 更适合直接消化 @引用和画布选择。
4. **用户批准与材料**：Eric 本地 Markdown/Runtime 冻结证据为权威，Linear 是索引与状态；Canvas 文本节点是展示投影，不是最终的 B 授权记录。Chat 审阅意见、Canvas UI 反馈要保留各自真实来源，不得互相冒充。

## 并发与操作边界（当前是规程，尚非已实现锁机制）

- **同一画布的一次修改只由一个主控路径执行**；先核项目 ID、实际连接的 clientId、当前选区与 B/Source/Shot SHA。Chat 不应在 Canvas Agent 忙于同一画布时并发提交修订。冲突或版本变化时停止，重新读状态并获取人工确认。
- 现有 Canvas Agent 的 busy 状态与 Runtime 文件锁只覆盖各自局部操作，**不能声称已实现跨 Chat/Canvas 的通用编辑锁、事务或 revision/CAS**。这些工程语义不在 WAR-90 偷偷落地，后续与 WAR-35/WAR-37 对齐。
- 不得凭一个随机项目名、最近画布或截断节点预览自动提交修改；要从实际 UI 选区/@引用或受用户确认的精确 ID 发起。
- 不从本轮实验向生产安装技能、切换服务、修改用户 Canvas、生成媒体或自动签 A/B。后续正式写操作必须明确授权及回滚范围。

## 当前真实验收（截至 2026-11-16）

- 路径 A 原生 Skill+Runtime+MCP **只读 PASS（有限）**；Codegraph/Hindsight 在隔离试验中的意外暴露，导致正式工具隔离**未验收**。
- 路径 B Chat→DCR→Canvas Agent API **独立测试画布读写/选区 PASS（有限）**；Chat 直接用 Skill 的完整专业修订及同一 Runtime 提交新 B **未验收**。
- 备用独立 Codex→Skill+CLI+MCP **只读 PASS（有限）**。
- Runtime 新增的目标 Shot 只读 compact 视图为试点能力，尚无原生 Agent 复测。生产集成仍未执行；真实 Shot02 用户表示暂时没有修改意见，不得伪造修订候选。
- 用户真正的修订→邻镜复检→Canvas 差异→再次人审 B **未验收**，按真实需求择期测试，不人为制造需求。

## 下一步优先级

1. 在 WAR-90 收口当前的 Runtime compact Shot 只读视图与多 Agent 代码审阅，不扩大到新 schema。
2. 独立核验 Codec/Codex 配置来源（空 CODEX_HOME 与用户环境已对照），在已有 Canvas Agent 工具审批路径上找到可验证的拒绝/拒执行证据；如果 MCP 工具默认自动通过且客户端没有可拒绝事件，记录**当前通路无法证明拒绝**，不为实验擅改生产权限机制。
3. 形成路径 A 与 B 的共同运行说明与最小权限矩阵；确认正式 Skill 安装/新会话/回滚的实际边界后，再让用户决定何时在正式 Canvas 使用。
4. 真正有用户修改要求时，选择一个入口完成隔离的完整改动闭环，外围多 Agent 审阅结论只能提供质量建议，不得代替用户 B 审批。

用户的主次排序属于已确认决策，不重新将 Chat 设为专业 Agent 的必经路由。


## IMPLEMENTATION: COMPLETE SCOPED GIT DIFF
diff --git a/tools/director-runtime-v0/cli.py b/tools/director-runtime-v0/cli.py
index 94a1db1..b97b558 100644
--- a/tools/director-runtime-v0/cli.py
+++ b/tools/director-runtime-v0/cli.py
@@ -36,6 +36,9 @@ def main(argv=None):
     status.add_argument('--workspace', required=True)
     preview = commands.add_parser('review-pack', help='Read-only preview handoff, not WAR-35 schema')
     preview.add_argument('--workspace', required=True)
+    review_shot = commands.add_parser('review-shot', help='Compact, pilot-only approved Shot read view')
+    review_shot.add_argument('--workspace', required=True)
+    review_shot.add_argument('--shot-id', required=True)
     args = parser.parse_args(argv)
     try:
         if args.command == 'init':
@@ -46,6 +49,8 @@ def main(argv=None):
                 result = pilot.status()
             elif args.command == 'review-pack':
                 result = pilot.review_packet()
+            elif args.command == 'review-shot':
+                result = pilot.review_shot(args.shot_id)
             elif args.command == 'record-review':
                 result = pilot.review(args.checkpoint, args.decision, args.evidence_file, args.actor)
             elif args.command == 'prepare-stage':
diff --git a/tools/director-runtime-v0/runtime.py b/tools/director-runtime-v0/runtime.py
index f6a6d8c..26d1abb 100644
--- a/tools/director-runtime-v0/runtime.py
+++ b/tools/director-runtime-v0/runtime.py
@@ -601,6 +601,101 @@ External DS/TF/VM sections are references only; their bodies were not loaded. Re
                             'DirectorPlan and not a Canvas Agent write command. '
                             'Media/geometry/audience require separate evidence.')}
 
+    def review_shot(self, shot_id):
+        """Pilot-only compact *read* view of one approved Shot and exact nearby excerpts.
+
+        All authority, evidence, source/skill hash and B/neighbor gates remain in
+        review_packet(). This projection cannot generate/submit/approve anything.
+        """
+        packet = self.review_packet()
+        shots = packet['shots']
+        ids = [item['id'] for item in shots]
+        if shot_id not in ids:
+            raise PilotError(f'Unknown approved Shot: {shot_id}')
+        position = ids.index(shot_id)
+        target = shots[position]
+        source = packet['authority']['source_text']
+        if digest(source.encode('utf-8')) != packet['authority']['source_sha256']:
+            raise PilotError('Source bytes do not match declared SHA256')
+
+        def neighbor(index, side):
+            if index < 0 or index >= len(shots):
+                return None
+            item = shots[index]
+            prefixes = ('切点',) if side == 'previous' else (
+                '入镜', '同镜连续动作', '观看任务')
+            lines = item['text'].splitlines()
+            found = next(((n + 1, line) for n, line in enumerate(lines)
+                          if any(line.startswith(prefix) for prefix in prefixes)), None)
+            return {
+                'id': item['id'],
+                'full_text_sha256': item['text_sha256'],
+                'full_text_included': False,
+                'excerpt': {
+                    'status': 'exact-source-line' if found else 'not-found',
+                    'line_number_1_based': found[0] if found else None,
+                    'text': found[1] if found else None,
+                    'not_complete_neighbor_context': True,
+                },
+                'full_text_json_path': f'$.shots[{index}].text',
+            }
+
+        review = packet['review']
+        return {
+            'format': 'war90-director-shot-preview-only-v0',
+            'purpose': 'Read-only target localization; not a revision or complete continuity review',
+            'pilot_only': True,
+            'scope': {'target_shot_id': shot_id, 'target_full_text': True,
+                      'neighbor_full_text': False, 'editing_authorized': False},
+            'authority': {
+                'approved_A_id': packet['authority']['approved_A_id'],
+                'approved_B_id': packet['authority']['approved_B_id'],
+                'source_sha256': packet['authority']['source_sha256'],
+                'approval_evidence_sha256': packet['authority']['approval_evidence_sha256'],
+            },
+            'hashes': {
+                'B_candidate_canonical_content': {
+                    'sha256': packet['authority']['approved_B_content_sha256'],
+                    'source_field': 'authority.approved_B_content_sha256',
+                    'object_scope': 'Approved pilot B candidate content, not Shot text',
+                },
+                'ShotPlan_stage_utf8_text': {
+                    'sha256': packet['stages']['shot']['text_sha256'],
+                    'source_field': 'stages.shot.text_sha256',
+                    'object_scope': 'Complete approved Shot Plan UTF-8 text',
+                },
+                'target_Shot_section_utf8_text': {
+                    'sha256': target['text_sha256'],
+                    'source_field': f'shots[{position}].text_sha256',
+                    'object_scope': 'Exact target Shot section UTF-8 text',
+                },
+                'cross_object_hashes_should_match': False,
+            },
+            'source': {'text': source,
+                       'sha256': packet['authority']['source_sha256'],
+                       'complete': True},
+            'target_shot': dict(target),
+            'neighbors': {'previous': neighbor(position - 1, 'previous'),
+                          'next': neighbor(position + 1, 'next')},
+            'stage_dependencies': {
+                stage: {'text_sha256': packet['stages'][stage]['text_sha256'],
+                        'text_not_included': True,
+                        'full_text_json_path': f'$.stages.{stage}.text'}
+                for stage in ('intent', 'beat', 'blocking')
+            },
+            'review_flags': {
+                key: value for key, value in review.items() if key != 'unknown'
+            } | {
+                'unknown_count': len(review['unknown']),
+                'unknown_requires_full_review': True,
+            },
+            'capabilities': dict(packet['capabilities']),
+            'full_context_command': 'review-pack --workspace <same-pilot>',
+            'warning': ('Pilot-only presentation, not WAR-35 or identity verification. '
+                        'Neighbor excerpts are not complete; use review-pack before '
+                        'cross-Stage or full continuity assessment. No editing authority.'),
+        }
+
     def status(self):
         state = self.load()
         problems = []
diff --git a/tools/director-runtime-v0/tests/test_runtime.py b/tools/director-runtime-v0/tests/test_runtime.py
index 8b479b3..2966a3e 100644
--- a/tools/director-runtime-v0/tests/test_runtime.py
+++ b/tools/director-runtime-v0/tests/test_runtime.py
@@ -497,6 +497,119 @@ class RuntimeTests(unittest.TestCase):
         with self.assertRaisesRegex(PilotError, 'No matching external human pilot B'):
             self.pilot.review_packet()
 
+    def test_review_shot_requires_approved_A_B_and_preserves_baseline(self):
+        with self.assertRaisesRegex(PilotError, 'pilot A/B'):
+            self.pilot.review_shot('Shot02')
+        self.with_realistic_shot_baseline()
+        before = self.tree()
+        view = self.pilot.review_shot('Shot02')
+        self.assertEqual(before, self.tree())
+        self.assertEqual(view['format'], 'war90-director-shot-preview-only-v0')
+        self.assertTrue(view['pilot_only'])
+        self.assertEqual(view['scope']['target_shot_id'], 'Shot02')
+        self.assertFalse(view['scope']['editing_authorized'])
+        self.assertFalse(view['capabilities']['write_canvas'])
+        self.assertFalse(view['review_flags']['identity_verified'])
+        self.assertFalse(view['review_flags']['formal_WAR35_approval'])
+
+    def test_review_shot_exact_text_and_all_sha_objects(self):
+        self.with_realistic_shot_baseline()
+        full = self.pilot.review_packet()
+        from runtime import digest
+        for item in full['shots']:
+            view = self.pilot.review_shot(item['id'])
+            self.assertEqual(view['target_shot'], item)
+            self.assertEqual(view['source']['text'], full['authority']['source_text'])
+            self.assertEqual(view['source']['sha256'], digest(view['source']['text'].encode()))
+            hashes = view['hashes']
+            self.assertEqual(hashes['B_candidate_canonical_content']['sha256'],
+                             full['authority']['approved_B_content_sha256'])
+            self.assertEqual(hashes['ShotPlan_stage_utf8_text']['sha256'],
+                             digest(full['stages']['shot']['text'].encode()))
+            self.assertEqual(hashes['target_Shot_section_utf8_text']['sha256'],
+                             digest(item['text'].encode()))
+            self.assertFalse(hashes['cross_object_hashes_should_match'])
+            self.assertEqual(view['authority']['approved_B_id'],
+                             full['authority']['approved_B_id'])
+
+    def test_review_shot_neighbor_exact_line_and_boundaries(self):
+        self.with_realistic_shot_baseline()
+        full = self.pilot.review_packet()
+        for pos,item in enumerate(full['shots']):
+            view = self.pilot.review_shot(item['id'])
+            for name,neighbor_index in [('previous',pos-1),('next',pos+1)]:
+                neighbor=view['neighbors'][name]
+                if neighbor_index<0 or neighbor_index>=len(full['shots']):
+                    self.assertIsNone(neighbor)
+                    continue
+                self.assertEqual(neighbor['id'],full['shots'][neighbor_index]['id'])
+                self.assertEqual(neighbor['full_text_sha256'],
+                                 full['shots'][neighbor_index]['text_sha256'])
+                self.assertFalse(neighbor['full_text_included'])
+                excerpt=neighbor['excerpt']
+                self.assertTrue(excerpt['not_complete_neighbor_context'])
+                if excerpt['status']=='exact-source-line':
+                    index=excerpt['line_number_1_based']
+                    self.assertEqual(
+                        excerpt['text'],full['shots'][neighbor_index]['text'].splitlines()[index-1])
+                else:
+                    self.assertEqual(excerpt['status'],'not-found')
+                    self.assertIsNone(excerpt['text'])
+
+    def test_review_shot_unknown_id_and_unapproved_edit_fail_closed(self):
+        self.with_realistic_shot_baseline()
+        before = self.tree()
+        for shot in ('Shot05','shot02','Shot02 ','Shot02\n',''):
+            with self.subTest(shot_id=shot),self.assertRaisesRegex(PilotError,'Unknown approved Shot'):
+                self.pilot.review_shot(shot)
+        self.assertEqual(self.tree(),before)
+        self.pilot.run('shot',targets=['Shot02'],
+            generator=self.fake(proposal=self.sample_shots().replace(
+                '纸移开露出 K 后，蓝夹再次盖 K。','纸移开露出 K 后，蓝夹盖 K。林让位。'),
+                changed_targets=['Shot02']))
+        with self.assertRaisesRegex(PilotError,'pilot A/B'):
+            self.pilot.review_shot('Shot02')
+
+    def test_review_shot_tampered_source_and_human_evidence_blocked(self):
+        self.with_realistic_shot_baseline()
+        src=self.source.read_bytes()
+        self.source.write_bytes(src+b' changed')
+        with self.assertRaisesRegex(PilotError,'hash changed'):
+            self.pilot.review_shot('Shot02')
+        self.source.write_bytes(src)
+        self.evidence.write_text('tampered by another participant')
+        with self.assertRaisesRegex(PilotError,'approval evidence has changed'):
+            self.pilot.review_shot('Shot02')
+
+    def test_review_shot_does_not_hide_unknown_or_claim_approval(self):
+        self.with_realistic_shot_baseline()
+        view=self.pilot.review_shot('Shot02')
+        full=self.pilot.review_packet()
+        self.assertEqual(view['review_flags']['unknown_count'],len(full['review']['unknown']))
+        self.assertTrue(view['review_flags']['unknown_requires_full_review'])
+        self.assertFalse(view['review_flags']['identity_verified'])
+        self.assertFalse(view['review_flags']['formal_WAR35_approval'])
+        self.assertFalse(view['review_flags']['geometry_verified'])
+        self.assertFalse(view['review_flags']['media_verified'])
+        self.assertFalse(view['review_flags']['audience_verified'])
+        self.assertIn('not a revision',view['purpose'])
+        self.assertIn('review-pack',view['full_context_command'])
+
+    def test_review_shot_cli_routes_and_blocks_unknown_id(self):
+        self.with_realistic_shot_baseline()
+        import cli
+        args=['review-shot','--workspace',str(self.workspace),'--shot-id','Shot02']
+        with patch('cli.Pilot',return_value=self.pilot), io.StringIO() as stdout, redirect_stdout(stdout):
+            code=cli.main(args)
+            result=json.loads(stdout.getvalue())
+        self.assertEqual(code,0)
+        self.assertEqual(result['target_shot']['id'],'Shot02')
+        with patch('cli.Pilot',return_value=self.pilot), io.StringIO() as stderr, redirect_stderr(stderr):
+            code=cli.main(args[:-1]+['Shot99'])
+            error=stderr.getvalue()
+        self.assertEqual(code,2)
+        self.assertIn('Blocked: Unknown approved Shot',error)
+
     def external_result(self, prepared, **values):
         directory = Path(prepared['result_path']).parent
         raw, _ = self.fake(**values)('', directory)


## APPROVED SOURCE GUARD (EXISTING)

        """Read-only, source-verified presentation view; never a Canvas execution API."""
        with self.locked() as state:
            self.check(state)
            active, a, b = state['active'], state['pilot_A'], state['pilot_B']
            if not a or not b or not active or state['stage'] != 'shot':
                raise PilotError('Canvas review preview requires a pilot A/B approved Shot')
            if state['phase'] != 'pilot-B-accepted' or state['pending_shots']:
                raise PilotError('Unresolved Shot neighbor review or unapproved revision')
            if active != b or active['id'] != b['id']:
                raise PilotError('Active candidate differs from the accepted pilot B')
            artifacts = active['artifacts']
            if set(artifacts) != {'intent', 'beat', 'blocking', 'shot'}:
                raise PilotError('Review preview requires four complete stage artifacts')
            if artifacts['intent'] != a['artifacts']['intent']:
                raise PilotError('Active Intent no longer matches approved pilot A')
            order = artifacts['shot']['shot_ids']
            segments = shot_sections(artifacts['shot']['proposal'], order)

            def matching_review(checkpoint, candidate):
                for review in reversed(state['reviews']):
                    if (review['checkpoint'] == checkpoint
                        and review['decision'] == 'accept'
                        and review['actor'] == 'human'
                        and review['candidate_id'] == candidate['id']
                        and review['candidate_sha256'] == candidate['content_sha256']
                        and review.get('pilot_only') is True
                        and review.get('formal_WAR35_approval') is False):
                        evidence = Path(review['evidence_origin'])
                        if digest(read_text(evidence)) != review['evidence_sha256']:
                            raise PilotError(f'Pilot {checkpoint} approval evidence has changed')
                        if digest(review['text'].encode()) != review['evidence_sha256']:
                            raise PilotError(f'Pilot {checkpoint} review text has changed')
                        return review
                raise PilotError(f'No matching external human pilot {checkpoint} approval evidence')

            review_a = matching_review('A', a)
            review_b = matching_review('B', b)
            source = read_text(self.path / 'source.txt').decode('utf-8')
            return {
                'format': 'war90-director-preview-only-v0',
                'purpose': 'read-only director review presentation for future Canvas Agent',
                'authority': {
                    'source_sha256': state['inputs']['source.txt']['sha256'],
                    'source_text': source,
                    'skill_sha256': {key: value['sha256'] for key, value
                                     in state['inputs'].items() if key.startswith('skill/')},
                    'approved_A_id': a['id'],
                    'approved_A_content_sha256': a['content_sha256'],
                    'approved_B_id': b['id'],
                    'approved_B_content_sha256': b['content_sha256'],
                    'approval_evidence_sha256': {
                        'A': review_a['evidence_sha256'], 'B': review_b['evidence_sha256']},
                },
                'stages': {stage: {'text': data['proposal'],
                                   'text_sha256': digest(data['proposal'].encode('utf-8'))}
                           for stage, data in artifacts.items()},
                'shots': [{'id': shot_id, 'text': segments[shot_id],
                           'text_sha256': digest(segments[shot_id].encode('utf-8'))}
                          for shot_id in order],
                'review': {'pilot_A_accepted': True, 'pilot_B_accepted': True,
                           'external_human_evidence_recorded': True,
                           'identity_verified': False,
                           'formal_WAR35_approval': False,
                           'pending_shots': [],
                           'unknown': state['unknown'],
                           'media_verified': False,
                           'geometry_verified': False,
                           'audience_verified': False},
                'capabilities': {'display_text': True, 'propose_edit': False,
                                 'write_canvas': False, 'generate_media': False,
                                 'production_approval': False},
                'warning': ('This is an experimental review projection, not WAR-35 '
                            'DirectorPlan and not a Canvas Agent write command. '
                            'Media/geometry/audience require separate evidence.')}



## PREVIOUS MAIN DESIGN REVIEW (BEFORE IMPLEMENTATION)
**主审裁定：targeted-revision；A3 按现稿执行为 block，实际隔离与拒绝效果为 unknown，不予 accept。** 我已对照冻结设计，亲自读取 Eric 的配置探针、审批分派、CLI 与 Runtime 源码，并核对两份 Reviewer 原报告。结论不依据票数；本轮未写文件、未运行模型试验、未签 A/B，未复算原 B 状态 SHA。

**审批问题比两份报告描述的更具体。** [codex-client.ts:706](/home/sean/projects/canvas-lab/infinite-canvas/canvas-agent/src/agent/codex-client.ts:706) 只将三类请求纳入 `codex_approval`：命令执行、文件变更、权限申请。`mcpServer/elicitation/request` 不在其中，普通线程分支反而自动返回 `action: "accept"`；其他未知请求返回通用 decline，也不构成人工审批闭环。不能把 elicitation 等同于工具执行授权，更不能把原生命令审批当作 `canvas_get_state` 自身审批。

因此，现有源码没有支持“A3 必能通过 codex_approval 拒绝 MCP 调用”的依据；`on-request` 也不能抵消配置中明确的 `default_tools_approval_mode: "approve"`。这不证明所有 Codex 版本均不支持 MCP 审批，但足以阻断当前测试脚本假设。两位 Reviewer 的“事件类型未证”须升级为“现有客户端接线存在明确缺口”。

**必须先修权限试验定义。** 核定安装版本支持的 MCP 控制配置、请求类型及响应结构，确认是否有现成通路；若没有，就报告当前通路不可验证，不为完成测试擅自扩建审批系统。A2 可作为独立隔离试验继续设计：探针仅证明全局配置启用 Hindsight/Codegraph、空 CODEX_HOME 无 MCP；须另核临时进程环境、cwd、认证来源、新线程生效配置及真实工具集合。`workspace-write` 只能称业务只读测试，不能称文件权限只读。

A3 的成功条件必须是调用与审批关联、decline 形成终态、工具入口证明确未执行。没有成功返回、超时或断连都不足以证明拒绝有效；无执行观测则保持 unknown，并验证取消后的迟到调用、进程和 busy/client 恢复。

**Compact 仅对定位与局部文本核对达到接近最低充分，尚不足以支撑导演判断。** 我确认 [runtime.py:528](/home/sean/projects/canvas-lab/tools/director-runtime-v0/runtime.py:528) 已复核来源、候选、A/B 人类证据及 pending_shots；`locked()` 读取并加锁，不自动保存。投影应直接复用 packet 的目标正文、哈希、review、capabilities 和 provenance，不再次解析审批或重建权威逻辑。B 哈希对应候选 artifacts 的规范编码，另两层对应 UTF-8 文本，不可跨对象比较。

必须补的是**故事源上下文**，不必塞入程序源码全文：从 `authority.source_text` 提供相关原文及可复现位置，并按判断需要补批准 Intent、Beat、Blocking 中的目标、人物知情、声音时序和空间依据。不能稳定关联就标 unknown，提供完整来源/阶段补读路径；不能靠模型摘要填空。邻镜节选须带范围、全文 SHA 和全文补读方式，连续性判断仍需完整邻镜。三层哈希只能验对象一致性，不能补足语义上下文。

**顺序裁定：不要求 A3 成功后才允许离线 CLI 实现。** 采纳工程 Reviewer 的依赖拆分；导演 Reviewer 对上下文的要求成立，但不必阻塞独立投影开发。允许 ChatGPT 的最小下一步是修订上述测试契约、固定字段与降级规则，随后仅实现试点 CLI 和确定性测试；原生集成复测仍受审批门槛约束。新增测试须覆盖逐字一致、来源失效、边界/重复 ID、哈希对象及业务状态不变，不能借既有 54 项宣称通过。

可选：独立允许分支验证观测链、结构化字段选择。延期：生产安装、正式 Schema/UI、候选提交、A/B 批准及媒体验证。

本轮终端读取命令被工具审批机制拒绝，原因是需要审批而当前策略为 never；已改用获准的只读文件工具完成核对，该拒绝不作为 A3 证据。

## ORIGIN PROBE JSON
{
  "test": "read-only config/read via actual Codex app-server; no model or browser",
  "inherited_HOME_CODEX_HOME": "/home/sean/.codex",
  "inherited_config": {
    "initialized": true,
    "mcp_names": [
      "blender",
      "codegraph",
      "cua_repl",
      "hindsight",
      "hindsight-direct",
      "infinite-canvas"
    ],
    "enabled": {
      "cua_repl": false,
      "hindsight": true,
      "codegraph": true,
      "blender": false,
      "hindsight-direct": false,
      "infinite-canvas": false
    }
  },
  "empty_isolated_config": {
    "initialized": true,
    "mcp_names": [],
    "enabled": {}
  },
  "no_auth_material_read": true,
  "no_global_config_modified": true,
  "important_scope": "config/read is config origin evidence, NOT actual thread tool scope or approval denial"
}


## PREVIOUS DEMONSTRATED MODEL ERROR
B candidate hash and Stage Shot text hash refer to different objects; cannot compare for equality.

## TEST RESULTS
61 Python unittest tests passed; actual approved B unchanged SHA256=23e78d5994ed18ea02d59c2c3eb588f36cc41d3b495b81009713ec7570d7e4b7. This is reported by the orchestrator, not an independently reproduced claim by reviewers.