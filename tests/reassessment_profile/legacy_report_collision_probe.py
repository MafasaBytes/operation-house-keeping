"""One scheduled red control reproducing the original reporting-hook collision."""
import os
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve();target=Path(sys.argv[2]).resolve()
os.chdir(root);sys.path.insert(0,str(root))
import pytest

class LegacyReporter:
    def pytest_runtest_logreport(self,report):
        with target.open('ab') as stream:
            stream.write((report.nodeid+' '+report.when+' '+report.outcome+'\n').encode())

node='tests/identity_binding/test_state_anchor.py::test_minter_has_no_io_store_network_environment_or_backend_dependency'
raise SystemExit(pytest.main(['-o','addopts=','-p','no:cacheprovider',node,'-q'],plugins=[LegacyReporter()]))
