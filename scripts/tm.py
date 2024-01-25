exec(open("sys_path_hack.py").read())

import argparse
import logging
import random
import time

import carla
import eventlet

eventlet.monkey_patch()

from agents.navigation.basic_agent import \
    BasicAgent  # pylint: disable=import-error
from agents.navigation.behavior_agent import \
    BehaviorAgent  # pylint: disable=import-error
from lib import MapManager, MapNames, SimulationVisualization, Simulator
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
client.set_timeout(10)



mapManager = MapManager(client)
mapManager.load(MapNames.circle_t_junctions)
# mapManager.load(MapNames.Town01_Opt, carla.MapLayer.NONE)
# mapManager.load(MapNames.Town03_Opt, carla.MapLayer.NONE)
# mapManager.load(MapNames.Town02_Opt, carla.MapLayer.NONE)
# mapManager.load(MapNames.Town04_Opt, carla.MapLayer.NONE)
# mapManager.load(MapNames.Town05_Opt, carla.MapLayer.NONE)
# mapManager.load(MapNames.Town07_Opt, carla.MapLayer.NONE)
# mapManager.load(MapNames.Town10HD_Opt, carla.MapLayer.NONE)


visualizer = SimulationVisualization(client, mapManager)
# visualizer.draw00()

map = mapManager.map


# visualizer.drawSpawnPoints(dropout=0.8)
# visualizer.drawSpectatorPoint()
# visualizer.drawAllWaypoints(life_time=0.0)

world = client.get_world()
controllers = world.get_blueprint_library().filter('controller.*')
print(controllers)


# @todo cannot import these directly.
bpLib = world.get_blueprint_library()
vehicles_list = []
traffic_manager = client.get_trafficmanager(args.tm_port)
traffic_manager.set_global_distance_to_leading_vehicle(2.5)
SetAutopilot = carla.command.SetAutopilot
FutureActor = carla.command.FutureActor
batch = []
vehicleBps = bpLib.filter('vehicle.*')

spawn_points = mapManager.spawn_points

for n, transform in enumerate(spawn_points):
    if n >= 5:
        break
    blueprint = random.choice(vehicleBps)
    if blueprint.has_attribute('color'):
        color = random.choice(blueprint.get_attribute('color').recommended_values)
        blueprint.set_attribute('color', color)
    if blueprint.has_attribute('driver_id'):
        driver_id = random.choice(blueprint.get_attribute('driver_id').recommended_values)
        blueprint.set_attribute('driver_id', driver_id)
    else:
        blueprint.set_attribute('role_name', 'autopilot')

    # spawn the cars and set their autopilot and light state all together
    batch.append(SpawnActor(blueprint, transform)
        .then(SetAutopilot(FutureActor, True, traffic_manager.get_port())))

for response in client.apply_batch_sync(batch, True):
    if response.error:
        logging.error("vehicle", response.error)
    else:
        vehicles_list.append(response.actor_id)

def destoryActors():
    print('\ndestroying %d vehicles' % len(vehicles_list))
    client.apply_batch([carla.command.DestroyActor(x) for x in vehicles_list])

time.sleep(5)
destoryActors()

print(client.get_available_maps())