"""Test-only corpus-destination substitution for test_delivery.py (F1 capacity).

``tests/reassessment_profile/delivery_budget.py`` hard-codes the Slice 4 corpus
``ROOT`` (an absolute path to ``nr-slice4-qualification-r1``) together with the
corpus caps and inventory assertions. That historical corpus has room for at
most one more delivery run under its own caps, and it must be preserved.

Under explicit owner authorization this plugin substitutes only the module
global ``delivery_budget.ROOT`` with a fresh, separately accounted corpus root
named by ``REL5_CORPUS_ROOT``, before test collection imports
``test_delivery`` (which binds ``ROOT`` by ``from delivery_budget import``).
Everything else in ``delivery_budget`` -- CAPS, the inventory assertions
(files <= 4096, dirs <= 512, physical <= 54,525,952, total <= 33,554,432, free
space), reserve/record/put/directory and the test assertions -- is unchanged
and now applies to the fresh root. The historical root is never touched.

The substituted root must already exist and satisfy the corpus shape the
module assumes: exactly the seven category directories and at least one
index record (``inventory()`` maps every top-level entry to a category;
``record()`` chains from the last existing index file; ``cli()`` runs with
cwd ``ROOT/recovery``). It must not be the historical root, must be a
directory on a supported local filesystem (``findmnt`` reports ext4 or xfs,
the same check the tests apply), and must be empty apart from that shape.
The plugin refuses loudly otherwise; it never creates or deletes anything.
"""
import os
import subprocess
from pathlib import Path

ENV = 'REL5_CORPUS_ROOT'
EVIDENCE_ENV = 'REL5_CORPUS_ROOT_EVIDENCE'   # optional: JSON record of original and substituted paths
HISTORICAL = Path('/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/nr-slice4-qualification-r1')
CATEGORIES = ('outputs', 'repairs', 'inputs', 'logs', 'recovery', 'indexes', 'exports')


def _validate(root):
    if not root.is_absolute() or not root.is_dir() or root.is_symlink():
        raise ValueError('REL5_CORPUS_ROOT must be an existing absolute directory')
    if root.resolve() == HISTORICAL.resolve() or HISTORICAL.resolve() in root.resolve().parents:
        raise ValueError('REL5_CORPUS_ROOT must not be the historical Slice 4 corpus')
    kind = subprocess.check_output(['findmnt', '-T', str(root), '-n', '-o', 'FSTYPE'], text=True).strip()
    if kind not in ('ext4', 'xfs'):
        raise ValueError('REL5_CORPUS_ROOT must be on a supported local filesystem, found %r' % kind)
    entries = sorted(p.name for p in root.iterdir())
    if entries != sorted(CATEGORIES):
        raise ValueError('REL5_CORPUS_ROOT must contain exactly the corpus categories, found %r' % entries)
    if not list((root / 'indexes').glob('*.json')):
        raise ValueError('REL5_CORPUS_ROOT needs a genesis index record')
    for name in CATEGORIES:
        if name != 'indexes' and any((root / name).iterdir()):
            raise ValueError('REL5_CORPUS_ROOT category %s is not empty' % name)


def _substitute():
    import delivery_budget
    import json
    root = Path(os.environ[ENV])
    _validate(root)
    original = delivery_budget.ROOT
    delivery_budget.ROOT = root
    evidence = os.environ.get(EVIDENCE_ENV)
    if evidence:
        with Path(evidence).open('x') as stream:
            json.dump(dict(module='delivery_budget', attribute='ROOT', original=str(original),
                           substituted=str(root), historical=str(HISTORICAL),
                           original_is_historical=original.resolve() == HISTORICAL.resolve(),
                           caps=delivery_budget.CAPS, categories=list(CATEGORIES)), stream, sort_keys=True)
    return root


SUBSTITUTED_ROOT = _substitute()


def pytest_report_header(config):
    return 'slice5_delivery_root_adapter: delivery_budget.ROOT substituted with %s' % SUBSTITUTED_ROOT
