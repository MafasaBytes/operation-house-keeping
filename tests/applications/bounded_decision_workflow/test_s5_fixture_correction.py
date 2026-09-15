import hashlib
import json

from tests.applications.bounded_decision_workflow.test_s1_input_public_admission import PACKAGE_PATH, object_bytes


def test_original_s5_package_preserved_and_only_three_recipes_changed():
    original_path = PACKAGE_PATH.with_name(PACKAGE_PATH.name.replace('.json', '-pre-s5-retention-correction.json'))
    raw = original_path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == '89ba39623a72326d876740d624af501b467179c608ae89ce9e40f66806ec0d4e'
    old, new = json.loads(raw), json.loads(PACKAGE_PATH.read_bytes())
    assert old['objects'] == new['objects'] and len(new['objects']) == 68
    for h in new['objects']: object_bytes(new, h)
    a = {v['variant_id']: v for c in old['acceptance_cases'] for v in c['variants']}
    b = {v['variant_id']: v for c in new['acceptance_cases'] for v in c['variants']}
    assert {k for k in a if a[k] != b[k]} == {'RET-3', 'RET-4', 'PATH-1-manifest-extra'}
    for change in new['s5_fixture_correction']['changes']:
        key = change['path'][1:]
        assert a[change['variant_id']][key] == change['before']
        assert b[change['variant_id']][key] == change['after']
    codes = {d['code']: d for d in new['diagnostic_catalogue']}
    for name in ('RET-3', 'RET-4'):
        expected = b[name]['expected']['by_fault_boundary']
        assert set(expected) == set(b[name]['input']['filesystem_setup_or_mutation']['fault_each_boundary'])
        for value in expected.values():
            d = value['stderr_line']; assert d == codes[d['code']]
    assert b['PATH-1-manifest-extra']['input']['argv'][3:] == ['verify', '--bundle', 'CORRUPT_BUNDLE']
