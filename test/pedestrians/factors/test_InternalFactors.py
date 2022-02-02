import pytest
from agents.pedestrians.factors import InternalFactors

@pytest.fixture
def factorPath():
    return "settings/internal_factors_default.yaml"


def test_factorLoad(factorPath):
    factors = InternalFactors(factorPath)
    assert False