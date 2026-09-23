"""Explicit measurement command dispatch; no matrices or injectable computations."""
import os
import argparse
import json
import sys
from . import reassessment_runtime as runtime
from .measurement_wire import Work, fail, DIAGNOSTIC_CEILING, BUNDLE_STATE
from .measurement_contracts import MeasurementContractError, canonical_json_bytes
from .errors import WorkflowInputError


class Parser(argparse.ArgumentParser):
    def error(self,message):fail('CLI_USAGE','arguments','usage')


def arguments(argv):
    p=Parser(add_help=False,allow_abbrev=False)
    sub=p.add_subparsers(dest='operation',required=True,parser_class=Parser)
    for mode in ['evaluate','verify','replay']:
        c=sub.add_parser('reassessment-'+mode,add_help=False,allow_abbrev=False)
        fields=['invocation','objects-dir','authority-pin','output-dir'] if mode=='evaluate' else ['bundle']+(['output-dir'] if mode=='replay' else [])
        for field in fields:c.add_argument('--'+field,required=True)
        if mode!='verify':c.add_argument('--limits')
    flags=[s.split('=',1)[0] for s in argv if s.startswith('--')]
    if len(flags)!=len(set(flags)):fail('CLI_USAGE','arguments','usage')
    return p.parse_args(argv)


def _emit(fd,wire):
    # Unbuffered writes avoid a second interpreter-shutdown flush/exit 120.
    view=memoryview(wire)
    while view:
        n=os.write(fd,view)
        if n<=0:raise OSError('output unavailable')
        view=view[n:]


def main(argv=None):
    defaults=Work()
    BUNDLE_STATE.set('absent')
    try:
        args=arguments(sys.argv[1:] if argv is None else argv)
        if args.operation=='reassessment-evaluate':
            answer=runtime.evaluate(args.invocation,args.objects_dir,args.authority_pin,args.output_dir,args.limits)
        elif args.operation=='reassessment-verify':answer=runtime.verify(args.bundle)
        else:answer=runtime.replay(args.bundle,args.output_dir,args.limits)
        wire=canonical_json_bytes(answer)+b'\n';defaults.guard('receipt_bytes',len(wire))
        _emit(1,wire);return 0
    except MeasurementContractError as error:
        code=error.code;stage=error.stage;field=error.target;details=error.details
        status=2 if stage=='usage' else 4 if code=='RESOURCE_LIMIT_EXCEEDED' else 5 if stage=='path' else 6 if stage=='retention' else 7 if stage=='internal' else 3
    except WorkflowInputError as error:
        d=error.diagnostic;code=d.code;stage='path' if d.exit_code==5 else 'retention' if d.exit_code==6 else 'phase_1';field=d.target;details={};status=d.exit_code
    except Exception:
        code='INTERNAL_ERROR';stage='internal';field='application';details={};status=7
    resource={k:details[k] for k in ['dimension','attempted','limit']} if all(k in details for k in ['dimension','attempted','limit']) else None
    diagnostic=dict(schema='nr.diagnostic.v2',code=code,stage=stage,target=dict(request=details.get('request'),field=field if field.startswith('/') else '/'+field,logical_id=details.get('logical_id'),references=details.get('references',[]),occurrence_count=details.get('occurrence_count')),
        resource=resource,retry='reduce_input_or_request_policy_review' if resource is not None else 'correct_input',bundle_state=BUNDLE_STATE.get() if BUNDLE_STATE.get()!='absent' else 'incomplete' if stage=='retention' else 'absent',message_key=code.lower())
    wire=canonical_json_bytes(diagnostic)+b'\n'
    if len(wire)>DIAGNOSTIC_CEILING.get():
        diagnostic.update(code='DIAGNOSTIC_LIMIT_EXCEEDED',target=None,resource=None,message_key='diagnostic_limit_exceeded')
        wire=canonical_json_bytes(diagnostic)+b'\n';status=4
    try:_emit(2,wire)
    except OSError:return 7
    return status


if __name__=='__main__':raise SystemExit(main())
