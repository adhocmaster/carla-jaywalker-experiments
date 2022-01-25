import carla
import argparse
import logging
import random
import time
import eventlet
# eventlet.monkey_patch()

from agents.navigation.behavior_agent import BehaviorAgent  # pylint: disable=import-error
from agents.navigation.basic_agent import BasicAgent  # pylint: disable=import-error
from agents.pedestrians.PedestrianAgent import PedestrianAgent
from settings.circular_t_junction_settings import circular_t_junction_settings
from settings import SettingsManager

from agents.pedestrians import PedestrianFactory

from lib import SimulationVisualization, MapNames, MapManager, Simulator
from lib.state import StateManager

SpawnActor = carla.command.SpawnActor

argparser = argparse.ArgumentParser()

argparser.add_argument(
    '--host',
    metavar='H',
    default='127.0.0.1',
    help='IP of the host server (default: 127.0.0.1)')
argparser.add_argument(
    '-p', '--port',
    metavar='P',
    default=2000,
    type=int,
    help='TCP port to listen to (default: 2000)')
argparser.add_argument(
    '--tm-port',
    metavar='P',
    default=8000,
    type=int,
    help='Port to communicate with TM (default: 8000)')

args = argparser.parse_args()

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

client = carla.Client(args.host, args.port)
client.set_timeout(5.0)

logging.info(f"Client carla version: {client.get_client_version()}")
logging.info(f"Server carla version: {client.get_server_version()}")

if client.get_client_version() != client.get_server_version():
    logging.warning("Client and server version mistmatch. May not work properly.")

SpawnActor = carla.command.SpawnActor

mapManager = MapManager(client)
# mapManager.load(MapNames.t_junction)
mapManager.load(MapNames.circle_t_junctions)

world = mapManager.world

visualizer = SimulationVisualization(client, mapManager)
# visualizer.draw00()

map = mapManager.map

# nav_points = mapManager.generateNavPoints(100)

# visualizer.drawWalkerNavigationPoints(nav_points)
visualizer.drawSpawnPoints()
visualizer.drawSpectatorPoint()
visualizer.drawAllWaypoints(life_time=0.0)


# setting = circular_t_junction_settings["setting1"]

# walkerSpawnPoint = carla.Transform(
#     location = carla.Location(
#         x = setting["walker_spawn_points"][1][0],
#         y = setting["walker_spawn_points"][1][1],
#         z = 1.0
#     )
# ) 

settingsManager = SettingsManager(client, circular_t_junction_settings)
settingsManager.load("setting1")
walkerSettings = settingsManager.getWalkerSettings()

walkerSetting = walkerSettings[1]
walkerSpawnPoint = carla.Transform(location = walkerSetting.source)
destination = walkerSetting.destination
visualizer.drawWalkerNavigationPoints([walkerSpawnPoint])

objectsInPath = world.cast_ray(walkerSetting.source, walkerSetting.destination)
print(objectsInPath)
for lb in objectsInPath:
    print(f"Labeled point location {lb.location} and semantic {lb.label} distance {walkerSetting.source.distance(lb.location)}")

# exit(0)


pedFactory = PedestrianFactory(world)
walker = pedFactory.spawn(walkerSpawnPoint)


world.wait_for_tick()


if walker is None:
    exit("Cannot spawn walker")
else:
    print(f"successfully spawn walker at {walkerSpawnPoint.location.x, walkerSpawnPoint.location.y, walkerSpawnPoint.location.z}")
    print(walker.get_control())
    print(walker.id)
    
    # visualizer.trackOnTick(walker.id, {"life_time": 1})      


time.sleep(1)

walkerAgent = PedestrianAgent(walker)

walkerAgent.set_destination(destination)
visualizer.drawDestinationPoint(destination)



def destoryActors():
    print('\ndestroying  walkers')
    walker.destroy()

def agentUpdate(world_snapshot):

    if walkerAgent.done():
        print(f"Walker {walkerAgent.walker.id} reached destination. Nothing to do")
        return

    if walkerAgent.canUpdate():
        control = walkerAgent.calculateControl()
        walker.apply_control(control)


stateManager = StateManager(client, trafficParticipants=[walker])


onTickers = [visualizer.onTick, stateManager.onTick, agentUpdate]
onEnders = [destoryActors]
simulator = Simulator(client, onTickers=onTickers, onEnders=onEnders)

simulator.run(1000)



