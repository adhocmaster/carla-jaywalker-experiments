import carla
import argparse
import logging
import random
import time
import os

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

args = argparser.parse_args()

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

client = carla.Client(args.host, args.port)
client.set_timeout(5.0)

logging.info(f"Client carla version: {client.get_client_version()}")
logging.info(f"Server carla version: {client.get_server_version()}")

if client.get_client_version() != client.get_server_version():
    logging.warning("Client and server version mistmatch. May not work properly.")


world = client.get_world()

# print(client.get_available_maps())

world = client.load_world('circle_t_junctions')

spectator = world.get_spectator()
spectator.set_transform(carla.Transform(carla.Location(x=-100, y=0, z=150), carla.Rotation(pitch=-90)))


print("A random location on sidewalk", world.get_random_location_from_navigation())
exit(0)

# open drive

# file = "roads/test_generateWithHorizontalControlines.xodr"
# xodr = ""
# with open(file, encoding='utf-8') as f:
#     xodr = f.read()

#     vertex_distance = 2.0  # in meters
#     max_road_length = 500.0 # in meters
#     wall_height = 1.0      # in meters
#     extra_width = 0.6      # in meters
#     config = carla.OpendriveGenerationParameters(
#                     vertex_distance=vertex_distance,
#                     max_road_length=max_road_length,
#                     wall_height=wall_height,
#                     additional_width=extra_width,
#                     smooth_junctions=True,
#                     enable_mesh_visibility=True,
#                     enable_pedestrian_navigation=True)
#     world = client.generate_opendrive_world(opendrive=xodr, parameters=config, reset_settings=True) 


# world = client.load_world('Town10HD')




# 1. take all the random locations to spawn
spawn_points = []
for i in range(5):
    spawn_point = carla.Transform()
    loc = world.get_random_location_from_navigation()
    # loc = world.get_random_location()
    print(loc)
    if (loc != None):
        spawn_point.location = loc
        spawn_points.append(spawn_point)

print(spawn_points)

actorIndex = 4


spectator = world.get_spectator()
# spectator.set_transform(carla.Transform(carla.Location(x=-70, y=0, z=150), carla.Rotation(pitch=-90)))
spectator.set_transform(carla.Transform(spawn_points[actorIndex].location + carla.Location(z=50), carla.Rotation(pitch=-90)))

# spawn a walker
bpLib = world.get_blueprint_library()
peds = bpLib.filter('walker.pedestrian.*')
# print(peds)

walker_speed = []
batch = []
for spawn_point in spawn_points:
    walker_bp = random.choice(peds)
    # set as not invincible
    if walker_bp.has_attribute('is_invincible'):
        walker_bp.set_attribute('is_invincible', 'false')
    # set the max speed
    if walker_bp.has_attribute('speed'):
        if (random.random() > 0.5):
            # walking
            walker_speed.append(walker_bp.get_attribute('speed').recommended_values[1])
        else:
            # running
            walker_speed.append(walker_bp.get_attribute('speed').recommended_values[2])
    else:
        print("Walker has no speed")
        walker_speed.append(0.0)
    batch.append(SpawnActor(walker_bp, spawn_point))

results = client.apply_batch_sync(batch, True)

walkers_list = []
walker_speed2 = []
for i in range(len(results)):
    if results[i].error:
        logging.error(results[i].error)
    else:
        walkers_list.append({"id": results[i].actor_id})
        walker_speed2.append(walker_speed[i])
walker_speed = walker_speed2


# 3. we spawn the walker controller
all_id = []
batch = []
walker_controller_bp = world.get_blueprint_library().find('controller.ai.walker')
for i in range(len(walkers_list)):
    batch.append(SpawnActor(walker_controller_bp, carla.Transform(), walkers_list[i]["id"]))
results = client.apply_batch_sync(batch, True)
for i in range(len(results)):
    if results[i].error:
        logging.error(results[i].error)
    else:
        walkers_list[i]["con"] = results[i].actor_id
# 4. we put together the walkers and controllers id to get the objects from their id
for i in range(len(walkers_list)):
    all_id.append(walkers_list[i]["con"])
    all_id.append(walkers_list[i]["id"])
all_actors = world.get_actors(all_id)


# 5. initialize each controller and set target to walk to (list is [controler, actor, controller, actor ...])
# set how many pedestrians can cross the road
world.set_pedestrians_cross_factor(1)
for i in range(0, len(all_id), 2):
    # start walker
    all_actors[i].start()
    # set walk to random point
    all_actors[i].go_to_location(world.get_random_location_from_navigation())
    # max speed
    all_actors[i].set_max_speed(float(walker_speed[int(i/2)]))

# print('spawned %d vehicles and %d walkers, press Ctrl+C to exit.' % (len(vehicles_list), len(walkers_list)))

# def onTick(snapshot):
#     print("world ticks")
# world.on_tick(onTick)
# world_snapshot = world.wait_for_tick()
# print("first tick")

# Debug
debug = world.debug

print(walkers_list)

for i in range(1000):
    world_snapshot = world.wait_for_tick()
    print("world ticks")

    for walker in walkers_list:
        actor_snapshot = world_snapshot.find(walker['id'])
        debug.draw_box(carla.BoundingBox(actor_snapshot.get_transform().location,carla.Vector3D(0.5,0.5,2)),actor_snapshot.get_transform().rotation, 0.05, carla.Color(0,0,0,0),0)


# clean 

print('\ndestroying %d walkers' % len(walkers_list))
client.apply_batch([carla.command.DestroyActor(x) for x in all_id])

time.sleep(0.5)

