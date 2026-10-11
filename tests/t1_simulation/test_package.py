import pytest
from applications.bounded_decision_workflow.t1_contracts import SimRefusal
from applications.bounded_decision_workflow.t1_package import manifest_bytes, member_path, Publication


def test_exact_manifest_cap_and_plus_one():
    # Data-only size guard, deliberately not an admitted manifest graph.
    assert len(manifest_bytes({'x': 'a' * 32760})) == 32768
    with pytest.raises(SimRefusal) as exc:
        manifest_bytes({'x': 'a' * 32761})
    assert (exc.value.target, exc.value.exit_class) == ('/M', 4)


def test_traversal_member_cannot_escape_package():
    with pytest.raises(SimRefusal):
        member_path('evidence/../outside')


def test_unapproved_final_name_refused_before_any_write(tmp_path):
    with pytest.raises(SimRefusal):
        Publication(tmp_path / 'never-created', final='../outside')
    assert list(tmp_path.iterdir()) == []
