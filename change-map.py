import carla
import argparse
import logging
import random
import time
import eventlet
eventlet.monkey_patch()

from agents.navigation.behavior_agent import BehaviorAgent  # pylint: disable=import-error
from agents.navigation.basic_agent import BasicAgent  # pylint: disable=import-error

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

print(client.get_available_maps())

if client.get_client_version() != client.get_server_version():
    logging.warning("Client and server version mistmatch. May not work properly.")


mapManager = MapManager(client)
# mapManager.load(MapNames.t_junction)
# mapManager.load(MapNames.circle_t_junctions)

# mapManager.load(MapNames.Town02_Opt, carla.MapLayer.GROUND)
mapManager.load(MapNames.Town02_Opt, carla.MapLayer.NONE)
mapManager.load(MapNames.Town04_Opt, carla.MapLayer.NONE)

# world = mapManager.world

# time_delta = 0.01
# settings = world.get_settings()
# settings.substepping = False
# settings.fixed_delta_seconds = time_delta
# world.apply_settings(settings)

visualizer = SimulationVisualization(client, mapManager)
# visualizer.draw00()

map = mapManager.map


visualizer.drawSpawnPoints(dropout=0.8)
visualizer.drawSpectatorPoint()
visualizer.drawAllWaypoints(life_time=0.0)

# exit(0)