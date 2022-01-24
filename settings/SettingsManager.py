import carla
import logging
from lib.ClientUser import ClientUser
from .WalkerSetting import WalkerSetting
from typing import List

class SettingsManager(ClientUser):

    def __init__(self, client, settingsDict) -> None:
        super().__init__(client)
        self.name = "SettingsManager"

        self.settingsDict = settingsDict
        self.currentSetting = None
        self._walkerSettings:List[WalkerSetting] = None
        self._walkerTransforms = None
        pass


    def load(self, settingsId):
        self.currentSetting = self.settingsDict[settingsId]
        self._walkerSettings = None
        self._walkerTransforms = None

    def assertCurrentSetting(self):
        if self.currentSetting is None:
            msg = f"{self.name}:currentSetting is None"
            self.error(msg)
    
    
    
    def _pointToLocation(self, point):
        
        location = carla.Location(
            x = point[0],
            y = point[1],
            z = 1.0
        )

        return location

    
    def _locationToVehicleSpawnPoint(self, location: carla.Location) -> carla.Transform:

        # find a way point
        waypoint = self.map.get_waypoint(location, project_to_road=True, lane_type=carla.LaneType.Driving)
        if waypoint is None:
            msg = f"{self.name}: Cannot create way point near {location}"
            self.error(msg)
        return waypoint


    def getEgoSpawnpoint(self) -> carla.Transform:
        self.assertCurrentSetting()
        
        point = self.currentSetting["ego_spawn_point"]
        location = self._pointToLocation(point)
        return self._locationToVehicleSpawnPoint(location)

    
    def getWalkerSettings(self):
        self.assertCurrentSetting()

        if self._walkerSettings is None:
            self._walkerSettings = []
            for setting in self.currentSetting["walker_settings"]:
                print(setting)
                sourcePoint = (setting[0], setting[1])
                destinationPoint = (setting[2], setting[3])

                self._walkerSettings.append(
                    WalkerSetting(
                        source=self._pointToLocation(sourcePoint),
                        destination=self._pointToLocation(destinationPoint)
                    )
                )

        return self._walkerSettings
    
    def getWalkerSpawnPoints(self):

        if self._walkerTransforms is None:
            walkerSettings = self.getWalkerSettings()
            self._walkerTransforms = []

            for walkerSetting in walkerSettings:
                sourceTransform = carla.Transform(
                    location = walkerSetting.source
                )
                destination = walkerSetting.destination

                self._walkerTransforms.append((sourceTransform, destination))

        return self._walkerTransforms



