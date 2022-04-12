
import pytest

from research.adversaries.EnvironmentFactory import *


def test_R1V1(host, port):
    env = EnvironmentFactory.create(AvailableEnvironments.R1V1Env1)
    assert env is not None
    