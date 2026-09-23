"""Test-only qualification custody; no production authority or synthetic builds."""
import json
import pytest
import qualification as q

@pytest.fixture
def corpus(tmp_path, monkeypatch):
    root=tmp_path/'r';root.mkdir()
    for name in q.CAPS:(root/name).mkdir()
    (root/'indexes'/'0000-identity.json').write_bytes(b'{}')
    monkeypatch.setattr(q,'ROOT',root)
    return root

def test_approved_caps():
    assert sum(q.CAPS.values())==1274019840
    assert q.CAPS['checkouts']==620756992

def test_record_chain_ignores_comparison_filenames(corpus):
    (corpus/'indexes'/'resumed-core-comparison.json').write_bytes(b'[]')
    q.record({'event':'first'})
    first=corpus/'indexes'/'0001-record.json'
    assert first.exists()
    q.record({'event':'second'})
    assert json.loads((corpus/'indexes'/'0002-record.json').read_bytes())['previous']==q.sha(first.read_bytes())

def test_transaction_durable_before_producer_and_bound(corpus):
    with q.transaction('small',{'repairs':5},files=1,dirs=0):
        events=[json.loads(p.read_bytes()) for p in (corpus/'indexes').glob('*record.json')]
        assert any(v.get('event')=='reservation_begin' for v in events)
        q.put(corpus/'repairs'/'five',b'12345')
        with pytest.raises(AssertionError):q.put(corpus/'repairs'/'one',b'1')
    assert not (corpus/'repairs'/'one').exists()

def test_unclosed_reservation_stops_new_producer(corpus):
    q.record({'event':'reservation_begin','id':'interrupted','charges':{'repairs':1}})
    with pytest.raises(AssertionError):
        with q.transaction('next',{'repairs':1},files=1,dirs=0):pass
