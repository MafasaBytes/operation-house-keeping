"""Proposed external G-app root adapter for the two unchanged S7 assertion bodies.

Configure before pytest starts. This substitutes three already verified roots for
the test helper's clone calls; fresh clone-helper behavior belongs to F-full.
"""

from pathlib import Path
import subprocess

CURRENT = 'c321f2e096a71a43bf65787f6f1605c4031266e7'
S6 = 'c37c24ee50667121d6b2dc4739aa3b7d12825c96'
NODES = {'test_two_clean_roots_twelve_constructions_and_exact_replay',
         'test_accepted_s6_archive_recovers_in_clean_matching_build'}


def _git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()


class RootAdapter:
    def __init__(self, current_a, current_b, historical):
        self.roots = [Path(p).resolve(strict=True) for p in
                      (current_a, current_b, historical)]
        if len(set(self.roots)) != 3:
            raise ValueError('three distinct roots required')
        for root, revision in zip(self.roots, (CURRENT, CURRENT, S6)):
            if _git(root, 'rev-parse', 'HEAD') != revision:
                raise ValueError(f'wrong root revision: {root}')
            if _git(root, 'status', '--porcelain'):
                raise ValueError(f'dirty root: {root}')
            if (root / '.git/objects/info/alternates').exists():
                raise ValueError(f'alternate object store: {root}')
            if not all((root / name).is_file() for name in
                       ('applications/bounded_decision_workflow/__main__.py',
                        'applications/bounded_decision_workflow/cli.py')):
                raise ValueError(f'missing executable material: {root}')
        stores = [(root / '.git/objects').stat() for root in self.roots]
        if len({(s.st_dev, s.st_ino) for s in stores}) != 3:
            raise ValueError('Git databases are not independent')

    def pytest_runtest_setup(self, item):
        if item.name not in NODES:
            return
        module = item.module
        if getattr(module, '_slice5_root_adapter_active', False):
            raise RuntimeError('root adapter already active')
        original = module.clone
        calls = []

        def selected_root(path, commit='HEAD'):
            expected = ('source-0', 'source-1') if item.name.startswith('test_two_') else ('accepted-source',)
            if len(calls) >= len(expected) or Path(path).name != expected[len(calls)]:
                raise AssertionError('unexpected clone request')
            if commit != ('HEAD' if item.name.startswith('test_two_') else S6):
                raise AssertionError('unexpected clone revision')
            root = self.roots[len(calls)] if item.name.startswith('test_two_') else self.roots[2]
            calls.append(root)
            return root

        expected_calls = 2 if item.name.startswith('test_two_') else 1
        module._slice5_root_adapter_active = True
        module._slice5_root_adapter_restore = (original, calls, expected_calls)
        module.clone = selected_root

    def pytest_runtest_teardown(self, item):
        if item.name not in NODES:
            return
        module = item.module
        original, calls, expected = module._slice5_root_adapter_restore
        module.clone = original
        del module._slice5_root_adapter_restore
        del module._slice5_root_adapter_active
        if len(calls) != expected:
            raise AssertionError('not every expected root was used')
