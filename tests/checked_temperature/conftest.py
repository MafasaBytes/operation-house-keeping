import pytest

from tests.checked_temperature import later_chain


@pytest.fixture(scope='session', autouse=True)
def _later_chain_base(tmp_path_factory):
    """Later-chain stores live inside this launch's basetemp (counted storage)."""
    later_chain.set_base(tmp_path_factory.mktemp('later-chains'))
    yield
