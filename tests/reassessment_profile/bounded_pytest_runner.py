"""Bounded pytest event handoff; plugin callbacks never perform file I/O.

The wrapper owns the pre-opened result descriptors and recorder thread. Reports
are buffered by node until teardown, then the external thread durably appends
them. A started marker is durably recorded before fixture setup begins.
"""
from collections import defaultdict
import json
import os
import queue
import threading
import time

import pytest

MAX_EVENT_BYTES=65536
MAX_BUFFERED_BYTES=24*1024*1024

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')+b'\n'

class Recorder:
    def __init__(self,collection_fd,results_fd):
        self.collection_fd=collection_fd;self.results_fd=results_fd
        self.pending=defaultdict(list);self.queue=queue.Queue(maxsize=8192)
        self.error=[];self.buffered=0;self.started=0;self.reported=0
        self.worker=threading.Thread(target=self._record,name='bounded-pytest-recorder',daemon=True)

    def start(self): self.worker.start()

    def _record(self):
        while True:
            stream,wire,durable=self.queue.get()
            try:
                if stream is None:return
                fd=self.collection_fd if stream=='collection' else self.results_fd
                view=memoryview(wire)
                while view:
                    n=os.write(fd,view);view=view[n:]
                if durable:os.fsync(fd)
            except BaseException as e:self.error.append(repr(e))
            finally:self.queue.task_done()

    def _put(self,stream,value,*,durable=False):
        wire=canonical(value)
        if len(wire)>MAX_EVENT_BYTES:
            value=dict(value,diagnostic_truncated=True)
            if 'longrepr' in value:value['longrepr']=value['longrepr'][:MAX_EVENT_BYTES//2]
            wire=canonical(value)
        if self.buffered+len(wire)>MAX_BUFFERED_BYTES:
            self.error.append('bounded report memory reservation exceeded')
            return
        self.buffered+=len(wire);self.queue.put((stream,wire,durable))

    def pytest_collection_finish(self,session):
        for index,item in enumerate(session.items):
            self._put('collection',{'node':item.nodeid,'skip':[str(m.kwargs.get('reason','')) for m in item.iter_markers('skip')]},durable=index==len(session.items)-1)

    def pytest_runtest_setup(self,item):
        if self.error:pytest.exit('external recorder failed; refusing further test starts',returncode=92)
        self.started+=1
        self._put('results',{'node':item.nodeid,'event':'started','monotonic_ns':time.monotonic_ns()},durable=True)

    def pytest_runtest_logreport(self,report):
        row={'node':report.nodeid,'when':report.when,'outcome':report.outcome,'duration':report.duration}
        if report.failed or report.skipped:row['longrepr']=str(report.longrepr)
        self.pending[report.nodeid].append(row)
        if report.when=='teardown':
            events=self.pending.pop(report.nodeid,[])
            for index,event in enumerate(events):self._put('results',event,durable=index==len(events)-1)
            self.reported+=1

    def finish(self):
        self.queue.put((None,b'',False));self.queue.join();self.worker.join()
        for fd in (self.collection_fd,self.results_fd):
            try:os.fsync(fd)
            except OSError as e:self.error.append(repr(e))
        return {'started':self.started,'teardown_reports':self.reported,
                'pending_without_teardown':{k:v for k,v in self.pending.items()},
                'recorder_errors':list(self.error),'buffer_bytes':self.buffered}

def main(argv,collection_path,results_path):
    cfd=os.open(collection_path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    rfd=os.open(results_path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    recorder=Recorder(cfd,rfd);recorder.start()
    try:
        status=pytest.main(argv,plugins=[recorder])
    except KeyboardInterrupt:
        status=130
    summary=recorder.finish()
    os.close(cfd);os.close(rfd)
    print(json.dumps(summary,sort_keys=True,separators=(',',':')),flush=True)
    if summary['recorder_errors'] or summary['pending_without_teardown']:
        return 92
    return int(status)
