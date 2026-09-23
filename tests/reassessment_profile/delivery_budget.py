"""Test-only owner-approved Slice 4 corpus accounting; no production switches."""
import contextlib
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path('/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/nr-slice4-qualification-r1')
CAPS=dict(outputs=14680064,repairs=4194304,inputs=6291456,logs=1048576,recovery=2097152,indexes=1048576,exports=4194304)
ACTIVE={}

def inventory():
    counts={k:0 for k in CAPS};physical=0;files=0;dirs=0
    for here,ds,fs in os.walk(ROOT,followlinks=False):
        physical+=os.lstat(here).st_blocks*512;dirs+=1
        for name in fs:
            p=Path(here)/name;s=p.lstat();physical+=s.st_blocks*512;files+=1
            cat=p.relative_to(ROOT).parts[0];counts[cat]+=s.st_size
    assert files<=4096 and dirs<=512 and physical<=54525952
    assert all(counts[k]+ACTIVE.get(k,0)<=CAPS[k] for k in CAPS)
    assert sum(counts.values())+sum(ACTIVE.values())<=33554432
    assert os.statvfs(ROOT).f_bavail*os.statvfs(ROOT).f_frsize>=54525952-physical
    return dict(categories=counts,total=sum(counts.values()),combined=65433988+sum(counts.values()),allocated=physical,files=files,directories=dirs)

def record(value):
    paths=sorted((ROOT/'indexes').glob('*.json'));previous=paths[-1]
    row=dict(previous_sha256=hashlib.sha256(previous.read_bytes()).hexdigest(),**value)
    raw=json.dumps(row,sort_keys=True).encode();used=inventory()['categories']['indexes'];assert used+len(raw)<=CAPS['indexes']
    with (ROOT/'indexes'/f'{len(paths):04d}-record.json').open('xb') as f:f.write(raw)

@contextlib.contextmanager
def reserve(category,size,label):
    inventory();ACTIVE[category]=ACTIVE.get(category,0)+size;inventory()
    record(dict(event='reserve',category=category,bytes=size,label=label))
    try:yield
    finally:
        ACTIVE[category]-=size
        record(dict(event='observed',label=label,inventory=inventory()))

def directory(category,label):
    p=ROOT/category/label;p.mkdir();return p

def put(path,raw):
    cat=path.relative_to(ROOT).parts[0]
    with reserve(cat,len(raw),str(path.relative_to(ROOT))):
        with path.open('xb') as f:f.write(raw)

if __name__=='__main__':
    # Driver stdout is bounded and retained, including red/fixed failures.
    tag=sys.argv[1];args=sys.argv[2:];log=ROOT/'logs'/(tag+'.log')
    record(dict(event='command',argv=args,head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()))
    # Test-owned I/O reservations run in the child; the parent reserves its log.
    with reserve('logs',65536,tag):
        with log.open('xb') as f:
            child=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
            total=0
            while True:
                b=child.stdout.read(4096)
                if not b:break
                if total+len(b)>65536:child.kill();b=b[:65536-total]
                f.write(b);total+=len(b)
                if total==65536:break
            status=child.wait()
    record(dict(event='exit',tag=tag,status=status,sha256=hashlib.sha256(log.read_bytes()).hexdigest()))
    print(log.read_text());print(json.dumps(inventory()));sys.exit(status)
