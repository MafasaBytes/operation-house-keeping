"""The qualification hook buffers reports only; an external writer persists them."""
import builtins
from pathlib import Path
from types import SimpleNamespace

import bounded_pytest_runner as runner

def test_logreport_never_opens_or_writes_and_waits_for_teardown(monkeypatch):
    def forbidden(*args,**kwargs):raise AssertionError('report hook performed I/O')
    monkeypatch.setattr(builtins,'open',forbidden)
    monkeypatch.setattr(Path,'open',forbidden)
    monkeypatch.setattr(runner.os,'write',forbidden)
    monkeypatch.setattr(runner.os,'fsync',forbidden)
    rec=runner.Recorder(3,4)
    call=SimpleNamespace(nodeid='test_no_io',when='call',outcome='passed',duration=.1,failed=False,skipped=False)
    teardown=SimpleNamespace(nodeid='test_no_io',when='teardown',outcome='passed',duration=.01,failed=False,skipped=False)
    rec.pytest_runtest_logreport(call)
    assert rec.queue.empty() and 'test_no_io' in rec.pending
    rec.pytest_runtest_logreport(teardown)
    assert not rec.pending and rec.queue.qsize()==2
    queued=list(rec.queue.queue)
    assert [x[2] for x in queued]==[False,True]
