"""Deterministic fake-generator storage tests. No professional/model acceptance."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from runtime import Pilot, PilotError, SKILL_FILES, initialize, atomic_json, codex_generate


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'script.txt'
        self.source.write_bytes('原文\r\n钥匙只有一把。周只推断，未看见钥匙。\r\n'.encode())
        self.skill = self.root / 'skill'
        for name in SKILL_FILES:
            path = self.skill / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('Test skill ' + name)
        self.workspace = self.root / 'pilots' / 'D'
        initialize(self.workspace, self.source, self.skill, root=self.root / 'pilots')
        self.pilot = Pilot(self.workspace, root=self.root / 'pilots')
        self.evidence = self.root / 'human.txt'
        self.evidence.write_text('SIMULATED human input for unit tests only')
        self.counter = 0

    def fake(self, **overrides):
        self.counter += 1
        payload = dict(proposal=f'FAKE substantive proposal {self.counter}',
                       reason='FAKE alternative and reason', changes='FAKE changed timing',
                       impact='FAKE adjacent shots', unknown=['readability unknown'],
                       next_action='human review', handoff=True, changed_targets=[],
                       shot_ids=['Shot01', 'Shot02', 'Shot03', 'Shot04'],
                       hard_conflicts=[], upstream_change=False)
        payload.update(overrides)

        def generate(prompt, directory):
            (directory / 'events.jsonl').write_text('{"fake": true}\n')
            return json.dumps(payload), 'fake-thread-for-tests'
        return generate

    def run_stage(self, stage, **kwargs):
        return self.pilot.run(stage, generator=self.fake(**kwargs))

    def accept_A(self):
        self.run_stage('intent')
        self.pilot.review('A', 'accept', self.evidence, 'human')

    def reach_shot(self):
        self.accept_A()
        for stage in ('beat', 'blocking', 'shot'):
            self.run_stage(stage)

    def tree(self):
        return {str(p.relative_to(self.workspace)): p.read_bytes()
                for p in self.workspace.rglob('*') if p.is_file()}

    def test_initial_none_and_no_overwrite(self):
        state = self.pilot.load()
        self.assertIsNone(state['active'])
        self.assertIsNone(state['pilot_A'])
        with self.assertRaises(PilotError):
            initialize(self.workspace, self.source, self.skill, root=self.root / 'pilots')
        self.assertEqual(len(state['inputs']), 8)

    def test_gate_A_blocks_every_downstream_stage(self):
        for stage in ('beat', 'blocking', 'shot'):
            with self.subTest(stage=stage), self.assertRaises(PilotError):
                self.run_stage(stage)
        self.assertFalse((self.workspace / 'runs').exists())

    def test_prompt_exact_source_and_initial_authority(self):
        prompt = self.pilot.packet(self.pilot.load(), 'intent', 'resume')
        self.assertIn(self.source.read_bytes().decode(), prompt)
        self.assertIn('"approved_intent_pilot_only": null', prompt)
        self.assertIn('"working_candidate": null', prompt)
        self.assertIn('Test skill stages/intent.md', prompt)
        self.assertNotIn('Test skill stages/shot-plan.md', prompt)

    def test_single_candidate_and_full_recovery(self):
        self.accept_A()
        self.run_stage('beat')
        first = self.pilot.load()['active']['id']
        self.run_stage('blocking')
        reopened = Pilot(self.workspace, root=self.root / 'pilots')
        state = reopened.load()
        self.assertNotEqual(first, state['active']['id'])
        prompt = reopened.packet(state, 'shot', 'resume')
        for stage in ('intent', 'beat', 'blocking'):
            self.assertIn(state['active']['artifacts'][stage]['proposal'], prompt)
        self.assertIn(state['pilot_A']['artifacts']['intent']['proposal'], prompt)

    def test_source_change_blocks_all_modes_and_review(self):
        self.run_stage('intent')
        self.source.write_text('Changed source')
        for mode in ('resume', 'continue', 'refresh'):
            with self.subTest(mode=mode), self.assertRaises(PilotError):
                self.pilot.packet(self.pilot.load(), 'intent', mode)
        with self.assertRaises(PilotError):
            self.pilot.review('A', 'accept', self.evidence, 'human')
        self.assertIsNone(self.pilot.status()['active_candidate'])
        self.assertFalse(self.pilot.status()['gates']['A'])

    def test_skill_origin_and_snapshot_change_block(self):
        for path in (self.skill / 'SKILL.md', self.workspace / 'skill/stages/beat.md'):
            original = path.read_bytes()
            path.chmod(0o644)
            path.write_text('changed')
            with self.assertRaises(PilotError):
                self.pilot.packet(self.pilot.load(), 'intent', 'resume')
            path.write_bytes(original)

    def test_rejected_candidate_not_in_recovery(self):
        self.run_stage('intent', proposal='REJECTED SECRET PROPOSAL')
        self.pilot.review('A', 'reject', self.evidence, 'human')
        prompt = self.pilot.packet(self.pilot.load(), 'intent', 'resume')
        self.assertNotIn('REJECTED SECRET PROPOSAL', prompt)
        self.assertIn('SIMULATED human input', prompt)
        self.assertIsNone(self.pilot.load()['thread_id'])

    def test_no_handoff_or_identical_proposal_no_snapshot(self):
        self.run_stage('intent', handoff=False)
        self.assertIsNone(self.pilot.load()['active'])
        self.assertEqual(list((self.workspace / 'runs').glob('*/candidate.json')), [])
        self.run_stage('intent', proposal='same')
        old = self.pilot.load()['active']['id']
        self.run_stage('intent', proposal='same')
        self.assertEqual(self.pilot.load()['active']['id'], old)
        self.assertEqual(len(list((self.workspace / 'runs').glob('*/candidate.json'))), 1)

    def test_local_return_marks_neighbors_and_never_global_pass(self):
        self.reach_shot()
        self.pilot.run('blocking', targets=['Shot02'], generator=self.fake(changed_targets=['Shot02']))
        state = self.pilot.load()
        self.assertEqual(state['pending_shots'], ['Shot01', 'Shot02', 'Shot03'])
        self.run_stage('shot')
        self.assertEqual(self.pilot.load()['pending_shots'], state['pending_shots'])
        self.assertIsNone(self.pilot.load()['pilot_B'])

    def test_local_scope_excess_and_unknown_target_block(self):
        self.reach_shot()
        old = self.pilot.load()['active']['id']
        with self.assertRaises(PilotError):
            self.pilot.run('blocking', targets=['Shot02'], generator=self.fake(changed_targets=['Shot04']))
        with self.assertRaises(PilotError):
            self.pilot.run('blocking', targets=['NoSuchShot'], generator=self.fake())
        with self.assertRaises(PilotError):
            self.pilot.run('blocking', generator=self.fake())
        self.assertEqual(self.pilot.load()['active']['id'], old)

    def test_conflict_and_upstream_change_quarantine(self):
        self.reach_shot()
        old = self.pilot.load()['active']['id']
        for values in ({'hard_conflicts': ['extra key']}, {'upstream_change': True}):
            with self.assertRaises(PilotError):
                self.run_stage('shot', **values)
        self.assertEqual(self.pilot.load()['active']['id'], old)
        self.assertEqual(len(self.pilot.status()['quarantined_runs']), 2)

    def test_approval_pilot_only_unknown_stays_unknown(self):
        self.reach_shot()
        self.pilot.review('B', 'accept', self.evidence, 'human')
        status = self.pilot.status()
        self.assertTrue(status['gates']['A'])
        self.assertTrue(status['gates']['B'])
        self.assertFalse(status['formal_WAR35_approval'])
        self.assertEqual(set(status['unknown']), {'media', 'geometry', 'audience', 'readability unknown'})
        self.assertFalse(self.pilot.load()['reviews'][-1]['identity_verified'])

    def test_model_cannot_approve_and_workspace_evidence_rejected(self):
        self.run_stage('intent', approved=True, actor='human')
        self.assertIsNone(self.pilot.load()['pilot_A'])
        with self.assertRaises(PilotError):
            self.pilot.review('A', 'accept', self.workspace / 'source.txt', 'human')
        with self.assertRaises(PilotError):
            self.pilot.review('A', 'accept', self.evidence, 'model')

    def test_source_change_during_generation_preserves_raw_and_state(self):
        baseline = self.pilot.load()
        fake = self.fake()
        def changing(prompt, directory):
            self.source.write_text('changed while running')
            return fake(prompt, directory)
        with self.assertRaises(PilotError):
            self.pilot.run('intent', generator=changing)
        self.assertEqual(self.pilot.load(), baseline)
        self.assertEqual(len(list((self.workspace / 'runs').glob('*/result.txt'))), 1)

    def test_state_change_during_generation_not_overwritten(self):
        fake = self.fake()
        def changing(prompt, directory):
            state = self.pilot.load()
            state['phase'] = 'external change'
            atomic_json(self.workspace / 'state.json', state)
            return fake(prompt, directory)
        with self.assertRaises(PilotError):
            self.pilot.run('intent', generator=changing)
        self.assertEqual(self.pilot.load()['phase'], 'external change')

    def test_dry_packet_no_files_changed(self):
        before = self.tree()
        self.pilot.packet(self.pilot.load(), 'intent', 'resume')
        self.assertEqual(before, self.tree())

    def test_reuse_modes_explicitly_rejected(self):
        self.accept_A()
        for mode in ('continue', 'refresh'):
            with self.assertRaisesRegex(PilotError, 'disabled'):
                self.pilot.run('beat', mode, generator=self.fake())

    def test_invalid_initial_input_is_atomic(self):
        target = self.root / 'pilots' / 'invalid'
        (self.skill / 'stages/beat.md').unlink()
        with self.assertRaises(PilotError):
            initialize(target, self.source, self.skill, root=self.root / 'pilots')
        self.assertFalse(target.exists())

    def test_path_escape_symlink_and_production_rejected(self):
        with self.assertRaises(PilotError):
            initialize(self.root / 'production', self.source, self.skill, root=self.root / 'pilots')
        (self.root / 'pilots/link').symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(PilotError):
            initialize(self.root / 'pilots/link/escape', self.source, self.skill, root=self.root / 'pilots')
        (self.workspace / 'redirect').symlink_to(self.source)
        with self.assertRaises(PilotError):
            Pilot(self.workspace, root=self.root / 'pilots')

    def test_baseline_mismatch_block(self):
        self.accept_A()
        self.run_stage('beat')
        state = self.pilot.load()
        state['active']['baseline_A'] = 'stale'
        atomic_json(self.workspace / 'state.json', state)
        with self.assertRaises(PilotError):
            self.pilot.packet(self.pilot.load(), 'blocking', 'resume')

    def test_revision_of_beat_invalidates_downstream(self):
        self.reach_shot()
        self.run_stage('beat')
        self.assertNotIn('shot', self.pilot.load()['active']['artifacts'])
        with self.assertRaises(PilotError):
            self.run_stage('shot')

    def test_rejected_B_removed_from_new_session(self):
        self.reach_shot()
        rejected = self.pilot.load()['active']['artifacts']['shot']['proposal']
        self.pilot.review('B', 'revise', self.evidence, 'human')
        prompt = self.pilot.packet(self.pilot.load(), 'beat', 'resume')
        self.assertNotIn(rejected, prompt)
        self.assertIsNotNone(self.pilot.load()['pilot_A'])
        self.assertIsNone(self.pilot.load()['active'])

    def test_local_shot_order_change_blocks(self):
        self.reach_shot()
        with self.assertRaisesRegex(PilotError, 'reorder'):
            self.pilot.run('shot', targets=['Shot02'],
                           generator=self.fake(shot_ids=['Shot02', 'Shot01']))

    def test_failed_generator_retains_evidence_and_candidate(self):
        self.run_stage('intent')
        old = self.pilot.load()['active']['id']
        def failed(prompt, directory):
            (directory / 'events.jsonl').write_text('FAKE partial event')
            raise PilotError('FAKE process failure')
        with self.assertRaises(PilotError):
            self.pilot.run('intent', generator=failed)
        self.assertEqual(self.pilot.load()['active']['id'], old)
        self.assertEqual(len(self.pilot.status()['quarantined_runs']), 1)

    def test_initializers_do_not_overwrite_under_concurrency(self):
        from concurrent.futures import ThreadPoolExecutor
        target = self.root / 'pilots' / 'concurrent'
        def attempt(_):
            try:
                initialize(target, self.source, self.skill, root=self.root / 'pilots')
                return 'created'
            except PilotError:
                return 'blocked'
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(attempt, range(2)))
        self.assertCountEqual(outcomes, ['created', 'blocked'])
        self.assertEqual(Pilot(target, root=self.root / 'pilots').load()['stage'], 'intent')

    def test_adapter_flags_events_and_credentials_cleanup_with_fake_process(self):
        directory = self.workspace / 'adapter-test'
        directory.mkdir()
        def process(command, **kwargs):
            self.assertIn('read-only', command)
            self.assertIn('gpt-6-astra', command)
            self.assertIn('model_reasoning_effort="medium"', command)
            self.assertIn('--ephemeral', command)
            self.assertEqual(kwargs['input'], 'test prompt')
            (directory / 'result.txt').write_text('FAKE raw result')
            kwargs['stdout'].write('{"type":"thread.started","thread_id":"fake-adapter-id"}\n')
            return subprocess.CompletedProcess(command, 0)
        with patch('runtime.subprocess.run', side_effect=process), patch.dict('os.environ', {'CODEX_HOME': str(self.root / 'no-auth')}):
            result, thread = codex_generate('test prompt', directory)
        self.assertEqual(thread, 'fake-adapter-id')
        self.assertEqual(result, 'FAKE raw result')
        self.assertFalse((directory / '.codex-home').exists())


    @staticmethod
    def sample_shots():
        return ("场景不变量：唯一钥匙，顺序固定。\n"
                "Shot01｜起因\n第一镜未露 K，周与林仍在寻找。\n"
                "Shot02｜观众先知\n纸移开露出 K 后，蓝夹再次盖 K。\n"
                "Shot03｜疑问发现\n周问一句，林揭夹，首次发现。\n"
                "Shot04｜一次交接\n林右手交周右手，周去门边。\n")

    def with_realistic_shot_baseline(self, approved=True):
        self.reach_shot()
        self.run_stage('shot', proposal=self.sample_shots())
        if approved:
            self.pilot.review('B', 'accept', self.evidence, 'human')
        return self.pilot.load()

    def test_local_compact_packet_preserves_all_stage_proposals_and_human_feedback(self):
        self.with_realistic_shot_baseline()
        state = self.pilot.load()
        state['unknown'].extend(['repeated historical uncertainty'] * 100)
        atomic_json(self.workspace / 'state.json', state)
        scope = 'Only amend Shot02; source, approvals and full proposals must remain'
        compact = self.pilot.packet(state, 'shot', 'resume', scope, ['Shot02'])
        full = self.pilot.packet(state, 'shot', 'resume', scope)
        self.assertIn('war90-local-compact-v1', compact)
        self.assertNotIn('SOURCE VERBATIM', compact)
        self.assertIn('SOURCE VERBATIM', full)
        self.assertLess(len(compact.encode()), len(full.encode()) * .8)
        self.assertIn(json.dumps(self.source.read_bytes().decode(), ensure_ascii=False), compact)
        self.assertEqual(compact.count("原文"), 1)
        self.assertNotIn('repeated historical uncertainty', compact)
        for stage in ('intent', 'beat', 'blocking', 'shot'):
            self.assertIn(json.dumps(state['active']['artifacts'][stage]['proposal'], ensure_ascii=False), compact)
        self.assertIn(state['reviews'][-1]['text'], compact)
        self.assertIn(state['pilot_A']['id'], compact)
        self.assertIn('formal_WAR35_approval', compact)
        self.assertIn('Test skill stages/shot-plan.md', compact)
        self.assertNotIn('Test skill stages/blocking.md', compact)

    def test_local_shot_guard_accepts_only_allowed_shot_content(self):
        baseline = self.with_realistic_shot_baseline()
        old_01 = baseline['active']['artifacts']['shot']['proposal'].split('Shot02｜')[0]
        revision = self.sample_shots().replace('纸移开露出 K 后，蓝夹再次盖 K。',
                                               '纸移开露出 K 后，蓝夹盖 K。林随后让位。')
        metadata = self.pilot.run('shot', targets=['Shot02'],
                                  generator=self.fake(proposal=revision, changed_targets=['Shot02']))
        state = self.pilot.load()
        self.assertEqual(metadata['status'], 'candidate-saved')
        self.assertEqual(metadata['context_profile'], 'war90-local-compact-v1')
        self.assertEqual(metadata['verified_changed_shots'], ['Shot02'])
        self.assertEqual(state['phase'], 'awaiting-human-B')
        self.assertIsNone(state['pilot_B'])
        self.assertEqual(state['active']['artifacts']['shot']['proposal'].split('Shot02｜')[0], old_01)
        self.assertEqual(state['pending_shots'], ['Shot01', 'Shot02', 'Shot03'])

    def test_local_shot_guard_rejects_hidden_nontarget_edit_without_mutating_B(self):
        baseline = self.with_realistic_shot_baseline()
        mutated = self.sample_shots().replace('第一镜未露 K', '第一镜已经露出 K')
        mutated = mutated.replace('纸移开露出 K 后，蓝夹再次盖 K。',
                                  '纸移开露出 K 后，蓝夹再次盖 K。林后退。')
        with self.assertRaisesRegex(PilotError, 'Non-target Shot'):
            self.pilot.run('shot', targets=['Shot02'],
                           generator=self.fake(proposal=mutated, changed_targets=['Shot02']))
        latest = self.pilot.load()
        self.assertEqual(latest, baseline)
        self.assertEqual(latest['pilot_B']['id'], baseline['pilot_B']['id'])
        metadata = [json.loads(p.read_text()) for p in (self.workspace / 'runs').glob('*/metadata.json')]
        self.assertEqual(sum(r['status'] == 'quarantined' for r in metadata), 1)
        self.assertEqual(sum(r['status'] == 'candidate-saved' for r in metadata),
                         len(baseline['runs']))

    def test_local_shot_guard_rejects_missing_duplicate_and_unreported_sections(self):
        state = self.with_realistic_shot_baseline()
        old = self.sample_shots()
        variants = [
            ('Local shot structure', old.replace('Shot03｜', 'MISSING-03｜')),
            ('Local shot structure', old + 'Shot01｜偷偷重复镜头\n'),
            ('underreported changed Shots', old.replace('周问一句', '周问完立刻看镜头')),
            ('Only global/preamble', old.replace('场景不变量', '偷偷更改故事约束')),
        ]
        for message, payload in variants:
            with self.subTest(message=message), self.assertRaisesRegex(PilotError, message):
                self.pilot.run('shot', targets=['Shot02','Shot03'],
                               generator=self.fake(proposal=payload,
                                                   changed_targets=['Shot02']))
            self.assertEqual(self.pilot.load(), state)

    def test_local_shot_nonhandoff_does_not_commit_new_candidate(self):
        before = self.with_realistic_shot_baseline()
        metadata = self.pilot.run('shot', targets=['Shot02'],
            generator=self.fake(handoff=False, proposal='Unable to produce a safe shot revision',
                                shot_ids=[], changed_targets=[]))
        self.assertEqual(metadata['status'], 'no-handoff')
        self.assertEqual(self.pilot.load()['active'], before['active'])
        self.assertEqual(self.pilot.load()['pilot_B'], before['pilot_B'])



if __name__ == '__main__':
    unittest.main()
