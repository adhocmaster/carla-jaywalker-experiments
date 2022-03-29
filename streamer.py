import carla
from carla import ColorConverter as cc

def process_img(image):
    image.convert(cc.Raw)
    image.save_to_disk('_out/%08d' % image.frame_number)

client = carla.Client('127.0.0.1', 2000)
client.set_timeout(2.0)

world = client.get_world()
spectator = world.get_actors().filter('spectator')[0]

bp_library = world.get_blueprint_library()
camera_bp = bp_library.find('sensor.camera.rgb')
camera_bp.set_attribute('image_size_x', '640')
camera_bp.set_attribute('image_size_y', '360')

camera = world.spawn_actor(camera_bp, spectator.get_transform())
camera.listen(process_img)

try:
    while True:
        world.wait_for_tick()
except KeyboardInterrupt:
    camera.destroy