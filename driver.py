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
    help='TCP port to listen to (default: 3000)')
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


visualizer.drawSpawnPoints()
visualizer.drawSpectatorPoint()
visualizer.drawAllWaypoints(life_time=0.0)


bpLib = world.get_blueprint_library()
vehicleBps = bpLib.filter('vehicle.*')
blueprint = random.choice(vehicleBps)


spawn_points = mapManager.spawn_points

spawnPoint = random.choice(spawn_points)

if blueprint.has_attribute('color'):
    color = random.choice(blueprint.get_attribute('color').recommended_values)
    blueprint.set_attribute('color', color)
if blueprint.has_attribute('driver_id'):
    driver_id = random.choice(blueprint.get_attribute('driver_id').recommended_values)
    blueprint.set_attribute('driver_id', driver_id)
else:
    blueprint.set_attribute('role_name', 'autopilot')


vehicle = world.try_spawn_actor(blueprint, spawnPoint)
world.wait_for_tick()

if vehicle is None:
    exit("Cannot spawn vehicle")
else:
    print(f"successfully spawn vehicle at {spawnPoint.location.x, spawnPoint.location.y, spawnPoint.location.z}")
    print(vehicle.get_acceleration())
    print(vehicle.get_velocity())
    print(vehicle.get_location())
    print(vehicle.id)
    # vehicle.set_target_velocity(carla.Vector3D(10, 10))
    print(vehicle.get_velocity())


time.sleep(1)

agent = BasicAgent(vehicle, target_speed=20)
destination = random.choice(mapManager.spawn_points).location
agent.set_destination(destination)
visualizer.drawDestinationPoint(destination)



def destoryActors():
    print('\ndestroying  vehicles')
    vehicle.destroy()

def agentUpdate(world_snapshot):
    if agent.done():
        destination = random.choice(mapManager.spawn_points).location
        agent.set_destination(destination)
        print("The target has been reached, searching for another target")
        visualizer.drawDestinationPoint(destination)

    
    control = agent.run_step()
    control.manual_gear_shift = False
    vehicle.apply_control(control)


stateManager = StateManager(client, trafficParticipants=[vehicle])


onTickers = [visualizer.onTick, stateManager.onTick, agentUpdate]
onEnders = [destoryActors]
simulator = Simulator(client, onTickers=onTickers, onEnders=onEnders)

simulator.run(10000)



