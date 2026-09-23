"""Offline documentation/fixture recovery, not a production measurement command.

Run as `python -m docs.next-measurement.recover` is not supported: use the documented
runpy invocation from the clean checkout so its actual application is importable.
"""
import argparse
import base64
import hashlib
import io
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT/'docs/superpowers/reports/2026-09-23-next-measurement-slice6-correction-evidence/frozen-authority.zip'
PACKAGE_SHA = 'a6e48ea447444e4f7c12993d9567905978c2a0c8972414e0ac421df47cd2217f'
MANIFEST_SHA = '18ed716ab327944f700b8e00b30235512a9ea6d5b41f49e87ab88b343680e2ea'
RECOVERY_SHA = 'ecfe3f62d796a21edc5509419206aebb68d46d8d3f10736d6708c412110a8dac'

def sha(b): return hashlib.sha256(b).hexdigest()
def wire(v): return json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument('--package-dir', type=Path)
    choice.add_argument('--example-dir', type=Path)
    args = parser.parse_args()
    with zipfile.ZipFile(ARCHIVE) as outer:
        # Archive member names are fixed, not discovered from a working directory.
        files = {name: outer.read(name) for name in ('package.zip', 'MANIFEST.json', 'recovery.json')}
    for name, expected in [('package.zip', PACKAGE_SHA), ('MANIFEST.json', MANIFEST_SHA), ('recovery.json', RECOVERY_SHA)]:
        if sha(files[name]) != expected: raise ValueError('frozen commitment mismatch: '+name)
    manifest = json.loads(files['MANIFEST.json'])
    with zipfile.ZipFile(io.BytesIO(files['package.zip'])) as package:
        payload = {}
        for e in manifest['files']:
            path = Path(e['path'])
            if path.is_absolute() or '..' in path.parts: raise ValueError('unsafe archived path')
            b = package.read(e['path'])
            if len(b) != e['bytes'] or sha(b) != e['sha256']: raise ValueError('payload commitment mismatch')
            payload[e['path']] = b
    if args.package_dir:
        dst = args.package_dir; dst.mkdir(parents=False, exist_ok=False)
        for name, b in {**payload, **files}.items():
            p = dst/name; p.parent.mkdir(parents=True, exist_ok=True)
            with p.open('xb') as f: f.write(b)
        print(json.dumps(dict(package_sha256=PACKAGE_SHA, members=len(payload), destination=str(dst))))
        return
    # Read only synthetic input premises. Frozen expected outputs are never used.
    from applications.bounded_decision_workflow.measurement_build import identity
    capture = json.loads(payload['inputs/P/capture.json'])
    members = {}
    for member in capture['members']:
        ref = member['reference']; b = base64.b64decode(member['bytes'], validate=True)
        if sha(b) != ref['sha256']: raise ValueError('input member commitment mismatch')
        members[(ref['kind'], ref['sha256'])] = b
    invocation = json.loads(members.pop(('nm.invocation.v1', capture['invocation']['sha256'])))
    members = {k:v for k,v in members.items() if k[0] != 'nm.prepared-build.v1'}
    build = identity(); invocation['build_identity'] = sha(build)
    members[('nm.build.v1', sha(build))] = build
    dst = args.example_dir; dst.mkdir(parents=False, exist_ok=False)
    objects = dst/'objects'; objects.mkdir()
    for (kind, digest), b in sorted(members.items()): (objects/(digest+'.'+kind)).write_bytes(b)
    (dst/'invocation.json').write_bytes(wire(invocation))
    (dst/'authority-pin.txt').write_text(capture['authority_pin']+'\n')
    print(json.dumps(dict(package_sha256=PACKAGE_SHA, authority_pin=capture['authority_pin'], build_sha256=sha(build), checkpoint=json.loads(build)['checkpoint'], destination=str(dst))))

if __name__ == '__main__': main()
