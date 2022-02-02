import pytest
from agents.pedestrians.factors import InternalFactors

@pytest.fixture
def factorPath():
    return "settings/internal_factors_default.yaml"


def test_factorLoad(factorPath):
    factors = InternalFactors(factorPath)
    print(factors.props)
    assert "relaxation_time" in factors.props
    assert factors.relaxation_time > 0.0
    assert factors["relaxation_time"] > 0.0
