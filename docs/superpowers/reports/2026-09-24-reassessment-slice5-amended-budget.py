"""Owner-approved full-regression accounting adapter; original qualification helper remains unchanged."""
"""Owner-authorized Slice 5 evidence driver; never imported by production.

Frozen expectations are comparison inputs only. Each application uses its public
CLI and captures its own inputs. All writes are exclusively created and reserved.
"""
import hashlib
import json
import os
from pathlib import Path
import resource
import selectors
import stat
import subprocess
import sys
import time
import zipfile
from contextlib import contextmanager

ROOT = Path('/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/nr-slice5-qualification-r1')
REPO = Path('/mnt/d/operation-house-keeping')
PACKAGE = REPO/'docs/superpowers/reports/2026-09-23-reassessment-preparation/package.zip'
CAPS = dict(outputs=103809024,inputs=71303168,repairs=188743680,regressions=335544320,
            checkouts=620756992,recovery=4194304,logs=8388608,indexes=8388608,exports=134217728)
ACTIVE = None
VERIFIED_EXPORTS = {}

def wire(x):
    return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()

def sha(b):
    return hashlib.sha256(b).hexdigest()

def expected_member(archive,name):
    raw=archive.read(name)
    overlay=REPO/'docs/superpowers/reports/2026-09-23-reassessment-p10-revision-target-overlay-v2.json'
    correction=json.loads(overlay.read_bytes())
    assert sha(PACKAGE.read_bytes())==correction['base_package_sha256']
    for row in correction['changes']:
        if row['member']==name:
            assert sha(raw)==row['old_sha256']
            old=row['byte_replacement']['old'].encode();new=row['byte_replacement']['new'].encode()
            assert raw.count(old)==1
            raw=raw.replace(old,new);assert sha(raw)==row['new_sha256']
    return raw

def census():
    counts=dict.fromkeys(CAPS,0);physical=0;files=0;dirs=0
    for here,ds,fs in os.walk(ROOT,followlinks=False):
        physical+=os.lstat(here).st_blocks*512;dirs+=1
        for n in fs+[n for n in ds if (Path(here)/n).is_symlink()]:
            p=Path(here)/n;s=p.lstat();files+=1;physical+=s.st_blocks*512
            counts[p.relative_to(ROOT).parts[0]]+=s.st_size
    external={}
    for p in (ROOT/'indexes').glob('*record.json'):
        row=json.loads(p.read_bytes())
        if row.get('event') in ('external_export','external_export_intent'):
            external[row['path']]=row
    for name,row in external.items():
        p=Path(name)
        if row.get('event')=='external_export_intent' and not p.exists():
            counts['exports']+=row['bytes'];physical+=((row['bytes']+4095)//4096)*4096
            files+=1
            continue
        s=p.stat();identity=(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,row['sha256'])
        if VERIFIED_EXPORTS.get(str(p))!=identity:
            b=p.read_bytes()
            assert len(b)==row['bytes'] and sha(b)==row['sha256']
            VERIFIED_EXPORTS[str(p)]=identity
        counts['exports']+=s.st_size;physical+=s.st_blocks*512;files+=1
    assert all(counts[k]<=CAPS[k] for k in counts)
    assert sum(counts.values())<=1274019840 and physical<=1572864000
    assert files<=65536 and dirs<=24576
    return dict(categories=counts,total=sum(counts.values()),combined=76560100+sum(counts.values()),physical=physical,files=files,directories=dirs)

def reserve(charges,files=1,dirs=0):
    now=census();growth=sum(charges.values())
    if ACTIVE is not None:
        for k,v in charges.items():
            assert now['categories'][k]+v<=ACTIVE['baseline']['categories'][k]+ACTIVE['charges'].get(k,0)
        assert now['files']+files<=ACTIVE['baseline']['files']+ACTIVE['files']+2
        assert now['directories']+dirs<=ACTIVE['baseline']['directories']+ACTIVE['dirs']
    assert all(now['categories'][k]+v<=CAPS[k] for k,v in charges.items())
    assert now['total']+growth<=1274019840
    assert now['files']+files<=65536 and now['directories']+dirs<=24576
    assert now['physical']+growth+files*4096+dirs*8192<=1572864000
    s=os.statvfs(ROOT);assert s.f_bavail*s.f_frsize>=1572864000-now['physical']

def put(p,b):
    reserve({p.relative_to(ROOT).parts[0]:len(b)})
    with p.open('xb') as f:f.write(b)

def record(x):
    names=sorted((ROOT/'indexes').glob('[0-9][0-9][0-9][0-9]-*.json'));last=names[-1]
    b=wire(dict(previous=sha(last.read_bytes()),**x))
    p=ROOT/'indexes'/f'{int(last.name[:4])+1:04d}-record.json'
    reserve({'indexes':len(b)})
    with p.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
    fd=os.open(ROOT/'indexes',os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)

@contextmanager
def transaction(label,charges,*,files,dirs):
    """Single writer. Incomplete intents block all subsequent producers.

    Each producer is bounded before launch; completion records its actual files.
    No interrupted reservation is automatically released on restart.
    """
    global ACTIVE
    assert ACTIVE is None
    pending=set()
    for p in sorted((ROOT/'indexes').glob('*record.json')):
        v=json.loads(p.read_bytes())
        if v.get('event')=='reservation_begin':pending.add(v['id'])
        if v.get('event')=='reservation_end':pending.discard(v['id'])
    assert not pending,('unresolved reservation',pending)
    charges=dict(charges);charges['indexes']=charges.get('indexes',0)+16384
    reserve(charges,files=files+2,dirs=dirs)
    baseline=census()
    record(dict(event='reservation_begin',id=label,charges=charges,files=files,dirs=dirs,baseline=baseline))
    ACTIVE=dict(baseline=baseline,charges=charges,files=files,dirs=dirs)
    try:
        yield
        now=census()
        assert all(now['categories'][k]<=baseline['categories'][k]+charges.get(k,0) for k in CAPS)
        assert now['files']<=baseline['files']+files+2
        assert now['directories']<=baseline['directories']+dirs
        record(dict(event='reservation_end',id=label,inventory=now))
    finally:
        ACTIVE=None

def publish_export(path, raw):
    """Single-writer export: durable charged intent before exclusive creation.

    An interrupted intent continues to consume its full allowance. Unexpected
    partial/different bytes fail census closed; no deletion or retry frees it.
    """
    path=Path(path).absolute()
    assert path.parent.is_dir() and not path.exists() and not path.is_symlink()
    assert not path.is_relative_to(ROOT)
    row=dict(path=str(path),bytes=len(raw),sha256=sha(raw))
    reserve({'exports':len(raw),'indexes':8192},files=3)
    record(dict(event='external_export_intent',**row))
    last=sorted((ROOT/'indexes').glob('*.json'))[-1]
    with last.open('rb') as f:os.fsync(f.fileno())
    fd=os.open(ROOT/'indexes',os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
    # Recheck after intent; census includes the promised bytes before writing.
    reserve({'indexes':4096},files=1)
    with path.open('xb') as f:
        f.write(raw);f.flush();os.fsync(f.fileno())
    record(dict(event='external_export',**row,reservation_timing='durable_intent_before_create'))

def mkdir(p):
    reserve({},files=0,dirs=1);p.mkdir()

def command(tag,args,output=None):
    charges={'logs':32768,'indexes':16384}
    if output:charges[output.relative_to(ROOT).parts[0]]=1048576
    # An enclosing durable transaction already owns its metadata envelope.
    # Record writes check their exact bytes; do not reserve a second full 16 KiB
    # after the transaction's intent has itself consumed metadata space.
    reserve({k:v for k,v in charges.items() if ACTIVE is None or k!='indexes'},files=12,dirs=1 if output else 0)
    argv=[sys.executable,'-m','applications.bounded_decision_workflow',*map(str,args)]
    record(dict(event='command',tag=tag,head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),argv=argv,reservation=charges))
    def limits():
        resource.setrlimit(resource.RLIMIT_AS,(536870912,536870912))
        resource.setrlimit(resource.RLIMIT_FSIZE,(1048576,1048576))
    started=time.monotonic();sel=selectors.DefaultSelector();streams={'stdout':bytearray(),'stderr':bytearray()};reason=None
    with (ROOT/'logs'/(tag+'.stdout')).open('xb') as so, (ROOT/'logs'/(tag+'.stderr')).open('xb') as se:
        child=subprocess.Popen(argv,cwd=ROOT/'recovery',env=dict(os.environ,PYTHONPATH=str(REPO),PYTHONDONTWRITEBYTECODE='1'),stdout=subprocess.PIPE,stderr=subprocess.PIPE,preexec_fn=limits)
        sel.register(child.stdout,selectors.EVENT_READ,('stdout',so));sel.register(child.stderr,selectors.EVENT_READ,('stderr',se))
        while sel.get_map():
            if time.monotonic()-started>30 and reason is None:reason='timeout';child.kill()
            for key,_ in sel.select(.1):
                b=os.read(key.fileobj.fileno(),4096)
                if not b:sel.unregister(key.fileobj);continue
                left=32768-sum(map(len,streams.values()))
                if len(b)>left:
                    if reason is None:reason='stream_limit';child.kill()
                    b=b[:left]
                name,f=key.data;f.write(b);streams[name].extend(b)
        status=child.wait()
    sel.close()
    result=dict(tag=tag,exit=status,termination=reason,elapsed_seconds=time.monotonic()-started,
                stdout_sha256=sha(streams['stdout']),stderr_sha256=sha(streams['stderr']))
    record(dict(event='command_result',**result,inventory=census()))
    return result,bytes(streams['stdout']),bytes(streams['stderr'])
