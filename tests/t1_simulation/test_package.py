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


def test_finish_syncs_directory_after_marker_removal(tmp_path, monkeypatch):
    """C13: the final durable transition includes the missing post-unlink barrier."""
    from applications.bounded_decision_workflow import t1_package
    root = tmp_path / 'new'
    publication = Publication(root, final='report.json')
    events = []
    original = t1_package._fsync_dir
    def observe(path):
        if path == root:
            events.append((root / 'PARTIAL').exists())
        return original(path)
    monkeypatch.setattr(t1_package, '_fsync_dir', observe)
    publication.finish(b'{}')
    assert events[-1] is False
    assert not (root / 'PARTIAL').exists()


def test_post_unlink_sync_failure_restores_incomplete_marker(tmp_path, monkeypatch):
    """C13: final bytes survive, but failed durability must never become success."""
    from applications.bounded_decision_workflow import t1_package, t1_workflow
    root = tmp_path / 'new'
    publication = Publication(root, final='report.json')
    original = t1_package._fsync_dir
    failed = []
    def fail_once(path):
        if path == root and not (root / 'PARTIAL').exists() and not failed:
            failed.append(True)
            raise OSError('post-unlink durability failure')
        return original(path)
    monkeypatch.setattr(t1_package, '_fsync_dir', fail_once)
    with pytest.raises(SimRefusal) as denied:
        publication.finish(b'{}')
    assert denied.value.code == 'SIM_PUBLICATION_INCOMPLETE'
    assert (root / 'report.json').read_bytes() == b'{}'
    assert (root / 'PARTIAL').exists()
    with pytest.raises(SimRefusal):
        t1_workflow.read_package(root)
