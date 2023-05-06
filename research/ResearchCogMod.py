from datetime import datetime as date
from enum import Enum
import carla
import logging
from agents.vehicles import VehicleFactory
from lib import SimulationMode
from lib.MapManager import MapNames
from lib import Simulator
from .BaseCogModResearch import BaseCogModResearch
from research.BaseResearch import BaseResearch
from settings.CogModSettings import CogModSettings


#  import for cogmod
from agents.vehicles.CogMod.CogModAgent import CogModAgent
from analytics.DataCollector import DataCollector


class ScenarioState(Enum):
    START = 0
    RUNNING = 1
    END = 2
    PENDING = 3
    DISCARD = 4
    pass


camera_angle = carla.Rotation(pitch=-45, yaw=0, roll=0)

class ResearchCogMod(BaseCogModResearch):

    def __init__(self,
                 client,
                 logLevel=logging.INFO,
                 outputDir="logs",
                 simulationMode=SimulationMode.ASYNCHRONOUS,
                 scenarioID="scenario1"):

        self.name = "ResearchCogMod"
        self.scenarioID = scenarioID
        self.researchSettings = CogModSettings(scenarioID)

        # getting the values for the scenarios
        self.mapName = self.researchSettings.getMapName()
        self.cogmodAgentSettings = self.researchSettings.getCogModAgentSettings()
        self.actorAgentSettings = self.researchSettings.getActorAgentSettings()
        self.triggerDistance = self.researchSettings.getTriggerDistance()

        self.scenario_state = ScenarioState.PENDING
        self.episode = 1
        self.nEpisode = 4

        # initializing the base class
        super().__init__(name=self.name, 
                         client=client, 
                         mapName=self.mapName, 
                         logLevel=logLevel, 
                         outputDir=outputDir, 
                         simulationMode=simulationMode,
                         showSpawnPoints=True)
        
        self.simulator = None
        self.cogmodAgent = None
        self.actorAgent = None

        self.data_collector = DataCollector()

        pass

    def restart_scenario(self):
        self.scenario_state = ScenarioState.PENDING
        self.episode += 1
        if self.episode > self.nEpisode:
            dateStr = date.now().strftime("%Y-%m-%d-%H-%M-%S")
            self.data_collector.saveCSV(dateStr, self.outputDir)
            self.logger.info("simulation ended saving data....")
            exit()
            
        self.cogmodAgent = self.createCogModAgent(self.cogmodAgentSettings)
        self.actorAgent = self.createActorAgent(self.actorAgentSettings)
        self.logger.info(f"running research in asynchronous mode")
        self.world.wait_for_tick()

        pass
 

    def run(self, maxTicks=100):
        
        if self.simulationMode == SimulationMode.ASYNCHRONOUS:
            self.cogmodAgent = self.createCogModAgent(self.cogmodAgentSettings)
            self.actorAgent = self.createActorAgent(self.actorAgentSettings)
            self.logger.info(f"running research in asynchronous mode")
            self.world.wait_for_tick()
            pass
        else:
            raise Exception(f"Simulation mode {self.simulationMode} not supported")


        # self.SetSpectator(self.cogmodAgent.get_vehicle().get_location(), 60)

        onTickers = [self.ScenarioState, self.dataCollectorOnTick,  self.onTick]
        onEnders = [self.onEnd]
        self.simulator = Simulator(self.client, onTickers=onTickers, onEnders=onEnders, simulationMode=self.simulationMode)
        self.simulator.run(maxTicks=maxTicks)
        
        pass

    def ScenarioState(self, world_snapshot):
        self.scenario_state = self.checkScenarioState(self.cogmodAgent, 
                                                    self.actorAgent,
                                                    self.triggerDistance)

    def dataCollectorOnTick(self, world_snapshot):

        scenario_state = self.scenario_state

        if scenario_state == ScenarioState.PENDING:
            # self.logger.info("Scenario pending")
            # self.data_collector.initDataDict()
            self.data_collector.collectStats(world_snapshot, 
                                             self.cogmodAgent,
                                             self.actorAgent,
                                             self.episode)
            return 
        elif scenario_state == ScenarioState.START:
            # self.data_collector.initDataDict()
            self.data_collector.collectStats(world_snapshot, 
                                             self.cogmodAgent,
                                             self.actorAgent,
                                             self.episode)
            self.logger.info("Scenario started")
        elif scenario_state == ScenarioState.RUNNING:
            self.data_collector.collectStats(world_snapshot, 
                                             self.cogmodAgent,
                                             self.actorAgent,
                                             self.episode)
            # self.logger.info("Scenario running")
        elif scenario_state == ScenarioState.END:
            self.data_collector.collectStats(world_snapshot,
                                             self.cogmodAgent,
                                             self.actorAgent,
                                             self.episode)
            self.data_collector.updateTrajectoryDF()
            self.logger.info("Scenario ended")
        elif scenario_state == ScenarioState.DISCARD:
            self.logger.info("Scenario discarded")
            pass
            
        pass

    def onTick(self, world_snapshot):

        scenario_state = self.scenario_state

        if scenario_state == ScenarioState.PENDING or \
            scenario_state == ScenarioState.START or \
            scenario_state == ScenarioState.RUNNING:

            cogomd_vehicle = self.cogmodAgent.get_vehicle()
            actor_vehicle = self.actorAgent.get_vehicle()

            actor_speed = self.actorAgent.get_vehicle().get_velocity().length()
            cogmod_speed = self.cogmodAgent.get_vehicle().get_velocity().length()

            print(f"Actor speed {actor_speed} Cogmod speed {cogmod_speed}")

            self.SetSpectator(cogomd_vehicle.get_location(), camera_angle, 60)

            # self.logger.info(f"Cogmod vehicle location {cogomd_vehicle.get_location()}")
            # self.logger.info(f"Actor vehicle location {actor_vehicle.get_location()}")

            distance = cogomd_vehicle.get_location().distance(actor_vehicle.get_location())
            
            if distance > self.triggerDistance:
                super().onTick(world_snapshot)
            
            else:
                actor_control = self.actorAgent.add_emergency_stop(carla.VehicleControl())
                actor_vehicle.apply_control(actor_control)
                cogmod_control = self.cogmodAgent.run_step()
                cogomd_vehicle.apply_control(cogmod_control)
        if scenario_state == ScenarioState.END or \
            scenario_state == ScenarioState.DISCARD:
            # restart the scenario
            self.onEnd()
            self.world.wait_for_tick()
            
            self.restart_scenario()

            pass

    def checkScenarioState(self, cogmod_agent, actor_agent, trigger_distance):
        
        actor_speed_threshold = 6
        cogmod_speed_threshold = 8
        start_distance_threshold = 1

        updated_threshold = trigger_distance + start_distance_threshold

        actor_speed = actor_agent.get_vehicle().get_velocity().length()
        cogmod_speed = cogmod_agent.get_vehicle().get_velocity().length()

        actor_location = actor_agent.get_vehicle().get_location()
        cogmod_location = cogmod_agent.get_vehicle().get_location()

        # if scneario pending: when the simulation started but the cogmod 
        # speed and actor speed is below threshold, and distance is greater 
        # than trigger distance 

        if self.scenario_state == ScenarioState.PENDING:
            distance = actor_location.distance(cogmod_location)
            #  if distance is in trigger distance and 
            #  both actor and cogmod speed is above threshold, start the scenario
            if distance < updated_threshold and \
                actor_speed >= actor_speed_threshold and \
                    cogmod_speed >= cogmod_speed_threshold:
                    self.scenario_state = ScenarioState.START
                    return self.scenario_state
            # if distance is in trigger distance and
            #  either actor or cogmod speed is below threshold, 
            # discard the scenario
            elif distance < updated_threshold and \
                (actor_speed < actor_speed_threshold or cogmod_speed < cogmod_speed_threshold):
                    self.scenario_state = ScenarioState.DISCARD
                    return self.scenario_state
            pass

        elif self.scenario_state == ScenarioState.DISCARD or \
             self.scenario_state == ScenarioState.END:
            #  self.scenario_state = ScenarioState.PENDING
             return self.scenario_state
        
        elif self.scenario_state == ScenarioState.RUNNING:
            rounded_actor_speed = int(actor_speed)
            rounded_cogmod_speed = int(cogmod_speed)
            if rounded_actor_speed == 0 and rounded_cogmod_speed == 0:
                self.scenario_state = ScenarioState.END
                return self.scenario_state
        elif self.scenario_state == ScenarioState.START:
            self.scenario_state = ScenarioState.RUNNING
            return self.scenario_state
        # self.logger.info(f"speed Cogmod: {round(cogmod_speed, 2) }, Actor: {round(actor_speed, 2)}")
        return self.scenario_state
        pass
