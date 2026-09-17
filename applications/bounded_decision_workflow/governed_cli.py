"""Explicit governed command adapter; no fallback to legacy evaluation."""
import json
import os
import re

from . import retention, governed_persistence as persistent, governed_review
from .governed_resources import Budget, problem
from .governed_contracts import D,S,A,T,I,Q,B,SHA
from .governed_admission import H
from .input import canonical_json_bytes as C


def _capture(path,cap,fault):
    absolute,parts=retention._parts(path)
    with retention._directory(absolute,parts[:-1]) as fd:
        try:return retention._read_at(fd,parts[-1],cap,fault).data
        except FileNotFoundError as e:raise retention._error('PATH_COMPONENT_UNSAFE') from e


def capture_inputs(invocation_path,objects_dir,*,fault=None):
    budget=Budget();iv=_capture(invocation_path,budget.caps['request_wire_bytes'],fault)
    absolute,parts=retention._parts(objects_dir);entries=[];total=len(iv)
    with retention._directory(absolute,parts) as fd:
        retention._filesystem(fd);names=[];before=retention._metadata(os.fstat(fd))
        with os.scandir(fd) as it:
            for e in it:
                if len(names)>=budget.caps['unique_objects']:raise problem('INPUT_RESOURCE_LIMIT_EXCEEDED',resource=True,target='unique_objects')
                names.append(e.name)
        for name in sorted(names):
            h,sep,kind=name.partition('.')
            if not sep or not SHA.fullmatch(h) or kind not in (D,S,A,T,I,Q,B,'captured-basis'):
                raise problem('AUTHORITY_REFERENCE_MISMATCH')
            cap=min(budget.caps['snapshot_wire_bytes' if kind==B else 'request_wire_bytes'],budget.caps['unique_bytes']-total+len(iv))
            try:wire=retention._read_at(fd,name,cap,fault).data
            except FileNotFoundError as e:raise retention._error('INPUT_CHANGED_DURING_READ') from e
            total+=len(wire)
            if H(wire)!=h:raise problem('AUTHORITY_REFERENCE_MISMATCH')
            entries.append((kind,wire))
        if retention._metadata(os.fstat(fd))!=before:raise retention._error('INPUT_CHANGED_DURING_READ')
    return iv,entries


def execute(args,*,fault=None,observer=None):
    mode=args.operation.removeprefix('governed-')
    if mode=='verify':
        inspected=persistent.verify(args.bundle,fault=fault,observer=observer)
        return {'operation':'verify','integrity_state':'complete_bundle','bundle_commitment':inspected.manifest_sha256}
    persistent.output_parent(args.output_dir)
    if mode=='replay':
        published=persistent.replay(args.bundle,args.output_dir,fault=fault,observer=observer)
    elif mode=='evaluate':
        if type(args.authority_pin) is not str or not SHA.fullmatch(args.authority_pin):raise problem('AUTHORITY_REFERENCE_MISMATCH')
        iv,objects=capture_inputs(args.invocation,args.objects_dir,fault=fault)
        prior=None;budget=Budget(observer=observer)
        if args.compare_to:
            prior=dict(persistent.capture_bundle(args.compare_to,fault=fault,observer=observer,_budget=budget).captured)
        review=governed_review._evaluate(iv,objects,args.authority_pin,prior,budget,observer)
        published=persistent.publish(args.output_dir,review,fault=fault,observer=observer)
    else:
        from .cli import _problem
        raise _problem('CLI_USAGE')
    result=json.loads(published.captured['result.json'])
    receipt={'operation':mode,'evaluation_permitted':result['admissibility']['evaluation_permitted'],
             'disposition':result['admissibility']['disposition'],'result_commitment':H(published.captured['result.json']),
             'bundle_commitment':published.manifest_sha256}
    if len(C(receipt))+1>512:raise retention._error('OUTPUT_LIMIT_EXCEEDED')
    return receipt
