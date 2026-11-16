import unittest
import hashlib
from chat_read_preflight import verify,PreflightBlocked

class ChatReadPreflightTests(unittest.TestCase):
    def setUp(self):
        self.health={'ok':True,'hasCanvas':True,'clients':1,'codexBusy':False}
        self.state={'projectId':'explicit-p','clientId':'explicit-client',
                    'nodes':[{'id':'chosen-node'}],'selectedNodeIds':['chosen-node']}
        self.selection={'nodes':[{'id':'chosen-node'}]}
        self.source_text='Original source exactly'
        self.shot_text='approved Shot02 full text'
        self.source_sha=hashlib.sha256(self.source_text.encode()).hexdigest()
        self.shot_sha=hashlib.sha256(self.shot_text.encode()).hexdigest()
        self.b_id='b7b4fd156b884907b2431b6b1e0d9960'
        self.authority={'pilot_only':True,'authority':{'approved_B_id':self.b_id},
            'source':{'text':self.source_text,'sha256':self.source_sha},
            'target_shot':{'id':'Shot02','text':self.shot_text,'text_sha256':self.shot_sha},
            'capabilities':{'write_canvas':False,'production_approval':False}}
        self.expected=dict(project_id='explicit-p',client_id='explicit-client',
                           node_id='chosen-node',expected_shot_id='Shot02',approved_b_id=self.b_id,
                           source_sha256=self.source_sha,shot_sha256=self.shot_sha)
    def call(self):
        return verify(self.health,self.state,self.selection,self.authority,**self.expected)
    def test_exact_data_allows_read_only_but_never_write(self):
        r=self.call()
        self.assertTrue(r['provided_identifiers_consistent'])
        self.assertEqual(r['client_id'],'explicit-client')
        self.assertIn('actually maps', ' '.join(r['not_verified']))
        self.assertFalse(r['can_write'])
    def test_multiple_tabs_denied(self):
        self.health['clients']=2
        with self.assertRaisesRegex(PreflightBlocked,'exactly one'):
            self.call()
    def test_codex_busy_or_unknown_denied(self):
        for v in (True,None):
            with self.subTest(v=v):
                self.health['codexBusy']=v
                with self.assertRaisesRegex(PreflightBlocked,'busy'):
                    self.call()
    def test_client_routing_mismatch_denied(self):
        self.state['clientId']='different-active-tab'
        with self.assertRaisesRegex(PreflightBlocked,'client ID'):
            self.call()
    def test_project_mismatch_denied(self):
        self.state['projectId']='other-project'
        with self.assertRaisesRegex(PreflightBlocked,'project ID'):
            self.call()
    def test_selection_mismatch_denied(self):
        self.state['selectedNodeIds']=['another-node']
        with self.assertRaisesRegex(PreflightBlocked,'selection'):
            self.call()
    def test_selection_readback_mismatch_denied(self):
        self.selection['nodes']=[{'id':'another-node'}]
        with self.assertRaisesRegex(PreflightBlocked,'readback'):
            self.call()
    def test_wrong_b_denied(self):
        self.authority['authority']['approved_B_id']='0'*32
        with self.assertRaisesRegex(PreflightBlocked,'approved B'):
            self.call()
    def test_wrong_source_and_shot_denied(self):
        self.authority['source']['sha256']='0'*64
        with self.assertRaisesRegex(PreflightBlocked,'source'):
            self.call()
        self.authority['source']['sha256']=self.source_sha
        self.authority['target_shot']['text_sha256']='0'*64
        with self.assertRaisesRegex(PreflightBlocked,'Shot'):
            self.call()
    def test_shot_id_mismatch_denied(self):
        self.expected['expected_shot_id']='Shot03'
        with self.assertRaisesRegex(PreflightBlocked,'Shot ID mismatch'):
            self.call()
    def test_all_missing_version_values_rejected(self):
        self.expected['approved_b_id']=None
        self.expected['source_sha256']=None
        self.expected['shot_sha256']=None
        self.authority['authority']['approved_B_id']=None
        self.authority['source']['sha256']=None
        self.authority['target_shot']['text_sha256']=None
        with self.assertRaisesRegex(PreflightBlocked,'valid approved B'):
            self.call()
    def test_empty_and_invalid_version_formats_rejected(self):
        for field in ('approved_b_id','source_sha256','shot_sha256'):
            for value in ('',None,'stale', 'g'*64):
                with self.subTest(field=field,value=value):
                    original=self.expected[field]
                    self.expected[field]=value
                    with self.assertRaises(PreflightBlocked):
                        self.call()
                    self.expected[field]=original
    def test_full_source_and_target_bytes_verified(self):
        self.authority['source']['text']='unapproved changed source'
        with self.assertRaisesRegex(PreflightBlocked,'source text SHA256'):
            self.call()
        self.authority['source']['text']=self.source_text
        self.authority['target_shot']['text']='unapproved changed Shot'
        with self.assertRaisesRegex(PreflightBlocked,'Shot text SHA256'):
            self.call()
    def test_stale_snapshot_cannot_be_proven_fresh(self):
        # Data may be replayed verbatim after a browser switches projects.
        result=self.call()
        self.assertTrue(result['provided_identifiers_consistent'])
        self.assertFalse(result['can_write'])
        self.assertIn('snapshot is fresh',' '.join(result['not_verified']))
    def test_node_shot_mapping_not_attested(self):
        # Distinct valid node and selected id remain internally consistent.
        # Pure-data checks must not claim that this node represents Shot02.
        self.state['nodes']=[{'id':'another-unrelated-node'}]
        self.state['selectedNodeIds']=['another-unrelated-node']
        self.selection['nodes']=[{'id':'another-unrelated-node'}]
        self.expected['node_id']='another-unrelated-node'
        r=self.call()
        self.assertFalse(r['can_write'])
        self.assertIn('Node actually maps',' '.join(r['not_verified']))
    def test_node_missing_duplicate_denied(self):
        self.state['nodes']=[]
        with self.assertRaisesRegex(PreflightBlocked,'missing or duplicate'):
            self.call()
        self.state['nodes']=[{'id':'chosen-node'},{'id':'chosen-node'}]
        with self.assertRaisesRegex(PreflightBlocked,'missing or duplicate'):
            self.call()
    def test_incomplete_authority_denied(self):
        self.authority['target_shot']['text']=''
        with self.assertRaisesRegex(PreflightBlocked,'full text'):
            self.call()
    def test_elevated_capability_claim_denied(self):
        self.authority['capabilities']['write_canvas']=True
        with self.assertRaisesRegex(PreflightBlocked,'write capability'):
            self.call()

if __name__=='__main__':unittest.main()
