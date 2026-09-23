"""Slice 4 real semantic delivery; no prepared result is a computation input."""
import json
import os
from pathlib import Path
import subprocess
import sys
import pytest
from test_capture import actual_case,key,wire
from delivery_budget import ROOT,directory,put,reserve,record,inventory
from applications.bounded_decision_workflow import reassessment_runtime as runtime


def test_real_delivery_replay():
    tag='real-'+os.environ.get('NR_ATTEMPT','red')
    root=directory('inputs',tag);c,p=actual_case();objects=root/'objects';objects.mkdir()
    for (kind,digest),raw in p.items():put(objects/(digest+'.'+kind),raw)
    iv=root/'invocation.json';put(iv,p[key(c['invocation'])])
    out=ROOT/'outputs'/tag
    with reserve('outputs',1048576,'evaluate '+tag):answer=runtime.evaluate(iv,objects,c['authority_pin'],out)
    assert answer['disposition']=='one_compatible'
    assert runtime.verify(out)['disposition']=='one_compatible'
    replay=ROOT/'outputs'/(tag+'-replay')
    with reserve('outputs',1048576,'replay '+tag):again=runtime.replay(out,replay)
    assert again['result_sha256']==answer['result_sha256']
    assert (out/'result.json').read_bytes()==(replay/'result.json').read_bytes()
