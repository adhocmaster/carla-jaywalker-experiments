import pytest
import carla

from settings import SettingsManager
from settings.circular_t_junction_settings import circular_t_junction_settings

@pytest.fixture
def client():   
    return carla.Client("127.0.0.1", 2000)
    

@pytest.fixture
def settingsManager():
    return SettingsManager(client, circular_t_junction_settings)


def test_walkerSettings(settingsManager):
    settingsManager.load("setting1")
    # validate vehicle spawn point
    # validate walker settings
    walkerSettings = settingsManager.getWalkerSettings()
    firstSetting = walkerSettings[0]
    assert firstSetting.source.x == -160.0 and firstSetting.source.y == -24.0
    assert firstSetting.destination.x == -151.0 and firstSetting.destination.y == -24.0