import json
import carla
import logging

from matplotlib import transforms
from agents.pedestrians.soft import NavObjectMapper, NavPath
from lib.ClientUser import ClientUser
from .SourceDestinationPair import SourceDestinationPair
from typing import List, Optional

class SettingsManager(ClientUser):

    def __init__(self, client, settingsDict) -> None:
        super().__init__(client)
        self.name = "SettingsManager"

        self.settingsDict = settingsDict
        self.currentSetting = None
        self._walkerSettings:List[SourceDestinationPair] = None
        self._walkerTransforms = None

        self._vehicleSettings: List[SourceDestinationPair] = None
        self._vehicleTransforms = None



        pass


    def load(self, settingsId):
        self.currentSetting = self.settingsDict[settingsId]

        self._walkerSettings = None
        self._walkerTransforms = None

        self._vehicleSettings = None
        self._vehicleTransforms = None
        

    def _assertCurrentSetting(self):
        if self.currentSetting is None:
            msg = f"{self.name}:currentSetting is None"
            self.error(msg)
    
    
    
    def _pointToLocation(self, point, z=1):
        
        location = carla.Location(
            x = point[0],
            y = point[1],
            z = z
        )

        return location

    
    def locationToVehicleSpawnPoint(self, location: carla.Location) -> carla.Transform:

        # find a way point
        waypoint = self.map.get_waypoint(location, project_to_road=True, lane_type=carla.LaneType.Driving)
        if waypoint is None:
            msg = f"{self.name}: Cannot create way point near {location}"
            self.error(msg)
        transform = carla.Transform(location = waypoint.transform.location + carla.Location(z=1), rotation = waypoint.transform.rotation)
        # print(waypoint.transform)
        # print(transform)
        # exit(1)
        return transform


    # def getEgoSpawnpoint(self) -> carla.Transform:
    #     self._assertCurrentSetting()
        
    #     point = self.currentSetting["ego_setting"]
    #     location = self._pointToLocation(point)
    #     return self.locationToVehicleSpawnPoint(location)

    
    def getVehicleSettings(self):
        self._assertCurrentSetting()

        if self._vehicleSettings is None:
            self._vehicleSettings = []
            for setting in self.currentSetting["ego_settings"]:
                sourcePoint = (setting[0], setting[1])
                destinationPoint = (setting[2], setting[3])

                self._vehicleSettings.append(
                    SourceDestinationPair(
                        source=self._pointToLocation(sourcePoint),
                        destination=self._pointToLocation(destinationPoint, z=0.1)
                    )
                )

        return self._vehicleSettings
    
    def getWalkerSettings(self) -> List[SourceDestinationPair]:
        self._assertCurrentSetting()

        if self._walkerSettings is None:
            self._walkerSettings = []
            for setting in self.currentSetting["walker_settings"]:
                sourcePoint = (setting[0], setting[1])
                destinationPoint = (setting[2], setting[3])

                self._walkerSettings.append(
                    SourceDestinationPair(
                        source=self._pointToLocation(sourcePoint),
                        destination=self._pointToLocation(destinationPoint, z=0.1)
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




    def getNumberOfVehicleWithSpawnPointAndDestination(self):
        numberOfVehicles = self.currentSetting["number_of_vehicles"]
        spawnPoints = self.currentSetting["spawn_points"]
        destinationPoints = self.currentSetting["destination_points"]

        spawnPoints_transforms = []
        destinationPoints_transforms = []

        for sp in spawnPoints:
            point_to_location = self._pointToLocation(sp)
            location_to_transform = self.locationToVehicleSpawnPoint(point_to_location)
            spawnPoints_transforms.append(location_to_transform)
        for dp in destinationPoints:
            point_to_location = self._pointToLocation(dp)
            location_to_transform = self.locationToVehicleSpawnPoint(point_to_location)
            destinationPoints_transforms.append(location_to_transform)

        return (numberOfVehicles, spawnPoints_transforms, destinationPoints_transforms)

    def getNumberOfCogmodAgentsWithParameters(self):
        cogmod_agent_settings = self.currentSetting["cogmod_agents"]
        numberOfAgents = cogmod_agent_settings["number_of_cogmod_agents"]

        agent_parameter_list = []
        for i in range(1, numberOfAgents+1):
            current_setting = cogmod_agent_settings[str(i)]

            spawn_coordinate = current_setting["spawn_point"]
            destination_coordinate = current_setting["destination_point"]

            spawn_location = self._pointToLocation(spawn_coordinate)
            destination_location = self._pointToLocation(destination_coordinate)

            spawn_transform = self.locationToVehicleSpawnPoint(spawn_location)
            destination_transform = self.locationToVehicleSpawnPoint(destination_location)

            current_setting['spawn_point'] = spawn_transform
            current_setting['destination_point'] = destination_transform

            agent_parameter_list.append(current_setting)

        # print(agent_parameter_list)
        return (numberOfAgents, agent_parameter_list)

    def getNumberOfActorAgentsWithTrajectories(self):
        actor_agent_settings = self.currentSetting["actor_agents"]
        numberOfAgents = actor_agent_settings["number_of_actor_agents"]

        actor_trajectory_list = []
        for i in range (1, numberOfAgents+1):
            current_setting = actor_agent_settings[str(i)]
            trajectory = current_setting["trajectory"]
            trajectory_transforms = []
            for coordinate, time in trajectory:
                # print(coordinate, time)
                point_to_location = self._pointToLocation(coordinate)
                location_to_transform = self.locationToVehicleSpawnPoint(point_to_location)
                trajectory_transforms.append((location_to_transform, time))
            actor_trajectory_list.append(trajectory_transforms)
            pass

        return (numberOfAgents, actor_trajectory_list)
    
    def getSpectatorSettings(self) -> Optional[carla.Transform]:
        if "spectator_settings" not in self.currentSetting:
            return None
        
        location = carla.Location(
            x = self.currentSetting["spectator_settings"]["x"],
            y = self.currentSetting["spectator_settings"]["y"],
            z = self.currentSetting["spectator_settings"]["z"]
        )
        rotation = carla.Rotation(
            pitch = self.currentSetting["spectator_settings"]["pitch"],
            yaw = self.currentSetting["spectator_settings"]["yaw"],
            roll = 0.0
        )

        return carla.Transform(location, rotation)
    
    def getVisualizationForceLocation(self) -> Optional[carla.Location]:
        if "visualization_force_location" not in self.currentSetting:
            return None
        
        return carla.Location(
            x = self.currentSetting["visualization_force_location"]["x"],
            y = self.currentSetting["visualization_force_location"]["y"],
            z = self.currentSetting["visualization_force_location"]["z"]
        )
    
    def getNavPaths(self, filePath: str) -> List[NavPath]:
        with open(filePath, "r") as f:
            dicts = json.loads(f.read())
            return NavObjectMapper.pathsFromDicts(dicts)
    
    
        



